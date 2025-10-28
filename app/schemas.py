from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task.

    All fields are optional to support partial updates via PUT.
    """

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Schema returned by the API representing a task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime

