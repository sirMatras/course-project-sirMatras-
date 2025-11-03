import pytest
from tests.conftest import auth_headers


def test_create_workout_success(client, user1_tokens):
    """Test successful workout creation"""
    headers = auth_headers(user1_tokens["access_token"])
    
    workout_data = {
        "date": "2024-01-01",
        "note": "Test workout",
        "sets": []
    }
    
    response = client.post("/api/v1/workouts", json=workout_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["date"] == "2024-01-01"
    assert data["note"] == "Test workout"
    assert "id" in data
    assert "user_id" in data


def test_create_workout_with_sets(client, user1_tokens):
    """Test workout creation with sets"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # First create an exercise
    exercise_response = client.post("/api/v1/exercises", 
        json={"name": "Bench Press"}, 
        headers=headers
    )
    exercise_id = exercise_response.json()["id"]
    
    workout_data = {
        "date": "2024-01-01",
        "note": "Chest day",
        "sets": [
            {"exercise_id": exercise_id, "reps": 10, "weight_kg": 60.0},
            {"exercise_id": exercise_id, "reps": 8, "weight_kg": 70.0}
        ]
    }
    
    response = client.post("/api/v1/workouts", json=workout_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert len(data["sets"]) == 2
    assert data["sets"][0]["reps"] == 10
    assert data["sets"][0]["weight_kg"] == 60.0


def test_get_own_workout(client, user1_tokens):
    """Test getting own workout returns 200"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create workout
    create_response = client.post("/api/v1/workouts", 
        json={"date": "2024-01-01", "note": "Test"}, 
        headers=headers
    )
    workout_id = create_response.json()["id"]
    
    # Get workout
    response = client.get(f"/api/v1/workouts/{workout_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workout_id
    assert data["note"] == "Test"


def test_get_nonexistent_workout(client, user1_tokens):
    """Test getting non-existent workout returns 404"""
    headers = auth_headers(user1_tokens["access_token"])
    
    response = client.get("/api/v1/workouts/99999", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "NOT_FOUND"


def test_get_another_user_workout(client, user1_tokens, user2_tokens):
    """Test getting another user's workout returns 404 (not 200)"""
    user1_headers = auth_headers(user1_tokens["access_token"])
    user2_headers = auth_headers(user2_tokens["access_token"])
    
    # User1 creates workout
    create_response = client.post("/api/v1/workouts", 
        json={"date": "2024-01-01", "note": "User1 workout"}, 
        headers=user1_headers
    )
    workout_id = create_response.json()["id"]
    
    # User2 tries to get User1's workout
    response = client.get(f"/api/v1/workouts/{workout_id}", headers=user2_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "NOT_FOUND"


def test_list_own_workouts(client, user1_tokens):
    """Test listing own workouts"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create multiple workouts
    for i in range(3):
        client.post("/api/v1/workouts", 
            json={"date": f"2024-01-0{i+1}", "note": f"Workout {i+1}"}, 
            headers=headers
        )
    
    # List workouts
    response = client.get("/api/v1/workouts?limit=10&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


def test_update_own_workout(client, user1_tokens):
    """Test updating own workout"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create workout
    create_response = client.post("/api/v1/workouts", 
        json={"date": "2024-01-01", "note": "Original note"}, 
        headers=headers
    )
    workout_id = create_response.json()["id"]
    
    # Update workout
    update_data = {"note": "Updated note"}
    response = client.patch(f"/api/v1/workouts/{workout_id}", 
        json=update_data, 
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["note"] == "Updated note"


def test_update_another_user_workout(client, user1_tokens, user2_tokens):
    """Test updating another user's workout returns 404"""
    user1_headers = auth_headers(user1_tokens["access_token"])
    user2_headers = auth_headers(user2_tokens["access_token"])
    
    # User1 creates workout
    create_response = client.post("/api/v1/workouts", 
        json={"date": "2024-01-01", "note": "User1 workout"}, 
        headers=user1_headers
    )
    workout_id = create_response.json()["id"]
    
    # User2 tries to update User1's workout
    response = client.patch(f"/api/v1/workouts/{workout_id}", 
        json={"note": "Hacked!"}, 
        headers=user2_headers
    )
    assert response.status_code == 404


def test_delete_own_workout(client, user1_tokens):
    """Test deleting own workout"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create workout
    create_response = client.post("/api/v1/workouts", 
        json={"date": "2024-01-01", "note": "To be deleted"}, 
        headers=headers
    )
    workout_id = create_response.json()["id"]
    
    # Delete workout
    response = client.delete(f"/api/v1/workouts/{workout_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify workout is deleted
    get_response = client.get(f"/api/v1/workouts/{workout_id}", headers=headers)
    assert get_response.status_code == 404


def test_delete_another_user_workout(client, user1_tokens, user2_tokens):
    """Test deleting another user's workout returns 404"""
    user1_headers = auth_headers(user1_tokens["access_token"])
    user2_headers = auth_headers(user2_tokens["access_token"])
    
    # User1 creates workout
    create_response = client.post("/api/v1/workouts", 
        json={"date": "2024-01-01", "note": "User1 workout"}, 
        headers=user1_headers
    )
    workout_id = create_response.json()["id"]
    
    # User2 tries to delete User1's workout
    response = client.delete(f"/api/v1/workouts/{workout_id}", headers=user2_headers)
    assert response.status_code == 404


def test_workout_validation_future_date(client, user1_tokens):
    """Test workout validation rejects future dates"""
    headers = auth_headers(user1_tokens["access_token"])
    
    from datetime import date, timedelta
    future_date = (date.today() + timedelta(days=1)).isoformat()
    
    workout_data = {
        "date": future_date,
        "note": "Future workout"
    }
    
    response = client.post("/api/v1/workouts", json=workout_data, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_set_validation_negative_values(client, user1_tokens):
    """Test set validation rejects negative reps/weight"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create exercise first
    exercise_response = client.post("/api/v1/exercises", 
        json={"name": "Test Exercise"}, 
        headers=headers
    )
    exercise_id = exercise_response.json()["id"]
    
    # Try to create workout with negative reps
    workout_data = {
        "date": "2024-01-01",
        "sets": [{"exercise_id": exercise_id, "reps": -5, "weight_kg": 50.0}]
    }
    
    response = client.post("/api/v1/workouts", json=workout_data, headers=headers)
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_unauthorized_access(client):
    """Test accessing protected endpoints without token returns 401"""
    response = client.post("/api/v1/workouts", json={"date": "2024-01-01"})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "UNAUTHORIZED"


def test_pagination(client, user1_tokens):
    """Test workout list pagination"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create 5 workouts
    for i in range(5):
        client.post("/api/v1/workouts", 
            json={"date": f"2024-01-0{i+1}", "note": f"Workout {i+1}"}, 
            headers=headers
        )
    
    # Test pagination
    response = client.get("/api/v1/workouts?limit=2&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert data["total"] >= 5
    assert len(data["items"]) == 2
