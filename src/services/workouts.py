from sqlalchemy.orm import Session
from typing import List

from adapters.sqlalchemy.models import Workout, Set
from domain.schemas import WorkoutCreate, WorkoutUpdate
from domain.exceptions import NotFound, Forbidden


def ensure_owner(entity_user_id: int, current_user_id: int) -> None:
    if entity_user_id != current_user_id:
        raise Forbidden("You do not have access to this resource")


def create_workout(db: Session, user_id: int, data: WorkoutCreate) -> Workout:
    workout = Workout(user_id=user_id, date=data.date, note=data.note)
    db.add(workout)
    db.flush()
    for s in data.sets:
        db.add(Set(workout_id=workout.id, exercise_id=s.exercise_id, reps=s.reps, weight_kg=s.weight_kg))
    db.flush()
    db.commit()
    db.refresh(workout)
    return workout


def get_workout(db: Session, user_id: int, workout_id: int) -> Workout:
    workout: Workout | None = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == user_id)
        .first()
    )
    if not workout:
        raise NotFound("Workout not found")
    return workout


def update_workout(db: Session, user_id: int, workout_id: int, data: WorkoutUpdate) -> Workout:
    workout = get_workout(db, user_id, workout_id)
    if data.date is not None:
        workout.date = data.date
    if data.note is not None:
        workout.note = data.note
    db.flush()
    db.commit()
    db.refresh(workout)
    return workout


def delete_workout(db: Session, user_id: int, workout_id: int) -> None:
    workout = get_workout(db, user_id, workout_id)
    db.delete(workout)
    db.commit()


