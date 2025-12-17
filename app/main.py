from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

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

    # healthcheck
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # удобный редирект на каталог
    @app.get("/", include_in_schema=False)
    async def root():
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
