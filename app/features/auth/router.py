from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.core.security import create_access_token, hash_password
from app.features.auth.service import auth_service
from app.features.auth.schemas import Token, UserLogin
from app.features.users.schemas import UserCreate, UserProfile
from app.models.user import User, UserRole
from app.infra.db import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    hashed_password = hash_password(user_data.password)

    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        patronymic=user_data.patronymic,
        phone=user_data.phone,
        password_hash=hashed_password,
        role=UserRole(user_data.role)
    )

    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UserProfile.model_validate(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании пользователя"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при регистрации: {str(e)}"
        )

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
        from app.core.security import decode_access_token
        payload = decode_access_token(token)
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
        from app.core.security import decode_access_token
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
        role = payload.get("role")

        if not user_id or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен"
            )

        result = await db.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или истекший токен"
        )
