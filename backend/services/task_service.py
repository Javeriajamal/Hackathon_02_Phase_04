from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import datetime
import uuid
import logging
from models.task import Task, TaskCreate, TaskUpdate
from models.user import User
from schemas.task import TaskPublic

logger = logging.getLogger(__name__)


def create_task_for_user(session: Session, task_create: TaskCreate, user_id: uuid.UUID) -> Optional[TaskPublic]:
    """Create a new task for the specified user."""
    try:
        # Verify user exists and is active
        user_statement = select(User).where(User.id == user_id).where(User.is_active == True)
        result = session.execute(user_statement)
        user = result.scalar_one_or_none()

        if not user:
            logger.warning(f"Task creation failed: user {user_id} not found or inactive")
            return None

        # Create new task with owner_id
        db_task = Task(
            title=task_create.title,
            description=task_create.description,
            status=task_create.status or "pending",
            priority=task_create.priority or "medium",
            due_date=task_create.due_date,
            owner_id=user_id
        )

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        # Convert to TaskPublic response
        task_public = TaskPublic(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=db_task.status,
            priority=db_task.priority,
            due_date=db_task.due_date,
            owner_id=db_task.owner_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            is_completed=db_task.is_completed
        )

        logger.info(f"Successfully created task {db_task.id} for user {user_id}")
        return task_public
    except Exception as e:
        logger.error(f"Task creation error: {str(e)}")
        session.rollback()
        return None


def get_tasks_for_user(
    session: Session,
    user_id: uuid.UUID,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> tuple[List[TaskPublic], int]:
    """Get all tasks for the specified user with optional filters."""
    try:
        # Build query with user ownership filter
        query = select(Task).where(Task.owner_id == user_id)

        # Apply status filter if provided
        if status:
            query = query.where(Task.status == status)

        # Apply priority filter if provided
        if priority:
            query = query.where(Task.priority == priority)

        # Get total count for pagination
        count_query = select(func.count(Task.id)).where(Task.owner_id == user_id)
        if status:
            count_query = count_query.where(Task.status == status)
        if priority:
            count_query = count_query.where(Task.priority == priority)

        result = session.execute(count_query)
        total_count = result.scalar()

        # Apply ordering, limit, and offset
        query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)
        result = session.execute(query)
        tasks = result.scalars().all()

        # Convert to TaskPublic responses
        task_list = []
        for task in tasks:
            task_public = TaskPublic(
                id=task.id,
                title=task.title,
                description=task.description,
                status=task.status,
                priority=task.priority,
                due_date=task.due_date,
                owner_id=task.owner_id,
                created_at=task.created_at,
                updated_at=task.updated_at,
                is_completed=task.is_completed
            )
            task_list.append(task_public)

        logger.info(f"Retrieved {len(task_list)} tasks for user {user_id}")
        return task_list, total_count
    except Exception as e:
        logger.error(f"Get tasks error: {str(e)}")
        return [], 0


def get_task_by_id_for_user(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[TaskPublic]:
    """Get a specific task by ID for the specified user."""
    try:
        statement = select(Task).where(Task.id == task_id).where(Task.owner_id == user_id)
        result = session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            return None

        task_public = TaskPublic(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            owner_id=task.owner_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            is_completed=task.is_completed
        )

        logger.info(f"Retrieved task {task.id} for user {user_id}")
        return task_public
    except Exception as e:
        logger.error(f"Get task by ID error: {str(e)}")
        return None


def update_task_for_user(
    session: Session,
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    user_id: uuid.UUID
) -> Optional[TaskPublic]:
    """Update a specific task by ID for the specified user."""
    try:
        # Get the existing task and verify ownership
        statement = select(Task).where(Task.id == task_id).where(Task.owner_id == user_id)
        result = session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            logger.warning(f"Task update failed: task {task_id} not found for user {user_id}")
            return None

        # Update only the fields that are provided
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)

        # Update the updated_at timestamp
        db_task.updated_at = datetime.utcnow()

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        # Convert to TaskPublic response
        task_public = TaskPublic(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=db_task.status,
            priority=db_task.priority,
            due_date=db_task.due_date,
            owner_id=db_task.owner_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            is_completed=db_task.is_completed
        )

        logger.info(f"Successfully updated task {db_task.id} for user {user_id}")
        return task_public
    except Exception as e:
        logger.error(f"Task update error: {str(e)}")
        session.rollback()
        return None


def delete_task_for_user(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    """Delete a specific task by ID for the specified user."""
    try:
        # Get the existing task and verify ownership
        statement = select(Task).where(Task.id == task_id).where(Task.owner_id == user_id)
        result = session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            logger.warning(f"Task deletion failed: task {task_id} not found for user {user_id}")
            return False

        session.delete(db_task)
        session.commit()

        logger.info(f"Successfully deleted task {db_task.id} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Task deletion error: {str(e)}")
        session.rollback()
        return False


def toggle_task_completion(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[TaskPublic]:
    """Toggle the completion status of a task."""
    try:
        # Get the existing task and verify ownership
        statement = select(Task).where(Task.id == task_id).where(Task.owner_id == user_id)
        result = session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            logger.warning(f"Task toggle failed: task {task_id} not found for user {user_id}")
            return None

        # Toggle completion status
        db_task.is_completed = not db_task.is_completed
        db_task.updated_at = datetime.utcnow()

        session.add(db_task)
        session.commit()
        session.refresh(db_task)

        # Convert to TaskPublic response
        task_public = TaskPublic(
            id=db_task.id,
            title=db_task.title,
            description=db_task.description,
            status=db_task.status,
            priority=db_task.priority,
            due_date=db_task.due_date,
            owner_id=db_task.owner_id,
            created_at=db_task.created_at,
            updated_at=db_task.updated_at,
            is_completed=db_task.is_completed
        )

        logger.info(f"Toggled completion status for task {db_task.id} (now {db_task.is_completed})")
        return task_public
    except Exception as e:
        logger.error(f"Task toggle error: {str(e)}")
        session.rollback()
        return None