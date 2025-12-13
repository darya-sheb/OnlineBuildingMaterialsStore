from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.features.auth.schemas import TokenData, UserLogin
from app.features.users.schemas import UserInDB


class AuthService:
    def __init__(self):
        self.secret_key = "your-secret-key-change-this-in-production-min-32-chars"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    async def authenticate_user(
            self,
            db: AsyncSession,
            email: str,
            password: str
    ) -> Optional[UserInDB]:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        if not user:
            return None

        if not self.verify_password(password, user.password_hash):
            return None
        return UserInDB.model_validate(user)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        return encoded_jwt

    def verify_token(self, token: str) -> TokenData:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            user_id: int = payload.get("user_id")
            email: str = payload.get("email")
            role: str = payload.get("role")

            if user_id is None or email is None or role is None:
                raise credentials_exception

            return TokenData(
                user_id=user_id,
                email=email,
                role=role
            )
        except JWTError as e:
            raise credentials_exception


auth_service = AuthService()

