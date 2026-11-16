from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.exceptions import (
    CredentialsError,
    InvalidVerificationCodeError,
    TooManyVerificationAttemptsError,
    UsernameOrEmailOccupiedError,
)
from backend.app.core.security import (
    DUMMY_HASH,
    generate_access_token,
    generate_refresh_token,
    generate_verification_code,
    hash_password,
    hash_refresh_token,
    hash_verification_code,
    send_verification_code,
    validate_verification_code,
    verify_password,
)
from backend.app.database.models import User
from backend.app.repository import refresh_token as repository_refresh_token
from backend.app.repository import user as repository_users
from backend.app.schemas.token import Token
from backend.app.schemas.user import RegisterConfirm, UserCreate


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


async def _ensure_free(session: AsyncSession, found: User | None):
    if found is None:
        return
    
    # Неподтвержденный аккаунт с истекшим кодом не будет занимать логин и email на вечность вечную
    expires_at = found.verification_code_expires_at
    if found.is_active or (expires_at is not None and expires_at > datetime.now(UTC) and found.verification_attempts < settings.max_verification_code_attempts):
        raise UsernameOrEmailOccupiedError()
    
    await session.delete(found)
    await session.flush()


async def register(user: UserCreate, session: AsyncSession):
    await _ensure_free(session, await repository_users.get_user_by_username(session, user.username))
    await _ensure_free(session, await repository_users.get_user_by_email(session, user.email))

    hashed_password = await hash_password(user.password.get_secret_value())

    new_user = await repository_users.create_user(
        session=session,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
    )

    code = generate_verification_code()
    new_user.verification_code_hash = hash_verification_code(code)
    new_user.verification_code_expires_at = datetime.now(UTC) + timedelta(seconds=settings.verification_code_ttl)


    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise UsernameOrEmailOccupiedError()
    
    send_verification_code(new_user.email, code)
    

# 5 попыток на ввод верификации. Неудача - регистрация заново
async def confirm_registration(data: RegisterConfirm, session: AsyncSession) -> Token:
    user = await repository_users.get_user_by_email(session, data.email)
    if (
        user is None
        or user.is_active
        or user.verification_code_hash is None
        or user.verification_code_expires_at is None
        or user.verification_code_expires_at <= datetime.now(UTC)
    ):
        raise InvalidVerificationCodeError()

    if user.verification_attempts >= settings.max_verification_code_attempts:
        raise TooManyVerificationAttemptsError()
    
    if not validate_verification_code(hash_verification_code(data.code), user.verification_code_hash):
        user.verification_attempts += 1
        await session.commit()
        raise InvalidVerificationCodeError()
    
    user.is_active = True
    user.verification_code_hash = None
    user.verification_code_expires_at = None
    
    return await _issue_token(user.id, session)


async def login(username: str, password: str, session: AsyncSession) -> Token:
    user = await repository_users.get_user_by_username_or_email(
        session,
        username=username,
        email=username
    )

    if user is None:
        await verify_password(password, DUMMY_HASH)
        raise CredentialsError()
    
    if not await verify_password(password, user.hash_password):
        raise CredentialsError()

    return await _issue_token(user.id, session)

