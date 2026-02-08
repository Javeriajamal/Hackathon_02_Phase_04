# Quickstart Guide: Todo Chatbot Kubernetes Deployment

## Overview
This guide provides step-by-step instructions to deploy the Todo Chatbot application on a local Kubernetes cluster using Minikube and AI-assisted tools.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Disk Space**: 10GB free space for Docker images and Minikube
- **CPU**: 2 cores minimum, 4 cores recommended

### Required Software
1. **Docker Desktop** or **Docker Engine**
   - Version: 20.10 or higher
   - Enable Kubernetes (optional) or ensure Docker daemon running

2. **kubectl**
   - Version: 1.25 or higher
   - Match within one minor version of your cluster

3. **Minikube**
   - Version: 1.28 or higher
   - Install: `choco install minikube` (Windows) or `brew install minikube` (macOS)

4. **Helm**
   - Version: 3.10 or higher
   - Install: `choco install kubernetes-helm` (Windows) or `brew install helm` (macOS)

5. **AI-Assisted Tools**
   - Gordon (AI Docker Assistant)
   - kubectl-ai (AI Kubernetes Assistant)
   - Kagent (AI Kubernetes Agent)

## Installation Steps

### 1. Start Minikube Cluster
```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Verify cluster is running
kubectl cluster-info

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Prepare Phase-3 Application Files
```bash
# Navigate to the project directory containing Phase-3 code
cd C:\Hackathon-II\Phase-4

# Verify Phase-3 structure exists
ls -la frontend/ backend/
```

### 3. Containerize Applications Using AI Assistance
```bash
# Use Gordon to help create Dockerfiles
# First for frontend:
cd frontend/
# (Here you would engage Gordon to create/verify Dockerfile)
# Expected: Dockerfile created with multi-stage build for Next.js

# Then for backend:
cd ../backend/
# (Here you would engage Gordon to create/verify Dockerfile)
# Expected: Dockerfile created with multi-stage build for Node.js
```

### 4. Build Container Images
```bash
# Build frontend image
docker build -t todo-frontend:v1.0.0 .

# Build backend image
docker build -t todo-backend:v1.0.0 .

# Tag images for Minikube registry
docker tag todo-frontend:v1.0.0 localhost:5000/todo-frontend:v1.0.0
docker tag todo-backend:v1.0.0 localhost:5000/todo-backend:v1.0.0
```

### 5. Deploy Images to Minikube
```bash
# Load images into Minikube
minikube image load todo-frontend:v1.0.0
minikube image load todo-backend:v1.0.0

# Verify images are loaded
minikube ssh docker images | grep todo
```

### 6. Create Helm Charts
```bash
# Create directory for Helm charts
mkdir -p helm/{todo-frontend,todo-backend,todo-chatbot}

# Create frontend Helm chart
cd helm/todo-frontend
helm create todo-frontend

# Create backend Helm chart
cd ../todo-backend
helm create todo-backend

# Create umbrella chart
cd ../todo-chatbot
# Initialize umbrella chart (can use AI assistance)
```

### 7. Configure Helm Charts
```bash
# Update frontend chart values
# File: helm/todo-frontend/values.yaml
# Modify to use your images and set appropriate resources
```

### 8. Deploy Using Helm
```bash
# Deploy backend first
helm install todo-backend ./todo-backend

# Deploy frontend (after backend is ready)
helm install todo-frontend ./todo-frontend

# Or use umbrella chart for coordinated deployment
helm install todo-chatbot ./todo-chatbot
```

### 9. Verify Deployment
```bash
# Check all pods are running
kubectl get pods

# Check services are available
kubectl get services

# Check deployment status
kubectl get deployments

# Get Minikube IP for accessing services
minikube ip
```

## AI-Assisted Operations

### Using kubectl-ai for Troubleshooting
```bash
# Ask questions in natural language:
kubectl-ai "show me all pods that are not running"
kubectl-ai "why is deployment todo-frontend failing?"
kubectl-ai "show me logs from backend in the last 10 minutes"
```

### Using Kagent for Coordination
```bash
# High-level operations:
kagent "scale frontend to 3 replicas"
kagent "roll back backend deployment to previous version"
kagent "show me the health of the entire todo-chatbot system"
```

### Using Gordon for Docker Operations
```bash
# Image-related tasks:
gordon "optimize my Dockerfile for smaller image size"
gordon "show me security issues in my current images"
gordon "suggest improvements to my multi-stage build"
```

## Accessing the Application

### Via Minikube Dashboard
```bash
# Open Minikube dashboard in browser
minikube dashboard
```

### Via Service Port Forwarding
```bash
# Forward frontend service to local port
kubectl port-forward svc/todo-frontend 3000:80

# Access via http://localhost:3000
```

### Via Ingress (if configured)
```bash
# Get Minikube tunnel IP
minikube tunnel  # Run in separate terminal

# Access via Minikube IP (get with: minikube ip)
# Usually accessible at http://[MINIKUBE_IP]
```

## Verification Steps

### 1. Check Pod Status
```bash
kubectl get pods -o wide
# Expected: All pods in Running state
```

### 2. Check Service Connectivity
```bash
kubectl get services
# Expected: Services showing external IPs (pending or actual)
```

### 3. Verify Application Functionality
```bash
# Test the Todo Chatbot functionality:
# - Navigate to the frontend URL
# - Verify login functionality works as in Phase-3
# - Verify todo creation, completion, and deletion
# - Check that all Phase-3 features are available
```

### 4. Check Resource Utilization
```bash
kubectl top nodes
kubectl top pods
# Expected: Resources within set limits and requests
```

## Common Issues and Solutions

### Issue: Images not loading in Minikube
**Solution**:
```bash
# Ensure images are loaded properly
minikube image load <image-name>:<tag>
# Check if they're present
minikube ssh -- docker images
```

### Issue: Services not accessible
**Solution**:
```bash
# Check service type and configuration
kubectl describe service <service-name>
# Use port forwarding if needed
kubectl port-forward service/<service-name> <local-port>:<service-port>
```

### Issue: Pod crashes or fails to start
**Solution**:
```bash
# Check pod status and events
kubectl describe pod <pod-name>
# Check logs
kubectl logs <pod-name>
# Use AI assistance
kubectl-ai "analyze logs from pod <pod-name>"
```

## Scaling and Management

### Scale Frontend
```bash
# Using kubectl
kubectl scale deployment todo-frontend --replicas=3

# Using AI tools
kubectl-ai "scale frontend deployment to 3 replicas"
```

### Update Configuration
```bash
# Update with new values
helm upgrade todo-chatbot ./todo-chatbot -f custom-values.yaml

# Or use AI assistance
kagent "upgrade todo-chatbot with new configuration from values.yaml"
```

### Rollback Deployment
```bash
# Check revision history
helm history todo-chatbot

# Rollback to previous version
helm rollback todo-chatbot 1
```

## Cleanup

### Uninstall Helm Release
```bash
helm uninstall todo-chatbot
helm uninstall todo-frontend
helm uninstall todo-backend
```

### Stop Minikube
```bash
minikube stop
```

### Delete Minikube Cluster (if needed)
```bash
minikube delete
```

## Next Steps

1. **Customize Values**: Adjust `values.yaml` files for your specific requirements
2. **Environment Promotion**: Adapt charts for different environments
3. **Monitoring Setup**: Implement Prometheus/Grafana for monitoring
4. **CI/CD Pipeline**: Set up automated deployment pipeline
5. **Security Hardening**: Implement network policies and security best practices