from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.templates import templates
from app.infra.db import get_db
from app.models.order import Order

web_router = APIRouter()

@web_router.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request):
    return templates.TemplateResponse(
        "orders/checkout.html",
        {"request": request}
    )

@web_router.post("/checkout", response_class=RedirectResponse)
async def checkout_form(
    request: Request,
    email: str = Form(),
    db: AsyncSession = Depends(get_db)
):
    try:
        from app.features.orders.service import create_simple_order
        order = await create_simple_order(db, email)
        return RedirectResponse(
            url=f"/orders/success/{order.order_id}",
            status_code=303
        )
    except Exception as error:
        return RedirectResponse(
            url=f"/orders/checkout?error={str(error)}",
            status_code=303
        )

@web_router.get("/success/{order_id}", response_class=HTMLResponse)
async def success_page(request: Request, order_id: int):
    return templates.TemplateResponse(
        "orders/success.html",
        {
            "request": request,
            "order_id": order_id
        }
    )
