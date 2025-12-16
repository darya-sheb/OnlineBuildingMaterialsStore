from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.features.users.depends import get_current_user
from app.models.user import User
from app.features.orders.service import create_order
from app.services.email_service import EmailService

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/checkout")
async def checkout_page():
    return {"message": "Checkout form - enter your email"}


@router.post("/checkout")
async def create_order_endpoint(
    email: str = Form(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    order = await create_order(session=session, user_id=user.id, email=email)

    try:
        email_service = EmailService()
        await email_service.send_order_confirmation(email, order.id)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {email}: {e}")

    return RedirectResponse(url=f"/orders/success/{order.id}", status_code=303)