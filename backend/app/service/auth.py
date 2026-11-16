from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.auth import RefreshRequest
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    CredentialsError,
    InactiveUserError,
    InvalidRefreshTokenError,
    InvalidVerificationCodeError,
    TooManyAccountVerificationAttemptsError,
    TooManyVerificationAttemptsError,
    UsernameOrEmailOccupiedError,
)
from backend.app.core.security import (
    DUMMY_HASH,
    generate_access_token,
    generate_password_reset_token,
    generate_refresh_token,
    generate_verification_code,
    hash_password,
    hash_refresh_token,
    hash_verification_code,
    send_verification_code,
    validate_password_reset_token,
    validate_verification_code,
    verify_password,
)
from backend.app.database.models import User
from backend.app.repository import refresh_token as repository_refresh_token
from backend.app.repository import user as repository_users
from backend.app.schemas.token import Token
from backend.app.schemas.user import (
    EmailChange,
    EmailChangeConfirm,
    PasswordChange,
    PasswordResetComplete,
    PasswordResetRequest,
    PasswordResetVerifyCode,
    RegisterConfirm,
    UserCreate,
)


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


def _clear_verification_code(user: User) -> None:
    user.verification_code_hash = None
    user.verification_code_expires_at = None
    user.verification_attempts = 0


async def _verify_account_code(
    user: User,
    candidate_hash: str,
    session: AsyncSession,
) -> None:
    if (
        user.verification_code_hash is None
        or user.verification_code_expires_at is None
        or user.verification_code_expires_at <= datetime.now(UTC)
    ):
        raise InvalidVerificationCodeError()

    if user.verification_attempts >= settings.max_verification_code_attempts:
        raise TooManyAccountVerificationAttemptsError()

    if not validate_verification_code(candidate_hash, user.verification_code_hash):
        user.verification_attempts += 1
        await session.commit()
        raise InvalidVerificationCodeError()


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

    if not user.is_active:
        raise InactiveUserError()

    return await _issue_token(user.id, session)


async def refresh_access_token(refresh_payload: RefreshRequest, session: AsyncSession) -> Token:
    stored_refresh_token = await repository_refresh_token.get_refresh_token_by_hash(
        session,
        hash_refresh_token(refresh_payload.refresh_token)
    )

    if stored_refresh_token is None:
        raise InvalidRefreshTokenError()

    user = await repository_users.get_user_by_id(session, stored_refresh_token.user_id)

    if user is None:
        raise InvalidRefreshTokenError()

    if stored_refresh_token.expires_at <= datetime.now(UTC):
        raise InvalidRefreshTokenError()
    
    if stored_refresh_token.revoked_at is not None:
        raise InvalidRefreshTokenError() # TODO: Заменить выходом со всех устройств (в реальном мире еще и ором на электронную почту)

    if not user.is_active:
        raise InactiveUserError()

    await repository_refresh_token.revoke_refresh_token(session, stored_refresh_token)
    await session.commit()

    return await _issue_token(user.id, session)


async def logout(refresh_payload: RefreshRequest, session: AsyncSession) -> None:
    stored_refresh_token = await repository_refresh_token.get_refresh_token_by_hash(
        session,
        hash_refresh_token(refresh_payload.refresh_token)
    )

    if stored_refresh_token is None or stored_refresh_token.revoked_at is not None:
        return
    
    await repository_refresh_token.revoke_refresh_token(
        session,
        stored_refresh_token
    )

    await session.commit()


async def logout_all_devices(refresh_payload: RefreshRequest, session: AsyncSession) -> None:
    stored_refresh_token = await repository_refresh_token.get_refresh_token_by_hash(
        session,
        hash_refresh_token(refresh_payload.refresh_token)
    )

    if stored_refresh_token is None:
        raise InvalidRefreshTokenError()

    if stored_refresh_token.expires_at <= datetime.now(UTC):
        raise InvalidRefreshTokenError()

    if stored_refresh_token.revoked_at is not None:
        raise InvalidRefreshTokenError()

    await repository_refresh_token.revoke_all_user_refresh_tokens(session, stored_refresh_token.user_id)
    await session.commit()


async def request_email_change(
    payload: EmailChange,
    user: User,
    session: AsyncSession,
) -> None:
    if payload.old_email != user.email:
        raise CredentialsError()

    existing_user = await repository_users.get_user_by_email(session, payload.new_email)
    if existing_user is not None and existing_user.id != user.id:
        raise UsernameOrEmailOccupiedError()

    code = generate_verification_code()
    user.verification_code_hash = hash_verification_code(f"{payload.new_email}:{code}")
    user.verification_code_expires_at = datetime.now(UTC) + timedelta(
        seconds=settings.verification_code_ttl
    )
    user.verification_attempts = 0
    await session.commit()
    send_verification_code(payload.new_email, code)


async def confirm_email_change(
    payload: EmailChangeConfirm,
    user: User,
    session: AsyncSession,
) -> None:
    existing_user = await repository_users.get_user_by_email(session, payload.email)
    if existing_user is not None and existing_user.id != user.id:
        raise UsernameOrEmailOccupiedError()

    await _verify_account_code(
        user,
        hash_verification_code(f"{payload.email}:{payload.code}"),
        session,
    )
    user.email = payload.email
    _clear_verification_code(user)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise UsernameOrEmailOccupiedError()


async def change_password(
    payload: PasswordChange,
    user: User,
    session: AsyncSession,
) -> None:
    if not await verify_password(payload.old_password.get_secret_value(), user.hash_password):
        raise CredentialsError()

    user.hash_password = await hash_password(payload.new_password.get_secret_value())
    await repository_refresh_token.revoke_all_user_refresh_tokens(session, user.id)
    await session.commit()


async def forgot_password(payload: PasswordResetRequest, session: AsyncSession):
    user = await repository_users.get_user_by_email(session, payload.email)

    if user is not None and user.is_active:
        code = generate_verification_code()
        user.verification_code_hash = hash_verification_code(code)
        user.verification_code_expires_at = datetime.now(UTC) + timedelta(
            seconds=settings.verification_code_ttl
        )
        user.verification_attempts = 0
        await session.commit()
        send_verification_code(user.email, code)


async def reset_password(
    payload: PasswordResetComplete,
    session: AsyncSession,
) -> None:
    user_id = validate_password_reset_token(payload.reset_token)
    if user_id is None:
        raise InvalidVerificationCodeError()

    user = await repository_users.get_user_by_id(session, user_id)
    if (
        user is None
        or not user.is_active
        or user.verification_code_hash is None
        or user.verification_code_expires_at is None
        or user.verification_code_expires_at <= datetime.now(UTC)
        or not validate_verification_code(
            hash_verification_code(payload.reset_token),
            user.verification_code_hash,
        )
    ):
        raise InvalidVerificationCodeError()

    user.hash_password = await hash_password(payload.new_password.get_secret_value())
    _clear_verification_code(user)
    await repository_refresh_token.revoke_all_user_refresh_tokens(session, user.id)
    await session.commit()


async def verify_password_reset_code(
    payload: PasswordResetVerifyCode,
    session: AsyncSession,
) -> str:
    user = await repository_users.get_user_by_email(session, payload.email)
    if user is None or not user.is_active:
        raise InvalidVerificationCodeError()

    await _verify_account_code(user, hash_verification_code(payload.code), session)
    reset_token = generate_password_reset_token(user.id)
    user.verification_code_hash = hash_verification_code(reset_token)
    user.verification_code_expires_at = datetime.now(UTC) + timedelta(
        seconds=settings.verification_code_ttl
    )
    user.verification_attempts = 0
    await session.commit()
    return reset_token
