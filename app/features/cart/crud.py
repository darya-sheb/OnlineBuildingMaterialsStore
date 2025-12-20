from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.features.cart.schemas import CartItemCreate, CartItemUpdate

class CartCRUD:
    @staticmethod
    async def get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
        try:
            stmt = select(Cart).where(Cart.user_id == user_id)
            result = await db.execute(stmt)
            cart = result.scalar_one_or_none()
            if not cart:
                cart = Cart(user_id=user_id)
                db.add(cart)
                await db.commit()
                await db.refresh(cart)
            return cart
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def get_cart_items(db: AsyncSession, user_id: int) -> List[CartItem]:
        try:
            cart = await CartCRUD.get_or_create_cart(db, user_id)
            stmt = select(CartItem).where(
                CartItem.cart_id == cart.cart_id
            ).options(
                selectinload(CartItem.product)
            )
            result = await db.execute(stmt)
            items = result.scalars().all()
            for item in items:
                if item.product:
                    item.product.price_rub = item.product.price / 100
            
            return items
        except Exception as e:
            raise e
    
    @staticmethod
    async def add_to_cart(
        db: AsyncSession, 
        user_id: int, 
        item_data: CartItemCreate
    ) -> CartItem:
        try:
            cart = await CartCRUD.get_or_create_cart(db, user_id)
            stmt = select(CartItem).where(
                and_(
                    CartItem.cart_id == cart.cart_id,
                    CartItem.product_id == item_data.product_id
                )
            )
            result = await db.execute(stmt)
            existing_item = result.scalar_one_or_none()
            
            if existing_item:
                existing_item.quantity += item_data.quantity
                db_item = existing_item
            else:
                db_item = CartItem(
                    cart_id=cart.cart_id,
                    product_id=item_data.product_id,
                    quantity=item_data.quantity
                )
                db.add(db_item)
            
            await db.commit()
            await db.refresh(db_item)
            return db_item
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def get_cart_item(
        db: AsyncSession, 
        user_id: int, 
        cart_item_id: int
    ) -> Optional[CartItem]:
        try:
            cart = await CartCRUD.get_or_create_cart(db, user_id)
            
            stmt = select(CartItem).where(
                and_(
                    CartItem.cart_item_id == cart_item_id,
                    CartItem.cart_id == cart.cart_id
                )
            ).options(selectinload(CartItem.product))
            
            result = await db.execute(stmt)
            item = result.scalar_one_or_none()
            
            if item and item.product:
                item.product.price_rub = item.product.price / 100
            
            return item
        except Exception as e:
            raise e
    
    @staticmethod
    async def update_cart_item(
        db: AsyncSession,
        user_id: int,
        cart_item_id: int,
        quantity: int
    ) -> Optional[CartItem]:
        try:
            cart = await CartCRUD.get_or_create_cart(db, user_id)
            
            stmt = select(CartItem).where(
                and_(
                    CartItem.cart_item_id == cart_item_id,
                    CartItem.cart_id == cart.cart_id
                )
            )
            result = await db.execute(stmt)
            item = result.scalar_one_or_none()
            
            if not item:
                return None
            
            if quantity <= 0:
                await db.delete(item)
                await db.commit()
                return None
            
            item.quantity = quantity
            await db.commit()
            await db.refresh(item)
            return item
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def remove_from_cart(
        db: AsyncSession, 
        user_id: int, 
        cart_item_id: int
    ) -> bool:
        try:
            cart = await CartCRUD.get_or_create_cart(db, user_id)
            
            stmt = select(CartItem).where(
                and_(
                    CartItem.cart_item_id == cart_item_id,
                    CartItem.cart_id == cart.cart_id
                )
            )
            result = await db.execute(stmt)
            item = result.scalar_one_or_none()
            
            if not item:
                return False
            
            await db.delete(item)
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise e
    
    @staticmethod
    async def clear_cart(db: AsyncSession, user_id: int) -> bool:
        try:
            cart = await CartCRUD.get_or_create_cart(db, user_id)
            stmt = select(CartItem).where(CartItem.cart_id == cart.cart_id)
            result = await db.execute(stmt)
            items = result.scalars().all()
            
            for item in items:
                await db.delete(item)
            
            await db.commit()
            return True
        except Exception as e:
            await db.rollback()
            raise e