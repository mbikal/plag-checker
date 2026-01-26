"""
Authentication module for plagiarism checker application.
Handles user registration, login, and certificate generation.
"""
import json
import os
import sys
import tempfile
import re
from datetime import datetime, timedelta

import bcrypt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from flask import Flask, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(BASE_DIR, "plag-system"))
from checker import analyze_and_sign  # pylint: disable=wrong-import-position,import-error

app = Flask(__name__)
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
CA_DIR = os.path.join(BASE_DIR, "ca/")
cert_dir = os.path.join(BASE_DIR, "certs/")
os.makedirs(cert_dir, exist_ok=True)
os.makedirs(CA_DIR, exist_ok=True)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")


@app.after_request
def add_cors_headers(response):
    """Add CORS headers to API responses."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def _password_error(password):
    """Return a validation error message for invalid passwords."""
    if len(password) < 8:
        return 'Password must be at least 8 characters long'
    if not re.search(r"[A-Z]", password):
        return 'Password must include an uppercase letter'
    if not re.search(r"[a-z]", password):
        return 'Password must include a lowercase letter'
    if not re.search(r"\d", password):
        return 'Password must include a number'
    if not re.search(r"[^A-Za-z0-9]", password):
        return 'Password must include a symbol'
    return None


def load_users():
    """Load existing users from the users file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as file_handle:
            try:
                return json.load(file_handle)
            except json.JSONDecodeError:
                return {}
    return {}


def _ensure_ca():
    ca_key_path = os.path.join(CA_DIR, "ca.key")
    ca_cert_path = os.path.join(CA_DIR, "ca.crt")

    if os.path.exists(ca_key_path) and os.path.exists(ca_cert_path):
        with open(ca_key_path, "rb") as f_key:
            ca_key = serialization.load_pem_private_key(f_key.read(), None)
        with open(ca_cert_path, "rb") as f_cert:
            ca_cert = x509.load_pem_x509_certificate(f_cert.read())
        return ca_key, ca_cert

    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Plag Checker"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Plag Checker CA"),
        ]
    )
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(ca_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    with open(ca_key_path, "wb") as f_key:
        f_key.write(
            ca_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    with open(ca_cert_path, "wb") as f_cert:
        f_cert.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    return ca_key, ca_cert


def generate_certificate(username, role):
    """
    Generate a certificate for a user.

    Args:
        username: The username for the certificate
        role: The role of the user (e.g., 'student', 'teacher')

    Returns:
        str: Path to the generated certificate file
    """
    ca_key, ca_cert = _ensure_ca()
    user_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, username),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "plag checker"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, role),
    ])

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(user_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .sign(ca_key, hashes.SHA256())
    )

    cert_path = os.path.join(cert_dir, f"{username}.crt")
    key_path = os.path.join(cert_dir, f"{username}.key")

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, "wb") as f:
        f.write(
            user_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            )
        )

    return cert_path


@app.route('/signup', methods=['POST'])
def signup():
    """
    Handle user registration.

    Returns:
        JSON response with success message or error
    """
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    password_error = _password_error(password)
    if password_error:
        return jsonify({'error': password_error}), 400

    users = load_users()
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    users[username] = {
        'password': hashed_password,
        'role': role
    }

    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    """
    Handle user login and certificate generation.

    Returns:
        JSON response with login status and certificate path
    """
    if not request.is_json:
        return jsonify({'error': 'JSON body required'}), 400

    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Invalid username or password'}), 401

    users = load_users()
    if username not in users:
        return jsonify({'error': 'Invalid username or password'}), 401

    stored_password = users[username]['password'].encode('utf-8')
    if not bcrypt.checkpw(password.encode('utf-8'), stored_password):
        return jsonify({'error': 'Invalid username or password'}), 401

    role = users[username]['role']
    cert_path = generate_certificate(username, role)

    return jsonify({
        'message': "Login successful",
        "role": role,
        "certificate_path": cert_path
    })


@app.route('/scan', methods=['POST'])
def scan():
    """
    Handle file upload and plagiarism scan.
    """
    if "file" not in request.files:
        return jsonify({"error": "File is required"}), 400

    uploaded = request.files["file"]
    if not uploaded.filename:
        return jsonify({"error": "Filename is required"}), 400
    if not uploaded.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400
    if uploaded.mimetype not in ("application/pdf", "application/x-pdf"):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(uploaded.filename)
    with tempfile.NamedTemporaryFile(
        dir=UPLOAD_DIR,
        suffix=f"_{filename}",
        delete=False,
    ) as temp_file:
        uploaded.save(temp_file.name)
        temp_path = temp_file.name

    scan_id = os.urandom(8).hex()
    annotated_path = os.path.join(UPLOAD_DIR, f"scan_{scan_id}.pdf")
    try:
        report = analyze_and_sign(temp_path, annotated_pdf_path=annotated_path)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    response = dict(report)
    base_url = request.host_url.rstrip("/")
    response["pdf_url"] = (
        f"{base_url}/scan/{scan_id}/pdf"
    )
    return jsonify(response)


@app.route('/scan/<scan_id>/pdf', methods=['GET'])
def scan_pdf(scan_id):
    """
    Serve annotated PDF for a completed scan.
    """
    filename = f"scan_{scan_id}.pdf"
    pdf_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(pdf_path):
        return jsonify({"error": "Scan not found"}), 404
    return send_file(pdf_path, mimetype="application/pdf")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if not os.path.isdir(FRONTEND_DIST):
        return jsonify({"error": "Frontend build not found"}), 404
    if path and os.path.exists(os.path.join(FRONTEND_DIST, path)):
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, "index.html")


if __name__ == '__main__':
    app.run(debug=False)
