from sqlmodel import select, Session
from models.task import Task, TaskCreate, TaskUpdate
from typing import List, Optional
import uuid


def get_tasks_by_user_id(session: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get tasks for a specific user with pagination"""
    statement = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
    result = session.execute(statement)
    return result.scalars().all()


def get_task_by_id_and_user_id(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
    """Get a specific task by ID and user ID (for user isolation)"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = session.execute(statement)
    return result.scalar_one_or_none()


def create_task(session: Session, task_create: TaskCreate, user_id: uuid.UUID) -> Task:
    """Create a new task for a user"""
    task_data = task_create.dict()
    task_data["user_id"] = user_id

    task = Task(**task_data)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def update_task(session: Session, task_id: uuid.UUID, user_id: uuid.UUID, task_update: TaskUpdate) -> Optional[Task]:
    """Update a task for a specific user (enforcing user isolation)"""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return None

    # Update fields
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def delete_task(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Delete a task for a specific user (enforcing user isolation)"""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return False

    session.delete(task)
    session.commit()
    return True


def toggle_task_status(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
    """Toggle the completion status of a task"""
    task = session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return None

    task.is_completed = not task.is_completed
    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def count_user_tasks(session: Session, user_id: uuid.UUID) -> int:
    """Count tasks for a specific user"""
    statement = select(Task).where(Task.user_id == user_id)
    result = session.execute(statement)
    tasks = result.scalars().all()
    return len(tasks)


def get_tasks_by_filters(session: Session, user_id: uuid.UUID, status: Optional[bool] = None,
                        priority: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Task]:
    """Get tasks with optional filters"""
    statement = select(Task).where(Task.user_id == user_id)

    if status is not None:
        statement = statement.where(Task.is_completed == status)

    if priority is not None:
        statement = statement.where(Task.priority == priority)

    statement = statement.offset(skip).limit(limit)
    result = session.execute(statement)
    return result.scalars().all()