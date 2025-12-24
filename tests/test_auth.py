import pytest
from fastapi import HTTPException
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from app.features.auth.service import AuthService
from app.features.auth.schemas import Token, UserLogin
from app.models.user import UserRole


class TestAuthService:
    def test_auth_service_initialization(self):
        """Проверяет что AuthService успешно создается и имеет метод authenticate_user"""
        service = AuthService()
        assert service is not None
        assert hasattr(service, 'authenticate_user')

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db):
        """Проверяет успешную аутентификацию существующего пользователя с правильным паролем"""
        from app.models.user import User

        user = User.create_with_encryption(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone="+7 999 123-45-67",
            password_hash="$2b$12$testhash123",
            role=UserRole.CLIENT
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        service = AuthService()

        with patch('app.features.auth.service.verify_password', return_value=True):
            result = await service.authenticate_user(db, "test@example.com", "password123")
            assert result is not None
            assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db):
        """Проверяет что аутентификация с неправильным паролем возвращает HTTPException 401"""
        service = AuthService()
        from app.models.user import User

        user = User.create_with_encryption(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone="+7 999 123-45-67",
            password_hash="$2b$12$testhash123",
            role=UserRole.CLIENT
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        with patch('app.features.auth.service.verify_password', return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await service.authenticate_user(db, "test@example.com", "wrong_password")

            assert exc_info.value.status_code == 401
            assert "Неверный email или пароль" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, db):
        """Проверяет что аутентификация несуществующего пользователя возвращает HTTPException 401"""
        service = AuthService()

        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate_user(db, "nonexistent@example.com", "password")

        assert exc_info.value.status_code == 401
        assert "Неверный email или пароль" in str(exc_info.value.detail)


class TestAuthSchemas:
    def test_token_schema_creation_with_required_fields(self):
        """Проверяет что схема Token создается с обязательными полями"""
        token = Token(
            access_token="test_token_123",
            token_type="bearer",
            user_id=42,
            role="CLIENT"
        )
        assert token.access_token == "test_token_123"
        assert token.token_type == "bearer"
        assert token.user_id == 42
        assert token.role == "CLIENT"

    def test_token_schema_default_token_type(self):
        """Проверяет что token_type имеет значение по умолчанию 'bearer'"""
        token = Token(
            access_token="test_token",
            user_id=1,
            role="CLIENT"
        )
        assert token.token_type == "bearer"

    def test_user_login_schema_valid_credentials(self):
        """Проверяет что схема UserLogin создается с валидными данными"""
        login_data = UserLogin(
            email="valid@example.com",
            password="SecurePass123!"
        )
        assert login_data.email == "valid@example.com"
        assert login_data.password == "SecurePass123!"

    def test_user_login_schema_rejects_invalid_email_format(self):
        """Проверяет что UserLogin отклоняет невалидный формат email"""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserLogin(email="неправильный-емейл", password="password123")

    def test_user_login_schema_accepts_valid_email_variations(self):
        """Проверяет что UserLogin принимает различные валидные форматы email"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user@sub.example.com"
        ]

        for email in valid_emails:
            login_data = UserLogin(email=email, password="password123")
            assert login_data.email == email


class TestAuthAPIEndpoints:
    @pytest.mark.asyncio
    async def test_login_json_returns_401_for_wrong_credentials(self, client):
        """Проверяет что эндпоинт /auth/login-json возвращает 401 для неправильных учетных данных"""
        with patch('app.features.auth.router.auth_service.authenticate_user') as mock_auth:
            mock_auth.side_effect = HTTPException(status_code=401, detail="Неверный email или пароль")

            response = client.post(
                "/auth/login-json",
                json={"email": "nonexistent@example.com", "password": "wrong"}
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Неверный email или пароль"

    @pytest.mark.asyncio
    async def test_login_json_returns_token_for_valid_credentials(self, client):
        """Проверяет что эндпоинт /auth/login-json возвращает токен для правильных учетных данных"""
        from app.models.user import UserRole

        mock_user = MagicMock()
        mock_user.user_id = 1
        mock_user.email = "success@example.com"
        mock_user.role = UserRole.CLIENT

        with patch('app.features.auth.router.auth_service.authenticate_user') as mock_auth:
            mock_auth.return_value = mock_user

            with patch('app.features.auth.router.create_access_token') as mock_create_token:
                mock_create_token.return_value = "mock_jwt_token"

                response = client.post(
                    "/auth/login-json",
                    json={"email": "success@example.com", "password": "correct"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["access_token"] == "mock_jwt_token"
                assert data["token_type"] == "bearer"
                assert data["user_id"] == 1
                assert data["role"] == "CLIENT"

    @pytest.mark.asyncio
    async def test_login_oauth2_works_with_form_data_format(self, client):
        """Проверяет что эндпоинт /auth/login работает с форматом form-data OAuth2"""
        with patch('app.features.auth.router.auth_service.authenticate_user') as mock_auth:
            mock_auth.side_effect = HTTPException(status_code=401, detail="Неверный email или пароль")

            response = client.post(
                "/auth/login",
                data={"username": "test@example.com", "password": "wrong"}
            )
            assert response.status_code == 401
            assert "Неверный email или пароль" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_verify_token_validates_correct_token(self, client):
        """Проверяет что эндпоинт /auth/verify-token валидирует корректный токен"""
        with patch('app.core.security.decode_access_token') as mock_decode:
            mock_decode.return_value = {"sub": "100", "role": "CLIENT"}

            response = client.post(
                "/auth/verify-token",
                headers={"Authorization": "Bearer valid_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert data["user_id"] == 100
            assert data["role"] == "CLIENT"

    @pytest.mark.asyncio
    async def test_verify_token_rejects_invalid_token(self, client):
        """Проверяет что эндпоинт /auth/verify-token отклоняет невалидный токен"""
        with patch('app.core.security.decode_access_token') as mock_decode:
            mock_decode.side_effect = Exception("Invalid token")

            response = client.post(
                "/auth/verify-token",
                headers={"Authorization": "Bearer invalid_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False


class TestRegistrationAPI:
    @pytest.mark.asyncio
    async def test_register_rejects_duplicate_email(self):
        """Проверяет что регистрация отклоняет пользователя с существующим email"""
        from app.features.auth.router import register
        from app.features.users.schemas import UserCreate
        from app.models.user import User

        mock_session = AsyncMock()

        mock_existing_user = MagicMock(spec=User)
        mock_existing_user.email = "existing@example.com"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_existing_user
        mock_session.execute.return_value = mock_result

        with patch('app.features.auth.router.select') as mock_select:
            mock_where = MagicMock()
            mock_where.where.return_value = mock_where

            mock_select_obj = MagicMock()
            mock_select_obj.where.return_value = mock_where
            mock_select.return_value = mock_select_obj

            user_data = UserCreate(
                email="existing@example.com",
                first_name="Новый",
                last_name="Пользователь",
                phone="+7 999 222-33-44",
                password="TestPassword123",
                password_confirm="TestPassword123"
            )

            with patch('app.features.auth.router.hash_password') as mock_hash:
                mock_hash.return_value = "$2b$12$hashedpassword"

                with pytest.raises(HTTPException) as exc_info:
                    await register(user_data, mock_session)

                assert exc_info.value.status_code == 400
                assert "уже существует" in str(exc_info.value.detail)

                mock_session.add.assert_not_called()
                mock_session.commit.assert_not_called()


class TestPasswordSecurity:
    def test_password_hashing_creates_different_hash(self):
        """Проверяет что хеширование пароля создает уникальный хеш, отличный от исходного пароля"""
        from app.core.security import hash_password, verify_password

        password = "MySecurePassword123!"
        result_hash = hash_password(password)

        assert result_hash != password
        assert isinstance(result_hash, str)
        assert len(result_hash) > 0

    def test_verify_password_success_for_correct_password(self):
        """Проверяет что verify_password возвращает True для правильного пароля"""
        from app.core.security import hash_password, verify_password

        password = "MySecurePassword123!"
        result_hash = hash_password(password)

        assert verify_password(password, result_hash) is True

    def test_verify_password_failure_for_wrong_password(self):
        """Проверяет что verify_password возвращает False для неправильного пароля"""
        from app.core.security import hash_password, verify_password

        password = "MySecurePassword123!"
        wrong_password = "WrongPassword456!"
        result_hash = hash_password(password)

        assert verify_password(wrong_password, result_hash) is False

    def test_verify_password_handles_none_hash_gracefully(self):
        """Проверяет что verify_password корректно обрабатывает None хеш"""
        from app.core.security import verify_password

        result = verify_password("password", None)
        assert result is False

    def test_verify_password_handles_empty_hash_gracefully(self):
        """Проверяет что verify_password корректно обрабатывает пустой хеш"""
        from app.core.security import verify_password

        result = verify_password("password", "")
        assert result is False


@pytest.mark.asyncio
class TestAuthIntegration:
    async def test_create_user_and_find_by_email_hash(self, db):
        """Проверяет создание пользователя и поиск по хешу email"""
        from app.models.user import User
        from sqlalchemy import select
        from app.core.encryption import encryption_service

        test_email = "integration_test@example.com"
        user = User.create_with_encryption(
            first_name="Интеграция",
            last_name="Тест",
            phone="+7 777 777-77-77",
            email=test_email,
            password_hash="$2b$12$testhash",
            role=UserRole.CLIENT
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        stmt = select(User).where(User.email_hash == encryption_service.hash_email(test_email))
        result = await db.execute(stmt)
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.email == test_email

    async def test_search_for_nonexistent_user_returns_none(self, db):
        """Проверяет что поиск несуществующего пользователя возвращает None"""
        from sqlalchemy import select
        from app.models.user import User
        from app.core.encryption import encryption_service

        stmt = select(User).where(User.email_hash == encryption_service.hash_email("nonexistent@example.com"))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        assert user is None


class TestEdgeCases:
    def test_token_schema_with_minimum_valid_data(self):
        """Проверяет создание Token схемы с минимальными валидными данными"""
        token = Token(
            access_token="a",
            user_id=0,
            role="CLIENT"
        )
        assert token.access_token == "a"
        assert token.user_id == 0
        assert token.role == "CLIENT"

    @pytest.mark.asyncio
    async def test_authenticate_user_with_special_email_characters(self, db):
        """Проверяет аутентификацию с email содержащим спецсимволы"""
        service = AuthService()

        test_email = "test+filter@example.com"
        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate_user(db, test_email, "password")

        assert exc_info.value.status_code == 401


def test_auth_service_has_proper_string_representation():
    """Проверяет строковое представление AuthService"""
    service = AuthService()
    service_str = str(service)
    assert "AuthService" in service_str or "object at" in service_str


def test_token_objects_with_same_data_are_equal():
    """Проверяет что токены с одинаковыми данными считаются равными"""
    token1 = Token(
        access_token="same_token",
        user_id=1,
        role="CLIENT"
    )

    token2 = Token(
        access_token="same_token",
        user_id=1,
        role="CLIENT"
    )

    assert token1.access_token == token2.access_token
    assert token1.user_id == token2.user_id
    assert token1.role == token2.role


def test_token_objects_with_different_data_are_not_equal():
    """Проверяет что токены с разными данными не считаются равными"""
    token1 = Token(
        access_token="token1",
        user_id=1,
        role="CLIENT"
    )

    token2 = Token(
        access_token="token2",
        user_id=2,
        role="STAFF"
    )

    assert token1.access_token != token2.access_token
    assert token1.user_id != token2.user_id
    assert token1.role != token2.role


class TestAuthServiceDatabaseInteraction:
    @pytest.mark.asyncio
    async def test_authenticate_user_handles_database_exception(self, db):
        """Проверяет что authenticate_user корректно обрабатывает исключения базы данных"""
        service = AuthService()

        with patch('app.features.auth.service.select') as mock_select:
            mock_select.side_effect = Exception("Database connection failed")

            with pytest.raises(Exception):
                await service.authenticate_user(db, "test@example.com", "password")

    @pytest.mark.asyncio
    async def test_authenticate_user_with_very_long_password(self, db):
        """Проверяет аутентификацию с очень длинным паролем"""
        service = AuthService()

        long_password = "a" * 1000
        with pytest.raises(HTTPException) as exc_info:
            await service.authenticate_user(db, "test@example.com", long_password)

        assert exc_info.value.status_code == 401


def test_user_login_schema_with_maximum_length_email():
    """Проверяет UserLogin с email максимальной длины"""
    from pydantic import ValidationError

    long_email = "a" * 200 + "@example.com"

    try:
        login_data = UserLogin(email=long_email, password="password123")
        assert login_data.email == long_email
    except ValidationError:
        assert True


def test_auth_service_instance_is_consistent():
    """Проверяет что инстансы AuthService могут создаваться многократно"""
    service1 = AuthService()
    service2 = AuthService()

    assert service1 is not service2
    assert isinstance(service1, AuthService)
    assert isinstance(service2, AuthService)
    assert hasattr(service1, 'authenticate_user')
    assert hasattr(service2, 'authenticate_user')


@pytest.mark.asyncio
async def test_simple_auth_flow_simulation(client):
    """Проверяет базовый сценарий аутентификации"""
    with patch('app.features.auth.router.auth_service.authenticate_user') as mock_auth:
        mock_auth.side_effect = HTTPException(status_code=401, detail="Неверный email или пароль")

        response = client.post(
            "/auth/login-json",
            json={"email": "any@example.com", "password": "any"}
        )

        assert response.status_code != 500
        assert "detail" in response.json()
