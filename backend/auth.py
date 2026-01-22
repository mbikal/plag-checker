"""
Authentication module for plagiarism checker application.
Handles user registration, login, and certificate generation.
"""
import json
import os
from datetime import datetime, timedelta

import bcrypt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from flask import Flask, request, jsonify

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
CA_DIR = os.path.join(BASE_DIR, "ca/")
cert_dir = os.path.join(BASE_DIR, "certs/")
os.makedirs(cert_dir, exist_ok=True)


def load_users():
    """Load existing users from the users file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as file_handle:
            return json.load(file_handle)
    return {}


# load CA private key and certificate
with open(os.path.join(CA_DIR, 'ca.key'), 'rb') as f_key:
    ca_key = serialization.load_pem_private_key(f_key.read(), None)

with open(os.path.join(CA_DIR, 'ca.crt'), 'rb') as f_cert:
    ca_cert = x509.load_pem_x509_certificate(f_cert.read())


def generate_certificate(username, role):
    """
    Generate a certificate for a user.

    Args:
        username: The username for the certificate
        role: The role of the user (e.g., 'student', 'teacher')

    Returns:
        str: Path to the generated certificate file
    """
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


if __name__ == '__main__':
    app.run(debug=False)
    
