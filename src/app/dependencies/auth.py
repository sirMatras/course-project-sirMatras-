from typing import Optional
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session

from app.security import decode_token
from app.dependencies.db import get_db
from adapters.sqlalchemy.models import User
from domain.exceptions import Unauthorized, Forbidden


security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise Unauthorized("Missing Authorization header")
    if credentials.scheme.lower() != "bearer":
        raise Unauthorized("Invalid authorization scheme; expected Bearer")
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise Unauthorized("Token has expired")
    except JWTError:
        raise Unauthorized("Invalid token")
    if payload.get("type") != "access":
        raise Unauthorized("Invalid token type")
    user_id = payload.get("sub")
    user: User | None = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise Unauthorized("User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise Forbidden("Admin access required")
    return user


