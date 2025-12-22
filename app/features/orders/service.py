from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends

from app.features.auth import get_current_user
from app.models.order import Order
from app.models.user import User
import logging

log = logging.getLogger(__name__)

async def create_simple_order(db: AsyncSession, order_email: str, phone: str, address: str, user: User = Depends(get_current_user)) -> Order:
    s = select(User).where(User.email == user.email)
    res = await db.execute(s)
    user = res.scalar_one_or_none()
    if user:
        user_id = user.user_id
    # else:
        # log.info("Пупупу пока тестик")
        # user = User(email=email, first_name="анон", last_name="анон", password_hash="qwer", role="CLIENT", phone="+79990000000")
        # db.add(user)
        # await db.flush()
        # user_id = user.user_id
        
    order = Order.create_with_encryption(
        user_id=user_id,
        order_email=order_email,
        total_price=0.00,
        address=address
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order