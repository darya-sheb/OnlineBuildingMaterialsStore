from pydantic import BaseModel
class OrderCreate(BaseModel):
    email: str