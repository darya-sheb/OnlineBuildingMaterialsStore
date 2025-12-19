from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token
from app.features.auth.service import auth_service
from app.features.auth.schemas import Token, UserLogin
from app.features.users.schemas import UserCreate, UserProfile
from app.models.user import UserRole
from app.infra.db import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# 1) Чисто бэк (API)
@router.post("/register",
             response_model=UserProfile,
             status_code=status.HTTP_201_CREATED,
             summary="Регистрация нового пользователя",
             description="Создание нового пользователя в системе с полной валидацией"
             )
async def register(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя с полной валидацией

    **Требования:**
    - Email должен быть уникальным
    - Пароль: минимум 8 символов, заглавная, строчная, цифра
    - Телефон: любой российский формат (будет нормализован в +7 XXX XXX-XX-XX)
    - Пароли должны совпадать
    """
    user = await auth_service.register_user(db, user_data)
    return UserProfile.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.authenticate_user(
            db,
            form_data.username,
            form_data.password
        )

        access_token = create_access_token(
            user_id=user.user_id,
            role=user.role.value,
            expires_minutes=120
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            role=user.role.value
        )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login-json", response_model=Token)
async def login_json(
        login_data: UserLogin,
        db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.authenticate_user(
            db,
            login_data.email,
            login_data.password
        )

        access_token = create_access_token(
            user_id=user.user_id,
            role=user.role.value,
            expires_minutes=120
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            role=user.role.value
        )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )


@router.post("/verify-token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = auth_service.verify_token(token)
        return {
            "valid": True,
            "user_id": int(payload.get("sub")),
            "role": payload.get("role")
        }
    except Exception:
        return {"valid": False}


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
        token: str,
        db: AsyncSession = Depends(get_db)
):
    try:
        payload = auth_service.verify_token(token)
        user_id = int(payload.get("sub"))
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен"
            )

        user = await auth_service.authenticate_user(db, user_id=user_id)

        access_token = create_access_token(
            user_id=user.user_id,
            role=user.role.value,
            expires_minutes=120
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            role=user.role.value
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истекший токен"
        )
