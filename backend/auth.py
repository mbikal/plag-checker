from flask import Flask, request, jsonify
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from datetime import datetime, timedelta
import bcrypt
import json
import os

app = Flask(__name__)

USERS_FILE = 'users.json'
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CA_DIR = os.path.join(BASE_DIR, "ca/")
cert_dir = os.path.join(BASE_DIR, "certs/")
os.makedirs(cert_dir, exist_ok=True)

# load existing users
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as file_handle:
            return json.load(file_handle)
    return {}

users = load_users()

# load CA private key and certificate
with open(os.path.join(CA_DIR, 'ca.key'), 'rb') as f_key:
    ca_key = serialization.load_pem_private_key(f_key.read(), None)

with open(os.path.join(CA_DIR, 'ca.crt'), 'rb') as f_cert:
    ca_cert = x509.load_pem_x509_certificate(f_cert.read())

#--------- ceritificate generation ---------
def generate_certificate(username, role):
    user_key = rsa.generate_private_key(
        publicexponent=65537,
        key_size=2048,
    )

    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, username),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "plag checker"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, role),

    ])

    cert = (
        x509.Name([
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(ca_cert.subject)
            .public_key(user_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .sign(ca_key, hashes.SHA256())
        ])
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

#--------- user registration ---------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    if username in users:
        return jsonify({'error': 'Username already exists'}), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users[username] = {
        'password': hashed_password,
        'role': role
    }

    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent = 4)

    return jsonify({'message': 'User registered successfully'}), 201

#--------- user login ---------
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

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
    app.run(debug=True)
    