from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.product import Product


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("cart_id", "product_id"),)

    cart_item_id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.cart_id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    cart: Mapped[Cart] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="cart_items")
