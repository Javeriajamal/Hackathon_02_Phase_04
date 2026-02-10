# Phase-4: Cloud-Native Deployment — Todo Chatbot Application

A production-ready cloud-native deployment of a full-stack Todo Chatbot application on Kubernetes using Docker, Helm, and Minikube. This project demonstrates modern DevOps practices including containerization, orchestration, and infrastructure-as-code.

## 📋 Project Overview

Phase-4 represents the cloud-native evolution of the Todo Chatbot application, transforming a traditional web application into a containerized, orchestrated system running on Kubernetes. This phase focuses on:

- **Containerization**: Packaging frontend and backend applications as Docker images
- **Orchestration**: Deploying services on Kubernetes with proper resource management
- **Infrastructure as Code**: Using Helm charts for reproducible deployments
- **Service Mesh**: Implementing microservices communication patterns
- **Local Development**: Running a production-like environment on Minikube

The deployment maintains 100% feature parity with Phase-3 while adding cloud-native capabilities for scalability, resilience, and portability.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                        │
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │   Frontend   │         │   Backend    │                │
│  │   (Next.js)  │────────▶│   (FastAPI)  │                │
│  │  Port: 3000  │         │  Port: 8000  │                │
│  └──────────────┘         └──────┬───────┘                │
│         │                         │                         │
│         │                         ▼                         │
│         │                  ┌──────────────┐                │
│         │                  │  PostgreSQL  │                │
│         │                  │  Port: 5432  │                │
│         │                  └──────────────┘                │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐                                          │
│  │   NodePort   │                                          │
│  │  :31020      │                                          │
│  └──────────────┘                                          │
│         │                                                   │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼
   http://127.0.0.1:51532
   (External Access)
```

**Communication Flow:**
1. User accesses frontend via NodePort service
2. Frontend communicates with backend via ClusterIP service
3. Backend connects to PostgreSQL via ClusterIP service
4. All services use Kubernetes DNS for service discovery

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Next.js 14.2.35 | Server-side rendered React application |
| **Backend** | FastAPI (Python 3.11) | RESTful API with async support |
| **Database** | PostgreSQL 18.1.0 | Relational database for data persistence |
| **Containerization** | Docker | Application packaging and isolation |
| **Orchestration** | Kubernetes (Minikube) | Container orchestration and management |
| **Package Manager** | Helm 4.1.0 | Kubernetes application deployment |
| **Container Runtime** | Docker Desktop | Local container execution |

## 📁 Folder Structure

```
Phase-4/
├── backend/                    # FastAPI backend application
│   ├── Dockerfile             # Backend container definition
│   ├── requirements.txt       # Python dependencies
│   ├── main.py               # Application entry point
│   └── services/             # Business logic
├── frontend/                  # Next.js frontend application
│   ├── Dockerfile            # Frontend container definition
│   ├── package.json          # Node.js dependencies
│   └── app/                  # Next.js app router
├── backend-chart/            # Backend Helm chart
│   ├── Chart.yaml           # Chart metadata
│   ├── values.yaml          # Configuration values
│   └── templates/           # Kubernetes manifests
├── frontend-chart/           # Frontend Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── helm/
│   └── todo-chatbot/        # Umbrella Helm chart
│       ├── Chart.yaml       # Coordinates subcharts
│       └── values.yaml      # Global configuration
├── specs/                    # Specification documents
│   └── 1-cloud-native-deployment/
│       ├── spec.md          # Feature specification
│       ├── plan.md          # Implementation plan
│       └── tasks.md         # Task breakdown
└── history/
    └── prompts/             # Prompt History Records (PHRs)
