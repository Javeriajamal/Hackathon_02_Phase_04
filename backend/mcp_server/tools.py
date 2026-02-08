from typing import List, Dict, Any, Optional
from sqlmodel import select, func
from datetime import datetime
from models.message import MessageRole
from models.conversation import Conversation, ConversationCreate
from models.message import Message, MessageCreate
from models.task import Task, TaskCreate, TaskUpdate, TaskStatus
from database import get_db_session
from uuid import UUID


class MCPTaskTools:
    """
    MCP (Model Context Protocol) tools for task management in the Phase-3 chatbot.
    These tools provide a stateless interface for the AI agent to interact with tasks.
    """

    def __init__(self, db_session):
        self.db_session = db_session

    async def add_task(self, user_id: str, title: str, description: Optional[str] = None,
                      priority: Optional[str] = None, due_date: Optional[str] = None,
                      category: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates a new task for the specified user.

        Args:
            user_id: The ID of the user creating the task
            title: The title of the task
            description: Optional description of the task
            priority: Optional priority level (low, medium, high)
            due_date: Optional due date string
            category: Optional category for the task

        Returns:
            Dictionary containing the created task ID and confirmation
        """
        # Create the task object
        from datetime import datetime

        # Prepare the task data
        task_kwargs = {
            "owner_id": UUID(user_id),
            "title": title,
            "description": description,
            "status": TaskStatus.pending,
            "priority": priority or "medium"
        }

        if due_date:
            try:
                parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                task_kwargs["due_date"] = parsed_date
            except ValueError:
                # If due_date is not in ISO format, try to parse it as a simple string
                task_kwargs["due_date"] = due_date

        # Don't add category if not in the model
        task = Task(**task_kwargs)

        # Add to database
        self.db_session.add(task)
        await self.db_session.commit()
        await self.db_session.refresh(task)

        return {
            "task_id": str(task.id),
            "created_at": task.created_at.isoformat(),
            "status": "active",
            "message": f"Task '{task.title}' created successfully"
        }

    async def list_tasks(self, user_id: str, status_filter: Optional[str] = None,
                        category_filter: Optional[str] = None,
                        priority_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves tasks for the specified user based on optional filters.

        Args:
            user_id: The ID of the user whose tasks to retrieve
            status_filter: Optional status to filter by (active, completed, all)
            category_filter: Optional category to filter by
            priority_filter: Optional priority to filter by

        Returns:
            Dictionary containing the list of tasks and metadata
        """
        # Build the query
        query = select(Task).where(Task.owner_id == UUID(user_id))

        if status_filter and status_filter != "all":
            if status_filter == "active":
                query = query.where(Task.status != TaskStatus.completed.value)
            elif status_filter == "completed":
                query = query.where(Task.status == TaskStatus.completed.value)

        # Skip category filter if Task model doesn't have category field
        # if category_filter:
        #     query = query.where(Task.category == category_filter)

        if priority_filter:
            query = query.where(Task.priority == priority_filter)

        # Execute the query
        result = await self.db_session.execute(query)
        tasks = result.scalars().all()

        # Convert tasks to dictionaries
        task_list = []
        for task in tasks:
            task_dict = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "priority": task.priority,
                "category": getattr(task, 'category', None),  # Handle missing category field
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None,
                "due_date": task.due_date.isoformat() if task.due_date else None
            }
            task_list.append(task_dict)

        return {
            "tasks": task_list,
            "total_count": len(task_list),
            "filtered_count": len(task_list),
            "message": f"Retrieved {len(task_list)} tasks for user {user_id}"
        }

    async def complete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Marks a specific task as completed.

        Args:
            user_id: The ID of the user who owns the task
            task_id: The ID of the task to complete

        Returns:
            Dictionary containing the task ID and completion confirmation
        """
        # Verify the task belongs to the user
        query = select(Task).where(Task.id == UUID(task_id)).where(Task.owner_id == UUID(user_id))
        result = await self.db_session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id} or user mismatch")

        if task.status == TaskStatus.completed.value:
            return {
                "task_id": task_id,
                "message": f"Task '{task.title}' is already completed"
            }

        # Update the task status
        task.status = TaskStatus.completed.value
        task.updated_at = datetime.utcnow()

        # Commit changes
        await self.db_session.commit()
        await self.db_session.refresh(task)

        return {
            "task_id": str(task.id),
            "previous_status": TaskStatus.pending.value,
            "completed_at": task.updated_at.isoformat(),
            "updated_status": task.status,
            "message": f"Task '{task.title}' marked as completed"
        }

    async def delete_task(self, user_id: str, task_id: str) -> Dict[str, Any]:
        """
        Permanently removes a task.

        Args:
            user_id: The ID of the user who owns the task
            task_id: The ID of the task to delete

        Returns:
            Dictionary containing the task ID and deletion confirmation
        """
        # Verify the task belongs to the user
        query = select(Task).where(Task.id == UUID(task_id)).where(Task.owner_id == UUID(user_id))
        result = await self.db_session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id} or user mismatch")

        # Delete the task
        await self.db_session.delete(task)
        await self.db_session.commit()

        return {
            "task_id": task_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "message": f"Task '{task.title}' deleted successfully"
        }

    async def update_task(self, user_id: str, task_id: str,
                         title: Optional[str] = None,
                         description: Optional[str] = None,
                         priority: Optional[str] = None,
                         due_date: Optional[str] = None,
                         category: Optional[str] = None,
                         status: Optional[str] = None) -> Dict[str, Any]:
        """
        Updates properties of an existing task.

        Args:
            user_id: The ID of the user who owns the task
            task_id: The ID of the task to update
            title: New title for the task (optional)
            description: New description for the task (optional)
            priority: New priority for the task (optional)
            due_date: New due date for the task (optional)
            category: New category for the task (optional)
            status: New status for the task (optional)

        Returns:
            Dictionary containing the task ID and update confirmation
        """
        # Verify the task belongs to the user
        query = select(Task).where(Task.id == UUID(task_id)).where(Task.owner_id == UUID(user_id))
        result = await self.db_session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id} or user mismatch")

        # Track which fields were updated
        updated_fields = {}

        if title is not None and title != task.title:
            task.title = title
            updated_fields["title"] = title

        if description is not None and description != task.description:
            task.description = description
            updated_fields["description"] = description

        if priority is not None and priority != task.priority:
            task.priority = priority
            updated_fields["priority"] = priority

        if due_date is not None and due_date != str(task.due_date):
            from datetime import datetime
            try:
                parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                task.due_date = parsed_date
            except ValueError:
                # If due_date is not in ISO format, try to parse it as a simple string
                task.due_date = due_date
            updated_fields["due_date"] = due_date

        if category is not None and category != task.category:
            task.category = category
            updated_fields["category"] = category

        if status is not None and status != task.status:
            # Validate the status
            try:
                TaskStatus(status)
                task.status = status
                updated_fields["status"] = status
            except ValueError:
                raise ValueError(f"Invalid status: {status}")

        # Update the timestamp
        task.updated_at = datetime.utcnow()

        # Commit changes
        await self.db_session.commit()
        await self.db_session.refresh(task)

        return {
            "task_id": str(task.id),
            "updated_fields": updated_fields,
            "updated_at": task.updated_at.isoformat(),
            "message": f"Task '{task.title}' updated successfully"
        }


# Helper function to create an instance of the tools
async def get_mcp_tools(db_session):
    """
    Factory function to create an instance of MCPTaskTools.

    Args:
        db_session: The database session to use for operations

    Returns:
        MCPTaskTools instance
    """
    return MCPTaskTools(db_session)