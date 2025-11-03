from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, workouts, exercises, stats
from app.utils.errors import add_error_handlers
from app.dependencies.db import init_db
from app.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Workout Log API",
        version="0.1.0",
        docs_url="/docs",
        description=(
            "Secure workout logging API with JWT auth, user-scoped CRUD, and stats.\n\n"
            "Authorization: First POST to /auth/login with email/password to obtain tokens.\n"
            "Then click 'Authorize' and paste: Bearer <your_access_token>."
        ),
        contact={
            "name": "Workout Log API",
            "url": "https://example.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_tags=[
            {"name": "auth", "description": "User registration, login, logout, and token refresh"},
            {"name": "workouts", "description": "Manage workouts and their sets (user-scoped)"},
            {"name": "exercises", "description": "Manage personal exercises (user-scoped)"},
            {"name": "stats", "description": "Aggregated statistics for the current user"},
        ],
        servers=[
            {"url": "/", "description": "Current environment"},
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_error_handlers(app)

    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(workouts.router, prefix="/api/v1", tags=["workouts"])
    app.include_router(exercises.router, prefix="/api/v1", tags=["exercises"])
    app.include_router(stats.router, prefix="/api/v1", tags=["stats"])

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    @app.on_event("startup")
    async def on_startup() -> None:
        init_db()
        try:
            print(f"✅ JWT: {settings.jwt_algorithm}, secret len={len(settings.jwt_secret)}")
        except Exception:
            pass

    return app


app = create_app()


