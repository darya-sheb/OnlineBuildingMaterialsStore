import asyncio
from app.features.products.crud import create_product
from app.infra.db import SessionLocal
from app.features.products.schemas import PrCreate


async def init_products():
    products = [
        {
            "id": 1,
            "name": "Кирпич красный М-150",
            "dimensions": "250х120х65 мм",
            "manufacturer": "Воскресенский кирпичный завод",
            "price": 22,
            "unit": "штука",
            "quantity_available": 1583
        },
        {
            "id": 2,
            "name": "Кирпич облицовочный белый",
            "dimensions": "250х120х88 мм",
            "manufacturer": "Борский силикатный завод",
            "price": 30,
            "unit": "штука",
            "quantity_available": 847
        },
        {
            "id": 3,
            "name": "Газоблок D500",
            "dimensions": "600х300х200 мм",
            "manufacturer": "Bonolit",
            "price": 123,
            "unit": "штука",
            "quantity_available": 478
        },
        {
            "id": 4,
            "name": "Пеноблок",
            "dimensions": "600х300х200 мм",
            "manufacturer": "Bonolit",
            "price": 96,
            "unit": "штука",
            "quantity_available": 352
        },
        {
            "id": 5,
            "name": "Цемент М500 (40 кг)",
            "manufacturer": "Цементум",
            "price": 448,
            "unit": "мешок",
            "quantity_available": 124
        },
        {
            "id": 6,
            "name": "Штукатурка гипсовая Волма Слой (30 кг)",
            "manufacturer": "Волма",
            "price": 382,
            "unit": "мешок",
            "quantity_available": 87
        },
        {
            "id": 7,
            "name": "Клей плиточный Ceresit CM 11 (25 кг)",
            "manufacturer": "Ceresit",
            "price": 565,
            "unit": "мешок",
            "quantity_available": 63
        },
        {
            "id": 8,
            "name": "Доска обрезная",
            "dimensions": "40х200х6000 мм",
            "manufacturer": "Лесопилка \"Тайга\"",
            "price": 15240,
            "unit": "м³",
            "quantity_available": 8
        },
        {
            "id": 9,
            "name": "Брус",
            "dimensions": "100х100х6000 мм",
            "manufacturer": "Лесопилка \"Тайга\"",
            "price": 18150,
            "unit": "м³",
            "quantity_available": 5
        },
        {
            "id": 10,
            "name": "Фанера ФК",
            "dimensions": "1525х1525х12 мм",
            "manufacturer": "Сыктывкарский ФЗ",
            "price": 947,
            "unit": "лист",
            "quantity_available": 49
        },
        {
            "id": 11,
            "name": "Металлочерепица 0,5 мм",
            "manufacturer": "Grand Line",
            "price": 452,
            "unit": "м²",
            "quantity_available": 124
        },
        {
            "id": 12,
            "name": "Утеплитель Rockwool 100 мм",
            "manufacturer": "Rockwool",
            "price": 1195,
            "unit": "упаковка",
            "quantity_available": 37
        },
        {
            "id": 13,
            "name": "Перфоратор Makita HR2470 780Вт 2,7 Дж",
            "manufacturer": "Makita",
            "price": 12480,
            "unit": "штука",
            "quantity_available": 7,
        },
        {
            "id": 14,
            "name": "Болгарка Интерскол 125 мм",
            "manufacturer": "Интерскол",
            "price": 3825,
            "unit": "штука",
            "quantity_available": 14,
        },
        {
            "id": 15,
            "name": "Набор инструментов 137 предметов",
            "manufacturer": "Tolsen",
            "price": 2490,
            "unit": "набор",
            "quantity_available": 17,
        }
    ]

    async with SessionLocal() as session:
        for product_data in products:
            product_id = product_data["id"]
            image_path = f"/products/stroimag_{product_id}.jpg"
            product_data["image_path"] = image_path
            del product_data["id"]
            await create_product(session, PrCreate(**product_data))
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_products())
