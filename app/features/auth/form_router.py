from app.features.auth.router import router, register as register_json, login_json
from fastapi import Request, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, RedirectResponse
from app.infra.templates import templates
from app.features.users import UserCreate, UserProfile
from app.infra.db import get_db
from pydantic import EmailStr
from app.features.auth.schemas import UserLogin


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/form/register", response_class=RedirectResponse)
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
        user_data = UserCreate(
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            phone=phone,
            password=password,
            password_confirm=password_confirm,
            role=role
        )

        await register_json(user_data, db)
        return RedirectResponse(
            url="/products/catalog?message=registration_success",
            status_code=303
        )
    except Exception as error:
        return RedirectResponse(
            url=f"/auth/register?error={str(error)}",
            status_code=303
        )


@router.post("/form/login", response_class=RedirectResponse)
async def login_redirect(
        email: EmailStr = Form(),
        password: str = Form(),
        password_confirm: str = Form(),
        db: AsyncSession = Depends(get_db)):
    try:
        login_data = UserLogin(
            email=email,
            password=password,
            password_confirm=password_confirm
        )
        await login_json(login_data, db)
        return RedirectResponse(
            url="/products/catalog?message=login_success",
            status_code=303
        )
    except Exception as error:
        return RedirectResponse(
            url=f"/auth/login?error={str(error)}"
        )
