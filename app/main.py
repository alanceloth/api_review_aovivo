from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db


app = FastAPI(
    title="Task Management API",
    description="API de gerenciamento de tarefas com FastAPI e SQLite.",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables on application startup."""
    Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root() -> dict:
    """Return a welcome message at the API root."""
    return {"message": "Bem-vindo à Task Management API"}


@app.post(
    "/tasks/",
    response_model=schemas.TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)) -> schemas.TaskResponse:
    """Create a new task with the provided title and optional description."""
    db_task = models.Task(title=task.title, description=task.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get(
    "/tasks/",
    response_model=List[schemas.TaskResponse],
    tags=["Tasks"],
)
def list_tasks(
    skip: int = 0,
    limit: int = 10,
    completed: Optional[bool] = None,
    db: Session = Depends(get_db),
) -> List[schemas.TaskResponse]:
    """List tasks with pagination and optional completion filter."""
    query = db.query(models.Task)
    if completed is not None:
        query = query.filter(models.Task.completed == completed)
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@app.get(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    tags=["Tasks"],
)
def get_task(task_id: int, db: Session = Depends(get_db)) -> schemas.TaskResponse:
    """Retrieve a task by its identifier.

    Raises 404 if the task does not exist.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task não encontrada")
    return task


@app.put(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    tags=["Tasks"],
)
def update_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
) -> schemas.TaskResponse:
    """Update an existing task. All fields are optional."""
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task não encontrada")

    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.completed is not None:
        task.completed = payload.completed

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a task by its identifier.

    Returns 204 No Content on success. Raises 404 if not found.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task não encontrada")
    db.delete(task)
    db.commit()
    return None

