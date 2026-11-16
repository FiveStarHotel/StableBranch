from datetime import UTC, datetime

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