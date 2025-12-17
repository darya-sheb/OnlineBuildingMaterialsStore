from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.features.users.depends import require_staff
from app.features.orders import service as order_service
from app.features.orders.schemas import OrderResponse

router = APIRouter(prefix="/staff/orders", tags=["staff-orders"])


@router.get("/", response_model=list[OrderResponse])
async def get_all_orders(
    session: AsyncSession = Depends(get_session),
    staff_user=Depends(require_staff)
):
    """Получить список всех заказов (только для работника)"""
    orders = await order_service.get_all_orders(session)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    staff_user=Depends(require_staff)
):
    """Получить детали заказа по ID (только для работника)"""
    order = await order_service.get_order_by_id(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/search", response_model=list[OrderResponse])
async def search_orders_by_email(
    email: str = Query(..., description="Email клиента для поиска заказов"),
    session: AsyncSession = Depends(get_session),
    staff_user=Depends(require_staff)
):
    """Найти все заказы по email клиента"""
    orders = await order_service.get_orders_by_email(session, email)
    return orders 