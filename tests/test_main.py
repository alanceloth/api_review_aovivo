"""Integration tests for FastAPI endpoints."""
from __future__ import annotations

from datetime import datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.models import Task


@pytest.mark.integration
class TestRootEndpoint:
    """Test the root endpoint."""

    def test_read_root(self, client: TestClient):
        """Test GET / returns welcome message."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Bem-vindo à Task Management API"}


@pytest.mark.integration
class TestCreateTask:
    """Test POST /tasks/ endpoint."""

    def test_create_task_success(self, client: TestClient, sample_task_data: dict):
        """Test creating a task with valid data."""
        response = client.post("/tasks/", json=sample_task_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data

    def test_create_task_minimal(self, client: TestClient):
        """Test creating a task with only required fields."""
        task_data = {"title": "Minimal Task"}
        response = client.post("/tasks/", json=task_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None
        assert data["completed"] is False

    def test_create_task_title_too_short(self, client: TestClient):
        """Test creating task with title shorter than 3 characters."""
        task_data = {"title": "AB"}
        response = client.post("/tasks/", json=task_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_title_too_long(self, client: TestClient):
        """Test creating task with title longer than 100 characters."""
        task_data = {"title": "A" * 101}
        response = client.post("/tasks/", json=task_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_description_too_long(self, client: TestClient):
        """Test creating task with description longer than 500 characters."""
        task_data = {
            "title": "Test Task",
            "description": "B" * 501
        }
        response = client.post("/tasks/", json=task_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_missing_title(self, client: TestClient):
        """Test creating task without title."""
        task_data = {"description": "No title"}
        response = client.post("/tasks/", json=task_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_task_with_special_characters(self, client: TestClient):
        """Test creating task with special characters in title."""
        task_data = {
            "title": "Task #1: Review @mentions & tags!",
            "description": "Special chars: $%^&*()"
        }
        response = client.post("/tasks/", json=task_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == task_data["title"]

    def test_create_task_unicode_characters(self, client: TestClient):
        """Test creating task with Unicode characters."""
        task_data = {
            "title": "Tarefa em português: café",
            "description": "Emojis: 🎉 🚀 ✨"
        }
        response = client.post("/tasks/", json=task_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == task_data["title"]

    def test_create_multiple_tasks(self, client: TestClient):
        """Test creating multiple tasks."""
        tasks = [
            {"title": "Task 1", "description": "First task"},
            {"title": "Task 2", "description": "Second task"},
            {"title": "Task 3", "description": "Third task"},
        ]
        
        ids = []
        for task_data in tasks:
            response = client.post("/tasks/", json=task_data)
            assert response.status_code == status.HTTP_201_CREATED
            ids.append(response.json()["id"])
        
        # All IDs should be unique
        assert len(ids) == len(set(ids))


@pytest.mark.integration
class TestListTasks:
    """Test GET /tasks/ endpoint."""

    def test_list_tasks_empty(self, client: TestClient):
        """Test listing tasks when database is empty."""
        response = client.get("/tasks/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_tasks_with_data(self, client: TestClient):
        """Test listing tasks with existing data."""
        # Create tasks
        for i in range(3):
            client.post("/tasks/", json={"title": f"Task {i+1}"})
        
        response = client.get("/tasks/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_list_tasks_pagination_skip(self, client: TestClient):
        """Test pagination with skip parameter."""
        # Create 5 tasks
        for i in range(5):
            client.post("/tasks/", json={"title": f"Task {i+1}"})
        
        response = client.get("/tasks/?skip=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3  # Should return 3 tasks (skipped first 2)

    def test_list_tasks_pagination_limit(self, client: TestClient):
        """Test pagination with limit parameter."""
        # Create 10 tasks
        for i in range(10):
            client.post("/tasks/", json={"title": f"Task {i+1}"})
        
        response = client.get("/tasks/?limit=5")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 5

    def test_list_tasks_pagination_skip_and_limit(self, client: TestClient):
        """Test pagination with both skip and limit."""
        # Create 10 tasks
        for i in range(10):
            client.post("/tasks/", json={"title": f"Task {i+1}"})
        
        response = client.get("/tasks/?skip=3&limit=4")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 4

    def test_list_tasks_filter_completed_true(self, client: TestClient):
        """Test filtering tasks by completed=true."""
        # Create completed and incomplete tasks
        client.post("/tasks/", json={"title": "Incomplete Task 1"})
        response = client.post("/tasks/", json={"title": "To Complete"})
        task_id = response.json()["id"]
        client.put(f"/tasks/{task_id}", json={"completed": True})
        
        response = client.get("/tasks/?completed=true")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["completed"] is True

    def test_list_tasks_filter_completed_false(self, client: TestClient):
        """Test filtering tasks by completed=false."""
        # Create completed and incomplete tasks
        client.post("/tasks/", json={"title": "Incomplete Task"})
        response = client.post("/tasks/", json={"title": "Complete Task"})
        task_id = response.json()["id"]
        client.put(f"/tasks/{task_id}", json={"completed": True})
        
        response = client.get("/tasks/?completed=false")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["completed"] is False

    def test_list_tasks_no_filter(self, client: TestClient):
        """Test listing all tasks without filter."""
        # Create completed and incomplete tasks
        client.post("/tasks/", json={"title": "Incomplete Task"})
        response = client.post("/tasks/", json={"title": "Complete Task"})
        task_id = response.json()["id"]
        client.put(f"/tasks/{task_id}", json={"completed": True})
        
        response = client.get("/tasks/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2

    def test_list_tasks_invalid_skip(self, client: TestClient):
        """Test invalid skip parameter."""
        response = client.get("/tasks/?skip=-1")
        
        # FastAPI might accept it or reject it depending on validation
        # Just verify we get a response
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_list_tasks_invalid_limit(self, client: TestClient):
        """Test invalid limit parameter."""
        response = client.get("/tasks/?limit=-1")
        
        # FastAPI might accept it or reject it
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


@pytest.mark.integration
class TestGetTask:
    """Test GET /tasks/{task_id} endpoint."""

    def test_get_task_success(self, client: TestClient, sample_task_data: dict):
        """Test retrieving an existing task."""
        # Create a task
        create_response = client.post("/tasks/", json=sample_task_data)
        task_id = create_response.json()["id"]
        
        # Retrieve the task
        response = client.get(f"/tasks/{task_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]

    def test_get_task_not_found(self, client: TestClient):
        """Test retrieving a non-existent task."""
        response = client.get("/tasks/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Task não encontrada" in response.json()["detail"]

    def test_get_task_invalid_id(self, client: TestClient):
        """Test retrieving task with invalid ID format."""
        response = client.get("/tasks/invalid")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_task_zero_id(self, client: TestClient):
        """Test retrieving task with ID 0."""
        response = client.get("/tasks/0")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_task_negative_id(self, client: TestClient):
        """Test retrieving task with negative ID."""
        response = client.get("/tasks/-1")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
class TestUpdateTask:
    """Test PUT /tasks/{task_id} endpoint."""

    def test_update_task_all_fields(self, client: TestClient):
        """Test updating all fields of a task."""
        # Create a task
        create_response = client.post("/tasks/", json={
            "title": "Original Title",
            "description": "Original description"
        })
        task_id = create_response.json()["id"]
        
        # Update the task
        update_data = {
            "title": "Updated Title",
            "description": "Updated description",
            "completed": True
        }
        response = client.put(f"/tasks/{task_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description"
        assert data["completed"] is True

    def test_update_task_only_title(self, client: TestClient):
        """Test updating only the title."""
        # Create a task
        create_response = client.post("/tasks/", json={
            "title": "Original",
            "description": "Keep this"
        })
        task_id = create_response.json()["id"]
        
        # Update only title
        response = client.put(f"/tasks/{task_id}", json={"title": "New Title"})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "Keep this"  # Should remain unchanged
        assert data["completed"] is False

    def test_update_task_only_description(self, client: TestClient):
        """Test updating only the description."""
        # Create a task
        create_response = client.post("/tasks/", json={"title": "Keep Title"})
        task_id = create_response.json()["id"]
        
        # Update only description
        response = client.put(f"/tasks/{task_id}", json={
            "description": "New description"
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Keep Title"
        assert data["description"] == "New description"

    def test_update_task_only_completed(self, client: TestClient):
        """Test updating only the completed status."""
        # Create a task
        create_response = client.post("/tasks/", json={"title": "Task"})
        task_id = create_response.json()["id"]
        
        # Mark as completed
        response = client.put(f"/tasks/{task_id}", json={"completed": True})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] is True

    def test_update_task_toggle_completed(self, client: TestClient):
        """Test toggling completed status back and forth."""
        # Create a task
        create_response = client.post("/tasks/", json={"title": "Toggle Task"})
        task_id = create_response.json()["id"]
        
        # Mark as completed
        response = client.put(f"/tasks/{task_id}", json={"completed": True})
        assert response.json()["completed"] is True
        
        # Mark as incomplete
        response = client.put(f"/tasks/{task_id}", json={"completed": False})
        assert response.json()["completed"] is False

    def test_update_task_not_found(self, client: TestClient):
        """Test updating a non-existent task."""
        response = client.put("/tasks/99999", json={"title": "New Title"})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Task não encontrada" in response.json()["detail"]

    def test_update_task_empty_payload(self, client: TestClient):
        """Test updating with empty payload (all fields optional)."""
        # Create a task
        create_response = client.post("/tasks/", json={
            "title": "Original",
            "description": "Original desc"
        })
        task_id = create_response.json()["id"]
        original_data = create_response.json()
        
        # Update with empty payload
        response = client.put(f"/tasks/{task_id}", json={})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Nothing should change
        assert data["title"] == original_data["title"]
        assert data["description"] == original_data["description"]

    def test_update_task_invalid_title_length(self, client: TestClient):
        """Test updating with invalid title length."""
        # Create a task
        create_response = client.post("/tasks/", json={"title": "Original"})
        task_id = create_response.json()["id"]
        
        # Try to update with short title
        response = client.put(f"/tasks/{task_id}", json={"title": "AB"})
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_task_clear_description(self, client: TestClient):
        """Test clearing the description by setting it to None."""
        # Create a task with description
        create_response = client.post("/tasks/", json={
            "title": "Task",
            "description": "Original description"
        })
        task_id = create_response.json()["id"]
        
        # Clear description
        response = client.put(f"/tasks/{task_id}", json={"description": None})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["description"] is None


@pytest.mark.integration
class TestDeleteTask:
    """Test DELETE /tasks/{task_id} endpoint."""

    def test_delete_task_success(self, client: TestClient):
        """Test successfully deleting a task."""
        # Create a task
        create_response = client.post("/tasks/", json={"title": "To Delete"})
        task_id = create_response.json()["id"]
        
        # Delete the task
        response = client.delete(f"/tasks/{task_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.text == ""
        
        # Verify task is deleted
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_task_not_found(self, client: TestClient):
        """Test deleting a non-existent task."""
        response = client.delete("/tasks/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Task não encontrada" in response.json()["detail"]

    def test_delete_task_invalid_id(self, client: TestClient):
        """Test deleting with invalid ID format."""
        response = client.delete("/tasks/invalid")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_task_multiple_times(self, client: TestClient):
        """Test that deleting the same task twice fails."""
        # Create a task
        create_response = client.post("/tasks/", json={"title": "Delete Once"})
        task_id = create_response.json()["id"]
        
        # First delete should succeed
        response1 = client.delete(f"/tasks/{task_id}")
        assert response1.status_code == status.HTTP_204_NO_CONTENT
        
        # Second delete should fail
        response2 = client.delete(f"/tasks/{task_id}")
        assert response2.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_all_tasks(self, client: TestClient):
        """Test deleting multiple tasks."""
        # Create multiple tasks
        task_ids = []
        for i in range(3):
            response = client.post("/tasks/", json={"title": f"Task {i+1}"})
            task_ids.append(response.json()["id"])
        
        # Delete all tasks
        for task_id in task_ids:
            response = client.delete(f"/tasks/{task_id}")
            assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify all are deleted
        list_response = client.get("/tasks/")
        assert len(list_response.json()) == 0


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete workflows and edge cases."""

    def test_complete_task_lifecycle(self, client: TestClient):
        """Test creating, reading, updating, and deleting a task."""
        # Create
        create_response = client.post("/tasks/", json={
            "title": "Lifecycle Task",
            "description": "Testing full lifecycle"
        })
        assert create_response.status_code == status.HTTP_201_CREATED
        task_id = create_response.json()["id"]
        
        # Read
        read_response = client.get(f"/tasks/{task_id}")
        assert read_response.status_code == status.HTTP_200_OK
        assert read_response.json()["title"] == "Lifecycle Task"
        
        # Update
        update_response = client.put(f"/tasks/{task_id}", json={
            "title": "Updated Lifecycle Task",
            "completed": True
        })
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["completed"] is True
        
        # Delete
        delete_response = client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deleted
        final_response = client.get(f"/tasks/{task_id}")
        assert final_response.status_code == status.HTTP_404_NOT_FOUND

    def test_concurrent_task_operations(self, client: TestClient):
        """Test multiple operations in sequence."""
        # Create multiple tasks
        tasks = []
        for i in range(5):
            response = client.post("/tasks/", json={"title": f"Concurrent Task {i+1}"})
            tasks.append(response.json())
        
        # Update some tasks
        for i in [0, 2, 4]:
            client.put(f"/tasks/{tasks[i]['id']}", json={"completed": True})
        
        # List completed tasks
        completed_response = client.get("/tasks/?completed=true")
        assert len(completed_response.json()) == 3
        
        # List incomplete tasks
        incomplete_response = client.get("/tasks/?completed=false")
        assert len(incomplete_response.json()) == 2
        
        # Delete some tasks
        for i in [1, 3]:
            client.delete(f"/tasks/{tasks[i]['id']}")
        
        # Verify final count
        all_tasks = client.get("/tasks/")
        assert len(all_tasks.json()) == 3

    def test_boundary_values(self, client: TestClient):
        """Test boundary values for all fields."""
        # Minimum valid title (3 chars)
        response = client.post("/tasks/", json={"title": "ABC"})
        assert response.status_code == status.HTTP_201_CREATED
        
        # Maximum valid title (100 chars)
        response = client.post("/tasks/", json={"title": "A" * 100})
        assert response.status_code == status.HTTP_201_CREATED
        
        # Maximum valid description (500 chars)
        response = client.post("/tasks/", json={
            "title": "Test",
            "description": "B" * 500
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_api_documentation_accessible(self, client: TestClient):
        """Test that API documentation endpoints are accessible."""
        # OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        assert "openapi" in response.json()
        
        # Swagger UI (might redirect)
        response = client.get("/docs", follow_redirects=False)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_307_TEMPORARY_REDIRECT]