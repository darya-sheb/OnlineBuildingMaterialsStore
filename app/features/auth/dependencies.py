from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.infra.db import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        role: str = payload.get("role")

        if user_id is None or role is None:
            raise credentials_exception

        result = await db.execute(
            select(User).where(User.user_id == int(user_id))
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise credentials_exception

        return user
    except (JWTError, ValueError):
        raise credentials_exception

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user

def require_role(required_role: UserRole):
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения этой операции"
            )
        return current_user
    return role_checker

get_current_client = require_role(UserRole.CLIENT)
get_current_staff = require_role(UserRole.STAFF)

async def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")

        if not user_id:
            return None

        result = await db.execute(
            select(User).where(User.user_id == int(user_id))
        )
        return result.scalar_one_or_none()
    except (JWTError, ValueError):
        return None
