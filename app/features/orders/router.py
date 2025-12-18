from fastapi import APIRouter
from .form_router import web_router

router = APIRouter(prefix="/orders", tags=["orders"])