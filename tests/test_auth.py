import pytest
import bcrypt
from fastapi import HTTPException

from app.features.auth.service import AuthService


@pytest.fixture
def auth_service():
    return AuthService()


class TestAuthService:
    def test_verify_password(self, auth_service: AuthService):
        test_password = "testpassword"

        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(test_password.encode('utf-8'), salt)
        hashed_password = hashed_bytes.decode('utf-8')

        assert bcrypt.checkpw(test_password.encode('utf-8'), hashed_password.encode('utf-8')) is True
        assert bcrypt.checkpw("wrongpassword".encode('utf-8'), hashed_password.encode('utf-8')) is False

    def test_create_access_token(self, auth_service: AuthService):
        data = {
            "user_id": 1,
            "email": "test@example.com",
            "role": "CLIENT"
        }

        token = auth_service.create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_success(self, auth_service: AuthService):
        data = {
            "user_id": 1,
            "email": "test@example.com",
            "role": "CLIENT"
        }

        token = auth_service.create_access_token(data)
        token_data = auth_service.verify_token(token)

        assert token_data.user_id == data["user_id"]
        assert token_data.email == data["email"]
        assert token_data.role == data["role"]

    def test_verify_token_invalid(self, auth_service: AuthService):
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_token("invalid.token.here")

        assert exc_info.value.status_code == 401
        assert "Неверные учетные данные" in str(exc_info.value.detail)


class TestAuthAPI:
    def test_login_empty_password(self, sync_client):
        response = sync_client.post(
            "/auth/login-json",
            json={
                "email": "test@example.com",
                "password": ""
            }
        )

        print(f"Empty password login response: {response.status_code}")
        assert response.status_code in [401, 422]


def test_token_schema():
    from app.features.auth.schemas import Token

    token_data = Token(
        access_token="test_token",
        token_type="bearer",
        user_id=1,
        role="CLIENT"
    )

    assert token_data.access_token == "test_token"
    assert token_data.token_type == "bearer"
    assert token_data.user_id == 1
    assert token_data.role == "CLIENT"


def test_user_login_schema():
    from app.features.auth.schemas import UserLogin

    login_data = UserLogin(
        email="test@example.com",
        password="password123"
    )

    assert login_data.email == "test@example.com"
    assert login_data.password == "password123"


def test_token_data_schema():
    from app.features.auth.schemas import TokenData

    token_data = TokenData(
        user_id=1,
        email="test@example.com",
        role="CLIENT"
    )

    assert token_data.user_id == 1
    assert token_data.email == "test@example.com"
    assert token_data.role == "CLIENT"


def test_auth_service_init():
    auth_service = AuthService()

    assert auth_service.secret_key is not None
    assert auth_service.algorithm == "HS256"
    assert auth_service.access_token_expire_minutes == 30
    assert auth_service.pwd_context is not None


def test_password_hashing():
    password = "test123"
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    hashed = hashed_bytes.decode('utf-8')

    assert hashed is not None
    assert isinstance(hashed, str)
    assert len(hashed) > 0

    assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')) is True
    assert bcrypt.checkpw("wrong".encode('utf-8'), hashed.encode('utf-8')) is False

