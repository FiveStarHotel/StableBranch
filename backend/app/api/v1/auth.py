from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.core.dependency import SessionDep
from backend.app.schemas.token import RefreshRequest, Token
from backend.app.schemas.user import RegisterConfirm, UserCreate
from backend.app.service import auth as service_auth

router = APIRouter(prefix="/auth")

@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register_user(payload: UserCreate, session: SessionDep):
    await service_auth.register(payload, session)
    return {"detail": "Verification code sent"}

@router.post("/register/confirm", response_model=Token)
async def confirm_registration(payload: RegisterConfirm, session: SessionDep):
    return await service_auth.confirm_registration(payload, session)

@router.post("/login", response_model=Token)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    return await service_auth.login(form.username, form.password, session)

@router.post("/refresh", response_model=Token)
async def refresh_access_token(payload: RefreshRequest, session: SessionDep):
    return await service_auth.refresh_access_token(payload, session)
