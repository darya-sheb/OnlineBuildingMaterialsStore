from pathlib import Path

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infra.db import get_db
from app.core.settings import settings
from app.models.product import Product


def create_app() -> FastAPI:
    app = FastAPI(title="Online Building Materials Store")

    # static/media - ПОКА ЧТО ЗАКОМИЧЕНО ДЛЯ ТЕСТИРОВАНИЯ ШАБЛОНОВ
    static_dir = Path(settings.STATIC_ROOT)
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    media_dir = Path(settings.MEDIA_ROOT)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

    # templates
    templates_dir = Path(__file__).parent.parent / "web" / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    # healthcheck
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # HTML pages
    # @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    # async def home_page(request: Request):
    #     return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/auth/register", response_class=HTMLResponse, include_in_schema=False)
    async def register_page(request: Request):
        return templates.TemplateResponse("auth/register.html", {"request": request})
    
    @app.get("/auth/login", response_class=HTMLResponse, include_in_schema=False)
    async def login_page(request: Request):
        return templates.TemplateResponse("auth/login.html", {"request": request})
    
    @app.get("/products/catalog", response_class=HTMLResponse)
    async def products_page(request: Request):
        products = [
            {
                "id": 1,
                "name": "Кирпич красный М-150 (250х120х65 мм)",
                "manufacturer": "Воскресенский кирпичный завод",
                "price": 22,
                "unit": "штука",
                "quantity_available": 1583,
                "image_path": "https://static.tildacdn.com/stor6531-3932-4364-a332-623664396532/33785359.jpg"
            },
            {
                "id": 2,
                "name": "Кирпич облицовочный белый (250х120х88 мм)",
                "manufacturer": "Борский силикатный завод",
                "price": 30,
                "unit": "штука",
                "quantity_available": 847,
                "image_path": "https://n-dom.com/upload/iblock/mye/myemvztczps2jqtcw0qn4wkpx12xb9o2.jpg"
            },
            {
                "id": 3,
                "name": "Газоблок D500 (600х300х200 мм)",
                "manufacturer": "Bonolit",
                "price": 123,
                "unit": "штука",
                "quantity_available": 478,
                "image_path": "https://gbi-istra.ru/wp-content/uploads/2022/03/original-925x925-fit-4.jpg"
            },
            {
                "id": 4,
                "name": "Пеноблок (600х300х200 мм)",
                "manufacturer": "Bonolit",
                "price": 96,
                "unit": "штука",
                "quantity_available": 352,
                "image_path": "https://stroy77.ru/upload/iblock/49c/49c40e590bf1aaf13bfd5c8e4ad72a07.jpg"
            },
            {
                "id": 5,
                "name": "Цемент М500 Д0 (50 кг)",
                "manufacturer": "Евроцемент",
                "price": 448,
                "unit": "мешок",
                "quantity_available": 124,
                "image_path": "https://cementum.ru/upload/weimg_cache/eca/ecaae813213eb5077f1e6acb444f7351/e51fj6nw9ei032rdydow4a5rn0gqku31.webp"
            },
            {
                "id": 6,
                "name": "Штукатурка гипсовая Волма Слой (30 кг)",
                "manufacturer": "Волма",
                "price": 382,
                "unit": "мешок",
                "quantity_available": 87,
                "image_path": "https://stroika-alfa.ru/upload/iblock/0aa/f3n7safsmf2butk175r8lfas4cw5kcsv/shtukaturka_gipsovaya_volma_sloy_30_kg_detail.jpg"
            },
            {
                "id": 7,
                "name": "Клей плиточный Ceresit CM 11 (25 кг)",
                "manufacturer": "Ceresit",
                "price": 565,
                "unit": "мешок",
                "quantity_available": 63,
                "image_path": "https://media.obi.ru/resize/780x780/media/catalog/product/3/8/3811205_1_a348.jpg?store=moscow&image-type=small_image"
            },
            {
                "id": 8,
                "name": "Доска обрезная 40х200х6000 мм",
                "manufacturer": "Лесопилка \"Тайга\"",
                "price": 15240,
                "unit": "м³",
                "quantity_available": 8,
                "image_path": "https://lesdok.ru/wa-data/public/shop/products/65/91/9165/images/12109/12109.970.jpg"
            },
            {
                "id": 9,
                "name": "Брус 100х100х6000 мм",
                "manufacturer": "Лесопилка \"Тайга\"",
                "price": 18150,
                "unit": "м³",
                "quantity_available": 5,
                "image_path": "https://grandlesmarket.ru/assets/cache_image/products/534/brus-obreznoj-kamernoj-sushki_900x760_cf6.webp"
            },
            {
                "id": 10,
                "name": "Фанера ФК 1525х1525х12 мм",
                "manufacturer": "Сыктывкарский ФЗ",
                "price": 947,
                "unit": "лист",
                "quantity_available": 49,
                "image_path": "https://ollq.ru/images/detailed/278/491b6fbd5409c9ceb9f8f296df86ac3b.jpg"
            },
            {
                "id": 11,
                "name": "Металлочерепица 0,5 мм",
                "manufacturer": "Grand Line",
                "price": 452,
                "unit": "м²",
                "quantity_available": 124,
                "image_path": "https://micro-line.ru/images/detailed/1265/83842822_01.jpg"
            },
            {
                "id": 12,
                "name": "Утеплитель Rockwool 100 мм",
                "manufacturer": "Rockwool",
                "price": 1195,
                "unit": "упаковка",
                "quantity_available": 37,
                "image_path": "https://avatars.mds.yandex.net/get-mpic/12140066/2a0000018eae752b1fffc8de0d589666de53/orig"
            },
            {
                "id": 13,
                "name": "Перфоратор Makita HR2470 780Вт 2,7 Дж",
                "manufacturer": "Makita",
                "price": 12480,
                "unit": "штука",
                "quantity_available": 7,
                "image_path": "https://saray.ru/upload/iblock/b9c/t6wqmxioxurj0bs4mvpmpdu4em0vxcbq.jpg"
            },
            {
                "id": 14,
                "name": "Болгарка Интерскол 125 мм",
                "manufacturer": "Интерскол",
                "price": 3825,
                "unit": "штука",
                "quantity_available": 14,
                "image_path": "https://static.baza.farpost.ru/v/1573884819809_bulletin"
            },
            {
                "id": 15,
                "name": "Набор инструментов 137 предметов",
                "manufacturer": "Tolsen",
                "price": 2490,
                "unit": "набор",
                "quantity_available": 17,
                "image_path": "https://avatars.mds.yandex.net/get-goods_pic/10963530/hat68c9da3893a7fb23ee0fa6e882549f9e/orig"
            }
        ]
        return templates.TemplateResponse("catalog/list.html", {
            "request": request,
            "products": products
        })

    @app.get("/cart", response_class=HTMLResponse, include_in_schema=False)
    async def cart_page(request: Request, db: AsyncSession = Depends(get_db)):
        from app.features.cart.router import get_cart
        cart_response = await get_cart(request, db)        
        cart_items = cart_response["Data"]
        total = cart_response["total_price"]
        return templates.TemplateResponse("cart/view.html", {
            "request": request,
            "cart_items": cart_items,
            "total": total
        })
    
    # Оформление заказа
    @app.get("/orders/checkout", response_class=HTMLResponse, include_in_schema=False)
    async def order_checkout_page(request: Request):
        return templates.TemplateResponse("cart/confirmation.html", {"request": request})
    
    @app.get("/orders/success/{order_id}", response_class=HTMLResponse, include_in_schema=False)
    async def order_success_page(request: Request, order_id: int):
        return templates.TemplateResponse("orders/success.html", {
            "request": request,
            "order_id": order_id
        })
    
    # Личный кабинет
    @app.get("/profile", response_class=HTMLResponse, include_in_schema=False)
    async def profile_page(request: Request):
        return templates.TemplateResponse("users/profile.html", {"request": request})
    
    # @app.get("/orders/my", response_class=HTMLResponse, include_in_schema=False)
    # async def user_orders_page(request: Request):
    #     return templates.TemplateResponse("orders/history.html", {"request": request})
    
    # @app.get("/orders/{order_id}", response_class=HTMLResponse, include_in_schema=False)
    # async def order_detail_page(request: Request, order_id: int):
    #     return templates.TemplateResponse("orders/detail.html", {
    #         "request": request,
    #         "order_id": order_id
    #     })
    
    # Staff
    # @app.get("/staff", response_class=HTMLResponse, include_in_schema=False)
    # async def staff_dashboard_page(request: Request):
    #     return templates.TemplateResponse("staff/dashboard.html", {"request": request})
    #
    # @app.get("/staff/orders", response_class=HTMLResponse, include_in_schema=False)
    # async def staff_orders_page(request: Request):
    #     return templates.TemplateResponse("staff/orders.html", {"request": request})
    #
    # @app.get("/staff/orders/{order_id}", response_class=HTMLResponse, include_in_schema=False)
    # async def staff_order_detail_page(request: Request, order_id: int):
    #     return templates.TemplateResponse("staff/order_detail.html", {
    #         "request": request,
    #         "order_id": order_id
    #     })
    #
    # @app.get("/staff/products", response_class=HTMLResponse, include_in_schema=False)
    # async def staff_products_page(request: Request):
    #     return templates.TemplateResponse("staff/products.html", {"request": request})
    
    # routers
    from app.features.auth.router import router as auth_router
    from app.features.auth.form_router import router as auth_form_router
    from app.features.cart.router import router as cart_router
    from app.features.orders.router import router as orders_router
    from app.features.products.router import router as products_router
    from app.features.products.form_router import router as products_form_router
    from app.features.staff.router import router as staff_router
    from app.features.users.router import router as users_router

    app.include_router(auth_router)
    app.include_router(auth_form_router)
    app.include_router(users_router)
    app.include_router(products_router)
    app.include_router(products_form_router)
    app.include_router(cart_router)
    app.include_router(orders_router)
    # app.include_router(staff_router)

    return app


app = create_app()
