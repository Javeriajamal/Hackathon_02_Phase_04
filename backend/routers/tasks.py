from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlmodel import Session
from typing import List
import logging
import uuid
from database import get_session
from schemas.task import TaskCreate, TaskUpdate, TaskPublic, TaskListResponse
from services.task_service import (
    create_task_for_user, get_tasks_for_user, get_task_by_id_for_user,
    update_task_for_user, delete_task_for_user, toggle_task_completion
)
from utils.security import get_current_user_id
from middleware.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

logger = logging.getLogger(__name__)


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    request: Request,
    status: str = Query(None, description="Filter by task status (pending, in_progress, completed)"),
    priority: str = Query(None, description="Filter by task priority (low, medium, high, urgent)"),
    limit: int = Query(20, ge=1, le=100, description="Number of tasks to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskListResponse:
    """Get all tasks for the authenticated user with optional filters."""
    try:
        logger.info(f"Getting tasks for user {current_user_id}, filters: status={status}, priority={priority}")

        tasks, total = get_tasks_for_user(session, current_user_id, status, priority, limit, offset)

        response = TaskListResponse(
            tasks=tasks,
            total=total,
            offset=offset,
            limit=limit
        )

        logger.info(f"Retrieved {len(tasks)} tasks for user {current_user_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get tasks error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving tasks"
        )


@router.post("", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: Request,
    task_create: TaskCreate,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskPublic:
    """Create a new task for the authenticated user."""
    try:
        logger.info(f"Creating task for user {current_user_id}")

        task_public = create_task_for_user(session, task_create, current_user_id)

        if task_public is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create task"
            )

        logger.info(f"Created task {task_public.id} for user {current_user_id}")
        return task_public
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create task error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error creating task"
        )


@router.get("/{task_id}", response_model=TaskPublic)
async def get_task(
    request: Request,
    task_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskPublic:
    """Get a specific task by ID for the authenticated user."""
    try:
        logger.info(f"Getting task {task_id} for user {current_user_id}")

        task_public = get_task_by_id_for_user(session, task_id, current_user_id)

        if task_public is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Retrieved task {task_id} for user {current_user_id}")
        return task_public
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get task by ID error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving task"
        )


@router.put("/{task_id}", response_model=TaskPublic)
async def update_task(
    request: Request,
    task_id: uuid.UUID,
    task_update: TaskUpdate,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskPublic:
    """Update a specific task by ID for the authenticated user."""
    try:
        logger.info(f"Updating task {task_id} for user {current_user_id}")

        task_public = update_task_for_user(session, task_id, task_update, current_user_id)

        if task_public is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or not owned by user"
            )

        logger.info(f"Updated task {task_id} for user {current_user_id}")
        return task_public
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update task error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error updating task"
        )


@router.delete("/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    request: Request,
    task_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> dict:
    """Delete a specific task by ID for the authenticated user."""
    try:
        logger.info(f"Deleting task {task_id} for user {current_user_id}")

        success = delete_task_for_user(session, task_id, current_user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or not owned by user"
            )

        logger.info(f"Deleted task {task_id} for user {current_user_id}")
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete task error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error deleting task"
        )


@router.patch("/{task_id}/toggle-completion", response_model=TaskPublic)
async def toggle_task_completion_endpoint(
    request: Request,
    task_id: uuid.UUID,
    current_user_id: uuid.UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> TaskPublic:
    """Toggle the completion status of a task."""
    try:
        logger.info(f"Toggling completion for task {task_id} for user {current_user_id}")

        task_public = toggle_task_completion(session, task_id, current_user_id)

        if task_public is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or not owned by user"
            )

        logger.info(f"Toggled completion for task {task_id}, now is_completed={task_public.is_completed}")
        return task_public
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Toggle task completion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error toggling task completion"
        )