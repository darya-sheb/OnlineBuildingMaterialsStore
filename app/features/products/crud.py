from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from app.models.product import Product
from app.features.products.schemas import PrCreate, PrUpdate

async def get_product(db: AsyncSession, product_id: int) -> Optional[Product]:
    stmt = select(Product).where(Product.product_id == product_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def get_products(db: AsyncSession) -> List[Product]:
    stmt = select(Product)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def get_products_by_ids(db: AsyncSession, product_ids: List[int]) -> List[Product]:
    if not product_ids:
        return []
    stmt = select(Product).where(Product.product_id.in_(product_ids))
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def create_product(db: AsyncSession, product: PrCreate) -> Product:
    db_pr = Product(**product.model_dump())
    db.add(db_pr)
    await db.commit()
    await db.refresh(db_pr)
    return db_pr

async def update_product(db: AsyncSession, product_id: int, update_data: PrUpdate) -> Optional[Product]:
    db_pr = await get_product(db, product_id)
    if not db_pr:
        return None
    updated = update_data.model_dump(exclude_unset=True)
    for key, value in updated.items():
        setattr(db_pr, key, value)
    await db.commit()
    await db.refresh(db_pr)
    return db_pr

async def delete_product(db: AsyncSession, product_id: int) -> bool:
    db_product = await get_product(db, product_id)
    if db_product:
        await db.delete(db_product)
        await db.commit()
        return True
    return False