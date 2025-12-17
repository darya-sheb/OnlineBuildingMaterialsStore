from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.features.users.depends import require_staff
from app.features.products.service import get_all_products, create_product, adjust_stock
from app.features.products.schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/staff", tags=["staff"])


@router.get("/products")
async def list_staff_products(
    session: AsyncSession = Depends(get_session),
    staff=Depends(require_staff)
):
    """Получить список всех товаров (бэкенд для таблицы товаров)"""
    products = await get_all_products(session)
    return products


@router.post("/products/new")
async def create_new_product(
    name: str = Form(...),
    manufacturer: str = Form(...),
    price: float = Form(...),
    unit: str = Form(...),
    image: UploadFile = File(None),
    session: AsyncSession = Depends(get_session),
    staff=Depends(require_staff)
):
    """Создать новый товар (с фото)"""
    product_in = ProductCreate(
        name=name,
        manufacturer=manufacturer,
        price=price,
        unit=unit
    )
    product = await create_product(session, product_in, image)
    return {"id": product.id, "name": product.name}


@router.post("/products/{product_id}/stock")
async def update_product_stock(
    product_id: int,
    delta: int = Form(...),
    session: AsyncSession = Depends(get_session),
    staff=Depends(require_staff)
):
    """Изменить остаток товара (приход/расход)"""
    product = await adjust_stock(session, product_id, delta)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден или недостаточно остатков")
    return {
        "id": product.id,
        "quantity_available": product.quantity_available
    }