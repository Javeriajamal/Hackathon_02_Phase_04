from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from typing import Optional
import logging
from database import get_db_session
from middleware.auth import verify_token
from services.chat_service import ChatService
from schemas.chat import ChatRequest, ChatResponse


# Set up logging
logger = logging.getLogger(__name__)

# Create the router
router = APIRouter(prefix="/api/v1", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    chat_request: ChatRequest,
    db_session: Session = Depends(get_db_session),
    user_id: str = Depends(verify_token)
):
    """
    Main chat endpoint that processes natural language input and returns AI-generated responses.

    Args:
        chat_request: Contains the user message and optional conversation context
        db_session: Database session for persistence operations
        user_id: Verified user ID from JWT token

    Returns:
        ChatResponse containing the AI-generated response and any tool execution results
    """
    try:
        # Create chat service instance
        chat_service = ChatService(db_session)

        # Process the chat request
        result = await chat_service.process_chat_message(
            user_id=user_id,
            message=chat_request.message,
            conversation_id=chat_request.conversation_id
        )

        logger.info(f"Chat processed successfully for user {user_id}")
        return ChatResponse(**result)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing chat for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {str(e)}"
        )


@router.get("/conversation/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: str,
    db_session: Session = Depends(get_db_session),
    user_id: str = Depends(verify_token)
):
    """
    Retrieve conversation history by conversation ID.

    Args:
        conversation_id: The ID of the conversation to retrieve
        db_session: Database session for querying
        user_id: Verified user ID from JWT token

    Returns:
        Dictionary containing conversation history
    """
    try:
        # Validate UUID format
        try:
            UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID format"
            )

        # Create chat service instance
        chat_service = ChatService(db_session)

        # Retrieve conversation history
        conversation = await chat_service.get_conversation_history(
            user_id=user_id,
            conversation_id=conversation_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        logger.info(f"Conversation {conversation_id} retrieved successfully for user {user_id}")
        return conversation

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation: {str(e)}"
        )


@router.delete("/conversation/{conversation_id}", response_model=dict)
async def delete_conversation(
    conversation_id: str,
    db_session: Session = Depends(get_db_session),
    user_id: str = Depends(verify_token)
):
    """
    Delete a conversation by conversation ID.

    Args:
        conversation_id: The ID of the conversation to delete
        db_session: Database session for deletion operations
        user_id: Verified user ID from JWT token

    Returns:
        Dictionary containing deletion confirmation
    """
    try:
        # Validate UUID format
        try:
            UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation ID format"
            )

        # Create chat service instance
        chat_service = ChatService(db_session)

        # Delete conversation
        result = await chat_service.delete_conversation(
            user_id=user_id,
            conversation_id=conversation_id
        )

        logger.info(f"Conversation {conversation_id} deleted successfully for user {user_id}")
        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )