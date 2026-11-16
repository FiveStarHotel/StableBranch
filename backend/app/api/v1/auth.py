from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.core.dependency import CurrentUserDep, SessionDep
from backend.app.schemas.token import RefreshRequest, Token
from backend.app.schemas.user import (
    EmailChange,
    EmailChangeConfirm,
    PasswordChange,
    PasswordResetComplete,
    PasswordResetRequest,
    PasswordResetVerifyCode,
    RegisterConfirm,
    UserCreate,
)
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

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, session: SessionDep):
    await service_auth.logout(payload, session)

@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all_devices(payload: RefreshRequest, session: SessionDep):
    await service_auth.logout_all_devices(payload, session)

@router.post("/change-email", status_code=status.HTTP_202_ACCEPTED)
async def request_email_change(
    payload: EmailChange,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    await service_auth.request_email_change(payload, current_user, session)
    return {"detail": "Verification code sent"}

@router.post("/change-email/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_email_change(
    payload: EmailChangeConfirm,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    await service_auth.confirm_email_change(payload, current_user, session)

@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: PasswordChange,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    await service_auth.change_password(payload, current_user, session)

@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(payload: PasswordResetRequest, session: SessionDep):
    await service_auth.forgot_password(payload, session)
    return {"detail": "If the email is registered, a verification code has been sent"}

@router.post("/forgot-password/verify-code")
async def verify_password_reset_code(
    payload: PasswordResetVerifyCode,
    session: SessionDep,
):
    reset_token = await service_auth.verify_password_reset_code(payload, session)
    return {"reset_token": reset_token}

@router.post("/forgot-password/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(payload: PasswordResetComplete, session: SessionDep):
    await service_auth.reset_password(payload, session)
