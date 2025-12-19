from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session

async def init_models() -> None:
    from app.models.base import Base
    from app.models.user import User
    from app.models.product import Product
    from app.models.cart import Cart
    from app.models.cart_item import CartItem
    from app.models.order import Order
    from app.models.order_item import OrderItem

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

