from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import ConfigDict

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

#переделать на response_model=HTMLResponse
@router.get("/me", response_model=UserProfile)
async def get_my_profile(
        current_user: User = Depends(get_current_active_user)
):
    return current_user

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
#     return user
