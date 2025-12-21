from fastapi import APIRouter
from app.infra.templates import templates
from fastapi.responses import HTMLResponse
from fastapi import Request, Depends
from app.infra.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.products.crud import get_products
from app.infra.media_checker import get_media_url

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/catalog", response_class=HTMLResponse)
async def catalog_page(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    products = await get_products(db)

    for product in products:
        product.image_url = get_media_url(product.image_path)

    return templates.TemplateResponse("catalog/list.html", {
        "request": request,
        "products": products
    })