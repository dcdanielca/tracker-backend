.PHONY: help install db-up db-down migrate run test clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install    - Instalar dependencias"
	@echo "  make db-up      - Levantar base de datos con Docker"
	@echo "  make db-down    - Detener base de datos"
	@echo "  make migrate    - Ejecutar migraciones"
	@echo "  make run        - Ejecutar la aplicación"
	@echo "  make test       - Ejecutar tests"
	@echo "  make clean      - Limpiar archivos temporales"

install:
	@echo "📦 Instalando dependencias..."
	@if command -v poetry >/dev/null 2>&1; then \
		poetry install; \
	else \
		pip3 install -r requirements.txt; \
	fi

db-up:
	@echo "🐳 Levantando base de datos PostgreSQL..."
	docker-compose up -d db
	@echo "⏳ Esperando que la base de datos esté lista..."
	@sleep 5

db-down:
	@echo "🛑 Deteniendo base de datos..."
	docker-compose down

migrate:
	@echo "🔄 Ejecutando migraciones..."
	@./run_migrations.sh

run:
	@echo "🚀 Iniciando servidor..."
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; \
	else \
		python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; \
	fi

test:
	@echo "🧪 Ejecutando tests..."
	@if command -v poetry >/dev/null 2>&1; then \
		poetry run pytest; \
	else \
		python3 -m pytest; \
	fi

clean:
	@echo "🧹 Limpiando archivos temporales..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov
