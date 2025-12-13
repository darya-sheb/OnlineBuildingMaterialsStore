from ....models import Order, OrderItem
from sqlalchemy.ext.asyncio import AsyncSession

async def create_order(db: AsyncSession, user_id, order_email, total_price) -> Order:
    pass

async def create_order_items(db: AsyncSession, order_id, items) -> list[OrderItem]:
    pass