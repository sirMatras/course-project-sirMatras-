from datetime import date
from typing import Literal, Optional, List
from pydantic import BaseModel, EmailStr, Field
from pydantic import field_validator
from pydantic.config import ConfigDict


Role = Literal["user", "admin"]


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: Role

    model_config = ConfigDict(from_attributes=True)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class ExerciseRead(BaseModel):
    id: int
    name: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class SetCreate(BaseModel):
    exercise_id: int
    reps: int = Field(ge=0)
    weight_kg: float = Field(ge=0)


class SetRead(BaseModel):
    id: int
    workout_id: int
    exercise_id: int
    reps: int
    weight_kg: float

    model_config = ConfigDict(from_attributes=True)


class WorkoutCreate(BaseModel):
    date: date
    note: str | None = Field(default=None, max_length=500)
    sets: List[SetCreate] = Field(default_factory=list)

    @field_validator("date")
    @classmethod
    def validate_date_not_future(cls, v: date):
        if v > date.today():
            raise ValueError("date must be today or earlier")
        return v


class WorkoutUpdate(BaseModel):
    date: Optional[date] = None
    note: Optional[str] = Field(default=None, max_length=500)

    @field_validator("date")
    @classmethod
    def validate_date_not_future(cls, v: Optional[date]):
        if v and v > date.today():
            raise ValueError("date must be today or earlier")
        return v


class WorkoutRead(BaseModel):
    id: int
    user_id: int
    date: date
    note: str | None
    sets: List[SetRead] = []

    model_config = ConfigDict(from_attributes=True)


class PaginatedResponse(BaseModel):
    items: list
    limit: int
    offset: int
    total: int


class StatsRead(BaseModel):
    total_workouts: int
    avg_reps: float | None
    total_sets: int


