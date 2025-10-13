from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED

from app.dependencies.db import get_db
from services.auth import hash_password, verify_password
from app.security import create_access_token, create_refresh_token, decode_token
from domain.schemas import UserCreate, TokenPair, UserRead
from domain.exceptions import BadRequest, Unauthorized
from adapters.sqlalchemy.models import User


router = APIRouter()


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
def login(payload: UserCreate, db: Session = Depends(get_db)):
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


