# Data Model: Phase-4 Cloud-Native Todo Chatbot Deployment

## Overview
This document describes the data models relevant to the Kubernetes deployment of the Todo Chatbot application. The models include both application-level data structures (inherited from Phase-3) and deployment-level configuration structures introduced in Phase-4.

## Application-Level Data Models

### Todo Entity (from Phase-3)
**Description**: Core entity representing a todo item in the system

**Fields**:
- `id` (string): Unique identifier for the todo item
- `title` (string): Title of the todo item (required, max 255 characters)
- `description` (string): Optional detailed description
- `completed` (boolean): Completion status, default false
- `createdAt` (timestamp): Creation timestamp
- `updatedAt` (timestamp): Last update timestamp
- `userId` (string): Owner of the todo item (for authentication)

**Validation Rules**:
- Title is required and must be between 1-255 characters
- createdAt and updatedAt are automatically managed
- userId must correspond to a valid authenticated user

### User Entity (from Phase-3)
**Description**: Represents authenticated users of the Todo Chatbot

**Fields**:
- `id` (string): Unique identifier for the user
- `email` (string): User's email address (unique, required)
- `passwordHash` (string): Hashed password (required)
- `createdAt` (timestamp): Account creation timestamp
- `lastLoginAt` (timestamp): Timestamp of last login

**Validation Rules**:
- Email must be valid and unique
- Password must meet security requirements
- Automatic timestamps managed by system

## Deployment-Level Configuration Models

### Kubernetes Deployment Configuration
**Description**: Configuration structure for Kubernetes deployment resources

**Fields**:
- `replicas` (integer): Number of pod replicas, default 1
- `image` (string): Container image reference with tag
- `imagePullPolicy` (string): Image pull policy (Always, IfNotPresent, Never)
- `resources.requests.cpu` (string): CPU request (e.g., "100m")
- `resources.requests.memory` (string): Memory request (e.g., "128Mi")
- `resources.limits.cpu` (string): CPU limit (e.g., "500m")
- `resources.limits.memory` (string): Memory limit (e.g., "256Mi")
- `env` (array): Environment variables as key-value pairs
- `ports` (array): Container port configurations

### Kubernetes Service Configuration
**Description**: Configuration structure for Kubernetes service resources

**Fields**:
- `type` (string): Service type (ClusterIP, NodePort, LoadBalancer)
- `port` (integer): Service port exposed externally
- `targetPort` (integer): Port on target pods
- `selector` (object): Labels to match target pods
- `name` (string): Service name

### Helm Values Configuration
**Description**: Configuration structure for Helm chart value customization

**Fields**:
- `global.imageRegistry` (string): Global image registry override
- `global.storageClass` (string): Default storage class for volumes
- `frontend.enabled` (boolean): Whether to deploy frontend component
- `frontend.image.repository` (string): Frontend image repository
- `frontend.image.tag` (string): Frontend image tag
- `frontend.service.type` (string): Frontend service type
- `frontend.service.port` (integer): Frontend service port
- `frontend.resources` (object): Frontend resource constraints
- `backend.enabled` (boolean): Whether to deploy backend component
- `backend.image.repository` (string): Backend image repository
- `backend.image.tag` (string): Backend image tag
- `backend.service.type` (string): Backend service type
- `backend.service.port` (integer): Backend service port
- `backend.database.url` (string): Database connection URL
- `backend.jwt.secret` (string): JWT secret for authentication
- `backend.resources` (object): Backend resource constraints
- `ingress.enabled` (boolean): Whether to create ingress resource
- `ingress.className` (string): Ingress class name
- `ingress.hosts` (array): Hostnames for ingress routing

### Container Configuration
**Description**: Docker container configuration parameters

**Fields**:
- `baseImage` (string): Base image for multi-stage build
- `buildArgs` (object): Arguments passed to build process
- `workingDir` (string): Working directory inside container
- `exposedPorts` (array): Ports exposed by container
- `healthCheck` (object): Health check configuration (cmd, interval, timeout)
- `user` (string): User to run container processes as
- `volumes` (array): Volume mount configurations

## State Transitions

### Todo Item State Transitions
- **Created**: New todo item with `completed: false`
- **Completed**: User marks todo as complete → `completed: true`
- **Reopened**: User reopens todo → `completed: false`
- **Updated**: Any field except `id` and `createdAt` can be modified
- **Deleted**: Todo item is removed from system

### Pod Lifecycle States (Kubernetes)
- **Pending**: Pod accepted by cluster but not yet running
- **Running**: Pod scheduled and all containers running
- **Succeeded**: All containers terminated successfully
- **Failed**: At least one container terminated with failure
- **Unknown**: State cannot be obtained

## Relationships

### Todo to User Relationship
- **Type**: Many-to-One
- **Description**: Multiple todos can belong to a single user
- **Constraint**: Each todo must have a valid `userId` reference
- **Cascade Behavior**: Deleting user deletes all associated todos

### Frontend to Backend Relationship
- **Type**: Dependency
- **Description**: Frontend communicates with backend API
- **Configuration**: Backend service URL configured in frontend environment
- **Network**: Communication through Kubernetes services

## Validation Rules

### Application Validation (from Phase-3)
- Todo titles must be 1-255 characters
- User emails must follow RFC 5322 format
- Passwords must meet minimum security requirements
- JWT tokens must be properly signed and not expired

### Deployment Validation (Phase-4)
- Resource requests must not exceed cluster limits
- Service ports must be available and not conflict
- Image pull secrets must be valid for private registries
- Persistent volume claims must have sufficient capacity
- Network policies must allow required inter-service communication

## Schema Evolution Considerations

### Backward Compatibility
- Existing API endpoints from Phase-3 must remain compatible
- Database schemas unchanged during deployment
- Authentication mechanisms preserved
- User data integrity maintained during deployment

### Future Extensions
- Schema designed to accommodate future features
- Flexible configuration patterns for different environments
- Extensible Helm chart structure for optional components
- Modular deployment design for independent scaling