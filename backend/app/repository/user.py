from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database.models import User


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = (
        select(User)
        .where(User.username == username)
        .limit(1)
    )

    user = await session.scalar(stmt)

    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    stmt = (
        select(User)
        .where(User.email == email)
        .limit(1)
    )

    user = await session.scalar(stmt)

    return user


async def get_user_by_username_or_email(session: AsyncSession, username: str, email: str) -> User | None:
    stmt = (
        select(User)
        .where(or_(User.username == username, User.email == email))
        .limit(1)
    )

    user = await session.scalar(stmt)

    return user


async def create_user(
    session: AsyncSession,
    username: str,
    email: str,
    hashed_password: str
) -> User:
    user = User(
        username=username,
        email=email,
        hash_password=hashed_password
    )

    session.add(user)
    await session.flush()

    return user
