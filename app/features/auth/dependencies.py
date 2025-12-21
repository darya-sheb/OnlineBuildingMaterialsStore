from typing import Optional
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.infra.db import get_db

async def get_current_user(
    access_token: Optional[str] = Cookie(None, alias="access_token"),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация",
        )
    try:
        payload = decode_access_token(access_token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Неверный токен")
        result = await db.execute(select(User).where(User.user_id == int(user_id)))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        return user
    except (JWTError, ValueError, AttributeError):
        raise HTTPException(status_code=401, detail="Неверный токен")

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
                detail="Недостаточно прав"
            )
        return current_user
    return role_checker

get_current_client = require_role(UserRole.CLIENT)
get_current_staff = require_role(UserRole.STAFF)

async def get_optional_user(
    access_token: Optional[str] = Cookie(None, alias="access_token"),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not access_token:
        return None
    try:
        payload = decode_access_token(access_token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        result = await db.execute(select(User).where(User.user_id == int(user_id)))
        return result.scalar_one_or_none()
    except (JWTError, ValueError, AttributeError):
        return None
