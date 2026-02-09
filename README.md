# 🎯 Tracker Backend

Sistema de tracker de casos de soporte y requerimientos construido con FastAPI y PostgreSQL.

## Pre-requisitos

### Opción 1: Con Docker (Recomendado)
- Docker 20+
- Docker Compose 2+
- Make 

### Opción 2: Sin Docker

- Python 3.12+
- Poetry 1.8.2 (gestor de dependencias)
- Docker y Docker Compose
- PostgreSQL 16 (si no usas Docker)

## 🚀 Quick Start

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar el repositorio y configurar variables de entorno
cp .env.example .env

# 2. Levantar todos los servicios DB y API
make docker-build
make docker-up

# 3. Aplicar migraciones
make migrate


# 3. Acceder a la aplicación
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Opción 2: Desarrollo Local

```bash
# 1. Instalar dependencias
poetry install --no-root --all-extras

# 2. Crear base de datos y usuario en postgres con permisos a DB

# 3. Aplicar migraciones ejecutando script sql en la base de datos (ruta: migrations/001_initial_schema.sql)

# 4. Ejecutar la aplicación
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Acceder a la aplicación
# API: http://localhost:8000
# Docs: http://localhost:8000/docs

```


## ✨ Características

- ✅ API RESTful con FastAPI
- ✅ PostgreSQL como base de datos
- ✅ Arquitectura Clean Architecture / Hexagonal
- ✅ Testing unitario, integración y e2e
- ✅ Docker y Docker Compose
- ✅ Type hints y validación con Pydantic
- ✅ Documentación interactiva (Swagger UI)
- ✅ Health checks
- ✅ CORS configurado
- ✅ Hot reload en desarrollo

## 🛠️ Tecnologías

- **Framework**: FastAPI 0.111.0
- **Base de datos**: PostgreSQL 16
- **ORM/Database**: asyncpg
- **Validación**: Pydantic v2
- **Testing**: pytest, pytest-asyncio, httpx
- **Linting**: ruff, black, mypy
- **Container**: Docker, Docker Compose
- **Task Runner**: Make

## 📁 Estructura del Proyecto

```
tracker-backend/
├── app/
│   ├── api/                      # Capa de API (Controllers)
│   │   ├── dependencies.py       # Inyección de dependencias
│   │   └── v1/
│   │       ├── routers/          # Routers de FastAPI
│   │       └── schemas/          # Schemas de request/response
│   ├── application/              # Casos de uso (Business Logic)
│   │   └── use_cases/
│   ├── domain/                   # Entidades y reglas de negocio
│   │   ├── entities/
│   │   └── repositories/         # Interfaces de repositorios
│   ├── infrastructure/           # Implementaciones técnicas
│   │   └── database/
│   │       └── repositories/     # Implementación de repositorios
│   ├── config.py                 # Configuración de la app
│   └── main.py                   # Entry point
├── tests/                        # Tests
│   ├── unit/                     # Tests unitarios
│   ├── integration/              # Tests de integración
│   └── e2e/                      # Tests end-to-end
├── scripts/                      # Scripts útiles
│   ├── backup-db.sh             # Backup de BD
│   └── restore-db.sh            # Restaurar BD
├── nginx/                        # Configuración Nginx (producción)
├── Dockerfile                    # Imagen Docker
├── docker-compose.yml           # Docker Compose (desarrollo)
├── docker-compose.prod.yml      # Docker Compose (producción)
├── Makefile                      # Comandos útiles
└── pyproject.toml               # Dependencias y configuración
```


### Testing

```bash
make test              # Ejecutar tests en Docker
make test-local        # Ejecutar tests localmente
make test-cov          # Ejecutar tests con cobertura en Docker
make test-cov-local    # Ejecutar tests con cobertura localmente
make test-watch        # Ejecutar tests en modo watch (local)
```

### Calidad de Código

```bash
make lint              # Linter (ruff)
make format            # Formatear código (black)
make type-check        # Verificar tipos (mypy)
make check             # Todas las verificaciones
```

### Base de Datos

```bash
make migrate           # Ejecutar migraciones
make db-shell          # Shell de PostgreSQL
make db-reset          # Resetear BD (elimina datos)
make pgadmin-up        # Levantar PgAdmin
```

### Utilidades

```bash
make clean             # Limpiar archivos temporales
make clean-all         # Limpiar todo (incluye Docker)
make help              # Ver todos los comandos
```

## 🌐 API Endpoints

### Health Checks

- `GET /` - Hello World
- `GET /health` - Health check simple
- `GET /health/ready` - Readiness check (verifica DB)

### Cases (Casos)

- `GET /api/v1/cases` - Listar todos los casos
- `GET /api/v1/cases/{id}` - Obtener un caso por ID
- `POST /api/v1/cases` - Crear un nuevo caso

### Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

El proyecto incluye tres tipos de tests:

### Ejecución con Docker (Recomendado)

```bash
# Ejecutar todos los tests
make test

# Ejecutar tests con cobertura
make test-cov

# Ejecutar tests por tipo
docker compose exec app poetry run pytest tests/unit/
docker compose exec app poetry run pytest tests/integration/
docker compose exec app poetry run pytest tests/e2e/
```

### Ejecución Local

```bash
# Ejecutar todos los tests
make test-local

# Ejecutar tests con cobertura
make test-cov-local

# Ejecutar tests por tipo
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/e2e/

# Modo watch (desarrollo)
make test-watch
```

### Cobertura

```bash
# Con Docker
make test-cov

# Local
make test-cov-local

# Abre htmlcov/index.html en el navegador para ver el reporte detallado
```

## 🔐 Variables de Entorno

Copia `.env.example` a `.env` y ajusta según necesites:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=tracker_user
DB_PASSWORD=tracker_pass
DB_NAME=tracker_db

# App
APP_PORT=8000
APP_NAME=Tracker API
DEBUG=true
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## 🏗️ Arquitectura

El proyecto sigue **Clean Architecture** / **Arquitectura Hexagonal**:

```
┌─────────────────────────────────────────────┐
│            API Layer (FastAPI)              │
│  Controllers, Routers, Schemas, DTOs        │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│        Application Layer (Use Cases)        │
│       Business Logic, Orchestration         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│            Domain Layer (Core)              │
│    Entities, Value Objects, Interfaces      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│     Infrastructure Layer (Technical)        │
│   Repositories, Database, External APIs     │
└─────────────────────────────────────────────┘
```

### Principios

- ✅ Inyección de dependencias
- ✅ Inversión de control
- ✅ Separación de responsabilidades
- ✅ Testeable y mantenible


Desarrollado con ❤️ usando FastAPI y Python
