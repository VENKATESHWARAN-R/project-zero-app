#!/bin/bash

# Project Zero App Authentication Service Deployment Script
# Supports local development, Docker, and cloud deployment

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="auth-service"
IMAGE_NAME="project-zero/${SERVICE_NAME}"
VERSION="${VERSION:-1.0.0}"
ENVIRONMENT="${ENVIRONMENT:-development}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_deps=()

    if ! command_exists python3; then
        missing_deps+=("python3")
    fi

    if ! command_exists uv; then
        missing_deps+=("uv")
    fi

    if [[ ${#missing_deps[@]} -ne 0 ]]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Please install missing dependencies and try again"
        exit 1
    fi

    log_success "All prerequisites satisfied"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."

    cd "$SCRIPT_DIR"

    # Copy environment file if it doesn't exist
    if [[ ! -f .env ]]; then
        if [[ -f .env.example ]]; then
            cp .env.example .env
            log_warning "Created .env from .env.example. Please review and update values."
        else
            log_error ".env.example not found"
            exit 1
        fi
    fi

    # Install dependencies
    log_info "Installing Python dependencies..."
    uv sync

    log_success "Environment setup complete"
}

# Run tests
run_tests() {
    log_info "Running tests..."

    cd "$SCRIPT_DIR"

    # Run the test suite
    if uv run pytest tests/ -v --tb=short; then
        log_success "All tests passed"
    else
        log_error "Some tests failed"
        return 1
    fi
}

# Local development deployment
deploy_local() {
    log_info "Starting local development deployment..."

    check_prerequisites
    setup_environment

    # Optional: Run tests
    if [[ "${RUN_TESTS:-true}" == "true" ]]; then
        run_tests || {
            log_warning "Tests failed, but continuing with deployment"
        }
    fi

    log_info "Starting authentication service on http://localhost:8001"
    log_info "API Documentation: http://localhost:8001/docs"
    log_info "Health Check: http://localhost:8001/health"

    cd "$SCRIPT_DIR"
    uv run uvicorn main:app --host 0.0.0.0 --port 8001 --reload
}

# Docker deployment
deploy_docker() {
    log_info "Starting Docker deployment..."

    if ! command_exists docker; then
        log_error "Docker is not installed or not running"
        exit 1
    fi

    cd "$SCRIPT_DIR"

    # Build Docker image
    log_info "Building Docker image: ${IMAGE_NAME}:${VERSION}"
    docker build -t "${IMAGE_NAME}:${VERSION}" -t "${IMAGE_NAME}:latest" .

    # Stop existing container if running
    if docker ps -q -f name="${SERVICE_NAME}" | grep -q .; then
        log_info "Stopping existing container..."
        docker stop "${SERVICE_NAME}" >/dev/null
        docker rm "${SERVICE_NAME}" >/dev/null
    fi

    # Run new container
    log_info "Starting new container..."
    docker run -d \
        --name "${SERVICE_NAME}" \
        -p 8001:8001 \
        -e DATABASE_URL="${DATABASE_URL:-sqlite:///./auth.db}" \
        -e JWT_SECRET_KEY="${JWT_SECRET_KEY:-dev-secret-change-in-production}" \
        -e ENVIRONMENT="${ENVIRONMENT}" \
        "${IMAGE_NAME}:${VERSION}"

    # Wait for service to be ready
    log_info "Waiting for service to be ready..."
    for i in {1..30}; do
        if curl -f http://localhost:8001/health >/dev/null 2>&1; then
            log_success "Service is ready!"
            break
        fi
        if [[ $i -eq 30 ]]; then
            log_error "Service failed to start within 30 seconds"
            docker logs "${SERVICE_NAME}"
            exit 1
        fi
        sleep 1
    done

    log_success "Docker deployment complete"
    log_info "Service available at: http://localhost:8001"
    log_info "View logs: docker logs ${SERVICE_NAME}"
    log_info "Stop service: docker stop ${SERVICE_NAME}"
}

# Docker Compose deployment
deploy_compose() {
    log_info "Starting Docker Compose deployment..."

    if ! command_exists docker-compose && ! command_exists docker; then
        log_error "Docker Compose is not available"
        exit 1
    fi

    cd "$SCRIPT_DIR"

    # Stop existing services
    log_info "Stopping existing services..."
    docker-compose down >/dev/null 2>&1 || true

    # Start services
    log_info "Starting services with Docker Compose..."
    if command_exists docker-compose; then
        docker-compose up -d
    else
        docker compose up -d
    fi

    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 10

    for i in {1..30}; do
        if curl -f http://localhost:8001/health >/dev/null 2>&1; then
            log_success "Services are ready!"
            break
        fi
        if [[ $i -eq 30 ]]; then
            log_error "Services failed to start within 30 seconds"
            docker-compose logs
            exit 1
        fi
        sleep 2
    done

    log_success "Docker Compose deployment complete"
    log_info "Services:"
    log_info "  - Auth Service: http://localhost:8001"
    log_info "  - PostgreSQL: localhost:5432"
    log_info "  - Redis: localhost:6379"
    log_info "View logs: docker-compose logs -f"
    log_info "Stop services: docker-compose down"
}

# GCP Cloud Run deployment
deploy_gcp_cloudrun() {
    log_info "Starting GCP Cloud Run deployment..."

    if ! command_exists gcloud; then
        log_error "Google Cloud SDK (gcloud) is not installed"
        exit 1
    fi

    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with Google Cloud. Run: gcloud auth login"
        exit 1
    fi

    # Get project ID
    PROJECT_ID=$(gcloud config get-value project)
    if [[ -z "$PROJECT_ID" ]]; then
        log_error "No Google Cloud project set. Run: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi

    REGION="${GCP_REGION:-us-central1}"
    SERVICE_ACCOUNT="${GCP_SERVICE_ACCOUNT:-${SERVICE_NAME}@${PROJECT_ID}.iam.gserviceaccount.com}"

    log_info "Deploying to project: $PROJECT_ID"
    log_info "Region: $REGION"

    cd "$SCRIPT_DIR"

    # Build and push to Container Registry
    log_info "Building and pushing container..."
    gcloud builds submit --tag gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${VERSION}

    # Deploy to Cloud Run
    log_info "Deploying to Cloud Run..."
    gcloud run deploy ${SERVICE_NAME} \
        --image gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${VERSION} \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --port 8001 \
        --memory 512Mi \
        --cpu 1 \
        --max-instances 10 \
        --set-env-vars ENVIRONMENT=production \
        --set-env-vars DATABASE_URL="${DATABASE_URL}" \
        --set-env-vars JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
        --service-account "${SERVICE_ACCOUNT}"

    # Get service URL
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

    log_success "GCP Cloud Run deployment complete"
    log_info "Service URL: ${SERVICE_URL}"
    log_info "Health check: ${SERVICE_URL}/health"
    log_info "API docs: ${SERVICE_URL}/docs"
}

# Show usage information
show_usage() {
    echo "Project Zero App Authentication Service Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  local          Start local development server"
    echo "  docker         Deploy using Docker"
    echo "  compose        Deploy using Docker Compose"
    echo "  gcp-cloudrun   Deploy to Google Cloud Run"
    echo "  test           Run tests only"
    echo "  setup          Setup environment only"
    echo "  help           Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  ENVIRONMENT    Deployment environment (development/staging/production)"
    echo "  VERSION        Image version tag (default: 1.0.0)"
    echo "  RUN_TESTS      Run tests before deployment (default: true)"
    echo "  GCP_REGION     GCP region for Cloud Run (default: us-central1)"
    echo "  DATABASE_URL   Database connection string"
    echo "  JWT_SECRET_KEY JWT secret key"
    echo ""
    echo "Examples:"
    echo "  $0 local                    # Start local development"
    echo "  $0 docker                   # Deploy with Docker"
    echo "  VERSION=1.1.0 $0 docker     # Deploy specific version"
    echo "  ENVIRONMENT=production $0 gcp-cloudrun  # Deploy to GCP"
}

# Main script logic
main() {
    case "${1:-help}" in
        local)
            deploy_local
            ;;
        docker)
            deploy_docker
            ;;
        compose)
            deploy_compose
            ;;
        gcp-cloudrun)
            deploy_gcp_cloudrun
            ;;
        test)
            check_prerequisites
            setup_environment
            run_tests
            ;;
        setup)
            check_prerequisites
            setup_environment
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"