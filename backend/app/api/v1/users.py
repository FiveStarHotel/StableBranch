from fastapi import APIRouter

from backend.app.core.dependency import CurrentUserDep
from backend.app.schemas.user import UserRead
from backend.app.service import users as service_users

router = APIRouter(prefix="/users")

@router.get("/me", response_model=UserRead)
async def who_am_i(current_user: CurrentUserDep):
    return service_users.who_am_i(current_user)