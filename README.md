# Tracker Backend

Sistema de tracker de casos de soporte y requerimientos con FastAPI y PostgreSQL.

## Stack Tecnológico

- **Python**: 3.12
- **Framework Web**: FastAPI 0.111.0
- **Base de Datos**: PostgreSQL 16.3
- **Driver DB**: asyncpg (SQL directo, sin ORM)
- **Validación**: Pydantic 2.x

## Estructura del Proyecto

```
tracker-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Entry point de FastAPI
│   ├── config.py                  # Configuración
│   ├── domain/                    # Capa de Dominio
│   │   ├── entities/              # Entidades de negocio
│   │   ├── value_objects/         # Value Objects
│   │   └── exceptions.py          # Excepciones de dominio
│   └── infrastructure/            # Capa de Infraestructura
│       └── database/
│           └── connection.py      # Pool de conexiones
├── migrations/                    # Migraciones SQL
│   ├── 001_initial_schema.sql
│   └── rollback/
│       └── 001_initial_schema.sql
├── pyproject.toml
├── .env.example
└── README.md
```

## Instalación

1. **Instalar dependencias**
```bash
poetry install
```

O si usas pip:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install fastapi[standard] uvicorn asyncpg pydantic pydantic-settings
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Crear base de datos PostgreSQL**
```bash
createdb tracker_db
```

4. **Ejecutar migraciones**
```bash
psql -U tracker_user -d tracker_db -f migrations/001_initial_schema.sql
```

## Ejecutar la aplicación

```bash
# Modo desarrollo con poetry
poetry run uvicorn app.main:app --reload

# O directamente con Python
python -m app.main
```

La API estará disponible en: http://localhost:8000

## Endpoints disponibles

- `GET /` - Hello World
- `GET /health` - Health check básico
- `GET /health/ready` - Readiness check (verifica DB)
- `GET /docs` - Documentación interactiva (Swagger UI)
- `GET /redoc` - Documentación alternativa (ReDoc)

## Próximos pasos

- [ ] Implementar endpoints de casos (POST /api/v1/cases, GET /api/v1/cases)
- [ ] Implementar repositorios
- [ ] Implementar use cases
- [ ] Agregar tests
- [ ] Configurar Docker

## Licencia

MIT