```

## ✅ Prerequisites

Before starting, ensure you have the following installed:

### Required Software

- **Docker Desktop** (v29.2.0 or later)
  - Download: https://www.docker.com/products/docker-desktop
  - Ensure Docker daemon is running

- **Minikube** (v1.38.0 or later)
  - Installation: https://minikube.sigs.k8s.io/docs/start/
  - Driver: Docker

- **kubectl** (Kubernetes CLI)
  - Installation: https://kubernetes.io/docs/tasks/tools/
  - Should be configured to use Minikube context

- **Helm** (v4.1.0 or later)
  - Installation: https://helm.sh/docs/intro/install/

### System Requirements

- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: Minimum 4GB available for Minikube
- **CPU**: 4 cores recommended
- **Disk**: 20GB free space

### Verification Commands

```bash
# Verify Docker
docker --version

# Verify Minikube
minikube version

# Verify kubectl
kubectl version --client

# Verify Helm
helm version
```

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Phase-4
```

### Step 2: Start Minikube

```bash
# Start Minikube cluster with appropriate resources
minikube start --cpus=4 --memory=3584 --driver=docker

# Verify cluster is running
minikube status

# Check nodes
kubectl get nodes
```

### Step 3: Build Docker Images

```bash
# Build frontend image
cd frontend
docker build -t todo-frontend:v1.0.0 .

# Build backend image
cd ../backend
docker build -t todo-backend:v1.0.2 .

# Verify images
docker images | grep todo
```

### Step 4: Load Images into Minikube

```bash
# Load frontend image
minikube image load todo-frontend:v1.0.0

# Load backend image
minikube image load todo-backend:v1.0.2

# Verify images in Minikube
minikube image ls | grep todo
```

### Step 5: Add Helm Repository

```bash
# Add Bitnami repository for PostgreSQL
helm repo add bitnami https://charts.bitnami.com/bitnami

# Update Helm repositories
helm repo update
```

### Step 6: Deploy PostgreSQL Database

```bash
# Install PostgreSQL using Bitnami Helm chart
helm install postgres bitnami/postgresql \
  --set auth.username=user \
  --set auth.password=password \
  --set auth.database=todo_db \
  --set primary.service.type=ClusterIP \
  --set primary.persistence.enabled=false

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgresql --timeout=300s

# Verify PostgreSQL is running
kubectl get pods -l app.kubernetes.io/name=postgresql
```

### Step 7: Deploy Application with Helm

```bash
# Navigate to Helm chart directory
cd helm/todo-chatbot

# Update chart dependencies
helm dependency update

# Install the umbrella chart
helm install todo-chatbot .

# Verify deployment
kubectl get pods
kubectl get services
```

## 🌐 Running the Application

### Access the Frontend

```bash
# Get the frontend service URL
minikube service todo-chatbot-frontend-chart --url
```

The command will output a URL like: `http://127.0.0.1:51532`

Open this URL in your browser to access the Todo Chatbot application.

### Verify All Services

```bash
# Check all pods are running
kubectl get pods

# Expected output:
# NAME                                          READY   STATUS    RESTARTS   AGE
# postgres-postgresql-0                         1/1     Running   0          10m
# todo-chatbot-backend-chart-6758848bf9-xxxxx   1/1     Running   0          5m
# todo-chatbot-frontend-chart-9df644499-xxxxx   1/1     Running   0          5m

# Check all services
kubectl get services

# Check deployments
kubectl get deployments
```

### View Application Logs

```bash
# Frontend logs
kubectl logs -l app.kubernetes.io/name=frontend-chart --tail=50

# Backend logs
kubectl logs -l app.kubernetes.io/name=backend-chart --tail=50

# PostgreSQL logs
kubectl logs postgres-postgresql-0 --tail=50
```

## 📦 Deployment Details

### Docker Images

| Image | Tag | Size | Purpose |
|-------|-----|------|---------|
| `docker.io/library/todo-frontend` | v1.0.0 | ~200MB | Next.js frontend application |
| `docker.io/library/todo-backend` | v1.0.2 | ~300MB | FastAPI backend with dependencies |
| `bitnami/postgresql` | latest | ~150MB | PostgreSQL database |

### Helm Charts

**Umbrella Chart: `todo-chatbot`**
- Version: 0.1.0
- Coordinates frontend and backend subcharts
- Manages global configuration

**Frontend Chart: `frontend-chart`**
- Version: 0.1.0
- Deployment: 1 replica
- Service: ClusterIP → NodePort (for external access)
- Resources: 128Mi memory request, 256Mi limit

**Backend Chart: `backend-chart`**
- Version: 0.1.0
- Deployment: 1 replica
- Service: ClusterIP (internal only)
- Resources: 128Mi memory request, 512Mi limit

### Kubernetes Services

| Service Name | Type | Port | Target |
|-------------|------|------|--------|
| `todo-chatbot-frontend-chart` | NodePort | 3000:31020 | Frontend pods |
| `todo-chatbot-backend-chart` | ClusterIP | 8000 | Backend pods |
| `postgres-postgresql` | ClusterIP | 5432 | PostgreSQL pod |

### Resource Configuration

```yaml
# Frontend Resources
requests:
  memory: "128Mi"
  cpu: "100m"
limits:
  memory: "256Mi"
  cpu: "200m"

# Backend Resources
requests:
  memory: "128Mi"
  cpu: "100m"
limits:
  memory: "512Mi"
  cpu: "300m"
```

## 🔧 Issues Resolved

During the deployment process, several issues were identified and resolved:

### 1. Missing Python Dependency
**Issue**: Backend crashed with `ModuleNotFoundError: No module named 'email_validator'`

**Solution**: Added `email-validator` to `backend/requirements.txt`

### 2. F-String Syntax Error
**Issue**: Python syntax error in `backend/services/chat_service.py:161`

**Solution**: Fixed quote mismatch in f-string from `result["tasks"]` to `result['tasks']`

### 3. Database Driver Mismatch
**Issue**: SQLAlchemy async engine required async driver but received synchronous driver

**Solution**: Changed database URL from `postgresql://` to `postgresql+asyncpg://`

### 4. Missing Database Service
**Issue**: Backend couldn't connect to PostgreSQL (service didn't exist)

**Solution**: Deployed PostgreSQL using Bitnami Helm chart before application deployment

### 5. Service Name Mismatch
**Issue**: Backend configured to connect to `postgres:5432` but actual service was `postgres-postgresql:5432`

**Solution**: Updated `backend-chart/values.yaml` with correct service name

### 6. Image Caching
**Issue**: Kubernetes used cached old images despite rebuilds

**Solution**: Incremented image tags (v1.0.0 → v1.0.1 → v1.0.2) to force fresh pulls

## ✔️ Validation & Testing

### Health Checks

```bash
# Check pod health
kubectl get pods

# Describe pods for detailed status
kubectl describe pod -l app.kubernetes.io/instance=todo-chatbot

# Check pod readiness and liveness probes
kubectl get pods -o wide
```

### Service Connectivity

```bash
# Test backend API from within cluster
kubectl run curl-test --image=curlimages/curl -i --rm --restart=Never -- \
  curl -s http://todo-chatbot-backend-chart:8000/

# Expected output: {"message":"Welcome to the Todo Chatbot API"}

# Test PostgreSQL connection
kubectl run psql-test --image=postgres:latest -i --rm --restart=Never -- \
  psql -h postgres-postgresql -U user -d todo_db -c "SELECT version();"
```

### Application Functionality

1. **Access Frontend**: Open `http://127.0.0.1:51532` in browser
2. **Test Registration**: Create a new user account
3. **Test Login**: Authenticate with created credentials
4. **Test Todo CRUD**: Create, read, update, and delete todos
5. **Test Chat**: Interact with the AI chatbot feature

### Resource Usage

```bash
# Enable metrics server (if not already enabled)
minikube addons enable metrics-server

# Wait for metrics to be available (30-60 seconds)
sleep 60

# Check resource usage
kubectl top pods
kubectl top nodes
```

## 💡 Key Learnings

### DevOps Best Practices

1. **Infrastructure First**: Deploy infrastructure components (database) before application services to avoid connection failures

