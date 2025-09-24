# Project Zero App

## Project Overview

This is a comprehensive e-commerce platform built using a modern microservices architecture. The application serves as a realistic demonstration environment for AI-powered DevOps and security analysis.

The project consists of a `frontend` application built with Next.js and TypeScript, and several backend `services` built with Python/FastAPI and Node.js/Express. Data is stored in PostgreSQL and Redis. The entire application is containerized using Docker and orchestrated with Docker Compose for local development.

## Building and Running

The project uses Docker Compose to manage the local development environment. The `Makefile` provides convenient scripts for common tasks.

**Key Commands:**

*   **Start all services:**
    ```bash
    make up
    ```
*   **Stop all services:**
    ```bash
    make down
    ```
*   **Build all services:**
    ```bash
    make build
    ```
*   **Restart all services:**
    ```bash
    make restart
    ```
*   **View logs for all services:**
    ```bash
    make logs
    ```
*   **View logs for a specific service:**
    ```bash
    make logs SERVICE=<service-name>
    ```
    (e.g., `make logs SERVICE=frontend`)
*   **Clean up the environment (removes containers, networks, and volumes):**
    ```bash
    make clean
    ```

**Accessing the application:**

*   **Frontend:** [http://localhost:3000](http://localhost:3000)
*   **API Documentation:**
    *   Auth Service: [http://localhost:8001/docs](http://localhost:8001/docs)
    *   Product Catalog: [http://localhost:8004/docs](http://localhost:8004/docs)
    *   Cart Service: [http://localhost:8007/docs](http://localhost:8007/docs)

## Development Conventions

The project follows **Specification-Driven Development (SDD)**. Specifications for each service are located in the `specs` directory.

**Project Structure:**

*   `.github/`: GitHub-related files, including prompts and Copilot instructions.
*   `frontend/`: The Next.js frontend application.
*   `services/`: The backend microservices.
*   `specs/`: Feature specifications.
*   `docker-compose.yml`: Defines the services, networks, and volumes for the local development environment.
*   `Makefile`: Provides convenient commands for managing the Docker Compose environment.
*   `README.md`: Detailed project documentation.
