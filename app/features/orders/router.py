from fastapi import APIRouter
from .routers import my_router, detail_router
from .form_router import web_router

router = APIRouter(prefix="/orders", tags=["orders"])
router.include_router(my_router)
router.include_router(detail_router)
router.include_router(web_router)