2. **Async Driver Requirements**: When using SQLAlchemy with async engines, ensure the database URL uses async-compatible drivers (`asyncpg` for PostgreSQL)

3. **Image Versioning Strategy**: Use semantic versioning for Docker images and increment versions to force Kubernetes to pull updated images

4. **Health Check Configuration**: Liveness and readiness probes need appropriate delays and timeouts for services with longer startup times

5. **Service Discovery**: Kubernetes DNS follows the pattern `<service-name>.<namespace>.svc.cluster.local` for cross-service communication

### Kubernetes Insights

- **ClusterIP vs NodePort**: Use ClusterIP for internal services and NodePort/LoadBalancer only for external access
- **Resource Limits**: Always set resource requests and limits to prevent resource starvation
- **Pod Restart Policies**: Understand CrashLoopBackOff and how to debug failing containers
- **Helm Dependencies**: Umbrella charts simplify multi-service deployments with coordinated configuration

### Debugging Techniques

- Use `kubectl logs` to inspect application output
- Use `kubectl describe pod` to see events and error messages
- Use `kubectl exec` to access running containers for troubleshooting
- Check service endpoints with `kubectl get endpoints`

## 🚀 Future Improvements

### Production Readiness

- [ ] **Persistent Storage**: Add PersistentVolumeClaims for PostgreSQL data persistence
- [ ] **Database Migrations**: Implement Alembic or similar tool for schema version control
- [ ] **Secrets Management**: Use Kubernetes Secrets or external secret managers (Vault, AWS Secrets Manager)
- [ ] **TLS/SSL**: Configure ingress with TLS certificates for HTTPS
- [ ] **Ingress Controller**: Replace NodePort with proper Ingress for production routing

### Observability

- [ ] **Monitoring**: Deploy Prometheus and Grafana for metrics collection
- [ ] **Logging**: Implement centralized logging with ELK stack or Loki
- [ ] **Tracing**: Add distributed tracing with Jaeger or Zipkin
- [ ] **Alerting**: Configure alerting rules for critical failures

### Scalability

- [ ] **Horizontal Pod Autoscaling**: Configure HPA based on CPU/memory metrics
- [ ] **Database Replication**: Set up PostgreSQL read replicas for load distribution
- [ ] **Caching Layer**: Add Redis for session management and API caching
- [ ] **CDN Integration**: Serve static assets through CDN

### Security

- [ ] **Network Policies**: Implement Kubernetes NetworkPolicies to restrict pod communication
- [ ] **Pod Security Standards**: Apply security contexts and pod security policies
- [ ] **Image Scanning**: Integrate Trivy or Clair for vulnerability scanning
- [ ] **RBAC**: Configure Role-Based Access Control for cluster resources

### CI/CD

- [ ] **GitHub Actions**: Automate Docker builds and Helm deployments
- [ ] **GitOps**: Implement ArgoCD or Flux for declarative deployments
- [ ] **Automated Testing**: Add integration and e2e tests in pipeline
- [ ] **Rollback Strategy**: Implement blue-green or canary deployments

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the project structure
4. Test your changes locally with Minikube
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards

- Follow existing code style and formatting
- Update documentation for any changed functionality
- Add tests for new features
- Ensure all pods start successfully before submitting PR

### Reporting Issues

When reporting issues, please include:
- Kubernetes version (`kubectl version`)
- Minikube version (`minikube version`)
- Error logs (`kubectl logs <pod-name>`)
- Steps to reproduce the issue

## 📄 License

This project is part of the "Evolution of Todo" hackathon series demonstrating cloud-native deployment practices.

For licensing information, please contact the project maintainers.

---

## 📞 Support

For questions or support:
- Create an issue in the GitHub repository
- Review the [Kubernetes documentation](https://kubernetes.io/docs/)
- Check [Helm documentation](https://helm.sh/docs/)
- Consult [Minikube troubleshooting guide](https://minikube.sigs.k8s.io/docs/handbook/troubleshooting/)

---

**Built with ❤️ using Kubernetes, Docker, and Helm**
