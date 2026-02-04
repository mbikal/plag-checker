"""Certificate authority helpers."""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from backend import config


def ensure_ca():
    """Ensure a local CA exists and return (private_key, certificate)."""
    ca_key_path = os.path.join(config.CA_DIR, "ca.key")
    ca_cert_path = os.path.join(config.CA_DIR, "ca.crt")

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


def generate_certificate(username: str, role: str) -> str:
    """Generate a certificate for a user and return path to cert file."""
    ca_key, ca_cert = ensure_ca()
    user_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, username),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "plag checker"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, role),
        ]
    )

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

    cert_path = os.path.join(config.CERT_DIR, f"{username}.crt")
    key_path = os.path.join(config.CERT_DIR, f"{username}.key")

    with open(cert_path, "wb") as f_cert:
        f_cert.write(cert.public_bytes(serialization.Encoding.PEM))

    with open(key_path, "wb") as f_key:
        f_key.write(
            user_key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            )
        )

    return cert_path


def verify_certificate(cert_bytes: bytes, username: str, role: str) -> str | None:
    """Validate a user certificate against the local CA."""
    ca_cert_path = os.path.join(config.CA_DIR, "ca.crt")
    if not os.path.exists(ca_cert_path):
        return "CA certificate not found"
    with open(ca_cert_path, "rb") as ca_handle:
        ca_cert = x509.load_pem_x509_certificate(ca_handle.read())

    try:
        cert = x509.load_pem_x509_certificate(cert_bytes)
    except ValueError:
        return "Invalid certificate format"

    if cert.issuer != ca_cert.subject:
        return "Certificate issuer mismatch"

    try:
        ca_cert.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
    except Exception:  # pylint: disable=broad-except
        return "Certificate signature invalid"

    now = datetime.utcnow()
    if cert.not_valid_before > now or cert.not_valid_after < now:
        return "Certificate is expired or not yet valid"

    subject = cert.subject
    common_names = subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    if not common_names or common_names[0].value != username:
        return "Certificate username mismatch"

    org_units = subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)
    if role and (not org_units or org_units[0].value != role):
        return "Certificate role mismatch"

    return None
