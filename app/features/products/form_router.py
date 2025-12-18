from fastapi import APIRouter
from app.infra.templates import templates
from fastapi.responses import HTMLResponse
from fastapi import Request, Depends
from app.infra.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Product

router = APIRouter(prefix="/products", tags=["products"])

# @router.get("/catalog", response_class=HTMLResponse)
# async def catalog_page(
#         request: Request,
#         db: AsyncSession = Depends(get_db)
# ):
#     user = request.state.user
#     result = await db.execute(select(Product))
#     products = result.scalars().all()
#
#     return templates.TemplateResponse("catalog.html", {
#         "request": request
#     })