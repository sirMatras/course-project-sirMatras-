import pytest
from tests.conftest import auth_headers


def test_create_exercise_success(client, user1_tokens):
    """Test successful exercise creation"""
    headers = auth_headers(user1_tokens["access_token"])
    
    response = client.post("/api/v1/exercises", 
        json={"name": "Bench Press"}, 
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Bench Press"
    assert "id" in data
    assert "user_id" in data


def test_create_duplicate_exercise(client, user1_tokens):
    """Test creating duplicate exercise returns 400"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create first exercise
    client.post("/api/v1/exercises", 
        json={"name": "Squat"}, 
        headers=headers
    )
    
    # Try to create duplicate
    response = client.post("/api/v1/exercises", 
        json={"name": "Squat"}, 
        headers=headers
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "BAD_REQUEST"
    assert "already exists" in data["detail"]["message"]


def test_get_own_exercise(client, user1_tokens):
    """Test getting own exercise returns 200"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create exercise
    create_response = client.post("/api/v1/exercises", 
        json={"name": "Deadlift"}, 
        headers=headers
    )
    exercise_id = create_response.json()["id"]
    
    # Get exercise
    response = client.get(f"/api/v1/exercises/{exercise_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == exercise_id
    assert data["name"] == "Deadlift"


def test_get_nonexistent_exercise(client, user1_tokens):
    """Test getting non-existent exercise returns 404"""
    headers = auth_headers(user1_tokens["access_token"])
    
    response = client.get("/api/v1/exercises/99999", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "NOT_FOUND"


def test_get_another_user_exercise(client, user1_tokens, user2_tokens):
    """Test getting another user's exercise returns 404"""
    user1_headers = auth_headers(user1_tokens["access_token"])
    user2_headers = auth_headers(user2_tokens["access_token"])
    
    # User1 creates exercise
    create_response = client.post("/api/v1/exercises", 
        json={"name": "User1 Exercise"}, 
        headers=user1_headers
    )
    exercise_id = create_response.json()["id"]
    
    # User2 tries to get User1's exercise
    response = client.get(f"/api/v1/exercises/{exercise_id}", headers=user2_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "NOT_FOUND"


def test_list_own_exercises(client, user1_tokens):
    """Test listing own exercises"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create multiple exercises
    exercises = ["Push-ups", "Pull-ups", "Squats"]
    for exercise_name in exercises:
        client.post("/api/v1/exercises", 
            json={"name": exercise_name}, 
            headers=headers
        )
    
    # List exercises
    response = client.get("/api/v1/exercises?limit=10&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3
    
    # Check that exercises are sorted by name
    exercise_names = [item["name"] for item in data["items"]]
    assert exercise_names == sorted(exercise_names)


def test_update_own_exercise(client, user1_tokens):
    """Test updating own exercise"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create exercise
    create_response = client.post("/api/v1/exercises", 
        json={"name": "Original Name"}, 
        headers=headers
    )
    exercise_id = create_response.json()["id"]
    
    # Update exercise
    update_data = {"name": "Updated Name"}
    response = client.patch(f"/api/v1/exercises/{exercise_id}", 
        json=update_data, 
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


def test_update_another_user_exercise(client, user1_tokens, user2_tokens):
    """Test updating another user's exercise returns 404"""
    user1_headers = auth_headers(user1_tokens["access_token"])
    user2_headers = auth_headers(user2_tokens["access_token"])
    
    # User1 creates exercise
    create_response = client.post("/api/v1/exercises", 
        json={"name": "User1 Exercise"}, 
        headers=user1_headers
    )
    exercise_id = create_response.json()["id"]
    
    # User2 tries to update User1's exercise
    response = client.patch(f"/api/v1/exercises/{exercise_id}", 
        json={"name": "Hacked!"}, 
        headers=user2_headers
    )
    assert response.status_code == 404


def test_delete_own_exercise(client, user1_tokens):
    """Test deleting own exercise"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create exercise
    create_response = client.post("/api/v1/exercises", 
        json={"name": "To be deleted"}, 
        headers=headers
    )
    exercise_id = create_response.json()["id"]
    
    # Delete exercise
    response = client.delete(f"/api/v1/exercises/{exercise_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify exercise is deleted
    get_response = client.get(f"/api/v1/exercises/{exercise_id}", headers=headers)
    assert get_response.status_code == 404


def test_delete_another_user_exercise(client, user1_tokens, user2_tokens):
    """Test deleting another user's exercise returns 404"""
    user1_headers = auth_headers(user1_tokens["access_token"])
    user2_headers = auth_headers(user2_tokens["access_token"])
    
    # User1 creates exercise
    create_response = client.post("/api/v1/exercises", 
        json={"name": "User1 Exercise"}, 
        headers=user1_headers
    )
    exercise_id = create_response.json()["id"]
    
    # User2 tries to delete User1's exercise
    response = client.delete(f"/api/v1/exercises/{exercise_id}", headers=user2_headers)
    assert response.status_code == 404


def test_exercise_validation_empty_name(client, user1_tokens):
    """Test exercise validation rejects empty name"""
    headers = auth_headers(user1_tokens["access_token"])
    
    response = client.post("/api/v1/exercises", 
        json={"name": ""}, 
        headers=headers
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_exercise_validation_long_name(client, user1_tokens):
    """Test exercise validation rejects too long name"""
    headers = auth_headers(user1_tokens["access_token"])
    
    long_name = "x" * 101  # Exceeds max_length=100
    
    response = client.post("/api/v1/exercises", 
        json={"name": long_name}, 
        headers=headers
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_unauthorized_access(client):
    """Test accessing protected endpoints without token returns 401"""
    response = client.post("/api/v1/exercises", json={"name": "Test"})
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["code"] == "UNAUTHORIZED"


def test_pagination(client, user1_tokens):
    """Test exercise list pagination"""
    headers = auth_headers(user1_tokens["access_token"])
    
    # Create 5 exercises
    for i in range(5):
        client.post("/api/v1/exercises", 
            json={"name": f"Exercise {i+1}"}, 
            headers=headers
        )
    
    # Test pagination
    response = client.get("/api/v1/exercises?limit=2&offset=0", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert data["total"] >= 5
    assert len(data["items"]) == 2


def test_exercises_are_user_scoped(client, user1_tokens, user2_tokens):
    """Test that exercises are properly scoped to users"""
    user1_headers = auth_headers(user1_tokens["access_token"])
    user2_headers = auth_headers(user2_tokens["access_token"])
    
    # User1 creates exercise
    client.post("/api/v1/exercises", 
        json={"name": "User1 Exercise"}, 
        headers=user1_headers
    )
    
    # User2 creates exercise with same name (should work)
    response = client.post("/api/v1/exercises", 
        json={"name": "User1 Exercise"}, 
        headers=user2_headers
    )
    assert response.status_code == 201
    
    # Each user should only see their own exercises
    user1_list = client.get("/api/v1/exercises", headers=user1_headers)
    user2_list = client.get("/api/v1/exercises", headers=user2_headers)
    
    assert user1_list.json()["total"] == 1
    assert user2_list.json()["total"] == 1
    assert user1_list.json()["items"][0]["name"] == "User1 Exercise"
    assert user2_list.json()["items"][0]["name"] == "User1 Exercise"
