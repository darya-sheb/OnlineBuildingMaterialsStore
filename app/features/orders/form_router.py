from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.templates import templates
from app.infra.db import get_db
from app.models.user import User
from app.features.auth.dependencies import get_optional_user

router = APIRouter(prefix="/orders", tags = ["orders"])

@router.get("/checkout", response_class=HTMLResponse)
async def checkout_page(request: Request, user: User | None = Depends(get_optional_user)):
    return templates.TemplateResponse(
        "cart/confirmation.html",
        {"request": request, "user": user}
    )

@router.post("/checkout", response_class=RedirectResponse)
async def checkout_form(
    request: Request,
    phone: str = Form(None),
    email: str = Form(),
    address: str = Form(),
    db: AsyncSession = Depends(get_db)
):
    try:
        from app.features.orders.service import create_simple_order
        order = await create_simple_order(db, email, phone, address)
        return RedirectResponse(
            url=f"/orders/success/{order.order_id}",
            status_code=303
        )
    except Exception as error:
        return RedirectResponse(
            url=f"/orders/checkout?error={str(error)}",
            status_code=303
        )

@router.get("/success/{order_id}", response_class=HTMLResponse)
async def success_page(request: Request, order_id: int, user: User | None = Depends(get_optional_user)):
    return templates.TemplateResponse(
        "orders/success.html",
        {
            "request": request,
            "order_id": order_id,
            "user": user
        }
    )
