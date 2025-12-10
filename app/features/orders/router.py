from fastapi import APIRouter
from .routers import *

router = APIRouter(prefix="/orders", tags=["orders"])
router.include_router(checkout_router)
router.include_router(my_router)
router.include_router(detail_router)
