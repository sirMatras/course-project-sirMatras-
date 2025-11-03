from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import hashlib
import hmac

from jose import jwt

from app.settings import settings


def hash_password(password: str) -> str:
    # Simple PBKDF2 alternative via HMAC-SHA256 with secret pepper
    # For production, prefer passlib/bcrypt/argon2; here we avoid extra deps
    pepper = settings.jwt_secret.encode()
    return hmac.new(pepper, password.encode(), hashlib.sha256).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(password), hashed)


def create_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    return create_token(subject, timedelta(minutes=settings.access_token_exp_minutes), "access")


def create_refresh_token(subject: str) -> str:
    return create_token(subject, timedelta(days=settings.refresh_token_exp_days), "refresh")


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


