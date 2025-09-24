COMPOSE_FILE ?= docker-compose.yml
DOCKER_COMPOSE := docker compose -f $(COMPOSE_FILE)
SERVICE ?=

.PHONY: up down build restart logs ps watch clean start stop

start: up

up:
	@echo "Starting services $(if $(SERVICE),($(SERVICE)),(all)) via docker compose..."
	@DOCKER_BUILDKIT=1 $(DOCKER_COMPOSE) up -d $(SERVICE)

stop: down

down:
	@echo "Stopping services $(if $(SERVICE),($(SERVICE)),(all))..."
	@$(DOCKER_COMPOSE) down

build:
	@echo "Building images $(if $(SERVICE),for $(SERVICE),for all services)..."
	@DOCKER_BUILDKIT=1 $(DOCKER_COMPOSE) build $(SERVICE)

restart:
	@echo "Restarting services $(if $(SERVICE),($(SERVICE)),(all))..."
	@$(DOCKER_COMPOSE) restart $(SERVICE)

logs:
	@echo "Tailing logs $(if $(SERVICE),for $(SERVICE),for all services)..."
	@$(DOCKER_COMPOSE) logs -f $(SERVICE)

ps:
	@$(DOCKER_COMPOSE) ps

watch:
	@echo "Watching for source changes $(if $(SERVICE),on $(SERVICE),on all services)..."
	@DOCKER_BUILDKIT=1 $(DOCKER_COMPOSE) watch $(SERVICE)

clean:
	@echo "Stopping and removing containers, networks, and volumes..."
	@$(DOCKER_COMPOSE) down --volumes --remove-orphans
