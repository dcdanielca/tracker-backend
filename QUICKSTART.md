# 🚀 Inicio Rápido - Tracker Backend

## Pasos para levantar el proyecto

### 1. Instalar dependencias

```bash
# Opción 1: Con Poetry (recomendado)
poetry install

# Opción 2: Con pip
pip3 install -r requirements.txt
```

### 2. Levantar base de datos PostgreSQL

```bash
# Con Docker (recomendado)
make db-up

# O manualmente con docker-compose
docker-compose up -d
```

### 3. Ejecutar migraciones

```bash
# Con make
make migrate

# O manualmente
./run_migrations.sh

# O directamente con psql
psql -h localhost -U tracker_user -d tracker_db -f migrations/001_initial_schema.sql
```

### 4. Ejecutar la aplicación

```bash
# Opción 1: Con make
make run

# Opción 2: Con Poetry
poetry run uvicorn app.main:app --reload

# Opción 3: Directamente con Python
python3 -m uvicorn app.main:app --reload

# Opción 4: Ejecutar el script main.py
python3 app/main.py
```

### 5. Probar la aplicación

Abre tu navegador en:

- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc

### Endpoints disponibles:

```bash
# Hello World
curl http://localhost:8000/

# Health check
curl http://localhost:8000/health

# Readiness check (verifica DB)
curl http://localhost:8000/health/ready
```

## Comandos útiles del Makefile

```bash
make help      # Ver todos los comandos disponibles
make install   # Instalar dependencias
make db-up     # Levantar base de datos
make db-down   # Detener base de datos
make migrate   # Ejecutar migraciones
make run       # Ejecutar la aplicación
make test      # Ejecutar tests
make clean     # Limpiar archivos temporales
```

## Estructura del proyecto

```
tracker-backend/
├── app/
│   ├── main.py                    # ✅ Entry point de FastAPI
│   ├── config.py                  # ✅ Configuración con Pydantic
│   ├── domain/                    # ✅ Capa de Dominio
│   │   ├── entities/
│   │   │   └── case.py           # ✅ Entidades SupportCase y CaseQuery
│   │   ├── value_objects/        # ✅ Enums: Status, Type, Priority
│   │   ├── repositories/         # Interfaces de repositorios
│   │   └── exceptions.py         # ✅ Excepciones de dominio
│   ├── application/              # Use Cases (próximamente)
│   ├── infrastructure/           # ✅ Implementaciones
│   │   └── database/
│   │       └── connection.py     # ✅ Pool de conexiones asyncpg
│   └── api/                      # Routers y schemas (próximamente)
├── migrations/                   # ✅ Migraciones SQL
│   ├── 001_initial_schema.sql   # ✅ Schema inicial
│   └── rollback/                # ✅ Scripts de rollback
├── tests/                        # Tests (próximamente)
├── docker-compose.yml            # ✅ PostgreSQL con Docker
├── pyproject.toml                # ✅ Dependencias con Poetry
├── requirements.txt              # ✅ Dependencias alternativas
└── Makefile                      # ✅ Comandos útiles
```

## Próximos pasos

1. ✅ Estructura del proyecto creada
2. ✅ Modelos de dominio (entities, value objects)
3. ✅ Database connection con asyncpg
4. ✅ Migraciones SQL
5. ✅ Hello World funcionando
6. 🔲 Implementar repositorios
7. 🔲 Implementar use cases
8. 🔲 Crear endpoints de API v1
9. 🔲 Agregar tests

## Troubleshooting

### Error: "Database pool not initialized"
- Asegúrate de que PostgreSQL esté corriendo: `docker ps`
- Verifica las credenciales en `.env`

### Error: "Module not found"
- Instala las dependencias: `pip3 install -r requirements.txt`

### Error en migraciones
- Verifica que la base de datos exista: `docker-compose ps`
- Revisa las credenciales en `.env`

## Variables de entorno

Edita el archivo `.env` con tu configuración:

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_USER=tracker_user
DB_PASSWORD=tracker_pass
DB_NAME=tracker_db

# App
DEBUG=true
LOG_LEVEL=INFO
```
