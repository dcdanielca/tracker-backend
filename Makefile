.PHONY: help install dev-install

# Variables
DOCKER_COMPOSE = docker compose
DOCKER = docker

# Colores para output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help:
	@echo "$(GREEN)Tracker Backend - Comandos disponibles:$(NC)"
	@echo ""
	@echo "$(YELLOW)🚀 Inicio Rápido:$(NC)"
	@echo "  make check-docker    - Verificar configuración de Docker"
	@echo "  make init            - Inicializar proyecto (recomendado para primera vez)"
	@echo "  make troubleshoot    - Diagnosticar problemas comunes"
	@echo ""
	@echo "$(YELLOW)🔧 Desarrollo Local (sin Docker):$(NC)"
	@echo "  make install         - Instalar dependencias de producción"
	@echo "  make dev-install     - Instalar dependencias de desarrollo"
	@echo "  make run             - Ejecutar la aplicación localmente"
	@echo "  make db-up           - Levantar solo la base de datos con Docker"
	@echo "  make db-down         - Detener la base de datos"
	@echo ""
	@echo "$(YELLOW)🐳 Docker (entorno completo):$(NC)"
	@echo "  make docker-build    - Construir imágenes de Docker"
	@echo "  make docker-up       - Levantar todos los servicios"
	@echo "  make docker-down     - Detener todos los servicios"
	@echo "  make docker-restart  - Reiniciar todos los servicios"
	@echo "  make docker-logs     - Ver logs de todos los servicios"
	@echo "  make docker-logs-app - Ver logs solo de la aplicación"
	@echo "  make docker-logs-db  - Ver logs solo de la base de datos"
	@echo "  make docker-shell    - Acceder al shell del contenedor de la app"
	@echo "  make docker-clean    - Limpiar contenedores, imágenes y volúmenes"
	@echo ""
	@echo "$(YELLOW)🧪 Testing:$(NC)"
	@echo "  make test            - Ejecutar tests localmente"
	@echo "  make test-docker     - Ejecutar tests en Docker"
	@echo "  make test-watch      - Ejecutar tests en modo watch"
	@echo "  make test-cov        - Ejecutar tests con cobertura"
	@echo ""
	@echo "$(YELLOW)🔍 Calidad de código:$(NC)"
	@echo "  make lint            - Ejecutar linter (ruff)"
	@echo "  make format          - Formatear código (black)"
	@echo "  make type-check      - Verificar tipos (mypy)"
	@echo "  make check           - Ejecutar lint + format + type-check"
	@echo ""
	@echo "$(YELLOW)🗄️  Base de datos:$(NC)"
	@echo "  make migrate         - Ejecutar migraciones"
	@echo "  make db-shell        - Acceder al shell de PostgreSQL"
	@echo "  make db-reset        - Resetear base de datos (elimina datos)"
	@echo ""
	@echo "$(YELLOW)🛠️  Utilidades:$(NC)"
	@echo "  make clean           - Limpiar archivos temporales"
	@echo "  make clean-all       - Limpiar todo (incluye Docker)"

# ============================================
# Inicio Rápido y Diagnóstico
# ============================================

check-docker:
	@echo "$(GREEN)🔍 Verificando configuración de Docker...$(NC)"
	@chmod +x scripts/check-docker.sh
	@./scripts/check-docker.sh

init:
	@echo "$(GREEN)🚀 Inicializando proyecto...$(NC)"
	@chmod +x scripts/init-project.sh scripts/check-docker.sh
	@./scripts/init-project.sh

troubleshoot:
	@echo "$(GREEN)🔍 Ejecutando diagnóstico...$(NC)"
	@chmod +x scripts/troubleshoot.sh
	@./scripts/troubleshoot.sh

# ============================================
# Instalación
# ============================================

install:
	@echo "$(GREEN)📦 Instalando dependencias de producción...$(NC)"
	@if command -v poetry >/dev/null 2>&1; then \
		poetry install --only main; \
	else \
		echo "$(RED)❌ Poetry no está instalado. Instálalo primero.$(NC)"; \
		exit 1; \
	fi

dev-install:
	@echo "$(GREEN)📦 Instalando dependencias de desarrollo...$(NC)"
	@if command -v poetry >/dev/null 2>&1; then \
		poetry install; \
	else \
		echo "$(RED)❌ Poetry no está instalado. Instálalo primero.$(NC)"; \
		exit 1; \
	fi

# ============================================
# Desarrollo Local
# ============================================

run:
	@echo "$(GREEN)🚀 Iniciando servidor en modo desarrollo...$(NC)"
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

db-up:
	@echo "$(GREEN)🐳 Levantando base de datos PostgreSQL...$(NC)"
	@if ! $(DOCKER) ps >/dev/null 2>&1; then \
		echo "$(RED)❌ Error: No tienes permisos de Docker${NC}"; \
		echo "$(YELLOW)Ejecuta: newgrp docker${NC}"; \
		echo "$(YELLOW)O usa: ./scripts/check-docker.sh para más info${NC}"; \
		exit 1; \
	fi
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠️  Creando .env desde .env.example...$(NC)"; \
		cp .env.example .env; \
	fi
	$(DOCKER_COMPOSE) up -d db
	@echo "$(YELLOW)⏳ Esperando que la base de datos esté lista...$(NC)"
	@sleep 5
	@if $(DOCKER_COMPOSE) exec -T db pg_isready -U tracker_user -d tracker_db >/dev/null 2>&1; then \
		echo "$(GREEN)✅ Base de datos lista en localhost:5432$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  La base de datos puede tardar unos segundos más...$(NC)"; \
		echo "$(YELLOW)Verifica con: make docker-logs-db$(NC)"; \
	fi

