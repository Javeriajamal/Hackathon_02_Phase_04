from typing import Dict, Any, Optional, List
from sqlmodel import select, Session
from uuid import UUID
from datetime import datetime
import logging
import json
from models.conversation import Conversation, ConversationCreate
from models.message import Message, MessageRole
from mcp_server.tools import MCPTaskTools
from mcp_server.server import mcp_server
from database import get_db_session


# Set up logging
logger = logging.getLogger(__name__)


class ChatService:
    """
    Service class to handle chat operations including message processing,
    conversation management, and integration with MCP tools.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def process_chat_message(self, user_id: str, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a chat message by:
        1. Creating/storing the user message
        2. Analyzing the intent
        3. Calling appropriate MCP tools
        4. Generating AI response
        5. Storing the AI response
        6. Returning the response and tool execution results

        Args:
            user_id: The ID of the user sending the message
            message: The natural language message from the user
            conversation_id: Optional conversation ID (creates new if not provided)

        Returns:
            Dictionary containing the response and any tool execution results
        """
        # Create or retrieve conversation
        if conversation_id:
            # Validate UUID format
            try:
                UUID(conversation_id)
            except ValueError:
                raise ValueError("Invalid conversation ID format")

            # Retrieve existing conversation
            conversation_query = select(Conversation).where(
                Conversation.id == conversation_id
            ).where(Conversation.user_id == user_id)
            conversation_result = await self.db_session.execute(conversation_query)
            conversation = conversation_result.scalar_one_or_none()

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found for user {user_id}")
        else:
            # Create new conversation
            conversation = Conversation(user_id=str(user_id), title=message[:50] if len(message) > 50 else message)
            self.db_session.add(conversation)
            await self.db_session.commit()
            await self.db_session.refresh(conversation)
            conversation_id = str(conversation.id)

        # Store user message
        user_message = Message(
            conversation_id=conversation_id,
            user_id=str(user_id),
            role=MessageRole.USER,
            content=message
        )
        self.db_session.add(user_message)
        await self.db_session.commit()
        await self.db_session.refresh(user_message)

        # Analyze intent and call MCP tools
        tool_calls, ai_response = await self._analyze_and_execute_tools(user_id, message, conversation_id)

        # Store AI response
        ai_message = Message(
            conversation_id=conversation_id,
            user_id=str(user_id),  # AI acts on behalf of the user
            role=MessageRole.ASSISTANT,
            content=ai_response
        )
        self.db_session.add(ai_message)
        await self.db_session.commit()

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        self.db_session.add(conversation)
        await self.db_session.commit()

        return {
            "conversation_id": conversation_id,
            "response": ai_response,
            "timestamp": datetime.utcnow().isoformat(),
            "tool_calls": tool_calls,
            "context_summary": {
                "last_intent": self._extract_intent(message),
                "referenced_tasks": [],  # Will be populated based on tool calls
                "conversation_state": "active"
            }
        }

    async def _analyze_and_execute_tools(self, user_id: str, message: str, conversation_id: str) -> tuple[List[Dict], str]:
        """
        Analyze the user message and execute appropriate MCP tools.

        Args:
            user_id: The ID of the user
            message: The user's message
            conversation_id: The conversation ID

        Returns:
            Tuple of (tool_calls, ai_response)
        """
        # Simple intent analysis based on keywords
        intent = self._extract_intent(message.lower())
        tool_calls = []
        ai_response = ""

        # Create MCP tools instance
        mcp_tools = MCPTaskTools(self.db_session)

        try:
            # Check for add intent
            if intent == "add" or any(word in message.lower() for word in ["add", "create", "new"]):
                # Extract task details from message
                task_title = self._extract_task_title(message)
                if task_title:
                    result = await mcp_tools.add_task(user_id, task_title)
                    tool_calls.append({
                        "tool_name": "add_task",
                        "parameters": {"title": task_title},
                        "result": result
                    })
                    ai_response = f"I've added the task '{task_title}' to your list."
                else:
                    ai_response = "I need more details to create a task. Please specify what task you'd like to add."

            # Check for list intent
            elif intent == "list" or any(word in message.lower() for word in ["list", "show", "view", "see"]):
                # Call list_tasks tool
                result = await mcp_tools.list_tasks(user_id)
                tool_calls.append({
                    "tool_name": "list_tasks",
                    "parameters": {},
                    "result": result
                })

                if result["tasks"]:
                    task_list = [f"{i+1}. {task['title']}" for i, task in enumerate(result["tasks"][:5])]  # Limit to first 5
                    ai_response = f"Here are your tasks:\n" + "\n".join(task_list)
                    if len(result["tasks"]) > 5:
                        ai_response += f"\n\n...and {len(result["tasks"]) - 5} more tasks."
                else:
                    ai_response = "You don't have any tasks in your list."

            # Check for complete intent
            elif intent == "complete" or any(word in message.lower() for word in ["complete", "done", "finish", "completed"]):
                # Extract task ID or title from message
                task_identifier = self._extract_task_identifier(message)
                if task_identifier:
                    # First, try to find the task by title if identifier is not a UUID
                    task_id = await self._find_task_id_by_identifier(user_id, task_identifier)
                    if task_id:
                        result = await mcp_tools.complete_task(user_id, str(task_id))
                        tool_calls.append({
                            "tool_name": "complete_task",
                            "parameters": {"task_id": str(task_id)},
                            "result": result
                        })
                        ai_response = result.get("message", f"Task marked as completed.")
                    else:
                        ai_response = f"I couldn't find a task matching '{task_identifier}'."
                else:
                    ai_response = "I need to know which task to mark as complete. Please specify the task."

            # Check for delete intent
            elif intent == "delete" or any(word in message.lower() for word in ["delete", "remove", "cancel"]):
                # Extract task title from message (removing command verbs)
                task_title = self._extract_task_title_for_deletion(message)
                if task_title:
                    task_id = await self._find_task_id_by_identifier(user_id, task_title)
                    if task_id:
                        result = await mcp_tools.delete_task(user_id, str(task_id))
                        tool_calls.append({
                            "tool_name": "delete_task",
                            "parameters": {"task_id": str(task_id)},
                            "result": result
                        })
                        ai_response = result.get("message", f"Task '{task_title}' deleted successfully.")
                    else:
                        ai_response = f"I couldn't find a task matching '{task_title}'."
                else:
                    ai_response = "I need to know which task to delete. Please specify the task."

            # Check for update intent
            elif intent == "update" or any(word in message.lower() for word in ["update", "change", "modify", "edit"]):
                # Extract old title and new title from message
                old_title, new_title = self._extract_update_titles(message)
                if old_title and new_title:
                    task_id = await self._find_task_id_by_identifier(user_id, old_title)
                    if task_id:
                        result = await mcp_tools.update_task(user_id, str(task_id), title=new_title)
                        tool_calls.append({
                            "tool_name": "update_task",
                            "parameters": {"task_id": str(task_id), "title": new_title},
                            "result": result
                        })
                        ai_response = result.get("message", f"Task '{old_title}' updated to '{new_title}' successfully.")
                    else:
                        ai_response = f"I couldn't find a task matching '{old_title}'."
                else:
                    ai_response = "I need to know which task to update and what to change it to. For example: 'Change task 'gym' to 'workout''."

            else:
                # Default response for unrecognized intents
                ai_response = f"I understand you said: '{message}'. I can help you manage your tasks by adding, listing, completing, updating, or deleting them. How can I assist you?"

        except Exception as e:
            logger.error(f"Error executing tools for user {user_id}: {str(e)}")
            ai_response = f"I encountered an error processing your request: {str(e)}. Please try again."

        return tool_calls, ai_response

    def _extract_intent(self, message: str) -> str:
        """
        Extract the intent from the user message.

        Args:
            message: The user's message

        Returns:
            The extracted intent
        """
        message_lower = message.lower()
        if any(word in message_lower for word in ["add", "create", "new"]):
            return "add"
        elif any(word in message_lower for word in ["list", "show", "view", "see"]):
            return "list"
        elif any(word in message_lower for word in ["complete", "done", "finish", "completed"]):
            return "complete"
        elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
            return "delete"
        elif any(word in message_lower for word in ["update", "change", "modify", "edit"]):
            return "update"
        else:
            return "unknown"

    def _extract_task_title(self, message: str) -> Optional[str]:
        """
        Extract task title from message using heuristics.

        Args:
            message: The user's message

        Returns:
            The extracted task title or None
        """
        # Normalize the message
        message_clean = message.strip()

        # Look for common patterns like "create a task to X" or "add a task to X"
        import re
        patterns = [
            r'(?:create|add|make|set up)\s+(?:a\s+)?(?:task|todo)\s+(?:to|for|that|which)\s+(.+)',
            r'(?:create|add|make|set up)\s+(?:a\s+)?(?:task|todo)\s+(.+)',
            r'(?:please\s+)?(?:create|add|make|set up)\s+(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, message_clean, re.IGNORECASE)
            if match:
                task_title = match.group(1).strip()
                # Remove trailing punctuation
                task_title = task_title.rstrip('.,!?')
                if len(task_title) > 0 and len(task_title) < 100:
                    return task_title

        # If the entire message seems to be the task (e.g., "buy groceries"), return it
        if len(message_clean) > 3 and len(message_clean) < 100:
            # Remove common prefixes
            prefixes = ['create', 'add', 'make', 'please', 'task:', 'todo:']
            task_title = message_clean
            for prefix in prefixes:
                if task_title.lower().startswith(prefix.lower()):
                    task_title = task_title[len(prefix):].strip()
                    break

            task_title = task_title.strip('.,!?')
            if len(task_title) > 0 and len(task_title) < 100:
                return task_title

        return None

    def _extract_task_identifier(self, message: str) -> Optional[str]:
        """
        Extract task identifier (ID or title) from message.

        Args:
            message: The user's message

        Returns:
            The extracted task identifier or None
        """
        # Try to find a UUID in the message
        import re
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        uuid_match = re.search(uuid_pattern, message)
        if uuid_match:
            return uuid_match.group()

        # Otherwise, extract the meaningful part of the message
        message_lower = message.lower()
        # Remove common action words
        for word in ["complete", "done", "finish", "delete", "remove", "update", "change", "the", "task", "that", "is"]:
            message_lower = message_lower.replace(f" {word} ", " ").strip()

        # Extract the important part
        parts = message_lower.split()
        if len(parts) > 1:
            # Take the last few words as the identifier
            identifier = " ".join(parts[-3:])  # Last 3 words should be enough
            if len(identifier) > 1:
                return identifier

        return None

    def _extract_task_and_update_details(self, message: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract task identifier and update details from message.

        Args:
            message: The user's message

        Returns:
            Tuple of (task_identifier, update_details)
        """
        # Simplified extraction - in a real implementation, this would be more sophisticated
        message_lower = message.lower()

        # Find the task part and update part
        if "to" in message_lower:
            parts = message_lower.split("to", 1)
            task_part = parts[0].strip()
            update_part = parts[1].strip()

            # Extract identifier from task part
            task_identifier = self._extract_task_identifier(task_part)
            return task_identifier, update_part

        return None, None

    def _extract_update_titles(self, message: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract old title and new title from update message.

        Args:
            message: The user's message

        Returns:
            Tuple of (old_title, new_title)
        """
        import re

        message_lower = message.lower().strip()

        # Look for patterns like "update 'old' to 'new'", "change 'old' to 'new'", "update task: old to new", etc.
        # Pattern: update/change/modify [the] task[:]? ["|'|`]old["|'|`] to ["|'|`]new["|'|`]
        pattern = r'(?:update|change|modify|rename)\s+(?:the\s+)?task\s*:?\s*(?:\'|\"|`)?([^\'\"\`]*?)(?:\'|\"|`)?\s+to\s+(?:\'|\"|`)?([^\'\"\`]+?)(?:\'|\"|`)?$'
        match = re.search(pattern, message_lower)

        if match:
            old_title = match.group(1).strip()
            new_title = match.group(2).strip()
            return old_title, new_title

        # Alternative pattern: update/change [the] task [:|titled|called|named] ["|'|`]old["|'|`] to ["|'|`]new["|'|`]
        alt_pattern = r'(?:update|change|modify|rename)\s+(?:the\s+)?task\s+:\s*(?:\'|\"|`)?([^\'\"\`]*?)(?:\'|\"|`)?\s+to\s+(?:\'|\"|`)?([^\'\"\`]+?)(?:\'|\"|`)?$'
        alt_match = re.search(alt_pattern, message_lower)

        if not alt_match:
            # Alternative pattern: update/change [the] task titled ["|'|`]old["|'|`] to ["|'|`]new["|'|`]
            alt_pattern = r'(?:update|change|modify|rename)\s+(?:the\s+)?task\s+.*?(?:titled|called|named)\s*(?:\'|\"|`)?([^\'\"\`]*?)(?:\'|\"|`)?\s+to\s+(?:\'|\"|`)?([^\'\"\`]+?)(?:\'|\"|`)?$'
            alt_match = re.search(alt_pattern, message_lower)

        if alt_match:
            old_title = alt_match.group(1).strip()
            new_title = alt_match.group(2).strip()
            return old_title, new_title

        # If we can't find a clear pattern, try to extract from a general format
        if ' to ' in message_lower:
            parts = message_lower.split(' to ', 1)
            if len(parts) == 2:
                old_part = parts[0].strip()
                new_part = parts[1].strip()

                # Remove common action words from the old part using regex
                for word in ['update', 'change', 'modify', 'rename', 'the', 'task', 'titled', 'called', 'is']:
                    # Remove the word when surrounded by spaces, at the start, or at the end
                    old_part = re.sub(rf'\b{re.escape(word)}\b\s*', '', old_part, flags=re.IGNORECASE)
                    old_part = re.sub(rf'^{re.escape(word)}\s+', '', old_part, flags=re.IGNORECASE)
                    old_part = re.sub(rf'\s+{re.escape(word)}$', '', old_part, flags=re.IGNORECASE)

                old_part = old_part.strip(' .,!?')

                return old_part.strip(), new_part.strip()

        return None, None


    def _extract_task_title_for_deletion(self, message: str) -> Optional[str]:
        """
        Extract task title from deletion message.

        Args:
            message: The user's message

        Returns:
            The extracted task title or None
        """
        import re

        message_lower = message.lower().strip()

        # Look for patterns like "delete 'task'", "remove task 'title'", "delete task: title", etc.
        # Pattern: delete/remove/cancel [the] task[:]? ["|'|`]title["|'|`]
        pattern = r'(?:delete|remove|cancel)\s+(?:the\s+)?task\s*:?\s*(?:\'|\"|`)?([^\'\"\`]+?)(?:\'|\"|`)?$'
        match = re.search(pattern, message_lower)

        if match:
            return match.group(1).strip()

        # Alternative pattern: delete/remove [the] task [:] title
        alt_pattern = r'(?:delete|remove|cancel)\s+(?:the\s+)?task\s*:\s*([^\']+?)(?:\'|\"|`)?$'
        alt_match = re.search(alt_pattern, message_lower)

        if not alt_match:
            # Alternative pattern: delete/remove [the] task titled ["|'|`]title["|'|`]
            alt_pattern = r'(?:delete|remove|cancel)\s+(?:the\s+)?task\s+.*?(?:titled|called|named)\s*(?:\'|\"|`)?([^\'\"\`]+?)(?:\'|\"|`)?$'
            alt_match = re.search(alt_pattern, message_lower)

        if alt_match:
            return alt_match.group(1).strip()

        # If we can't find a clear pattern, try to extract the meaningful part
        # Remove common action words using regex
        for word in ['delete', 'remove', 'cancel', 'the', 'task', 'titled', 'called', 'is', 'please']:
            # Remove the word when surrounded by spaces, at the start, or at the end
            message_lower = re.sub(rf'\b{re.escape(word)}\b\s*', '', message_lower, flags=re.IGNORECASE)
            message_lower = re.sub(rf'^{re.escape(word)}\s+', '', message_lower, flags=re.IGNORECASE)
            message_lower = re.sub(rf'\s+{re.escape(word)}$', '', message_lower, flags=re.IGNORECASE)

        # Return what's left if it's meaningful
        message_lower = message_lower.strip(' .,!?')
        if len(message_lower) > 1 and len(message_lower) < 100:  # Reasonable title length
            return message_lower

        return None


    def _parse_update_parameters(self, update_details: str) -> Dict[str, Any]:
        """
        Parse update details into parameters for update_task.

        Args:
            update_details: The update details from the message

        Returns:
            Dictionary of update parameters
        """
        params = {}

        # Simple parsing - in a real implementation, this would be more sophisticated
        update_lower = update_details.lower()

        if "high" in update_lower or "urgent" in update_lower:
            params["priority"] = "high"
        elif "low" in update_lower or "not important" in update_lower:
            params["priority"] = "low"
        elif "medium" in update_lower:
            params["priority"] = "medium"

        # Check for title changes
        if "title" in update_lower or "name" in update_lower:
            # Extract new title (simplified)
            pass

        # Check for status changes
        if "completed" in update_lower or "done" in update_lower:
            params["status"] = "completed"
        elif "pending" in update_lower or "not done" in update_lower:
            params["status"] = "pending"

        return params

    async def _find_task_id_by_identifier(self, user_id: str, identifier: str) -> Optional[UUID]:
        """
        Find a task ID by its identifier (either UUID or title).

        Args:
            user_id: The user ID
            identifier: The task identifier (UUID or partial title)

        Returns:
            The task UUID or None if not found
        """
        # Convert user_id to UUID for query
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            # If user_id is not a valid UUID, return None
            return None

        try:
            # First, try if it's a UUID
            task_uuid = UUID(identifier)
            from models.task import Task
            query = select(Task).where(Task.id == task_uuid).where(Task.owner_id == user_uuid)
            result = await self.db_session.execute(query)
            task = result.scalar_one_or_none()
            if task:
                return task.id
        except ValueError:
            # Not a UUID, treat as title
            pass

        # Search in the Task table by title (case-insensitive, partial match)
        from models.task import Task
        query = select(Task).where(
            Task.owner_id == user_uuid
        ).where(
            Task.title.ilike(f"%{identifier}%")  # Case-insensitive partial match on task title
        )
        result = await self.db_session.execute(query)
        task = result.scalar_one_or_none()

        if task:
            return task.id

        # If still not found, try exact match in description
        query = select(Task).where(
            Task.owner_id == user_uuid
        ).where(
            Task.description.contains(identifier)
        )
        result = await self.db_session.execute(query)
        task = result.scalar_one_or_none()

        if task:
            return task.id

        # If still not found, try in title with contains (case-sensitive)
        query = select(Task).where(
            Task.owner_id == user_uuid
        ).where(
            Task.title.contains(identifier)
        )
        result = await self.db_session.execute(query)
        task = result.scalar_one_or_none()

        if task:
            return task.id

        return None

    async def get_conversation_history(self, user_id: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation history for a specific conversation.

        Args:
            user_id: The ID of the user
            conversation_id: The ID of the conversation

        Returns:
            Dictionary containing the conversation history or None
        """
        # Validate conversation belongs to user
        conversation_query = select(Conversation).where(
            Conversation.id == conversation_id
        ).where(Conversation.user_id == user_id)
        conversation_result = await self.db_session.execute(conversation_query)
        conversation = conversation_result.scalar_one_or_none()

        if not conversation:
            return None

        # Get all messages in the conversation
        messages_query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())
        messages_result = await self.db_session.execute(messages_query)
        messages = messages_result.scalars().all()

        # Format the conversation history
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "id": str(msg.id),
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            })

        return {
            "conversation_id": conversation_id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": formatted_messages
        }

    async def delete_conversation(self, user_id: str, conversation_id: str) -> Dict[str, str]:
        """
        Delete a conversation and all associated messages.

        Args:
            user_id: The ID of the user
            conversation_id: The ID of the conversation to delete

        Returns:
            Dictionary with deletion confirmation
        """
        # Validate conversation belongs to user
        conversation_query = select(Conversation).where(
            Conversation.id == conversation_id
        ).where(Conversation.user_id == user_id)
        conversation_result = await self.db_session.execute(conversation_query)
        conversation = conversation_result.scalar_one_or_none()

        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found for user {user_id}")

        # Delete all messages in the conversation first (due to foreign key constraint)
        messages_query = select(Message).where(Message.conversation_id == conversation_id)
        messages_result = await self.db_session.execute(messages_query)
        messages = messages_result.scalars().all()

        for message in messages:
            await self.db_session.delete(message)

        # Delete the conversation
        await self.db_session.delete(conversation)
        await self.db_session.commit()

        return {
            "conversation_id": conversation_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "message": f"Conversation '{conversation.title}' and all messages deleted successfully"
        }