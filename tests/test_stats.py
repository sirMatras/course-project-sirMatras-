import pytest
from tests.conftest import auth_headers


def test_stats_empty_user(client, user1_tokens):
    """Test stats endpoint returns empty data for user with no workouts"""
    headers = auth_headers(user1_tokens["access_token"])
    
    response = client.get("/api/v1/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_workouts"] == 0
    assert data["total_sets"] == 0
    assert data["avg_reps"] is None


def test_stats_with_workouts(client, user1_tokens):
    """Test stats endpoint returns correct data for user with workouts"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create exercise first
    exercise_response = client.post("/api/v1/exercises", 
        json={"name": "Bench Press"}, 
        headers=headers
    )
    exercise_id = exercise_response.json()["id"]
    
    # Create workout with sets
    workout_data = {
        "date": "2024-01-01",
        "note": "Test workout",
        "sets": [
            {"exercise_id": exercise_id, "reps": 10, "weight_kg": 60.0},
            {"exercise_id": exercise_id, "reps": 8, "weight_kg": 70.0},
            {"exercise_id": exercise_id, "reps": 6, "weight_kg": 80.0}
        ]
    }
    client.post("/api/v1/workouts", json=workout_data, headers=headers)
    
    # Create another workout
    workout_data2 = {
        "date": "2024-01-02",
        "note": "Second workout",
        "sets": [
            {"exercise_id": exercise_id, "reps": 12, "weight_kg": 50.0},
            {"exercise_id": exercise_id, "reps": 10, "weight_kg": 60.0}
        ]
    }
    client.post("/api/v1/workouts", json=workout_data2, headers=headers)
    
    # Get stats
    response = client.get("/api/v1/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_workouts"] == 2
    assert data["total_sets"] == 5
    # Average reps: (10 + 8 + 6 + 12 + 10) / 5 = 9.2
    assert data["avg_reps"] == 9.2


def test_stats_user_isolation(client, user1_tokens, user2_tokens):
    """Test that stats are isolated between users"""
    user1_headers = auth_headers(user1_tokens["access_token"])
    user2_headers = auth_headers(user2_tokens["access_token"])
    
    # User1 creates exercise and workout
    exercise_response = client.post("/api/v1/exercises", 
        json={"name": "User1 Exercise"}, 
        headers=user1_headers
    )
    exercise_id = exercise_response.json()["id"]
    
    workout_data = {
        "date": "2024-01-01",
        "sets": [{"exercise_id": exercise_id, "reps": 10, "weight_kg": 60.0}]
    }
    client.post("/api/v1/workouts", json=workout_data, headers=user1_headers)
    
    # User2 creates exercise and workout
    exercise_response2 = client.post("/api/v1/exercises", 
        json={"name": "User2 Exercise"}, 
        headers=user2_headers
    )
    exercise_id2 = exercise_response2.json()["id"]
    
    workout_data2 = {
        "date": "2024-01-01",
        "sets": [
            {"exercise_id": exercise_id2, "reps": 15, "weight_kg": 50.0},
            {"exercise_id": exercise_id2, "reps": 12, "weight_kg": 55.0}
        ]
    }
    client.post("/api/v1/workouts", json=workout_data2, headers=user2_headers)
    
    # Get stats for each user
    user1_stats = client.get("/api/v1/stats", headers=user1_headers)
    user2_stats = client.get("/api/v1/stats", headers=user2_headers)
    
    user1_data = user1_stats.json()
    user2_data = user2_stats.json()
    
    # User1 should only see their own data
    assert user1_data["total_workouts"] == 1
    assert user1_data["total_sets"] == 1
    assert user1_data["avg_reps"] == 10.0
    
    # User2 should only see their own data
    assert user2_data["total_workouts"] == 1
    assert user2_data["total_sets"] == 2
    assert user2_data["avg_reps"] == 13.5  # (15 + 12) / 2


def test_stats_unauthorized_access(client):
    """Test accessing stats without token returns 401"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "UNAUTHORIZED"


def test_stats_with_workouts_no_sets(client, user1_tokens):
    """Test stats with workouts that have no sets"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create workout without sets
    workout_data = {
        "date": "2024-01-01",
        "note": "Empty workout",
        "sets": []
    }
    client.post("/api/v1/workouts", json=workout_data, headers=headers)
    
    # Get stats
    response = client.get("/api/v1/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_workouts"] == 1
    assert data["total_sets"] == 0
    assert data["avg_reps"] is None


def test_stats_multiple_workouts_same_day(client, user1_tokens):
    """Test stats with multiple workouts on the same day"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create exercise
    exercise_response = client.post("/api/v1/exercises", 
        json={"name": "Test Exercise"}, 
        headers=headers
    )
    exercise_id = exercise_response.json()["id"]
    
    # Create multiple workouts on same day
    for i in range(3):
        workout_data = {
            "date": "2024-01-01",
            "note": f"Workout {i+1}",
            "sets": [{"exercise_id": exercise_id, "reps": 5 + i, "weight_kg": 50.0 + i}]
        }
        client.post("/api/v1/workouts", json=workout_data, headers=headers)
    
    # Get stats
    response = client.get("/api/v1/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_workouts"] == 3
    assert data["total_sets"] == 3
    # Average reps: (5 + 6 + 7) / 3 = 6.0
    assert data["avg_reps"] == 6.0


def test_stats_response_format(client, user1_tokens):
    """Test that stats response has correct format"""
    headers = auth_headers(user1_tokens["access_token"])
    
    response = client.get("/api/v1/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields exist
    assert "total_workouts" in data
    assert "total_sets" in data
    assert "avg_reps" in data
    
    # Check field types
    assert isinstance(data["total_workouts"], int)
    assert isinstance(data["total_sets"], int)
    assert data["avg_reps"] is None or isinstance(data["avg_reps"], (int, float))
    
    # Check non-negative values
    assert data["total_workouts"] >= 0
    assert data["total_sets"] >= 0
    if data["avg_reps"] is not None:
        assert data["avg_reps"] >= 0
