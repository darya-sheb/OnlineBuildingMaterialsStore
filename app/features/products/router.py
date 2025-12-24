from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.infra.db import get_db
from app.features.products import crud as product_crud
from app.features.products.schemas import PrRead

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[PrRead])
async def read_products(db: AsyncSession = Depends(get_db)):
    return await product_crud.get_products(db)
