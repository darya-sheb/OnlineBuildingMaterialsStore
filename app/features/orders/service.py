from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.order import Order
from app.models.user import User
import logging

log = logging.getLogger(__name__)

async def create_simple_order(db: AsyncSession, email: str) -> Order:
    s = select(User).where(User.email == email)
    res = await db.execute(s)
    user = res.scalar_one_or_none()
    if user:
        user_id = user.user_id
    else:
        log.info("Пупупу пока тестик")
        user = User(email=email, first_name="анон", last_name="анон", password_hash="qwer", role="CLIENT", phone="+79990000000")
        db.add(user)
        await db.flush()
        user_id = user.user_id
        
    order = Order(
        user_id=user_id,
        order_email=email,
        total_price=0.00
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order