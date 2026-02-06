# Plag Checker

## Tutorial video


https://github.com/user-attachments/assets/8c9911c3-3ca6-4971-9f82-9c495084d449





## Vite API URL (VITE_API_URL)
Use `VITE_API_URL` to point the frontend at the backend API.

macOS/Linux:
```bash
cd frontend
VITE_API_URL=http://127.0.0.1:5000 npm run dev
```

Windows (PowerShell):
```bash
cd frontend
$env:VITE_API_URL="http://127.0.0.1:5000"
npm run dev
```

In code, access it with `import.meta.env.VITE_API_URL`.

## Project overview and purpose
Plag Checker is a web application that helps detect plagiarism in PDF documents. Users can upload a PDF, compare it against a local corpus, and receive a similarity report with highlighted matches. The system also supports role-based access for admins, teachers, and students.

## System features
- User authentication with roles (admin, teacher, student).
- PDF upload and plagiarism scanning against a local corpus.
- Annotated PDF reports highlighting matched passages.
- Admin dashboard for logs, user management, and corpus management.
- Teacher dashboard to review uploads and reports.

## Technologies used
- React frontend (Vite)
- Python backend (Flask)
- Cryptography:
  - RSA key generation/sign/verify (`rsa.generate_private_key`, `ca_key.sign`, `public_key.verify`)
  - Ed25519 report signing (`Ed25519PrivateKey.generate`, `private_key.sign`)
  - PKCS#12 keystore (`pkcs12.serialize_key_and_certificates`, `pkcs12.load_key_and_certificates`)
  - AES‑GCM hybrid encryption (`AESGCM.encrypt`, `AESGCM.decrypt`)
  - Password hashing (`bcrypt.hashpw`, `bcrypt.checkpw`)
- PDF processing: `pdfplumber`, `PyPDF2`, `reportlab`
- CI/CD: GitHub Actions
- Containerization: Docker, Docker Compose

## Repo structure
```
backend/            Flask backend (auth, admin, scan, crypto, config)
frontend/           React frontend (Vite app)
plag_system/        Plagiarism engine + crypto helpers
uploads/            Encrypted scan outputs
plag_system/corpus/ Encrypted corpus PDFs
keys/               Master encryption key + signing keystore
ca/                 CA private key + cert
certs/              User certificates
README.md
Dockerfile
docker-compose.yml
requirements.txt
```

## Installation and setup instructions
1. Clone the repository and enter the project directory.
2. Create and activate a Python virtual environment.
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```
5. (Optional) Set the keystore password used for signing reports:
   ```bash
   export PLAG_KEYSTORE_PASSWORD="your-strong-password"
   ```

## How to run the frontend and backend
### Backend
From the repository root:
```bash
python3 backend/auth.py
```
The API will run at `http://127.0.0.1:5000`.

### Frontend
From the repository root:
```bash
cd frontend
npm run dev
```
The frontend will run at `http://localhost:5173` and will call the backend API.

## Docker setup
### Build the image
From the repository root:
```bash
docker build -t plag-checker:local .
```

### Run the container
```bash
docker run --rm -p 5000:5000 \
  -e PLAG_KEYSTORE_PASSWORD="your-strong-password" \
  plag-checker:local
```
The app will be available at `http://127.0.0.1:5000`.

### Docker Compose (optional)
If you want to use the included Compose file:
```bash
docker compose up --build
```

## GHCR publish steps (GitHub Actions only)
Images are published by GitHub Actions on tagged releases.

### Image names
- `ghcr.io/mbikal/plag-checker-frontend`
- `ghcr.io/mbikal/plag-checker-backend`

### Tag scheme
- Version tags: `v1.0.*` (for example `v1.0.4`)
- The workflow also applies `latest` for the most recent release.

### How to publish
1. Create a release tag (example):
   ```bash
   git tag v1.0.4
   git push origin v1.0.4
   ```
2. The GitHub Actions workflow builds and pushes both images to GHCR.

### Pulling a published image
```bash
docker pull ghcr.io/mbikal/plag-checker-backend:v1.0.4
docker pull ghcr.io/mbikal/plag-checker-frontend:v1.0.4
```

## Production deployment notes
- Use a production WSGI server (e.g., Gunicorn) instead of the Flask dev server.
- Store secrets such as `PLAG_KEYSTORE_PASSWORD` in a secure secret manager or environment variables.
- Mount persistent volumes for uploads, corpus files, and keystore storage.
- Ensure HTTPS is enabled and set appropriate CORS/host configurations.
