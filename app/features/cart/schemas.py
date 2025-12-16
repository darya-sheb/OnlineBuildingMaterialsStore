from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemRead(BaseModel):
    cart_item_id: int
    product_id: int
    quantity: int
    product_name: str
    product_price: Decimal
    product_unit: str
    total_price: Decimal


class CartRead(BaseModel):
    cart_id: int
    items: List[CartItemRead]
    total_items: int
    total_price: Decimal