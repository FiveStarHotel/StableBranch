from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.exceptions import UsernameOrEmailOccupiedError
from backend.app.core.security import (
    generate_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
)
from backend.app.repository import refresh_token as repository_refresh_token
from backend.app.repository import user as repository_users
from backend.app.schemas.token import Token
from backend.app.schemas.user import UserCreate


async def _issue_token(user_id: int, session: AsyncSession) -> Token:
    expires_at = datetime.now(UTC) + timedelta(seconds=settings.refresh_token_ttl)
    token = generate_refresh_token()

    await repository_refresh_token.create_refresh_token(
        session,
        user_id,
        hash_refresh_token(token),
        expires_at
    )

    await session.commit()

    return Token(
        access_token=generate_access_token(user_id),
        refresh_token=token
    )


async def register(user: UserCreate, session: AsyncSession):
    if await repository_users.get_user_by_username(session, user.username) is not None:
        raise UsernameOrEmailOccupiedError()

    if await repository_users.get_user_by_email(session, user.email) is not None:
        raise UsernameOrEmailOccupiedError()

    hashed_password = await hash_password(str(user.password))

    new_user = await repository_users.create_user(
        session=session,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise UsernameOrEmailOccupiedError()
    
    return await _issue_token(
        new_user.id,
        session
    )