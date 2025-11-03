from sqlalchemy import func
from sqlalchemy.orm import Session

from adapters.sqlalchemy.models import Workout, Set


def get_user_stats(db: Session, user_id: int) -> dict:
    total_workouts = db.query(func.count(Workout.id)).filter(Workout.user_id == user_id).scalar() or 0
    total_sets = db.query(func.count(Set.id)).join(Workout, Workout.id == Set.workout_id).filter(Workout.user_id == user_id).scalar() or 0
    avg_reps = (
        db.query(func.avg(Set.reps)).join(Workout, Workout.id == Set.workout_id).filter(Workout.user_id == user_id).scalar()
    )
    return {
        "total_workouts": int(total_workouts),
        "avg_reps": float(avg_reps) if avg_reps is not None else None,
        "total_sets": int(total_sets),
    }


