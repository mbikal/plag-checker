"""
Unit tests for the authentication module.
"""
import json
import os
import sys
import tempfile
import pytest

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pylint: disable=wrong-import-position,import-error
from backend.auth import app, load_users, generate_certificate


@pytest.fixture(name='test_client')
def fixture_client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(name='users_file')
def fixture_temp_users_file():
    """Create a temporary users file for testing."""
    temp_fd, temp_path = tempfile.mkstemp(suffix='.json')
    os.close(temp_fd)

    # Store original USERS_FILE
    # pylint: disable=import-outside-toplevel
    import backend.auth as auth_module
    original_users_file = auth_module.USERS_FILE
    auth_module.USERS_FILE = temp_path

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)
    auth_module.USERS_FILE = original_users_file


class TestLoadUsers:
    """Tests for the load_users function."""

    def test_load_users_empty_file(self, users_file):
        """Test loading users when file doesn't exist."""
        os.remove(users_file)
        users = load_users()
        assert users == {}

    def test_load_users_with_data(self, users_file):
        """Test loading users with existing data."""
        test_data = {
            'testuser': {
                'password': 'hashed_password',
                'role': 'student'
            }
        }
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # pylint: disable=import-outside-toplevel
        import backend.auth as auth_module
        auth_module.USERS_FILE = users_file
        users = load_users()
        assert 'testuser' in users
        assert users['testuser']['role'] == 'student'


class TestSignup:
    """Tests for the signup endpoint."""

    def test_signup_success(self, test_client, users_file):  # pylint: disable=unused-argument
        """Test successful user registration."""
        response = test_client.post('/signup', json={
            'username': 'newuser',
            'password': 'Password123!',
            'role': 'student'
        })
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User registered successfully'

    def test_signup_missing_username(self, test_client):
        """Test signup with missing username."""
        response = test_client.post('/signup', json={
            'password': 'password123'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_signup_missing_password(self, test_client):
        """Test signup with missing password."""
        response = test_client.post('/signup', json={
            'username': 'testuser'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_signup_requires_json(self, test_client):
        """Test signup with non-JSON body."""
        response = test_client.post('/signup', data='username=testuser')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_signup_duplicate_username(self, test_client, users_file):  # pylint: disable=unused-argument
        """Test signup with duplicate username."""
        # First signup
        test_client.post('/signup', json={
            'username': 'duplicate',
            'password': 'Password123!'
        })

        # Second signup with same username
        response = test_client.post('/signup', json={
            'username': 'duplicate',
            'password': 'Password456!'
        })
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']


class TestLogin:
    """Tests for the login endpoint."""

    @pytest.fixture(name='user')
    def fixture_registered_user(self, test_client, users_file):  # pylint: disable=unused-argument
        """Create a registered user for login tests."""
        test_client.post('/signup', json={
            'username': 'testuser',
            'password': 'Testpass123!',
            'role': 'student'
        })
        return {'username': 'testuser', 'password': 'Testpass123!'}

    def test_login_success(self, test_client, user):
        """Test successful login."""
        response = test_client.post('/login', json={
            'username': user['username'],
            'password': user['password']
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Login successful'
        assert 'role' in data
        assert 'certificate_path' in data

    def test_login_invalid_username(self, test_client):
        """Test login with invalid username."""
        response = test_client.post('/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid username or password' in data['error']

    def test_login_invalid_password(self, test_client, user):
        """Test login with invalid password."""
        response = test_client.post('/login', json={
            'username': user['username'],
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'Invalid username or password' in data['error']

    def test_login_requires_json(self, test_client):
        """Test login with non-JSON body."""
        response = test_client.post('/login', data='username=testuser')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestCors:
    """Tests for CORS headers."""

    def test_cors_headers_present(self, test_client):
        """CORS headers should be present on API responses."""
        response = test_client.post('/signup', json={
            'username': 'corsuser',
            'password': 'password123',
            'role': 'student'
        })
        assert response.headers.get('Access-Control-Allow-Origin') == '*'

    def test_options_preflight(self, test_client):
        """Preflight requests should include CORS headers."""
        response = test_client.options('/signup')
        assert response.status_code in (200, 204)
        assert response.headers.get('Access-Control-Allow-Origin') == '*'


class TestGenerateCertificate:
    """Tests for certificate generation."""

    def test_generate_certificate_creates_files(self):
        """Test that certificate generation creates cert and key files."""
        username = 'testuser_cert'
        role = 'student'

        cert_path = generate_certificate(username, role)

        # Check certificate file exists
        assert os.path.exists(cert_path)
        assert cert_path.endswith('.crt')

        # Check key file exists
        key_path = cert_path.replace('.crt', '.key')
        assert os.path.exists(key_path)

        # Cleanup
        if os.path.exists(cert_path):
            os.remove(cert_path)
        if os.path.exists(key_path):
            os.remove(key_path)

    def test_generate_certificate_returns_path(self):
        """Test that certificate generation returns correct path."""
        username = 'testuser_path'
        role = 'teacher'

        cert_path = generate_certificate(username, role)

        assert username in cert_path
        assert cert_path.endswith('.crt')

        # Cleanup
        key_path = cert_path.replace('.crt', '.key')
        if os.path.exists(cert_path):
            os.remove(cert_path)
        if os.path.exists(key_path):
            os.remove(key_path)
