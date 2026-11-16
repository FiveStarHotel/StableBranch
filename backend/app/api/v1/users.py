from fastapi import APIRouter, status

from backend.app.core.dependency import CurrentUserDep, SessionDep
from backend.app.schemas.user import UserProfileUpdate, UserRead
from backend.app.service import users as service_users

router = APIRouter(prefix="/users")

@router.get("/me", response_model=UserRead)
async def who_am_i(current_user: CurrentUserDep):
    return service_users.who_am_i(current_user)


@router.patch("/me", response_model=UserRead)
async def update_profile(
    payload: UserProfileUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    return await service_users.update_profile(payload, current_user, session)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(current_user: CurrentUserDep, session: SessionDep):
    await service_users.delete_account(current_user, session)