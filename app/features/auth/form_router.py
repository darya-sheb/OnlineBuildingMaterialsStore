from fastapi import APIRouter, Request, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, RedirectResponse
from app.infra.templates import templates
from app.infra.db import get_db
from app.features.users.schemas import UserCreate, UserProfile
from app.features.auth.schemas import UserLogin
from app.models.user import User, UserRole
from sqlalchemy.future import select
from app.core.security import hash_password, create_access_token, verify_password
from app.features.auth.service import auth_service

router = APIRouter(prefix="/auth", tags=["authentication-forms"])


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/register/redirect", response_class=RedirectResponse)
async def register_redirect(
        request: Request,
        email: str = Form(),
        first_name: str = Form(),
        last_name: str = Form(),
        patronymic: str = Form(None),
        phone: str = Form(None),
        password: str = Form(),
        password_confirm: str = Form(),
        role: str = Form("CLIENT"),
        db: AsyncSession = Depends(get_db)
):
    try:
        user_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "patronymic": patronymic,
            "phone": phone,
            "password": password,
            "password_confirm": password_confirm,
            "role": role
        }

        user_create = UserCreate(**user_data)

        from app.features.auth.router import register as api_register
        user_profile = await api_register(user_create, db)

        access_token = create_access_token(
            user_id=user_profile.user_id,
            role=user_profile.role,
            expires_minutes=120
        )

        response = RedirectResponse(
            url="/products/catalog",
            status_code=303
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=120 * 60,
            samesite="lax"
        )
        return response

    except HTTPException as e:
        return RedirectResponse(
            url=f"/auth/register?error={str(e.detail)}",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/auth/register?error=Ошибка сервера: {str(e)}",
            status_code=303
        )


@router.post("/login/redirect", response_class=RedirectResponse)
async def login_redirect(
        email: str = Form(),
        password: str = Form(),
        db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth_service.authenticate_user(
            db,
            email=email,
            password=password
        )

        access_token = create_access_token(
            user_id=user.user_id,
            role=user.role.value,
            expires_minutes=120
        )

        response = RedirectResponse(
            url="/products/catalog",
            status_code=303
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=120 * 60,
            samesite="lax",
            secure=True,
            path="/"
        )
        return response
    except HTTPException as e:
        if e.status_code == 401:
            error_code = "invalid_credentials"
        else:
            error_code = "auth_failed"
        return RedirectResponse(
            url=f"/auth/login?error={error_code}",
            status_code=303
        )
    except Exception:
        return RedirectResponse(
            url="/auth/login?error=server_error",
            status_code=303
        )
