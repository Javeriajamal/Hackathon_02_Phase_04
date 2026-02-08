"""
MCP (Model Context Protocol) Server Configuration for Phase-3 Chatbot

This module provides configuration and utility functions for the MCP tools
used by the AI agent to interact with the task management system.
"""

from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session
from database import get_db_session
from middleware.auth import verify_token
from .tools import MCPTaskTools, get_mcp_tools
import logging


# Set up logging
logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server class that manages the tools available to the AI agent.
    """

    def __init__(self):
        self.tools = {}
        self.tool_functions = {
            "add_task": self._execute_add_task,
            "list_tasks": self._execute_list_tasks,
            "complete_task": self._execute_complete_task,
            "delete_task": self._execute_delete_task,
            "update_task": self._execute_update_task
        }

    async def register_tool(self, name: str, function):
        """
        Register a tool with the server.

        Args:
            name: Name of the tool
            function: Function to execute the tool
        """
        self.tools[name] = function
        logger.info(f"MCP tool '{name}' registered successfully")

    async def execute_tool(self, tool_name: str, params: Dict[str, Any], user_id: str, db_session: Session) -> Dict[str, Any]:
        """
        Execute a registered tool with the given parameters.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool
            user_id: ID of the user executing the tool
            db_session: Database session for the operation

        Returns:
            Result of the tool execution
        """
        if tool_name not in self.tools:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tool '{tool_name}' not found"
            )

        try:
            # Add user_id to params for authentication
            params_with_user = params.copy()
            params_with_user['user_id'] = user_id

            # Execute the tool
            result = await self.tools[tool_name](db_session, **params_with_user)
            logger.info(f"MCP tool '{tool_name}' executed successfully for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error executing MCP tool '{tool_name}' for user {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error executing tool '{tool_name}': {str(e)}"
            )

    # Tool execution methods
    async def _execute_add_task(self, db_session: Session, user_id: str, title: str, description: Optional[str] = None,
                               priority: Optional[str] = None, due_date: Optional[str] = None,
                               category: Optional[str] = None) -> Dict[str, Any]:
        """Execute the add_task tool."""
        tools_instance = await get_mcp_tools(db_session)
        return await tools_instance.add_task(user_id, title, description, priority, due_date, category)

    async def _execute_list_tasks(self, db_session: Session, user_id: str, status_filter: Optional[str] = None,
                                 category_filter: Optional[str] = None,
                                 priority_filter: Optional[str] = None) -> Dict[str, Any]:
        """Execute the list_tasks tool."""
        tools_instance = await get_mcp_tools(db_session)
        return await tools_instance.list_tasks(user_id, status_filter, category_filter, priority_filter)

    async def _execute_complete_task(self, db_session: Session, user_id: str, task_id: str) -> Dict[str, Any]:
        """Execute the complete_task tool."""
        tools_instance = await get_mcp_tools(db_session)
        return await tools_instance.complete_task(user_id, task_id)

    async def _execute_delete_task(self, db_session: Session, user_id: str, task_id: str) -> Dict[str, Any]:
        """Execute the delete_task tool."""
        tools_instance = await get_mcp_tools(db_session)
        return await tools_instance.delete_task(user_id, task_id)

    async def _execute_update_task(self, db_session: Session, user_id: str, task_id: str,
                                  title: Optional[str] = None,
                                  description: Optional[str] = None,
                                  priority: Optional[str] = None,
                                  due_date: Optional[str] = None,
                                  category: Optional[str] = None,
                                  status_param: Optional[str] = None) -> Dict[str, Any]:
        """Execute the update_task tool."""
        tools_instance = await get_mcp_tools(db_session)
        return await tools_instance.update_task(user_id, task_id, title, description, priority, due_date, category, status_param)


# Global MCP server instance
mcp_server = MCPServer()


async def initialize_mcp_server():
    """
    Initialize the MCP server with all required tools.
    """
    # Register all tools
    await mcp_server.register_tool("add_task", mcp_server._execute_add_task)
    await mcp_server.register_tool("list_tasks", mcp_server._execute_list_tasks)
    await mcp_server.register_tool("complete_task", mcp_server._execute_complete_task)
    await mcp_server.register_tool("delete_task", mcp_server._execute_delete_task)
    await mcp_server.register_tool("update_task", mcp_server._execute_update_task)

    logger.info("MCP server initialized with all task management tools")


# Dependency to get the MCP server
async def get_mcp_server() -> MCPServer:
    """
    Dependency to get the MCP server instance.

    Returns:
        MCPServer instance
    """
    return mcp_server


# Lifespan event for FastAPI to initialize the MCP server
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event to initialize and shutdown the MCP server.
    """
    # Initialize MCP server
    await initialize_mcp_server()
    yield
    # Cleanup if needed
    logger.info("MCP server shut down")