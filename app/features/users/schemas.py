from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
import re


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: str

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # валидируем номер телефона
        right_pattern_of_phone_number = r'^\+7\s?\d{3}\s?\d{3}-\d{2}-\d{2}$'
        if not re.match(right_pattern_of_phone_number, v):
            raise ValueError('Номер телефона неверный, должен быть формат: +7 XXX XXX-XX-XX')
        return v


class UserInDB(UserBase):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    role: str
    patronymic: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserProfile(UserInDB):
    pass


