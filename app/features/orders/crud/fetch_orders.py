from ....models import Order
from sqlalchemy.ext.asyncio import AsyncSession


async def get_order_for_user(db: AsyncSession, order_id, user_id) -> Order:
    pass

async def list_user_orders(db: AsyncSession, user_id) -> list[Order]:
    pass

async def get_order_with_items(db: AsyncSession, order_id) -> Order:
    pass