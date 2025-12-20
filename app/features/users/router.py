from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.responses import HTMLResponse
from app.infra.templates import templates
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import traceback

from app.features.auth.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_staff,
    require_role
)
from app.features.users.schemas import (
    UserProfile,
    UserUpdate,
    UserPublic,
    ChangePasswordRequest,
    UserCreate
)
from app.core.security import hash_password, verify_password
from app.infra.db import get_db
from app.models.user import User, UserRole

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """
    Страница профиля пользователя
    """
    return templates.TemplateResponse(
        "users/profile.html",
        {
            "request": request,
            "user": current_user
        }
    )


@router.get("/me/api", response_model=UserProfile)
async def get_my_profile_api(
        current_user: User = Depends(get_current_active_user)
):
    return current_user


@router.put("/me", response_model=UserProfile)
async def update_my_profile(
        update_data: UserUpdate,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        print(f"DEBUG: Starting profile update for user_id={current_user.user_id}")
        print(f"DEBUG: Update data: {update_data}")

        # Используем model_dump для Pydantic v2
        update_dict = update_data.model_dump(exclude_unset=True)
        print(f"DEBUG: Update dict: {update_dict}")

        if not update_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления"
            )

        # Обновляем поля
        updated_fields = []
        for key, value in update_dict.items():
            print(f"DEBUG: Setting {key} = {value}")
            if hasattr(current_user, key):
                old_value = getattr(current_user, key)
                setattr(current_user, key, value)
                updated_fields.append(f"{key}: {old_value} -> {value}")
            else:
                print(f"WARNING: User object has no attribute {key}")

        print(f"DEBUG: Fields changed: {updated_fields}")
        print(f"DEBUG: User before commit: {current_user.__dict__}")

        await db.commit()
        print("DEBUG: Commit successful")

        # Обновляем объект из БД
        await db.refresh(current_user)
        print(f"DEBUG: User after refresh: {current_user.__dict__}")

        return current_user

    except HTTPException:
        raise

    except ValidationError as e:
        await db.rollback()
        print(f"VALIDATION ERROR: {e.errors()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {e.errors()}"
        )

    except IntegrityError as e:
        await db.rollback()
        print(f"INTEGRITY ERROR: {str(e)}")
        # Возможно, дублирование email или других уникальных полей
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка целостности данных (возможно, email уже занят)"
        )

    except SQLAlchemyError as e:
        await db.rollback()
        print(f"SQLALCHEMY ERROR: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка базы данных: {str(e)}"
        )

    except Exception as e:
        await db.rollback()
        print(f"UNEXPECTED ERROR: {type(e).__name__}: {str(e)}")
        traceback.print_exc()  # Печатаем полный traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Неожиданная ошибка: {type(e).__name__}"
        )


@router.post("/me/change-password")
async def change_my_password(
        password_data: ChangePasswordRequest,
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль"
        )

    try:
        UserCreate.validate_password(password_data.new_password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    current_user.password_hash = hash_password(password_data.new_password)

    try:
        await db.commit()
        return {"message": "Пароль успешно изменен"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при изменении пароля: {str(e)}"
        )


# для отладки, смотреть список всех юзеров через апи
@router.get("/users", response_model=List[UserPublic])
async def get_all_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        current_user: User = Depends(get_current_staff),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    return users
#скорее всего не будем верстать
# @router.put("/me", response_model=UserProfile)
# async def update_my_profile(
#         update_data: UserUpdate,
#         current_user: User = Depends(get_current_active_user),
#         db: AsyncSession = Depends(get_db)
# ):
#     update_dict = update_data.dict(exclude_unset=True)
#     for key, value in update_dict.items():
#         setattr(current_user, key, value)
#
#     try:
#         await db.commit()
#         await db.refresh(current_user)
#         return current_user
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Ошибка при обновлении профиля: {str(e)}"
#         )

#скорее всего не будем верстать
# @router.post("/me/change-password")
# async def change_my_password(
#         password_data: ChangePasswordRequest,
#         current_user: User = Depends(get_current_active_user),
#         db: AsyncSession = Depends(get_db)
# ):
#     if not verify_password(password_data.current_password, current_user.password_hash):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Неверный текущий пароль"
#         )
#
#     try:
#         UserCreate.validate_password(password_data.new_password)
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#
#     current_user.password_hash = hash_password(password_data.new_password)
#
#     try:
#         await db.commit()
#         return {"message": "Пароль успешно изменен"}
#     except Exception as e:
#         await db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Ошибка при изменении пароля: {str(e)}"
#         )


# для отладки, смотреть список всех юзеров через апи
# скорее всего не будем верстать, возможно пригодится для отладки через апи
# @router.get("/users/{user_id}", response_model=UserProfile)
# async def get_user_by_id(
#         user_id: int,
#         current_user: User = Depends(get_current_active_user),
#         db: AsyncSession = Depends(get_db)
# ):
#     if current_user.role != UserRole.STAFF and current_user.user_id != user_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Недостаточно прав для просмотра этого профиля"
#         )
#
#     result = await db.execute(
#         select(User).where(User.user_id == user_id)
#     )
#     user = result.scalar_one_or_none()
#
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Пользователь не найден"
#         )
#
#     return user]
