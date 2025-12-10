from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from starlette.responses import Response

from app.core.settings import settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd.verify(password, password_hash)


def create_access_token(user_id: int, role: str, expires_minutes: int = 120) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": str(user_id), "role": role, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


def set_auth_cookie(resp: Response, token: str) -> None:
    resp.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        path="/",
    )


def clear_auth_cookie(resp: Response) -> None:
    resp.delete_cookie(settings.AUTH_COOKIE_NAME, path="/")
