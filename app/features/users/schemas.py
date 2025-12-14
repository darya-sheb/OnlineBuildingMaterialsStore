from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum
import re

class UserRole(PyEnum):
    CLIENT = "CLIENT"
    STAFF = "STAFF"


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str
    patronymic: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        right_pattern_of_phone_number = r'^\+7\s?\d{3}\s?\d{3}-\d{2}-\d{2}$'
        if not re.match(right_pattern_of_phone_number, v):
            raise ValueError('Номер телефона неверный, должен быть формат: +7 XXX XXX-XX-XX')
        return v


class UserCreate(UserBase):
    password: str
    role: Optional[str] = "CLIENT"

    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ["CLIENT", "STAFF"]:
            raise ValueError('Роль должна быть CLIENT или STAFF')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен быть не менее 8 символов')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not re.search(r'\d', v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronymic: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        return UserBase.validate_phone(v)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    role: str
    created_at: datetime
    updated_at: datetime


class UserProfile(UserInDB):
    pass


class UserPublic(BaseModel):
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "ChangePasswordRequest",
    "UserInDB",
    "UserProfile",
    "UserPublic"
]

