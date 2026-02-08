from fastapi import Request, HTTPException, status
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
import uuid as uuid_pkg
from utils.security import verify_token
from schemas.user import TokenData

logger = logging.getLogger(__name__)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[TokenData]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                logger.warning("Invalid authentication scheme")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme."
                )

            token_data = self.verify_jwt(credentials.credentials)
            if not token_data:
                logger.warning("Invalid or expired token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token."
                )

            # Attach token data to request for use in route handlers
            request.state.user = token_data
            return token_data
        else:
            logger.warning("No credentials provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No credentials provided."
            )

    def verify_jwt(self, token: str) -> Optional[TokenData]:
        """Verify JWT token and return token data."""
        try:
            token_data = verify_token(token)
            return token_data
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None


# Alternative function-based approach for getting current user
async def get_current_user(request: Request) -> TokenData:
    """Extract current user from request state."""
    if hasattr(request.state, 'user') and request.state.user:
        return request.state.user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def get_current_user_id(request: Request) -> str:
    """Extract current user ID from request state and return as string."""
    if hasattr(request.state, 'user') and request.state.user:
        # Convert UUID to string for consistency with database operations
        return str(request.state.user.user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def verify_token(request: Request) -> str:
    """Verify the token and return the user ID as string."""
    # Get the authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No valid authorization header"
        )

    # Extract the token
    token = auth_header.split(" ")[1]

    # Verify the token using the security utility
    from utils.security import verify_token as verify_jwt_token
    token_data = verify_jwt_token(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # Return the user_id as string
    return str(token_data.user_id)