from fastapi import APIRouter
from app.infra.templates import templates
from fastapi.responses import HTMLResponse
from fastapi import Request, Depends
from app.infra.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Product
from app.features.products.crud import get_products

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/catalog", response_class=HTMLResponse)
async def catalog_page(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    products = get_products(db)
    return templates.TemplateResponse("catalog/list.html", {
        "request": request,
        "products": products
    })