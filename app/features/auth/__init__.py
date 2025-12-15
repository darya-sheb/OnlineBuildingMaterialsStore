from .router import router
from .service import auth_service, AuthService
from .schemas import Token, UserLogin, TokenData
from .dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_client,
    get_current_staff,
    require_role,
    get_optional_user,
    oauth2_scheme
)

__all__ = [
    "router",
    "auth_service",
    "AuthService",
    "Token",
    "UserLogin",
    "TokenData",
    "get_current_user",
    "get_current_active_user",
    "get_current_client",
    "get_current_staff",
    "require_role",
    "get_optional_user",
    "oauth2_scheme"
]