db-down:
	@echo "$(YELLOW)🛑 Deteniendo base de datos...$(NC)"
	$(DOCKER_COMPOSE) down

# ============================================
# Docker
# ============================================

docker-build:
	@echo "$(GREEN)🔨 Construyendo imágenes de Docker...$(NC)"
	$(DOCKER_COMPOSE) build

docker-up:
	@echo "$(GREEN)🐳 Levantando todos los servicios...$(NC)"
	@if ! $(DOCKER) ps >/dev/null 2>&1; then \
		echo "$(RED)❌ Error: No tienes permisos de Docker${NC}"; \
		echo "$(YELLOW)Ejecuta: newgrp docker${NC}"; \
		echo "$(YELLOW)O usa: ./scripts/check-docker.sh para más info${NC}"; \
		exit 1; \
	fi
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠️  Creando .env desde .env.example...$(NC)"; \
		cp .env.example .env; \
	fi
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ Servicios levantados:$(NC)"
	@echo "  - API: http://localhost:8000"
	@echo "  - Health: http://localhost:8000/health"
	@echo "  - Docs: http://localhost:8000/docs"
	@$(DOCKER_COMPOSE) ps

docker-down:
	@echo "$(YELLOW)🛑 Deteniendo todos los servicios...$(NC)"
	$(DOCKER_COMPOSE) down

docker-restart:
	@echo "$(YELLOW)🔄 Reiniciando servicios...$(NC)"
	$(DOCKER_COMPOSE) restart

docker-logs:
	@echo "$(GREEN)📋 Logs de todos los servicios:$(NC)"
	$(DOCKER_COMPOSE) logs -f

docker-logs-app:
	@echo "$(GREEN)📋 Logs de la aplicación:$(NC)"
	$(DOCKER_COMPOSE) logs -f app

docker-logs-db:
	@echo "$(GREEN)📋 Logs de la base de datos:$(NC)"
	$(DOCKER_COMPOSE) logs -f db

docker-shell:
	@echo "$(GREEN)🐚 Accediendo al shell del contenedor...$(NC)"
	$(DOCKER_COMPOSE) exec app /bin/bash

docker-ps:
	@echo "$(GREEN)📊 Estado de los contenedores:$(NC)"
	$(DOCKER_COMPOSE) ps

docker-clean:
	@echo "$(RED)🧹 Limpiando contenedores, imágenes y volúmenes...$(NC)"
	$(DOCKER_COMPOSE) down -v --remove-orphans
	@$(DOCKER) system prune -f

# ============================================
# Testing
# ============================================

test:
	@echo "$(GREEN)🧪 Ejecutando tests...$(NC)"
	poetry run pytest

test-docker:
	@echo "$(GREEN)🧪 Ejecutando tests en Docker...$(NC)"
	$(DOCKER_COMPOSE) exec app pytest

test-watch:
	@echo "$(GREEN)🧪 Ejecutando tests en modo watch...$(NC)"
	poetry run pytest-watch

test-cov:
	@echo "$(GREEN)🧪 Ejecutando tests con cobertura...$(NC)"
	poetry run pytest --cov=app --cov-report=html --cov-report=term

# ============================================
# Calidad de código
# ============================================

lint:
	@echo "$(GREEN)🔍 Ejecutando linter...$(NC)"
	poetry run ruff check app/ tests/

format:
	@echo "$(GREEN)✨ Formateando código...$(NC)"
	poetry run black app/ tests/

format-check:
	@echo "$(GREEN)✨ Verificando formato...$(NC)"
	poetry run black --check app/ tests/

type-check:
	@echo "$(GREEN)🔍 Verificando tipos...$(NC)"
	poetry run mypy app/

check: lint format-check type-check
	@echo "$(GREEN)✅ Todas las verificaciones completadas$(NC)"

# ============================================
# Base de datos
# ============================================

migrate:
	@echo "$(GREEN)🔄 Ejecutando migraciones...$(NC)"
	@if [ -f ./run_migrations.sh ]; then \
		./run_migrations.sh; \
	else \
		echo "$(YELLOW)⚠️  Script de migraciones no encontrado$(NC)"; \
	fi

db-shell:
	@echo "$(GREEN)🐚 Accediendo al shell de PostgreSQL...$(NC)"
	$(DOCKER_COMPOSE) exec db psql -U tracker_user -d tracker_db

db-reset:
	@echo "$(RED)⚠️  Reseteando base de datos...$(NC)"
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) up -d db
	@sleep 5
	@echo "$(GREEN)✅ Base de datos reseteada$(NC)"

# ============================================
# Utilidades
# ============================================

pgadmin-up:
	@echo "$(GREEN)🔧 Levantando PgAdmin...$(NC)"
	$(DOCKER_COMPOSE) --profile tools up -d pgadmin
	@echo "$(GREEN)✅ PgAdmin disponible en http://localhost:5050$(NC)"
	@echo "  Email: admin@tracker.com"
	@echo "  Password: admin"

clean:
	@echo "$(GREEN)🧹 Limpiando archivos temporales...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ dist/ build/
	@echo "$(GREEN)✅ Limpieza completada$(NC)"

clean-all: clean docker-clean
	@echo "$(GREEN)✅ Limpieza total completada$(NC)"
