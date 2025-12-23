from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.templates import templates
from app.infra.db import get_db
from app.features.orders.service import create_simple_order
from app.models.user import User
from app.features.auth.dependencies import get_optional_user
from typing import Optional
from sqlalchemy import select
from app.models.order import Order
import logging
from app.features.orders.service import create_simple_order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request, user: User | None = Depends(get_optional_user),
                        db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse("cart/confirmation.html", {"request": request, "user": user})


@router.post("/checkout", response_class=RedirectResponse)
async def checkout_form(order_email: str = Form(), phone: str = Form(None), address: str = Form(),
                        db: AsyncSession = Depends(get_db), user: User | None = Depends(get_optional_user)):
    try:
        order = await create_simple_order(db, order_email, phone, address, user)
        return RedirectResponse(url=f"/orders/success/{order.order_id}", status_code=303)
    except Exception as error:
        import logging
        logging.error(f"Ошибка при оформлении заказа: {error}")
        return RedirectResponse(url=f"/orders/checkout?error={str(error)}", status_code=303)


@router.get("/success/{order_id}", response_class=HTMLResponse)
async def success_page(request: Request, order_id: int, user: User | None = Depends(get_optional_user),
                       db: AsyncSession = Depends(get_db)):
    stmt = select(Order).where(Order.order_id == order_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    return templates.TemplateResponse("orders/success.html", {"request": request, "order_id": order_id,
                                                              "order_email": order.order_email, "user": user})
