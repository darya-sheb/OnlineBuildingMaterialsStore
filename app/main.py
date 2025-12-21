from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.db import get_db
from app.core.settings import settings
from app.features.auth.dependencies import get_optional_user
from app.models.user import User


def create_app() -> FastAPI:
    app = FastAPI(title="Online Building Materials Store")

    static_dir = Path(settings.STATIC_ROOT)
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    media_dir = Path(settings.MEDIA_ROOT)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

    templates_dir = Path(__file__).parent.parent / "web" / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/auth/register", response_class=HTMLResponse, include_in_schema=False)
    async def register_page(request: Request, user: Optional[User] = Depends(get_optional_user)):
        return templates.TemplateResponse("auth/register.html", {"request": request, "user": user})
    
    @app.get("/auth/login", response_class=HTMLResponse, include_in_schema=False)
    async def login_page(request: Request, user: Optional[User] = Depends(get_optional_user)):
        return templates.TemplateResponse("auth/login.html", {"request": request, "user": user})


    @app.get("/cart", response_class=HTMLResponse, include_in_schema=False)
    async def cart_page(
        request: Request,
        user: Optional[User] = Depends(get_optional_user)
    ):
        if not user:
            return RedirectResponse("/auth/login", status_code=303)
        return templates.TemplateResponse("cart/view.html", {
            "request": request,
            "user": user
        })
    
    @app.get("/orders/checkout", response_class=HTMLResponse, include_in_schema=False)
    async def order_checkout_page(
        request: Request,
        user: Optional[User] = Depends(get_optional_user)
    ):
        if not user:
            return RedirectResponse("/auth/login", status_code=303)
        return templates.TemplateResponse("cart/confirmation.html", {
            "request": request,
            "user": user
        })
    
    @app.get("/orders/success/{order_id}", response_class=HTMLResponse, include_in_schema=False)
    async def order_success_page(
        request: Request,
        order_id: int,
        user: Optional[User] = Depends(get_optional_user)
    ):
        return templates.TemplateResponse("orders/success.html", {
            "request": request,
            "order_id": order_id,
            "user": user
        })
    
    @app.get("/profile", response_class=HTMLResponse, include_in_schema=False)
    async def profile_page(
        request: Request,
        user: Optional[User] = Depends(get_optional_user)
    ):
        if not user:
            return RedirectResponse("/auth/login", status_code=303)
        return templates.TemplateResponse("users/profile.html", {
            "request": request,
            "user": user
        })

    # routers
    from app.features.auth.router import router as auth_router
    from app.features.auth.form_router import router as auth_form_router
    from app.features.cart.router import router as cart_router
    from app.features.orders.router import router as orders_router
    from app.features.products.router import router as products_router
    from app.features.products.form_router import router as products_form_router
    from app.features.users.router import router as users_router

    app.include_router(auth_router)
    app.include_router(auth_form_router)
    app.include_router(users_router)
    app.include_router(products_router)
    app.include_router(products_form_router)
    app.include_router(cart_router)
    app.include_router(orders_router)

    return app


app = create_app()
