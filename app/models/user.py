from __future__ import annotations
import enum
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    DateTime,
    Enum,
    String,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.order import Order


class UserRole(str, enum.Enum):
    CLIENT = "CLIENT"
    STAFF = "STAFF"


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.CLIENT)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    phone: Mapped[str] = mapped_column(String(16), nullable=False) # формат +7 923 456-78-90
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    orders: Mapped[list[Order]] = relationship(back_populates="user")
    cart: Mapped[Cart | None] = relationship(back_populates="user", uselist=False)
