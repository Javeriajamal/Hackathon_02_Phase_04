# Phase-2 Backend CLAUDE.md - FastAPI Implementation

## Project Overview

This file provides implementation guidelines for the Phase-2 backend using FastAPI, SQLModel, and Neon PostgreSQL. The backend serves as the API layer for the Evolution of Todo project, handling all business logic, data persistence, and authentication.

## Technology Stack

### Core Technologies
- **Framework**: FastAPI (Python 3.9+)
- **ORM**: SQLModel (combining SQLAlchemy and Pydantic)
- **Database**: Neon Serverless PostgreSQL
- **Validation**: Pydantic models for request/response validation
- **Authentication**: JWT token verification with Better Auth integration

### Project Structure
```
backend/
├── main.py                 # Application entry point
├── database.py            # Database connection management
├── models/                # SQLModel data models
│   ├── __init__.py
│   ├── user.py            # User model
│   └── task.py            # Task model
├── schemas/               # Pydantic schemas for validation
│   ├── __init__.py
│   ├── user.py
│   └── task.py
├── routers/               # API route definitions
│   ├── __init__.py
│   ├── auth.py            # Authentication endpoints
│   └── tasks.py           # Task management endpoints
├── services/              # Business logic services
│   ├── __init__.py
│   ├── auth_service.py
│   └── task_service.py
├── middleware/            # Request middleware
│   ├── __init__.py
│   └── auth.py           # JWT verification middleware
└── utils/                 # Utility functions
    ├── __init__.py
    └── security.py       # Password hashing, token utilities
```

## API Conventions

### RESTful Design Principles
- Use standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Use plural nouns for resource endpoints
- Use nested routes for relationships (e.g., `/api/users/{id}/tasks`)
- Return appropriate HTTP status codes:
  - 200: Success for GET, PUT, PATCH
  - 201: Created for POST
  - 204: No Content for successful DELETE
  - 400: Bad Request for validation errors
  - 401: Unauthorized for authentication failures
  - 403: Forbidden for authorization failures
  - 404: Not Found for missing resources
  - 500: Internal Server Error for server issues

### Endpoint Naming
- Use `/api/v1/` prefix for all endpoints
- Use kebab-case for URL paths
- Use consistent parameter naming (e.g., `{user_id}`, `{task_id}`)
- Include versioning in the URL path

### Response Format
- Use consistent response structure
- Include `detail` field for error messages
- Use `data` field for successful responses when needed
- Include `timestamp` for error responses

## Pydantic Usage

### Request/Response Models
- Create separate Pydantic models for requests and responses
- Use `BaseModel` for shared fields
- Use `Create` suffix for creation models (e.g., `TaskCreate`)
- Use `Update` suffix for update models (e.g., `TaskUpdate`)
- Use `Public` suffix for models sent to clients (e.g., `TaskPublic`)

### Validation
- Use Pydantic field validators for custom validation
- Implement `Config` class with `orm_mode=True` for database models
- Use `Field` for custom validation constraints
- Handle validation errors gracefully with proper error responses

## JWT Authentication

### Token Verification
- Implement middleware to verify JWT tokens
- Extract user ID from token claims
- Return 401 for invalid/missing tokens
- Validate token expiration
- Ensure all protected endpoints require authentication

### User Isolation
- Always verify that users can only access their own data
- Include user ID in database queries
- Return 403 for cross-user access attempts
- Implement proper authorization checks

## Database Connection

### Environment Variables
- Use `DATABASE_URL` environment variable for database connection
- Support Neon PostgreSQL connection string format
- Implement connection pooling configuration
- Handle environment-specific configurations

### Connection Management
- Use SQLAlchemy async engine for async operations
- Implement proper session management
- Handle connection lifecycle (create, close, error handling)
- Use dependency injection for database sessions

### SQLModel Best Practices
- Use `SQLModel` as base class for all models
- Implement proper relationships between models
- Use UUID primary keys
- Include proper indexes for performance
- Implement soft deletes if needed

## Error Handling

### Global Exception Handlers
- Implement handlers for common exceptions
- Return consistent error response format
- Log errors appropriately
- Don't expose internal error details to clients

### Validation Errors
- Handle Pydantic validation errors
- Return 400 status with detailed error information
- Use FastAPI's automatic validation error handling
- Provide meaningful error messages

## Development Guidelines

### Code Organization
- Follow FastAPI best practices for dependency injection
- Separate concerns into models, schemas, routers, and services
- Use async/await for I/O operations
- Implement proper logging

### Testing
- Write unit tests for all business logic
- Implement integration tests for API endpoints
- Use pytest for testing framework
- Mock external dependencies for testing

### Security
- Validate and sanitize all inputs
- Use parameterized queries to prevent SQL injection
- Implement rate limiting for public endpoints
- Use HTTPS in production

## Spec-Driven Development

### Agentic Development Constraints
- All code must be AI-generated based on specifications
- Follow spec-driven development methodology
- No manual coding allowed - use skill agents
- Ensure all functionality matches feature specifications
- Maintain traceability from specs to implementation

### Implementation Workflow
1. Generate specification from feature requirements
2. Create implementation plan based on spec
3. Generate tasks from plan
4. Execute with appropriate skill agents
5. Verify implementation matches specification

## Performance Considerations

### Query Optimization
- Use proper indexing strategies
- Implement pagination for large datasets
- Use select-in-load for relationship queries
- Avoid N+1 query problems

### Caching
- Implement caching for frequently accessed data
- Use appropriate cache invalidation strategies
- Consider Redis for distributed caching

This CLAUDE.md file serves as the authoritative guide for backend development in Phase-2, ensuring consistency and adherence to project standards while following spec-driven, agentic development principles.