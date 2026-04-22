"""
FastAPI endpoint tests for Mergington High School API.
All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest
from fastapi.testclient import TestClient


# ============================================================================
# GET / - Root Redirect Endpoint
# ============================================================================

def test_root_redirects_to_static_index(client):
    """
    Test that GET / redirects to /static/index.html
    
    AAA Pattern:
    - Arrange: TestClient is ready (from fixture)
    - Act: Make GET request to root
    - Assert: Verify 307 redirect status and Location header
    """
    # Arrange
    # (client fixture is already prepared)
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


# ============================================================================
# GET /activities - List All Activities
# ============================================================================

def test_get_activities_returns_all_nine_activities(client):
    """
    Test that GET /activities returns all 9 activities with correct structure.
    
    AAA Pattern:
    - Arrange: TestClient is ready, expect 9 activities
    - Act: Make GET request to /activities
    - Assert: Verify 200 status, 9 activities returned, correct fields present
    """
    # Arrange
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Swimming Club",
        "Art Studio",
        "Drama Club",
        "Debate Team",
        "Science Club"
    ]
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    assert response.status_code == 200
    assert len(data) == 9
    
    # Verify all expected activities are present
    for activity_name in expected_activities:
        assert activity_name in data
    
    # Verify correct fields in each activity
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_get_activities_includes_pre_existing_participants(client):
    """
    Test that GET /activities returns activities with pre-registered participants.
    
    AAA Pattern:
    - Arrange: Know the expected initial participants for each activity
    - Act: Make GET request to /activities
    - Assert: Verify that pre-existing participants are in the response
    """
    # Arrange
    expected_initial_participants = {
        "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
        "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"]
    }
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    for activity_name, expected_participants in expected_initial_participants.items():
        actual_participants = data[activity_name]["participants"]
        assert actual_participants == expected_participants


# ============================================================================
# POST /activities/{activity_name}/signup - Sign Up (Success Case)
# ============================================================================

def test_signup_new_student_to_empty_activity(client):
    """
    Test successful signup of a new student to an activity with no participants.
    
    AAA Pattern:
    - Arrange: Choose an empty activity (Basketball Team) and new email
    - Act: Send POST request to signup endpoint
    - Assert: Verify 200 status, student added to participants list
    """
    # Arrange
    activity_name = "Basketball Team"
    new_email = "alex@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    
    # Verify student was added by fetching activities
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert new_email in participants


def test_signup_new_student_to_activity_with_participants(client):
    """
    Test successful signup of a new student to an activity that already has participants.
    
    AAA Pattern:
    - Arrange: Choose an activity with existing participants (Chess Club) and new email
    - Act: Send POST request to signup endpoint
    - Assert: Verify 200 status, new student added to participants list
    """
    # Arrange
    activity_name = "Chess Club"
    new_email = "james@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")
    
    # Assert
    assert response.status_code == 200
    
    # Verify student was added to the existing participants
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert new_email in participants
    # Also verify existing participants are still there
    assert "michael@mergington.edu" in participants
    assert "daniel@mergington.edu" in participants


# ============================================================================
# POST /activities/{activity_name}/signup - Sign Up (Nonexistent Activity)
# ============================================================================

def test_signup_to_nonexistent_activity_returns_404(client):
    """
    Test that signup to a nonexistent activity returns 404 error.
    
    AAA Pattern:
    - Arrange: Choose a fake activity name and valid email
    - Act: Send POST request to signup endpoint
    - Assert: Verify 404 status and error detail
    """
    # Arrange
    fake_activity = "Fake Club"
    email = "student@mergington.edu"
    
    # Act
    response = client.post(f"/activities/{fake_activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# ============================================================================
# POST /activities/{activity_name}/signup - Sign Up (Duplicate)
# ============================================================================

def test_signup_duplicate_student_returns_400(client):
    """
    Test that signing up an already-registered student returns 400 error.
    
    AAA Pattern:
    - Arrange: Choose an existing participant (michael@mergington.edu is in Chess Club)
    - Act: Try to signup the same student again
    - Assert: Verify 400 status and error detail
    """
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"  # Already in Chess Club
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")
    
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# ============================================================================
# DELETE /activities/{activity_name}/unregister - Unregister (Success Case)
# ============================================================================

def test_unregister_existing_participant_success(client):
    """
    Test successful unregistration of a student from an activity.
    
    AAA Pattern:
    - Arrange: Choose an activity with participants (Chess Club)
    - Act: Send DELETE request to unregister endpoint with existing participant
    - Assert: Verify 200 status, student removed from participants list
    """
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"  # Pre-existing participant
    
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email_to_remove}")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email_to_remove} from {activity_name}"
    
    # Verify student was removed from participants
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email_to_remove not in participants
    # Verify other participants are still there
    assert "daniel@mergington.edu" in participants


# ============================================================================
# DELETE /activities/{activity_name}/unregister - Unregister (Nonexistent Activity)
# ============================================================================

def test_unregister_from_nonexistent_activity_returns_404(client):
    """
    Test that unregistering from a nonexistent activity returns 404 error.
    
    AAA Pattern:
    - Arrange: Choose a fake activity name and valid email
    - Act: Send DELETE request to unregister endpoint
    - Assert: Verify 404 status and error detail
    """
    # Arrange
    fake_activity = "Fake Club"
    email = "student@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{fake_activity}/unregister?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# ============================================================================
# DELETE /activities/{activity_name}/unregister - Unregister (Not a Participant)
# ============================================================================

def test_unregister_non_participant_returns_404(client):
    """
    Test that unregistering a non-participant from an activity returns 404 error.
    
    AAA Pattern:
    - Arrange: Choose an activity and email not in that activity's participants
    - Act: Send DELETE request to unregister endpoint
    - Assert: Verify 404 status and error detail
    """
    # Arrange
    activity_name = "Basketball Team"  # Has no participants initially
    email = "nonexistent@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_unregister_non_participant_from_activity_with_participants_returns_404(client):
    """
    Test that unregistering someone not in an activity (but activity has others) returns 404.
    
    AAA Pattern:
    - Arrange: Choose an activity with participants, use email not in that activity
    - Act: Send DELETE request to unregister endpoint
    - Assert: Verify 404 status and error detail
    """
    # Arrange
    activity_name = "Chess Club"  # Has michael@ and daniel@
    email = "not_in_this_activity@mergington.edu"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


# ============================================================================
# Integration Test: Signup and Unregister Flow
# ============================================================================

def test_signup_then_unregister_flow(client):
    """
    Test a complete flow: signup a student, verify they're added, then unregister.
    
    AAA Pattern:
    - Arrange: Choose an activity and new email
    - Act: 
      1. Signup the student
      2. Get activities to verify signup
      3. Unregister the student
      4. Get activities to verify removal
    - Assert: Verify each step's results
    """
    # Arrange
    activity_name = "Swimming Club"
    email = "swimmer@mergington.edu"
    
    # Act & Assert - Step 1: Signup
    signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert signup_response.status_code == 200
    
    # Act & Assert - Step 2: Verify signup
    activities_after_signup = client.get("/activities").json()
    assert email in activities_after_signup[activity_name]["participants"]
    
    # Act & Assert - Step 3: Unregister
    unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert unregister_response.status_code == 200
    
    # Act & Assert - Step 4: Verify unregister
    activities_after_unregister = client.get("/activities").json()
    assert email not in activities_after_unregister[activity_name]["participants"]
