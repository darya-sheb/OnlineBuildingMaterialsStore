import pytest
from fastapi import HTTPException
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from sqlalchemy import select
from pydantic import ValidationError
from types import SimpleNamespace
from app.features.cart.schemas import CartItemCreate, CartItemUpdate
from app.features.cart.crud import CartCRUD
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User, UserRole


class TestCartCRUD:
    @pytest.mark.asyncio
    async def test_get_or_create_cart_existing(self, db):
        with patch('app.core.encryption.encryption_service') as mock_encryption:
            mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
            mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")
            mock_encryption.hash_email.side_effect = lambda x: f"hash_{x}"
            
            user = User.create_with_encryption(
                first_name="Test",
                last_name="User",
                phone="+79991234567",
                email="test@example.com",
                password_hash="$2b$12$testhash",
                role=UserRole.CLIENT
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)

        cart = Cart(user_id=user.user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        result_cart = await CartCRUD.get_or_create_cart(db, user.user_id)
        assert result_cart is not None
        assert result_cart.user_id == user.user_id
        assert result_cart.cart_id == cart.cart_id

    @pytest.mark.asyncio
    async def test_get_or_create_cart_new(self, db):
        with patch('app.core.encryption.encryption_service') as mock_encryption:
            mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
            mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")
            mock_encryption.hash_email.side_effect = lambda x: f"hash_{x}"
            
            user = User.create_with_encryption(
                first_name="Test",
                last_name="User",
                phone="+79991234567",
                email="test@example.com",
                password_hash="$2b$12$testhash",
                role=UserRole.CLIENT
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)

        result_cart = await CartCRUD.get_or_create_cart(db, user.user_id)
        assert result_cart is not None
        assert result_cart.user_id == user.user_id

    @pytest.mark.asyncio
    async def test_add_to_cart_new_item(self, db):
        with patch('app.core.encryption.encryption_service') as mock_encryption:
            mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
            mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")
            mock_encryption.hash_email.side_effect = lambda x: f"hash_{x}"
            user = User.create_with_encryption(
                first_name="Test",
                last_name="User",
                phone="+79991234567",
                email="test@example.com",
                password_hash="$2b$12$testhash",
                role=UserRole.CLIENT
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        product = Product(
            manufacturer="Test Manufacturer",
            name="Test Product",
            dimensions="10x10x10",
            unit="шт",
            price=10000, 
            quantity_available=10
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        item_data = CartItemCreate(
            product_id=product.product_id,
            quantity=2
        )
        cart_item = await CartCRUD.add_to_cart(db, user.user_id, item_data)
        assert cart_item is not None
        assert cart_item.product_id == product.product_id
        assert cart_item.quantity == 2

    @pytest.mark.asyncio
    async def test_add_to_cart_existing_item(self, db):
        with patch('app.core.encryption.encryption_service') as mock_encryption:
            mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
            mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")
            mock_encryption.hash_email.side_effect = lambda x: f"hash_{x}"
            
            user = User.create_with_encryption(
                first_name="Test",
                last_name="User",
                phone="+79991234567",
                email="test@example.com",
                password_hash="$2b$12$testhash",
                role=UserRole.CLIENT
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)

        product = Product(
            manufacturer="Test Manufacturer",
            name="Test Product",
            unit="шт",
            price=10000,
            quantity_available=10
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)

        item_data = CartItemCreate(
            product_id=product.product_id,
            quantity=2
        )
        cart_item1 = await CartCRUD.add_to_cart(db, user.user_id, item_data)
        item_data2 = CartItemCreate(
            product_id=product.product_id,
            quantity=3
        )
        cart_item2 = await CartCRUD.add_to_cart(db, user.user_id, item_data2)
        assert cart_item1.cart_item_id == cart_item2.cart_item_id
        assert cart_item2.quantity == 5  # 2 + 3

    @pytest.mark.asyncio
    async def test_get_cart_items(self, db):
        with patch('app.core.encryption.encryption_service') as mock_encryption:
            mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
            mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")
            mock_encryption.hash_email.side_effect = lambda x: f"hash_{x}"
            
            user = User.create_with_encryption(
                first_name="Test",
                last_name="User",
                phone="+79991234567",
                email="test@example.com",
                password_hash="$2b$12$testhash",
                role=UserRole.CLIENT
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)

        product1 = Product(
            manufacturer="Manufacturer 1",
            name="Product 1",
            unit="шт",
            price=10000,
            quantity_available=10
        )
        product2 = Product(
            manufacturer="Manufacturer 2", 
            name="Product 2",
            unit="шт",
            price=20000,
            quantity_available=5
        )
        
        db.add(product1)
        db.add(product2)
        await db.commit()
        await db.refresh(product1)
        await db.refresh(product2)
        item_data1 = CartItemCreate(product_id=product1.product_id, quantity=1)
        item_data2 = CartItemCreate(product_id=product2.product_id, quantity=2)
        
        await CartCRUD.add_to_cart(db, user.user_id, item_data1)
        await CartCRUD.add_to_cart(db, user.user_id, item_data2)
        cart_items = await CartCRUD.get_cart_items(db, user.user_id)
        
        assert len(cart_items) == 2
        assert cart_items[0].product_id in [product1.product_id, product2.product_id]
        assert cart_items[1].product_id in [product1.product_id, product2.product_id]

    @pytest.mark.asyncio
    async def test_update_cart_item(self, db):
        with patch('app.core.encryption.encryption_service') as mock_encryption:
            mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
            mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")
            mock_encryption.hash_email.side_effect = lambda x: f"hash_{x}"
            
            user = User.create_with_encryption(
                first_name="Test",
                last_name="User",
                phone="+79991234567",
                email="test@example.com",
                password_hash="$2b$12$testhash",
                role=UserRole.CLIENT
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)

        product = Product(
            manufacturer="Test Manufacturer",
            name="Test Product",
            unit="шт",
            price=10000,
            quantity_available=10
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        item_data = CartItemCreate(product_id=product.product_id, quantity=2)
        cart_item = await CartCRUD.add_to_cart(db, user.user_id, item_data)
        updated_item = await CartCRUD.update_cart_item(db, user.user_id, cart_item.cart_item_id, 5)
        assert updated_item is not None
        assert updated_item.quantity == 5

    @pytest.mark.asyncio
    async def test_update_cart_item_remove_when_zero(self, db):
        with patch('app.core.encryption.encryption_service') as mock_encryption:
            mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
            mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")
            mock_encryption.hash_email.side_effect = lambda x: f"hash_{x}"
            user = User.create_with_encryption(
                first_name="Test",
                last_name="User",
                phone="+79991234567",
                email="test@example.com",
                password_hash="$2b$12$testhash",
                role=UserRole.CLIENT
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        product = Product(
            manufacturer="Test Manufacturer",
            name="Test Product",
            unit="шт",
            price=10000,
            quantity_available=10
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        item_data = CartItemCreate(product_id=product.product_id, quantity=2)
        cart_item = await CartCRUD.add_to_cart(db, user.user_id, item_data)
        result = await CartCRUD.update_cart_item(db, user.user_id, cart_item.cart_item_id, 0)
        assert result is None
        cart_items = await CartCRUD.get_cart_items(db, user.user_id)
        assert len(cart_items) == 0

    @pytest.mark.asyncio
    async def test_remove_from_cart(self, db):
        with patch('app.core.encryption.encryption_service') as mock_encryption:
            mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
            mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")
            mock_encryption.hash_email.side_effect = lambda x: f"hash_{x}"
            user = User.create_with_encryption(
                first_name="Test",
                last_name="User",
                phone="+79991234567",
                email="test@example.com",
                password_hash="$2b$12$testhash",
                role=UserRole.CLIENT
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
        product = Product(
            manufacturer="Test Manufacturer",
            name="Test Product",
            unit="шт",
            price=10000,
            quantity_available=10
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        item_data = CartItemCreate(product_id=product.product_id, quantity=2)
        cart_item = await CartCRUD.add_to_cart(db, user.user_id, item_data)
        result = await CartCRUD.remove_from_cart(db, user.user_id, cart_item.cart_item_id)
        assert result is True
        cart_items = await CartCRUD.get_cart_items(db, user.user_id)
        assert len(cart_items) == 0

    @pytest.mark.asyncio
    async def test_clear_cart(self, db):
        with patch('app.core.encryption.encryption_service') as mock_encryption:
            mock_encryption.encrypt.side_effect = lambda x: f"encrypted_{x}"
            mock_encryption.decrypt.side_effect = lambda x: x.replace("encrypted_", "")
            mock_encryption.hash_email.side_effect = lambda x: f"hash_{x}"
            
            user = User.create_with_encryption(
                first_name="Test",
                last_name="User",
                phone="+79991234567",
                email="test@example.com",
                password_hash="$2b$12$testhash",
                role=UserRole.CLIENT
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)

        for i in range(3):
            product = Product(
                manufacturer=f"Manufacturer {i}",
                name=f"Product {i}",
                unit="шт",
                price=10000 + i * 1000,
                quantity_available=10
            )
            db.add(product)
        await db.commit()

        stmt = select(Product)
        result = await db.execute(stmt)
        products = result.scalars().all()

        for product in products:
            item_data = CartItemCreate(product_id=product.product_id, quantity=1)
            await CartCRUD.add_to_cart(db, user.user_id, item_data)
        cart_items = await CartCRUD.get_cart_items(db, user.user_id)
        assert len(cart_items) == 3
        result = await CartCRUD.clear_cart(db, user.user_id)
    
        assert result is True
        cart_items = await CartCRUD.get_cart_items(db, user.user_id)
        assert len(cart_items) == 0


class TestCartSchemas:
    def test_cart_item_create_schema(self):
        data = {
            "product_id": 1,
            "quantity": 2
        }
        item = CartItemCreate(**data)
        assert item.product_id == 1
        assert item.quantity == 2

    def test_cart_item_update_schema(self):
        data = {"quantity": 5}
        item = CartItemUpdate(**data)
        assert item.quantity == 5


class TestCartAPIEndpoints:
    @pytest.mark.asyncio
    async def test_get_cart_endpoint_requires_auth(self, client):
        response = client.get("/cart/api")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_cart_endpoint_returns_cart(self, auth_client):
        with patch('app.features.cart.crud.CartCRUD.get_cart_items') as mock_get:
            mock_item = MagicMock()
            mock_item.cart_item_id = 1
            mock_item.quantity = 2
            mock_item.product = MagicMock(
                product_id=1,
                name="Test Product",
                price=10000
            )
            mock_get.return_value = [mock_item]
            response = auth_client.get("/cart/api")
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert len(data["items"]) == 1
            assert data["total_price"] == 20000

    @pytest.mark.asyncio
    async def test_add_to_cart_endpoint(self, auth_client):
        with patch('app.features.cart.router.check_product_availability') as mock_check:
            product = SimpleNamespace(product_id=1, name="Test Product", price=10000)
            mock_check.return_value = product
            
            with patch('app.features.cart.crud.CartCRUD.add_to_cart') as mock_add:
                mock_add.return_value = SimpleNamespace(cart_item_id=1)
                
                with patch('app.features.cart.crud.CartCRUD.get_cart_item') as mock_get_item:
                    cart_item_with_product = SimpleNamespace(
                        cart_item_id=1,
                        product=product,
                        quantity=2
                    )
                    mock_get_item.return_value = cart_item_with_product
                    
                    response = auth_client.post(
                        "/cart/items/",
                        json={"product_id": 1, "quantity": 2}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    print(f"Ответ от сервера: {data}")
                    assert data["cart_item_id"] == 1
                    assert data["name"] == "Test Product"
                    assert data["price"] == 100.0
                    assert data["quantity"] == 2
                    assert data["total"] == 200.0

    @pytest.mark.asyncio
    async def test_update_cart_item_endpoint(self, auth_client):
        with patch('app.features.cart.crud.CartCRUD.get_cart_item') as mock_get_item:
            mock_get_item.return_value = MagicMock(
                cart_item_id=1,
                product_id=1
            )
            
            with patch('app.features.cart.router.check_product_availability') as mock_check:
                mock_check.return_value = MagicMock(product_id=1, price=10000)
                
                with patch('app.features.cart.crud.CartCRUD.update_cart_item') as mock_update:
                    mock_update.return_value = MagicMock()
                    
                    response = auth_client.put(
                        "/cart/items/1",
                        json={"quantity": 3}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["cart_item_id"] == 1
                    assert data["quantity"] == 3

    @pytest.mark.asyncio
    async def test_remove_from_cart_endpoint(self, auth_client):
        with patch('app.features.cart.crud.CartCRUD.remove_from_cart') as mock_remove:
            mock_remove.return_value = True
            response = auth_client.delete("/cart/items/1")
            assert response.status_code == 200
            assert response.json()["deleted"] == 1

    @pytest.mark.asyncio
    async def test_clear_cart_endpoint(self, auth_client):
        with patch('app.features.cart.crud.CartCRUD.clear_cart') as mock_clear:
            mock_clear.return_value = True
            
            response = auth_client.post("/cart/clear")
            assert response.status_code == 200
            assert response.json()["cleared"] is True