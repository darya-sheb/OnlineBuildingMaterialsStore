from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.infra.db import get_db
from app.features.products import crud as product_crud
from app.features.products.schemas import PrRead, PrCreate, PrUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[PrRead])
async def read_products(db: AsyncSession = Depends(get_db)):
    return await product_crud.get_products(db)


# полезно для staff
@router.post("/", response_model=PrRead, status_code=201)
async def create_product(product: PrCreate, db: AsyncSession = Depends(get_db)):
    return await product_crud.create_product(db, product)


# то же самое для staff
@router.put("/{product_id}", response_model=PrRead)
async def update_product(product_id: int, product: PrUpdate, db: AsyncSession = Depends(get_db)):
    updated = await product_crud.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(404, detail="Товар не найден")
    return updated


# нужно проверить каскадное удаление по таблицам
@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    if not await product_crud.delete_product(db, product_id):
        raise HTTPException(404, detail="Товар не найден")
