from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import UsernameOrEmailOccupiedError
from backend.app.database.models import User
from backend.app.repository import refresh_token as repository_refresh_token
from backend.app.repository import user as repository_users
from backend.app.schemas.user import UserProfileUpdate, UserRead


def who_am_i(user: User):
    return UserRead.model_validate(user)


async def update_profile(
    payload: UserProfileUpdate,
    user: User,
    session: AsyncSession,
) -> UserRead:
    if payload.username is not None and payload.username != user.username:
        existing_user = await repository_users.get_user_by_username(session, payload.username)
        if existing_user is not None and existing_user.id != user.id:
            raise UsernameOrEmailOccupiedError()

        try:
            await repository_users.update_username(session, user, payload.username)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise UsernameOrEmailOccupiedError()

    return UserRead.model_validate(user)


async def delete_account(user: User, session: AsyncSession) -> None:
    await repository_refresh_token.delete_user_refresh_tokens(session, user.id)
    await repository_users.delete_user(session, user)
    await session.commit()