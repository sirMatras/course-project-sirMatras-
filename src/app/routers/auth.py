from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time

from app.dependencies.db import get_db
from services.auth import hash_password, verify_password
from app.security import create_access_token, create_refresh_token, decode_token
from domain.schemas import UserCreate, TokenPair, UserRead
from domain.exceptions import BadRequest, Unauthorized
from adapters.sqlalchemy.models import User


router = APIRouter()


# Simple in-memory rate limiter for /auth/login (5 requests / 60 seconds per IP)
_RATE_LIMIT_WINDOW_SECONDS = 60
_RATE_LIMIT_MAX_REQUESTS = 5
_rate_limit_store: dict[str, list[float]] = {}


def _rate_limit_login(request: Request) -> None:
    now = time.monotonic()
    client_ip = (request.client.host if request.client else "unknown") or "unknown"
    window_start = now - _RATE_LIMIT_WINDOW_SECONDS
    timestamps = _rate_limit_store.get(client_ip, [])
    # Drop old timestamps
    timestamps = [t for t in timestamps if t >= window_start]
    if len(timestamps) >= _RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts. Please try later.")
    timestamps.append(now)
    _rate_limit_store[client_ip] = timestamps


@router.post("/register", response_model=UserRead, status_code=HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise BadRequest("Email already registered")
    user = User(email=payload.email, hashed_password=hash_password(payload.password), role="user")
    db.add(user)
    db.flush()
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
def login(payload: UserCreate, db: Session = Depends(get_db), _: None = Depends(_rate_limit_login)):
    user: User | None = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise Unauthorized("Invalid credentials")
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/logout")
def logout():
    # Stateless JWT: client discards tokens. For production, integrate token revocation list.
    return {"detail": "logged out"}


@router.post("/refresh", response_model=TokenPair)
def refresh(token_pair: TokenPair):
    payload = decode_token(token_pair.refresh_token)
    if payload.get("type") != "refresh":
        raise Unauthorized("Invalid token type")
    user_id = str(payload.get("sub"))
    return TokenPair(access_token=create_access_token(user_id), refresh_token=create_refresh_token(user_id))


