from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from domain.schemas import StatsRead
from services.stats import get_user_stats


router = APIRouter(prefix="/stats")


@router.get("", response_model=StatsRead)
def read_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_user_stats(db, user.id)


