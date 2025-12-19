from fastapi import APIRouter, Request, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from app.infra.templates import templates
from app.infra.db import get_db
from app.features.users.schemas import UserCreate
from app.features.auth.schemas import UserLogin
from app.core.security import create_access_token
import re
from typing import Optional

router = APIRouter(prefix="/auth", tags=["authentication-forms"])


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    """Нормализует телефон в формат +7 XXX XXX-XX-XX"""
    if not phone or not phone.strip():
        return None

    phone = phone.strip()

    # Очищаем от всех нецифровых символов
    digits = re.sub(r'\D', '', phone)

    if not digits:
        return None

    # Обрабатываем разные форматы
    if digits.startswith('7') and len(digits) == 11:
        # 7XXXXXXXXXX -> +7 XXX XXX-XX-XX
        return f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:]}"
    elif digits.startswith('8') and len(digits) == 11:
        # 8XXXXXXXXXX -> +7 XXX XXX-XX-XX
        return f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:]}"
    elif digits.startswith('+7') and len(digits) == 12:
        # +7XXXXXXXXXX -> +7 XXX XXX-XX-XX
        return f"+7 {digits[2:5]} {digits[5:8]}-{digits[8:10]}-{digits[10:]}"
    elif len(digits) == 10:
        # XXXXXXXXXX -> +7 XXX XXX-XX-XX
        return f"+7 {digits[0:3]} {digits[3:6]}-{digits[6:8]}-{digits[8:]}"
    else:
        # Неизвестный формат, возвращаем как есть
        return phone


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
        normalized_phone = normalize_phone(phone) if phone else None

        user_data = UserCreate(
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            phone=normalized_phone,
            password=password,
            password_confirm=password_confirm,
            role=role
        )

        from app.features.auth.router import register as api_register

        try:
            user_profile = await api_register(user_data, db)
        except HTTPException as e:
            error_msg = str(e.detail)
            if error_msg.startswith("Value error, "):
                error_msg = error_msg.replace("Value error, ", "")
            return RedirectResponse(
                url=f"/auth/register?error={error_msg}",
                status_code=303
            )

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

    except ValidationError as e:
        error_msg = "Ошибка в данных формы"
        for error in e.errors():
            if 'msg' in error:
                msg = error['msg']
                if 'Value error, ' in msg:
                    msg = msg.replace('Value error, ', '')
                error_msg = msg
                break
        return RedirectResponse(
            url=f"/auth/register?error={error_msg}",
            status_code=303
        )
    except Exception as e:
        print(f"Registration error: {e}")
        return RedirectResponse(
            url=f"/auth/register?error=Ошибка при регистрации",
            status_code=303
        )


@router.post("/login/redirect", response_class=RedirectResponse)
async def login_redirect(
        email: str = Form(),
        password: str = Form(),
        db: AsyncSession = Depends(get_db)
):
    try:
        login_data = UserLogin(email=email, password=password)
        from app.features.auth.router import login_json as api_login
        try:
            token_data = await api_login(login_data, db)
        except HTTPException as e:
            if e.status_code == 401:
                error_message = "Неверный email или пароль"
            else:
                error_message = str(e.detail)
                if error_message.startswith("Value error, "):
                    error_message = error_message.replace("Value error, ", "")

            return RedirectResponse(
                url=f"/auth/login?error={error_message}",
                status_code=303
            )

        response = RedirectResponse(
            url="/products/catalog",
            status_code=303
        )
        response.set_cookie(
            key="access_token",
            value=token_data.access_token,
            httponly=True,
            max_age=120 * 60,
            samesite="lax",
            secure=True,
            path="/"
        )
        return response

    except ValidationError as e:
        error_message = "Неверный формат email"
        return RedirectResponse(
            url=f"/auth/login?error={error_message}",
            status_code=303
        )
    except Exception:
        return RedirectResponse(
            url="/auth/login?error=Ошибка сервера",
            status_code=303
        )
