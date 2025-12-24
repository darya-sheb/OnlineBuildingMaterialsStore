import pytest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from sqlalchemy import select
from app.features.products import crud
from app.features.products.schemas import PrCreate, PrUpdate, PrRead
from app.models.product import Product
from app.models.user import User, UserRole


class TestProductsAPIEndpoints:
    @pytest.mark.asyncio
    async def test_get_all_products_endpoint(self, client):
        with patch('app.features.products.crud.get_products') as mock_get:
            products = [
                SimpleNamespace(
                    product_id=1,
                    manufacturer="Manufacturer 1",
                    name="Product 1",
                    dimensions="10x10x10",
                    unit="шт",
                    price=10000,
                    quantity_available=10,
                    image_path=None,
                    created_at="2023-01-01T00:00:00",
                    updated_at="2023-01-01T00:00:00"
                ),
                SimpleNamespace(
                    product_id=2,
                    manufacturer="Manufacturer 2",
                    name="Product 2",
                    unit="кг",
                    price=20000,
                    quantity_available=5,
                    image_path=None,
                    created_at="2023-01-01T00:00:00",
                    updated_at="2023-01-01T00:00:00"
                )
            ]
            mock_get.return_value = products
            response = client.get("/products/")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["product_id"] == 1
            assert data[0]["name"] == "Product 1"
            assert data[1]["product_id"] == 2
            assert data[1]["name"] == "Product 2"

    @pytest.mark.asyncio
    async def test_get_product_functionality(self, db):
        product = Product(
            manufacturer="Test Manufacturer",
            name="Test Product",
            dimensions="10x10x10",
            unit="шт",
            price=15000,
            quantity_available=10
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        found_product = await crud.get_product(db, product.product_id)
        assert found_product is not None
        assert found_product.product_id == product.product_id
        assert found_product.name == "Test Product"
        assert found_product.price == 15000


class TestProductsCRUD:
    @pytest.mark.asyncio
    async def test_get_products(self, db):
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
            unit="кг",
            price=20000,
            quantity_available=5
        )
        db.add(product1)
        db.add(product2)
        await db.commit()
        all_products = await crud.get_products(db)
        assert len(all_products) == 2
        names = {p.name for p in all_products}
        assert "Product 1" in names
        assert "Product 2" in names

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, db):
        product = await crud.get_product(db, 999)
        assert product is None

    @pytest.mark.asyncio
    async def test_get_product_exception_handling(self, db):
        with patch('app.features.products.crud.select') as mock_select:
            mock_select.side_effect = Exception("Database error")
            with pytest.raises(HTTPException) as exc_info:
                await crud.get_product(db, 1)
            assert exc_info.value.status_code == 500
            assert "Ошибка при получении товара" in str(exc_info.value.detail)


class TestProductsSchemas:
    def test_pr_create_schema(self):
        data = {
            "manufacturer": "Test Manufacturer",
            "name": "Test Product",
            "dimensions": "10x10x10",
            "unit": "шт",
            "price": 10050,
            "quantity_available": 10
        }
        product = PrCreate(**data)
        assert product.manufacturer == "Test Manufacturer"
        assert product.name == "Test Product"
        assert product.price == 10050
        assert product.quantity_available == 10

    def test_pr_read_schema(self):
        data = {
            "product_id": 1,
            "manufacturer": "Test",
            "name": "Test Product",
            "dimensions": "10x10x10",
            "unit": "шт",
            "price": 10000,
            "quantity_available": 10,
            "image_path": None,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        product = PrRead(**data)
        assert product.product_id == 1
        assert product.name == "Test Product"
        assert product.price == 10000