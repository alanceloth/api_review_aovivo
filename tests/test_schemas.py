"""Unit tests for Pydantic schemas."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas import TaskCreate, TaskResponse, TaskUpdate


@pytest.mark.unit
class TestTaskCreateSchema:
    """Test the TaskCreate Pydantic schema."""

    def test_task_create_valid_data(self):
        """Test creating TaskCreate with valid data."""
        data = {"title": "Test Task", "description": "Test description"}
        task = TaskCreate(**data)

        assert task.title == "Test Task"
        assert task.description == "Test description"

    def test_task_create_minimal_data(self):
        """Test creating TaskCreate with only required fields."""
        data = {"title": "Minimal"}
        task = TaskCreate(**data)

        assert task.title == "Minimal"
        assert task.description is None

    def test_task_create_title_min_length(self):
        """Test that title must be at least 3 characters."""
        data = {"title": "AB"}  # Too short
        
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(err) for err in errors)

    def test_task_create_title_exactly_min_length(self):
        """Test title with exactly minimum length."""
        data = {"title": "ABC"}  # Exactly 3 chars
        task = TaskCreate(**data)
        
        assert task.title == "ABC"

    def test_task_create_title_max_length(self):
        """Test that title cannot exceed 100 characters."""
        data = {"title": "A" * 101}  # Too long
        
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("at most 100 characters" in str(err) for err in errors)

    def test_task_create_title_exactly_max_length(self):
        """Test title with exactly maximum length."""
        data = {"title": "A" * 100}  # Exactly 100 chars
        task = TaskCreate(**data)
        
        assert len(task.title) == 100

    def test_task_create_description_max_length(self):
        """Test that description cannot exceed 500 characters."""
        data = {
            "title": "Test",
            "description": "B" * 501  # Too long
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("at most 500 characters" in str(err) for err in errors)

    def test_task_create_description_exactly_max_length(self):
        """Test description with exactly maximum length."""
        data = {
            "title": "Test",
            "description": "B" * 500
        }
        task = TaskCreate(**data)
        
        assert len(task.description) == 500

    def test_task_create_missing_title(self):
        """Test that title is required."""
        data = {"description": "No title"}
        
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(**data)
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("title",) for err in errors)

    def test_task_create_empty_title(self):
        """Test that empty title is invalid."""
        data = {"title": ""}
        
        with pytest.raises(ValidationError):
            TaskCreate(**data)

    def test_task_create_none_description(self):
        """Test that description can be None."""
        data = {"title": "Test", "description": None}
        task = TaskCreate(**data)
        
        assert task.description is None

    def test_task_create_whitespace_title(self):
        """Test title with whitespace."""
        data = {"title": "   Test Task   "}
        task = TaskCreate(**data)
        
        # Pydantic doesn't strip by default
        assert task.title == "   Test Task   "


@pytest.mark.unit
class TestTaskUpdateSchema:
    """Test the TaskUpdate Pydantic schema."""

    def test_task_update_all_fields(self):
        """Test updating all fields."""
        data = {
            "title": "Updated Title",
            "description": "Updated description",
            "completed": True
        }
        task = TaskUpdate(**data)

        assert task.title == "Updated Title"
        assert task.description == "Updated description"
        assert task.completed is True

    def test_task_update_only_title(self):
        """Test updating only title."""
        data = {"title": "New Title"}
        task = TaskUpdate(**data)

        assert task.title == "New Title"
        assert task.description is None
        assert task.completed is None

    def test_task_update_only_description(self):
        """Test updating only description."""
        data = {"description": "New description"}
        task = TaskUpdate(**data)

        assert task.title is None
        assert task.description == "New description"
        assert task.completed is None

    def test_task_update_only_completed(self):
        """Test updating only completed status."""
        data = {"completed": True}
        task = TaskUpdate(**data)

        assert task.title is None
        assert task.description is None
        assert task.completed is True

    def test_task_update_empty_payload(self):
        """Test TaskUpdate with no fields (all optional)."""
        data = {}
        task = TaskUpdate(**data)

        assert task.title is None
        assert task.description is None
        assert task.completed is None

    def test_task_update_title_min_length(self):
        """Test that title validation applies to updates."""
        data = {"title": "AB"}  # Too short
        
        with pytest.raises(ValidationError):
            TaskUpdate(**data)

    def test_task_update_title_max_length(self):
        """Test that title max length validation applies to updates."""
        data = {"title": "A" * 101}  # Too long
        
        with pytest.raises(ValidationError):
            TaskUpdate(**data)

    def test_task_update_description_max_length(self):
        """Test that description max length validation applies to updates."""
        data = {"description": "B" * 501}  # Too long
        
        with pytest.raises(ValidationError):
            TaskUpdate(**data)

    def test_task_update_completed_false(self):
        """Test setting completed to False."""
        data = {"completed": False}
        task = TaskUpdate(**data)

        assert task.completed is False

    def test_task_update_invalid_completed_type(self):
        """Test that completed must be boolean."""
        data = {"completed": "not a boolean"}
        
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(**data)
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("completed",) for err in errors)


@pytest.mark.unit
class TestTaskResponseSchema:
    """Test the TaskResponse Pydantic schema."""

    def test_task_response_all_fields(self):
        """Test TaskResponse with all fields."""
        now = datetime.now(timezone.utc)
        data = {
            "id": 1,
            "title": "Response Task",
            "description": "Response description",
            "completed": True,
            "created_at": now
        }
        task = TaskResponse(**data)

        assert task.id == 1
        assert task.title == "Response Task"
        assert task.description == "Response description"
        assert task.completed is True
        assert task.created_at == now

    def test_task_response_minimal_description(self):
        """Test TaskResponse with None description."""
        now = datetime.now(timezone.utc)
        data = {
            "id": 1,
            "title": "Test",
            "description": None,
            "completed": False,
            "created_at": now
        }
        task = TaskResponse(**data)

        assert task.description is None

    def test_task_response_missing_required_fields(self):
        """Test that all fields except description are required."""
        data = {"title": "Test"}
        
        with pytest.raises(ValidationError) as exc_info:
            TaskResponse(**data)
        
        errors = exc_info.value.errors()
        required_fields = {"id", "completed", "created_at"}
        error_fields = {err["loc"][0] for err in errors}
        
        assert required_fields.intersection(error_fields)

    def test_task_response_from_attributes_config(self):
        """Test that from_attributes is configured."""
        # This is tested implicitly in integration tests
        # but we verify the config exists
        assert TaskResponse.model_config.get("from_attributes") is True

    def test_task_response_invalid_id_type(self):
        """Test that id must be an integer."""
        now = datetime.now(timezone.utc)
        data = {
            "id": "not an int",
            "title": "Test",
            "completed": False,
            "created_at": now
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TaskResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("id",) for err in errors)

    def test_task_response_invalid_datetime(self):
        """Test that created_at must be a datetime."""
        data = {
            "id": 1,
            "title": "Test",
            "completed": False,
            "created_at": "not a datetime"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            TaskResponse(**data)
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("created_at",) for err in errors)

    def test_task_response_datetime_parsing(self):
        """Test that datetime strings are parsed correctly."""
        data = {
            "id": 1,
            "title": "Test",
            "completed": False,
            "created_at": "2024-01-01T12:00:00Z"
        }
        task = TaskResponse(**data)
        
        assert isinstance(task.created_at, datetime)