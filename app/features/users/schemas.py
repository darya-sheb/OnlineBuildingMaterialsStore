from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, model_validator
from datetime import datetime
from typing import Optional
import re


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    patronymic: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None or v == "":
            return None

        # Очищаем номер от всех нецифровых символов
        cleaned = re.sub(r'\D', '', v)

        # Проверяем российские форматы
        if cleaned.startswith('7') and len(cleaned) == 11:
            # Формат: 7XXXXXXXXXX -> конвертируем в +7 XXX XXX-XX-XX
            return f"+7 {cleaned[1:4]} {cleaned[4:7]}-{cleaned[7:9]}-{cleaned[9:]}"
        elif cleaned.startswith('8') and len(cleaned) == 11:
            # Формат: 8XXXXXXXXXX -> конвертируем в +7 XXX XXX-XX-XX
            return f"+7 {cleaned[1:4]} {cleaned[4:7]}-{cleaned[7:9]}-{cleaned[9:]}"
        elif cleaned.startswith('+7') and len(cleaned) == 12:
            # Формат: +7XXXXXXXXXX -> конвертируем в +7 XXX XXX-XX-XX
            return f"+7 {cleaned[2:5]} {cleaned[5:8]}-{cleaned[8:10]}-{cleaned[10:]}"
        elif len(cleaned) == 10:
            # Формат без кода страны: XXXXXXXXXX -> добавляем +7
            return f"+7 {cleaned[0:3]} {cleaned[3:6]}-{cleaned[6:8]}-{cleaned[8:]}"
        else:
            raise ValueError('Номер телефона должен содержать 10-11 цифр (Россия)')
        return v


class UserCreate(UserBase):
    password: str
    password_confirm: str
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
        errors = []
        if len(v) < 8:
            errors.append('не менее 8 символов')
        if not re.search(r'[A-Z]', v):
            errors.append('хотя бы одну заглавную букву')
        if not re.search(r'[a-z]', v):
            errors.append('хотя бы одну строчную букву')
        if not re.search(r'\d', v):
            errors.append('хотя бы одну цифру')

        if errors:
            raise ValueError(f'Пароль должен содержать: {", ".join(errors)}')
        return v

    @model_validator(mode='after')
    def validate_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Пароли не совпадают')
        return self


class UserCreateForm(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    phone: Optional[str] = None
    password: str
    password_confirm: str
    role: str = "CLIENT"


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
    "UserCreateForm",
    "UserUpdate",
    "ChangePasswordRequest",
    "UserInDB",
    "UserProfile",
    "UserPublic"
]
