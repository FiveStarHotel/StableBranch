import asyncio
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from backend.app.core.config import settings

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("stupiddummypassword")

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


def generate_verification_code() -> str:
    return f"{secrets.randbelow(10**6):06d}"

def hash_verification_code(code: str) -> str:
    return hmac.new(
        settings.secret_token.encode(),
        code.encode(),
        hashlib.sha256
    ).hexdigest()

def validate_verification_code(code: str, code_hashed: str) -> bool:
    return hmac.compare_digest(code, code_hashed)

def send_verification_code(email: str, code: str) -> None:
    print(f"[VERIFY-CODE] {email}: {code}")
