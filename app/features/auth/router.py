from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.service import auth_service
from app.features.auth.schemas import Token, UserLogin
from app.infra.db import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await auth_service.authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=auth_service.access_token_expire_minutes
    )
    access_token = auth_service.create_access_token(
        data={
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.user_id,
        role=user.role
    )


@router.post("/login-json", response_model=Token)
async def login_json(
        login_data: UserLogin,
        db: AsyncSession = Depends(get_db)
):
    user = await auth_service.authenticate_user(
        db,
        login_data.email,
        login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    access_token_expires = timedelta(
        minutes=auth_service.access_token_expire_minutes
    )
    access_token = auth_service.create_access_token(
        data={
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.user_id,
        role=user.role
    )


@router.post("/verify-token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        token_data = auth_service.verify_token(token)
        return {
            "valid": True,
            "user_id": token_data.user_id,
            "email": token_data.email,
            "role": token_data.role
        }
    except HTTPException:
        return {"valid": False}
