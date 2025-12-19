from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.infra.db import get_db
from app.features.cart import crud as cart_crud
from app.features.cart.schemas import CartItemCreate, CartItemUpdate
from app.features.auth.dependencies import get_current_user, get_optional_user
from app.infra.templates import templates
from app.models.user import User
from app.models.product import Product

router = APIRouter(prefix="/cart", tags=["cart"])


async def check_product_availability(db: AsyncSession, product_id: int, required_quantity: int):
    """Проверка доступности товара"""
    from app.features.products import crud as product_crud
    product = await product_crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    if hasattr(product, 'quantity_available') and product.quantity_available < required_quantity:
        raise HTTPException(status_code=400, detail="Недостаточно товара на складе")
    return product

# HTML endpoints
@router.get("/page", response_class=HTMLResponse)
async def cart_page(req: Request):
    return templates.TemplateResponse("cart/view.html", {"request": req})

@router.get("/confirmation", response_class=HTMLResponse)
async def confirmation_page(req: Request):
    return templates.TemplateResponse("cart/confirmation.html", {"request": req})

# API endpoints
@router.get("/")
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← ДОБАВЛЯЕМ!
):
    """Получить корзину пользователя"""
    try:
        items = await cart_crud.CartCRUD.get_cart_items(db, current_user.user_id)  # ← ИСПРАВЛЯЕМ!
        
        if not items:
            return {"items": [], "total_price": 0}
        
        data = []
        total_price = 0
        
        for item in items:
            if item.product:
                price_rub = item.product.price / 100
                item_total = price_rub * item.quantity
                
                data.append({
                    "cart_item_id": item.cart_item_id,
                    "product_id": item.product.product_id,
                    "name": item.product.name,
                    "price": price_rub,
                    "quantity": item.quantity,
                    "total": item_total
                })
                total_price += item_total
        
        return {
            "items": data,
            "total_price": total_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении корзины: {str(e)}")

@router.post("/items/")
async def add_item(
    item_data: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← ДОБАВЛЯЕМ!
):
    """Добавить товар в корзину"""
    try:
        product = await check_product_availability(db, item_data.product_id, item_data.quantity)
        
        cart_item = await cart_crud.CartCRUD.add_to_cart(db, current_user.user_id, item_data)  # ← ИСПРАВЛЯЕМ!
        
        cart_item_with_product = await cart_crud.CartCRUD.get_cart_item(
            db, current_user.user_id, cart_item.cart_item_id
        )
        
        if not cart_item_with_product or not cart_item_with_product.product:
            raise HTTPException(status_code=500, detail="Ошибка при получении информации о товаре")
        
        price_rub = cart_item_with_product.product.price / 100
        
        return {
            "cart_item_id": cart_item_with_product.cart_item_id,
            "product_id": cart_item_with_product.product.product_id,
            "name": cart_item_with_product.product.name,
            "price": price_rub,
            "quantity": cart_item_with_product.quantity,
            "total": price_rub * cart_item_with_product.quantity
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении в корзину: {str(e)}")

@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: int,
    update: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← ДОБАВЛЯЕМ!
):
    """Обновить количество товара в корзине"""
    try:
        cart_item = await cart_crud.CartCRUD.get_cart_item(db, current_user.user_id, item_id)
        if not cart_item:
            raise HTTPException(status_code=404, detail="Товар не найден в корзине")
        
        product = await check_product_availability(db, cart_item.product_id, update.quantity)
        
        updated_item = await cart_crud.CartCRUD.update_cart_item(
            db, current_user.user_id, item_id, update.quantity
        )
        
        if not updated_item:
            return {"deleted": item_id}
        
        price_rub = product.price / 100
        
        return {
            "cart_item_id": item_id,
            "product_id": product.product_id,
            "quantity": update.quantity,
            "total": price_rub * update.quantity
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении корзины: {str(e)}")

@router.delete("/items/{item_id}")
async def remove_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← ДОБАВЛЯЕМ!
):
    """Удалить товар из корзины"""
    try:
        success = await cart_crud.CartCRUD.remove_from_cart(db, current_user.user_id, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Товар не найден в корзине")
        return {"deleted": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении из корзины: {str(e)}")

@router.post("/clear")
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ← ДОБАВЛЯЕМ!
):
    """Очистить корзину"""
    try:
        success = await cart_crud.CartCRUD.clear_cart(db, current_user.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Корзина не найдена")
        return {"cleared": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при очистке корзины: {str(e)}")
