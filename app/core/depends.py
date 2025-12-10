from fastapi import Cookie, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.settings import settings
from app.core.security import decode_access_token


class AuthPayload(BaseModel):
    user_id: int
    role: str


async def get_auth_payload(
    token: str | None = Cookie(default=None, alias=settings.AUTH_COOKIE_NAME),
) -> AuthPayload:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
        return AuthPayload(user_id=int(payload["sub"]), role=str(payload["role"]))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def require_staff(payload: AuthPayload = Depends(get_auth_payload)) -> AuthPayload:
    if payload.role != "STAFF":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Staff only")
    return payload
