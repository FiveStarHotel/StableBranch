import asyncio
import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from backend.app.core.config import settings

password_hash = PasswordHash.recommended()

async def hash_password(password: str) -> str:
    return await asyncio.to_thread(password_hash.hash, password)

async def verify_password(password: str, hash: str) -> bool:
    return await asyncio.to_thread(password_hash.verify, password, hash)

def generate_access_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(seconds=settings.access_token_ttl)
    payload = {
        "sub": str(user_id),
        "iat": datetime.now(UTC),
        "exp": expires_at
    }
    return jwt.encode(
        payload,
        settings.secret_token,
        settings.jwt_algorithm
    )

def validate_access_token(token: str) -> int:
    payload = jwt.decode(
        token,
        settings.secret_token,
        [settings.jwt_algorithm],
        options={"require": ["sub", "exp", "iat"]}
    )

    return int(payload["sub"])

def generate_refresh_token() -> str:
    return secrets.token_hex(64)

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
