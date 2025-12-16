from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from typing import List
from app.infra.db import get_db
from app.features.cart import crud as cart_crud
from app.features.products import crud as product_crud
from app.features.cart.schemas import CartItemCreate, CartItemUpdate

router = APIRouter(prefix="/cart", tags=["cart"])

def get_session_id(req: Request) -> str:
    if sess_id := req.cookies.get("session_id"):
        return sess_id
    return str(uuid.uuid4())

async def available(db: AsyncSession, product_id: int, req: int):
    pr = await product_crud.get_product(db, product_id)
    if not pr:
        raise HTTPException(404, "Товар не найден")
    if pr.quantity_available < req:
        raise HTTPException(400, "Недостаточно товара")
    return pr

@router.get("/")
async def get_cart(req: Request, db: AsyncSession = Depends(get_db)):
    ses_id = get_session_id(req)
    items = cart_crud.get_cart_items(ses_id)
    if not items:
        return {"Data": [], "total_price": 0}
    product_ids = [i["product_id"] for i in items]
    products = await product_crud.get_products_by_ids(db, product_ids)
    products_dict = {p.product_id: p for p in products}
    sum=0
    data = []
    for i in items:
        pr = products_dict.get(i["product_id"])
        if pr:
            sum += pr.price * i["quantity"]
            data.append({
                "id": i["cart_item_id"],
                "product_id": pr.product_id,
                "name": pr.name,
                "price": pr.price,
                "unit": pr.unit,
                "quantity": i["quantity"]
            })
    return {"Data": data, "total_price": sum}

@router.post("/items/")
async def add_item(item_data: CartItemCreate, req: Request, db: AsyncSession = Depends(get_db)):
    ses_id = get_session_id(req)
    product = await available(db, item_data.product_id, item_data.quantity)
    cart_items = cart_crud.get_cart_items(ses_id)
    itemsl = None
    for i in cart_items:
        if i["product_id"] == item_data.product_id:
            itemsl = i
            break
    if itemsl:
        new_q = itemsl["quantity"] + item_data.quantity
        await available(db, item_data.product_id, new_q)
        itemm = cart_crud.update_cart_item(ses_id, itemsl["cart_item_id"], new_q)
    else:
        itemm = cart_crud.add_to_cart(ses_id, item_data.product_id, item_data.quantity)
    return {
        "id": itemm["cart_item_id"],
        "product_id": product.product_id,
        "name": product.name,
        "price": product.price,
        "quantity": itemm["quantity"]
    }


@router.put("/items/{item_id}")
async def update_cart_item(item_id: int, update: CartItemUpdate, req: Request, db: AsyncSession = Depends(get_db)):  # ← AsyncSession
    ses_id = get_session_id(req)
    cart_item = cart_crud.get_cart_item(ses_id, item_id)
    if not cart_item:
        raise HTTPException(404, "Товар не найден в корзине")
    product = await available(db, cart_item["product_id"], update.quantity)
    cart_crud.update_cart_item(ses_id, item_id, update.quantity)
    return {"id": item_id,
        "quantity": update.quantity,
        "total": product.price * update.quantity }


@router.delete("/items/{item_id}")
async def remove_item(item_id: int, req: Request):
    ses_id = get_session_id(req)
    if cart_crud.remove_from_cart(ses_id, item_id):
        return {"deleted": item_id}
    raise HTTPException(404, "Товар не найден в корзине")

@router.post("/clear")
async def clear_cart(req: Request):
    ses_id = get_session_id(req)
    cart_crud.clear_cart(ses_id)
    return {"cleared": True}