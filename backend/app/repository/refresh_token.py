from datetime import UTC, datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models import RefreshToken


async def create_refresh_token(
    session: AsyncSession,
    user_id: int,
    hash_token: str,
    expires_at: datetime
) -> None:
    refresh_token = RefreshToken(
        user_id=user_id,
        hash_token=hash_token,
        created_at=datetime.now(UTC),
        expires_at=expires_at
    )

    session.add(refresh_token)
    await session.flush()


async def get_refresh_token_by_hash(session: AsyncSession, token_hash: str) -> RefreshToken | None:
    stmt = (
        select(RefreshToken)
        .where(RefreshToken.hash_token == token_hash)
        .limit(1)
    )

    refresh_token = await session.scalar(stmt)

    return refresh_token


async def revoke_refresh_token(session: AsyncSession, token: RefreshToken) -> None:
    token.revoked_at = datetime.now(UTC)
    await session.flush()


async def revoke_all_user_refresh_tokens(session: AsyncSession, user_id: int) -> None:
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=datetime.now(UTC))
    )

    await session.execute(stmt)
    await session.flush()


async def delete_user_refresh_tokens(session: AsyncSession, user_id: int) -> None:
    stmt = delete(RefreshToken).where(RefreshToken.user_id == user_id)
    await session.execute(stmt)
    await session.flush()
