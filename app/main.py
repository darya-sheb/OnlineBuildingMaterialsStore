from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.settings import settings

from app.features.auth.router import router as auth_router
from app.features.cart.router import router as cart_router
from app.features.orders.router import router as orders_router
from app.features.products.form_router import router as products_router
from app.features.staff.router import router as staff_router
from app.features.users.router import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="Online Building Materials Store")

    # static/media (удобно для dev без nginx; с nginx тоже не мешает)
    static_dir = Path(settings.STATIC_ROOT)
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    media_dir = Path(settings.MEDIA_ROOT)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

    # Настройка шаблонов
    templates_dir = Path(__file__).parent.parent / "web" / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    # healthcheck
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # HTML страницы (публичные)
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def home_page(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/register", response_class=HTMLResponse, include_in_schema=False)
    async def register_page(request: Request):
        return templates.TemplateResponse("auth/register.html", {"request": request})
    
    @app.get("/login", response_class=HTMLResponse, include_in_schema=False)
    async def login_page(request: Request):
        return templates.TemplateResponse("auth/login.html", {"request": request})
    
    @app.get("/cart", response_class=HTMLResponse, include_in_schema=False)
    async def cart_page(request: Request):
        return templates.TemplateResponse("cart/view.html", {"request": request})
    
    @app.get("/products", response_class=HTMLResponse, include_in_schema=False)
    async def products_page(request: Request):
        return templates.TemplateResponse("catalog/list.html", {"request": request})
    
    @app.get("/products/{product_id}", response_class=HTMLResponse, include_in_schema=False)
    async def product_detail_page(request: Request, product_id: int):
        return templates.TemplateResponse("catalog/detail.html", {
            "request": request,
            "product_id": product_id
        })
    
    @app.get("/order-confirm", response_class=HTMLResponse, include_in_schema=False)
    async def order_confirm_page(request: Request):
        return templates.TemplateResponse("cart/confirmation.html", {"request": request})
    
    @app.get("/order-success", response_class=HTMLResponse, include_in_schema=False)
    async def order_success_page(request: Request):
        return templates.TemplateResponse("orders/success.html", {"request": request})
    
    # Личный кабинет пользователя
    @app.get("/profile", response_class=HTMLResponse, include_in_schema=False)
    async def profile_page(request: Request):
        return templates.TemplateResponse("users/profile.html", {"request": request})
    
    @app.get("/profile/orders", response_class=HTMLResponse, include_in_schema=False)
    async def user_orders_page(request: Request):
        return templates.TemplateResponse("orders/history.html", {"request": request})
    
    @app.get("/orders/{order_id}", response_class=HTMLResponse, include_in_schema=False)
    async def user_order_detail_page(request: Request, order_id: int):
        return templates.TemplateResponse("orders/detail.html", {
            "request": request,
            "order_id": order_id
        })
    
    # Панель сотрудника
    @app.get("/staff", response_class=HTMLResponse, include_in_schema=False)
    async def staff_dashboard_page(request: Request):
        return templates.TemplateResponse("staff/dashboard.html", {"request": request})
    
    @app.get("/staff/orders", response_class=HTMLResponse, include_in_schema=False)
    async def staff_orders_page(request: Request):
        return templates.TemplateResponse("staff/orders.html", {"request": request})
    
    @app.get("/staff/orders/{order_id}", response_class=HTMLResponse, include_in_schema=False)
    async def staff_order_detail_page(request: Request, order_id: int):
        return templates.TemplateResponse("staff/order_detail.html", {
            "request": request,
            "order_id": order_id
        })
    
    @app.get("/staff/products", response_class=HTMLResponse, include_in_schema=False)
    async def staff_products_page(request: Request):
        return templates.TemplateResponse("staff/products.html", {"request": request})
    
    # удобный редирект на каталог (оставить для API)
    @app.get("/api-redirect", include_in_schema=False)
    async def api_root():
        return RedirectResponse(url="/products")

    # routers
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(products_router)
    app.include_router(cart_router)
    app.include_router(orders_router)
    app.include_router(staff_router)

    return app


app = create_app()
