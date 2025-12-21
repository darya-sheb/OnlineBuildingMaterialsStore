from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.core.security import verify_password, decode_access_token, hash_password
from app.core.encryption import encryption_service
from app.models.user import User
from app.features.users.schemas import UserCreate
import re


class AuthService:
    async def authenticate_user(
            self,
            db: AsyncSession,
            email: str,
            password: str
    ):
        """Аутентификация пользователя по хэшу email"""
        email_hash = encryption_service.hash_email(email)
        result = await db.execute(select(User).where(User.email_hash == email_hash))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        return user

    async def register_user(
            self,
            db: AsyncSession,
            user_data: UserCreate
    ):
        """Регистрация нового пользователя с шифрованием данных"""
        email_hash = encryption_service.hash_email(user_data.email)

        result = await db.execute(select(User).where(User.email_hash == email_hash))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

        phone = user_data.phone
        if phone:
            phone = self.normalize_phone(phone)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Телефон обязателен"
            )

        hashed_password = hash_password(user_data.password)
        user = User.create_with_encryption(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=phone,
            email=user_data.email,
            password_hash=hashed_password,
            patronymic=user_data.patronymic,
            role=user_data.role
        )

        try:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при регистрации: {str(e)}"
            )

    def normalize_phone(self, phone: str) -> str:
        """Нормализует телефон в формат +7 XXX XXX-XX-XX"""
        if not phone or not phone.strip():
            return phone

        # Очищаем от всех нецифровых символов
        digits = re.sub(r'\D', '', phone)

        if not digits:
            return phone

        # Обрабатываем разные форматы
        if digits.startswith('7') and len(digits) == 11:
            return f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:]}"
        elif digits.startswith('8') and len(digits) == 11:
            return f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:]}"
        elif digits.startswith('+7') and len(digits) == 12:
            return f"+7 {digits[2:5]} {digits[5:8]}-{digits[8:10]}-{digits[10:]}"
        elif len(digits) == 10:
            return f"+7 {digits[0:3]} {digits[3:6]}-{digits[6:8]}-{digits[8:]}"
        else:
            return phone

    def verify_token(self, token: str):
        """Верификация JWT токена"""
        try:
            return decode_access_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные учетные данные",
                headers={"WWW-Authenticate": "Bearer"},
            )


auth_service = AuthService()