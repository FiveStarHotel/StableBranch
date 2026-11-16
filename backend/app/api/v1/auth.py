from fastapi import APIRouter, status

from backend.app.core.dependency import SessionDep
from backend.app.schemas.token import Token
from backend.app.schemas.user import RegisterConfirm, UserCreate
from backend.app.service import auth as service_users

router = APIRouter()

@router.post("/register", status_code=status.HTTP_202_ACCEPTED)
async def register_user(payload: UserCreate, session: SessionDep):
    await service_users.register(payload, session)
    return {"detail": "Verification code sent"}

@router.post("/register/confirm", response_model=Token)
async def confirm_registration(payload: RegisterConfirm, session: SessionDep):
    return await service_users.confirm_registration(payload, session)
