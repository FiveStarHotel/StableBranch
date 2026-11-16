from fastapi import APIRouter

from backend.app.core.dependency import SessionDep
from backend.app.schemas.token import Token
from backend.app.schemas.user import UserCreate
from backend.app.service import auth as service_users

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(payload: UserCreate, session: SessionDep):
    return await service_users.register(payload, session)