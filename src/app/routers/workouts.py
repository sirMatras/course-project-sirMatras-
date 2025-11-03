from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user, require_admin
from domain.schemas import WorkoutCreate, WorkoutRead, WorkoutUpdate, PaginatedResponse
from services.workouts import create_workout, get_workout, update_workout, delete_workout
from adapters.sqlalchemy.models import Workout


router = APIRouter(prefix="/workouts")


@router.post("", response_model=WorkoutRead, status_code=HTTP_201_CREATED)
def create(payload: WorkoutCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    w = create_workout(db, user.id, payload)
    return w


@router.get("/{workout_id}", response_model=WorkoutRead)
def read_one(workout_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_workout(db, user.id, workout_id)


@router.get("", response_model=PaginatedResponse)
def list_workouts(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    q = db.query(Workout).filter(Workout.user_id == user.id)
    total = q.count()
    orm_items = q.order_by(Workout.date.desc()).offset(offset).limit(limit).all()
    items = [WorkoutRead.model_validate(i) for i in orm_items]
    return {"items": items, "limit": limit, "offset": offset, "total": total}


@router.get("/admin/all", response_model=PaginatedResponse)
def admin_list_all(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    q = db.query(Workout)
    total = q.count()
    orm_items = q.order_by(Workout.date.desc()).offset(offset).limit(limit).all()
    items = [WorkoutRead.model_validate(i) for i in orm_items]
    return {"items": items, "limit": limit, "offset": offset, "total": total}


@router.patch("/{workout_id}", response_model=WorkoutRead)
def update(workout_id: int, payload: WorkoutUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return update_workout(db, user.id, workout_id, payload)


@router.delete("/{workout_id}", status_code=HTTP_204_NO_CONTENT)
def delete(workout_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    delete_workout(db, user.id, workout_id)
    return None


