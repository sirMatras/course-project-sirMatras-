from sqlalchemy.orm import Session

from adapters.sqlalchemy.models import Exercise
from domain.schemas import ExerciseCreate
from domain.exceptions import NotFound, Forbidden, BadRequest


def ensure_owner(entity_user_id: int, current_user_id: int) -> None:
    if entity_user_id != current_user_id:
        raise Forbidden("You do not have access to this resource")


def create_exercise(db: Session, user_id: int, data: ExerciseCreate) -> Exercise:
    exists = db.query(Exercise).filter(Exercise.user_id == user_id, Exercise.name == data.name).first()
    if exists:
        raise BadRequest("Exercise with this name already exists")
    ex = Exercise(user_id=user_id, name=data.name)
    db.add(ex)
    db.flush()
    db.commit()
    db.refresh(ex)
    return ex


def get_exercise(db: Session, user_id: int, exercise_id: int) -> Exercise:
    ex: Exercise | None = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not ex:
        raise NotFound("Exercise not found")
    ensure_owner(ex.user_id, user_id)
    return ex


def update_exercise(db: Session, user_id: int, exercise_id: int, data: ExerciseCreate) -> Exercise:
    ex = get_exercise(db, user_id, exercise_id)
    ex.name = data.name
    db.flush()
    db.commit()
    db.refresh(ex)
    return ex


def delete_exercise(db: Session, user_id: int, exercise_id: int) -> None:
    ex = get_exercise(db, user_id, exercise_id)
    db.delete(ex)
    db.commit()


