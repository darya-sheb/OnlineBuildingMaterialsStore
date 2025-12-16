from pydantic import BaseModel, EmailStr, model_validator

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str
    @model_validator(mode='after')
    def validate_passwords_match(self):
        password = self.password
        password_confirm = self.password_confirm
        if password != password_confirm:
            raise ValueError('Пароли не совпадают')
        return self

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str

