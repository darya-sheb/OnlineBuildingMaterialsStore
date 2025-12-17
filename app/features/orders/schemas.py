from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_per_item: float

class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_email: str
    total_price: float
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True