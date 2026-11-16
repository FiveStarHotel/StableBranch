from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import InactiveUserError, InvalidAccessToken
from backend.app.core.security import validate_access_token
from backend.app.database.base import SessionLocal
from backend.app.database.models import User
from backend.app.repository import user as repository_user


async def get_session():
    async with SessionLocal() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    try:
        user_id = validate_access_token(token)
    except jwt.InvalidTokenError:
        raise InvalidAccessToken()
    
    user = await repository_user.get_user_by_id(session, user_id)

    if user is None:
        raise InvalidAccessToken()

    if not user.is_active:
        raise InactiveUserError()

    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]
