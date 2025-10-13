import os
import sys
import pathlib
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.main import app
from app.dependencies.db import Base, get_db
from adapters.sqlalchemy.models import User, Workout, Exercise, Set


@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal()
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(test_db):
    return TestClient(app)


@pytest.fixture(scope="function")
def user1_tokens(client):
    # Register user1
    response = client.post("/auth/register", json={"email": "user1@test.com", "password": "password123"})
    assert response.status_code == 201
    
    # Login user1
    response = client.post("/auth/login", json={"email": "user1@test.com", "password": "password123"})
    assert response.status_code == 200
    return response.json()


@pytest.fixture(scope="function")
def user2_tokens(client):
    # Register user2
    response = client.post("/auth/register", json={"email": "user2@test.com", "password": "password123"})
    assert response.status_code == 201
    
    # Login user2
    response = client.post("/auth/login", json={"email": "user2@test.com", "password": "password123"})
    assert response.status_code == 200
    return response.json()


def auth_headers(access_token: str):
    return {"Authorization": f"Bearer {access_token}"}


