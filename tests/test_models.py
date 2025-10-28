"""Unit tests for SQLAlchemy models."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Task


@pytest.mark.unit
class TestTaskModel:
    """Test the Task SQLAlchemy model."""

    def test_task_creation_with_all_fields(self, db_session: Session):
        """Test creating a task with all fields provided."""
        task = Task(
            title="Complete project",
            description="Finish the FastAPI project by Friday",
            completed=False,
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.id is not None
        assert task.title == "Complete project"
        assert task.description == "Finish the FastAPI project by Friday"
        assert task.completed is False
        assert task.created_at is not None
        assert isinstance(task.created_at, datetime)

    def test_task_creation_minimal_fields(self, db_session: Session):
        """Test creating a task with only required fields."""
        task = Task(title="Minimal Task")
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.id is not None
        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.completed is False  # Default value
        assert task.created_at is not None

    def test_task_default_completed_false(self, db_session: Session):
        """Test that completed defaults to False."""
        task = Task(title="New Task")
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.completed is False

    def test_task_created_at_auto_populated(self, db_session: Session):
        """Test that created_at is automatically populated."""
        before = datetime.now(timezone.utc)
        task = Task(title="Time Test")
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        after = datetime.now(timezone.utc)

        assert task.created_at is not None
        assert before <= task.created_at <= after

    def test_task_title_not_null(self, db_session: Session):
        """Test that title cannot be null."""
        task = Task(description="No title")
        db_session.add(task)
        
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_task_completed_true(self, db_session: Session):
        """Test creating a task with completed=True."""
        task = Task(title="Completed Task", completed=True)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.completed is True

    def test_task_long_title(self, db_session: Session):
        """Test task with maximum length title."""
        long_title = "A" * 100
        task = Task(title=long_title)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.title == long_title
        assert len(task.title) == 100

    def test_task_long_description(self, db_session: Session):
        """Test task with maximum length description."""
        long_desc = "B" * 500
        task = Task(title="Test", description=long_desc)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        assert task.description == long_desc
        assert len(task.description) == 500

    def test_task_update_fields(self, db_session: Session):
        """Test updating task fields."""
        task = Task(title="Original Title", completed=False)
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        task.title = "Updated Title"
        task.completed = True
        task.description = "New description"
        db_session.commit()
        db_session.refresh(task)

        assert task.title == "Updated Title"
        assert task.completed is True
        assert task.description == "New description"

    def test_task_tablename(self):
        """Test that the table name is correctly set."""
        assert Task.__tablename__ == "tasks"

    def test_multiple_tasks_creation(self, db_session: Session):
        """Test creating multiple tasks."""
        tasks = [
            Task(title=f"Task {i}", description=f"Description {i}")
            for i in range(5)
        ]
        
        for task in tasks:
            db_session.add(task)
        db_session.commit()

        # Query all tasks
        all_tasks = db_session.query(Task).all()
        assert len(all_tasks) == 5
        
        # Verify IDs are unique
        ids = [task.id for task in all_tasks]
        assert len(ids) == len(set(ids))

    def test_task_query_by_id(self, db_session: Session):
        """Test querying a task by ID."""
        task = Task(title="Searchable Task")
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        found_task = db_session.query(Task).filter(Task.id == task.id).first()
        assert found_task is not None
        assert found_task.id == task.id
        assert found_task.title == "Searchable Task"

    def test_task_query_by_completed(self, db_session: Session):
        """Test filtering tasks by completed status."""
        completed_task = Task(title="Done", completed=True)
        incomplete_task = Task(title="Todo", completed=False)
        
        db_session.add(completed_task)
        db_session.add(incomplete_task)
        db_session.commit()

        completed_tasks = db_session.query(Task).filter(Task.completed).all()
        assert len(completed_tasks) == 1
        assert completed_tasks[0].title == "Done"

        incomplete_tasks = db_session.query(Task).filter(~Task.completed).all()
        assert len(incomplete_tasks) == 1
        assert incomplete_tasks[0].title == "Todo"

    def test_task_deletion(self, db_session: Session):
        """Test deleting a task."""
        task = Task(title="To Delete")
        db_session.add(task)
        db_session.commit()
        task_id = task.id

        db_session.delete(task)
        db_session.commit()

        deleted_task = db_session.query(Task).filter(Task.id == task_id).first()
        assert deleted_task is None