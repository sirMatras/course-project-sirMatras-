from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user, require_admin
from domain.schemas import ExerciseCreate, ExerciseRead, PaginatedResponse
from services.exercises import create_exercise, get_exercise, update_exercise, delete_exercise
from adapters.sqlalchemy.models import Exercise


router = APIRouter(prefix="/exercises")


@router.post("", response_model=ExerciseRead, status_code=HTTP_201_CREATED)
def create(payload: ExerciseCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return create_exercise(db, user.id, payload)


@router.get("/{exercise_id}", response_model=ExerciseRead)
def read_one(exercise_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_exercise(db, user.id, exercise_id)


@router.get("", response_model=PaginatedResponse)
def list_exercises(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Exercise).filter(Exercise.user_id == user.id)
    total = q.count()
    orm_items = q.order_by(Exercise.name.asc()).offset(offset).limit(limit).all()
    items = [ExerciseRead.model_validate(i) for i in orm_items]
    return {"items": items, "limit": limit, "offset": offset, "total": total}


@router.patch("/{exercise_id}", response_model=ExerciseRead)
def update(exercise_id: int, payload: ExerciseCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return update_exercise(db, user.id, exercise_id, payload)


@router.delete("/{exercise_id}", status_code=HTTP_204_NO_CONTENT)
def delete(exercise_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    delete_exercise(db, user.id, exercise_id)
    return None


@router.get("/admin/all", response_model=PaginatedResponse)
def admin_list_all(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    q = db.query(Exercise)
    total = q.count()
    orm_items = q.order_by(Exercise.id.desc()).offset(offset).limit(limit).all()
    items = [ExerciseRead.model_validate(i) for i in orm_items]
    return {"items": items, "limit": limit, "offset": offset, "total": total}


