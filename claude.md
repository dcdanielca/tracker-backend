# Guía de Arquitectura y Estilos - Backend FastAPI

## Tabla de Contenidos

0. [Contexto del Proyecto](#contexto-del-proyecto)
1. [Principios Arquitectónicos](#principios-arquitectónicos)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Arquitectura por Capas](#arquitectura-por-capas)
4. [Flujo de Request](#flujo-de-request)
5. [Acceso a Datos (sin ORM)](#acceso-a-datos-sin-orm)
6. [Manejo de Transacciones](#manejo-de-transacciones)
7. [Versionado de API](#versionado-de-api)
8. [Migraciones](#migraciones)
9. [Seguridad](#seguridad)
10. [Performance](#performance)
11. [Observabilidad](#observabilidad)
12. [Testing](#testing)
13. [Anti-patterns](#anti-patterns)
14. [12 Factor App](#12-factor-app)

---

## Contexto del Proyecto

### 🎯 Objetivo

Sistema de **tracker de casos de soporte y requerimientos** que permita registrar y consultar casos relacionados con consultas SQL ejecutadas en bases de datos, con trazabilidad completa para análisis posterior.

### 📋 Requisitos Funcionales

#### 1. Modelo de Base de Datos

Diseñar e implementar un modelo Entidad-Relación en PostgreSQL que almacene:

- **Casos de soporte/requerimientos** con información completa
- **Consultas SQL ejecutadas**: base de datos, esquema, query, resultados
- **Usuario que ejecuta**: persona responsable del caso
- **Trazabilidad completa**: historial de cambios, auditoría
- **Metadatos para análisis**: timestamps, duración, estado, prioridad

**Campos importantes a considerar:**
- Base de datos objetivo
- Esquema de la base de datos
- Consulta SQL ejecutada
- Persona que realiza la consulta
- Fecha/hora de creación y modificación
- Estado del caso
- Prioridad
- Tipo de caso (soporte, requerimiento, investigación, etc.)
- Resultado de la consulta
- Tiempo de ejecución

#### 2. API REST con FastAPI

**Restricciones técnicas:**

✅ **Permitido:**
- Solo operaciones de **INSERT** (crear) y **READ** (leer)
- Respuestas en formato **JSON**
- Códigos de respuesta HTTP apropiados (201, 200, 404, 422, etc.)

❌ **No permitido:**
- No usar ORMs (SQLAlchemy, Tortoise, etc.)
- No operaciones UPDATE o DELETE en la API
- Todo acceso a datos debe ser mediante SQL directo con asyncpg

**Estructura del código:**
- **Separación de responsabilidades**: No todo en un solo archivo
- **Enrutamientos separados**: Routers por dominio
- **Arquitectura por capas**: Presentación, Aplicación, Dominio, Infraestructura

### 🏗️ Arquitectura Objetivo

```
Tracker Backend
├── API Layer (FastAPI)
│   ├── POST /api/v1/cases - Crear caso
│   ├── GET /api/v1/cases - Listar casos (con filtros y paginación)
│   └── GET /api/v1/cases/{id} - Obtener caso específico
│
├── Use Cases (Application Layer)
│   ├── CreateSupportCase
│   ├── GetSupportCases (con filtros)
│   └── GetSupportCaseById
│
├── Domain Layer
│   ├── Entities: SupportCase, SQLQuery
│   ├── Value Objects: CasePriority, CaseStatus, CaseType, DatabaseInfo
│   └── Repositories: SupportCaseRepository, SQLQueryRepository, UserRepository
│
└── Infrastructure Layer
    ├── PostgreSQL repositories (sin ORM)
    ├── Migrations
    └── Database connection pool
```

### 📡 Especificación de Endpoints (API REST)

#### 1. Vista de Creación - Endpoints POST


**A. Crear Caso de Soporte**
```
POST /api/v1/cases
Content-Type: application/json

Request Body:
{
  "title": "Consulta sobre ventas del Q4 2025",
  "description": "Necesito extraer datos de ventas para análisis mensual",
  "case_type": "support",  // Enum: support | requirement | investigation
  "priority": "high",      // Enum: low | medium | high | critical
  "queries": [
    {
        "database_name": "sales_db",
        "schema_name": "public",
        "query_text": "SELECT * FROM sales WHERE date >= '2025-10-01'"
    }
  ]
  "created_by": "email-de-usuario"
}

Response: 201 Created
{
  "id": 1,
  "title": "Consulta sobre ventas del Q4 2025",
  "description": "Necesito extraer datos de ventas para análisis mensual",
  "case_type": "support",
  "priority": "high",
  "status": "open",        // Enum: open | in_progress | resolved | closed
  "created_by": "user@email.com",
  "created_at": "2026-02-08T10:30:00Z",
  "updated_at": "2026-02-08T10:30:00Z",
  "queries": [
        {
            "id": "uuid-v4",
            "case_id": "uuid-del-caso",
            "database_name": "sales_db",
            "schema_name": "public",
            "query_text": "SELECT * FROM sales WHERE date >= '2025-10-01'",
            "execution_time_ms": 245,
            "rows_affected": 1500,
            "executed_by": "soporte@admin.com",
            "executed_at": "2026-02-08T10:35:00Z",
        }
  ]
}
```

#### 2. Vista de Seguimiento - Endpoints GET

**A. Listar Casos con Filtros y Paginación**
```
GET /api/v1/cases?page=1&page_size=10&status=open&priority=high&case_type=support&search=ventas&created_by=admin@email.com

Query Parameters:
- page: int (default: 1) - Número de página
- page_size: int (default: 10, max: 50) - Elementos por página
- status: string (optional) - Filtrar por estado
- priority: string (optional) - Filtrar por prioridad
- case_type: string (optional) - Filtrar por tipo de caso
- created_by: string (optional) - Filtrar por email de usuario creador
- search: string (optional) - Búsqueda en title y description
- date_gte: datetime (optional) - Casos desde esta fecha
- date_lte: datetime (optional) - Casos hasta esta fecha
- sort_by: string (default: "created_at") - Campo para ordenar (por  status, priority, case_type, creared_by, created_at)
- sort_order: string (default: "desc") - asc | desc

Response: 200 OK
{
  "items": [
    {
      "id": 2,
      "title": "Consulta sobre ventas del Q4 2025",
      "description": "Necesito extraer datos...",
      "case_type": "support",
      "priority": "high",
      "status": "open",
      "created_by": "analista@empresa.com",
      "created_at": "2026-02-08T10:30:00Z",
      "updated_at": "2026-02-08T10:30:00Z",
      "queries_count": 3  // Número de queries asociadas
    }
  ],
  "total": 45,           // Total de registros
  "page": 1,            // Página actual
  "page_size": 10,      // Elementos por página
  "pages": 5            // Total de páginas
}
```

**B. Obtener Detalle de un Caso**
```
GET /api/v1/cases/{case_id}

Response: 200 OK
{
  "id": 3,
  "title": "Consulta sobre ventas del Q4 2025",
  "description": "Necesito extraer datos de ventas para análisis mensual",
  "case_type": "support",
  "priority": "high",
  "status": "open",
  "created_by": "analista@empresa.com",
  "created_at": "2026-02-08T10:30:00Z",
  "updated_at": "2026-02-08T10:30:00Z",
  "queries": [
        {
            "id": 1,
            "database_name": "sales_db",
            "schema_name": "public",
            "query_text": "SELECT * FROM sales...",
            "execution_time_ms": 245,
            "rows_affected": 1500,
            "executed_at": "2026-02-08T10:35:00Z",
            "executed_by": "juanpepito@mail.com"
        }
    ]
}
```

### 🎨 Stack Tecnológico

- **Python**: 3.12
- **Framework Web**: FastAPI 0.111.0
- **Base de Datos**: PostgreSQL 16.3
- **Driver DB**: asyncpg (SQL directo, sin ORM)
- **Validación**: Pydantic 2.x
- **Testing**: Pytest
- **Containerización**: Docker

 - Linting: formation y tests:
    - Ruff / Black
    - Pytest
    - Pre-commit
    - Mypy

### 📊 Modelo de Datos Preliminar

```sql
-- Casos de soporte
support_cases
  - id (PK)
  - title (VARCHAR)
  - description (TEXT)
  - case_type (ENUM: support, requirement, investigation)
  - priority (ENUM: low, medium, high, critical)
  - status (ENUM: open, in_progress, resolved, closed)
  - created_by (VARCHAR: email)
  - created_at (TIMESTAMP)
  - updated_at (TIMESTAMP)

-- Consultas SQL ejecutadas
case_queries
  - id (PK)
  - case_id (FK -> support_cases)
  - database_name (VARCHAR)
  - schema_name (VARCHAR)
  - query_text (TEXT)
  - execution_time_ms (INTEGER)
  - rows_affected (INTEGER)
  - executed_at (TIMESTAMP)
  - executed_by (VARCHAR: email)

```

### 🚀 Flujo de Trabajo Típico

1. **Crear caso de soporte**
   - POST /api/v1/cases
   - Body: { title, description, case_type, priority }
   - Response: 201 Created con datos del caso y queries

2. **Consultar casos**
   - GET /api/v1/cases?status=open&priority=high
   - Response: 200 OK con lista paginada

3. **Ver detalle de un caso**
   - GET /api/v1/cases/{case_id}/history
   - Response: 200 OK con lista de queries

### ⚠️ Consideraciones Importantes

- **Seguridad**: Prevenir SQL injection usando parámetros en todas las queries
- **Trazabilidad**: Cada cambio debe quedar registrado para auditoría
- **Performance**: Índices apropiados para búsquedas frecuentes (ver campos de busqueda en filtrado de casos)
- **Validación**: Pydantic schemas para validar entrada
- **Transacciones**: Operaciones atómicas 
- **Logging**: Registrar todas las operaciones para debugging (usando logger no prints)

---

## Principios Arquitectónicos

### Clean Architecture

- **Independencia de frameworks**: La lógica de negocio no depende de FastAPI
- **Testeable**: Las reglas de negocio pueden probarse sin UI, DB, o servicios externos
- **Independencia de la UI**: La UI puede cambiar sin afectar el resto del sistema
- **Independencia de la DB**: Puedes cambiar PostgreSQL por otro sin afectar las reglas de negocio
- **Independencia de agentes externos**: Las reglas de negocio no conocen el mundo exterior

### Dependency Rule

Las dependencias apuntan **hacia adentro**. Los círculos internos no conocen nada de los externos.

```
Presentation → Application → Domain ← Infrastructure
```

---

## Estructura del Proyecto

```
tracker-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Entry point de FastAPI
│   ├── config.py                  # Configuración (12 Factor)
│   │
│   ├── api/                       # Capa de Presentación
│   │   ├── __init__.py
│   │   ├── dependencies.py        # Inyección de dependencias
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── routers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── cases.py
│   │   │   └── schemas/           # DTOs de request/response
│   │   │       ├── __init__.py
│   │   │       ├── cases.py
│   │   │       └── queries.py
│   │   └── v2/
│   │
│   ├── domain/                    # Capa de Dominio (Core)
│   │   ├── __init__.py
│   │   ├── entities/              # Entidades de negocio
│   │   │   ├── __init__.py
│   │   │   ├── case.py
│   │   │   └── query.py
│   │   ├── value_objects/         # Value Objects
│   │   │   ├── __init__.py
│   │   │   ├── queries.py
│   │   │   └── case_status.py
│   │   ├── repositories/          # Interfaces (abstracciones)
│   │   │   ├── __init__.py
│   │   │   ├── case_repository.py
│   │   │   └── query_repository.py
│   │   ├── services/              # Lógica de negocio compleja
│   │   │   ├── __init__.py
│   │   │   └── query_assignment_service.py
│   │   └── exceptions.py          # Excepciones de dominio
│   │
│   ├── application/               # Capa de Aplicación (Use Cases)
│   │   ├── __init__.py
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   ├── create_case.py
│   │   │   ├── update_case_status.py
│   │   │   └── assign_case.py
│   │   └── interfaces/            # Puertos de salida
│   │       ├── __init__.py
│   │       └── unit_of_work.py
│   │
│   ├── infrastructure/            # Capa de Infraestructura
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py      # Pool de conexiones
│   │   │   ├── repositories/      # Implementaciones concretas
│   │   │   │   ├── __init__.py
│   │   │   │   ├── case_repository_impl.py
│   │   │   │   └── query_repository_impl.py
│   │   │   └── unit_of_work.py    # Implementación de UoW
│   │   ├── logging/
│   │   │   ├── __init__.py
│   │   │   └── setup.py
│   │   └── monitoring/
│   │       ├── __init__.py
│   │       └── metrics.py
│   │
│   └── shared/                    # Utilidades compartidas
│       ├── __init__.py
│       ├── utils.py
│       └── constants.py
│
├── migrations/                    # Migraciones SQL
│   ├── 001_initial_schema.sql
│   ├── 002_add_cases_table.sql
│   └── rollback/
│       ├── 001_initial_schema.sql
│       └── 002_add_cases_table.sql
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── .env.example
├── pyproject.toml
└── README.md
```

---

## Arquitectura por Capas

### 1. Capa de Presentación (API Layer)

**Responsabilidades:**
- Recibir requests HTTP
- Validar entrada con Pydantic schemas
- Autenticación y autorización
- Serializar respuestas
- Manejo de errores HTTP

**Ejemplo:**

```python
# app/api/v1/routers/cases.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas.cases import CreateCaseRequest, CaseResponse
from app.api.dependencies import get_create_case_use_case
from app.application.use_cases.create_case import CreateCaseUseCase
from app.domain.exceptions import DomainValidationError

router = APIRouter(prefix="/cases", tags=["cases"])

@router.post(
    "/",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo caso",
    description="Crea un nuevo caso de soporte con sus consultas SQL asociadas"
)
async def create_case(
    request: CreateCaseRequest,
    use_case: CreateCaseUseCase = Depends(get_create_case_use_case)
):
    try:
        case = await use_case.execute(
            title=request.title,
            description=request.description,
            case_type=request.case_type,
            priority=request.priority,
            queries=request.queries,
            created_by=request.created_by
        )
        return CaseResponse.from_entity(case)
    except DomainValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
```

```python
# app/api/v1/schemas/cases.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from app.domain.entities.case import SupportCase
from app.api.v1.schemas.queries import QueryResponse

class CreateCaseRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    case_type: str = Field(..., pattern="^(support|requirement|investigation)$")
    priority: str = Field(..., pattern="^(low|medium|high|critical)$")
    queries: List[dict] = Field(default_factory=list)
    created_by: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")  # Email validation

class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    case_type: str
    priority: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    queries: List[QueryResponse] = Field(default_factory=list)

    @classmethod
    def from_entity(cls, case: SupportCase) -> "CaseResponse":
        return cls(
            id=case.id,
            title=case.title,
            description=case.description,
            case_type=case.case_type.value,
            priority=case.priority.value,
            status=case.status.value,
            created_by=case.created_by,
            created_at=case.created_at,
            updated_at=case.updated_at,
            queries=[QueryResponse.from_entity(q) for q in case.queries]
        )
```

### 2. Capa de Aplicación (Use Cases)

**Responsabilidades:**
- Orquestar el flujo de datos
- Coordinar entidades y servicios de dominio
- Gestionar transacciones (Unit of Work)
- No contiene lógica de negocio

**Ejemplo:**

```python
# app/application/use_cases/create_case.py
from datetime import datetime
from uuid import UUID
from typing import List
from app.domain.entities.case import SupportCase
from app.domain.entities.query import CaseQuery
from app.domain.repositories.case_repository import CaseRepository
from app.domain.repositories.query_repository import QueryRepository
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.domain.value_objects.case_status import CaseStatus
from app.application.interfaces.unit_of_work import UnitOfWork
from app.domain.exceptions import DomainValidationError

class CreateCaseUseCase:
    def __init__(
        self,
        case_repository: CaseRepository,
        query_repository: QueryRepository,
        uow: UnitOfWork
    ):
        self._case_repository = case_repository
        self._query_repository = query_repository
        self._uow = uow

    async def execute(
        self,
        title: str,
        description: str | None,
        case_type: str,
        priority: str,
        queries: List[dict],
        created_by: str
    ) -> SupportCase:
        async with self._uow:
            # Crear entidad de dominio
            case = SupportCase.create(
                title=title,
                description=description,
                case_type=CaseType(case_type),
                priority=CasePriority(priority),
                created_by=created_by
            )

            # Persistir caso
            await self._case_repository.save(case)

            # Crear y persistir queries asociadas
            for query_data in queries:
                query = CaseQuery.create(
                    case_id=case.id,
                    database_name=query_data["database_name"],
                    schema_name=query_data["schema_name"],
                    query_text=query_data["query_text"],
                    executed_by=created_by
                )
                await self._query_repository.save(query)
                case.add_query(query)

            # Commit de la transacción
            await self._uow.commit()

            return case
```

### 3. Capa de Dominio (Core)

**Responsabilidades:**
- Contiene la lógica de negocio
- Entidades con comportamiento
- Value Objects inmutables
- Reglas de validación
- Interfaces de repositorios

**Ejemplo de Entidad:**

```python
# app/domain/entities/case.py
from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List
from app.domain.value_objects.case_status import CaseStatus
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.domain.entities.query import CaseQuery
from app.domain.exceptions import DomainValidationError

@dataclass
class SupportCase:
    id: UUID = field(default_factory=uuid4)
    title: str = field(default="")
    description: str | None = None
    case_type: CaseType = field(default=CaseType.SUPPORT)
    priority: CasePriority = field(default=CasePriority.MEDIUM)
    status: CaseStatus = field(default=CaseStatus.OPEN)
    created_by: str = field(default="")  # Email del usuario
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    queries: List[CaseQuery] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        title: str,
        case_type: CaseType,
        priority: CasePriority,
        created_by: str,
        description: str | None = None
    ) -> "SupportCase":
        """Factory method para crear un caso válido"""
        if not title or len(title.strip()) == 0:
            raise DomainValidationError("El título no puede estar vacío")

        if len(title) > 200:
            raise DomainValidationError("El título no puede exceder 200 caracteres")

        if not created_by or "@" not in created_by:
            raise DomainValidationError("El email del creador no es válido")

        return cls(
            title=title.strip(),
            description=description,
            case_type=case_type,
            priority=priority,
            created_by=created_by,
            status=CaseStatus.OPEN
        )

    def add_query(self, query: CaseQuery) -> None:
        """Agrega una query al caso"""
        if query.case_id != self.id:
            raise DomainValidationError("La query no pertenece a este caso")
        self.queries.append(query)
        self.updated_at = datetime.utcnow()

    def mark_as_in_progress(self) -> None:
        """Marca el caso como en progreso"""
        if self.status == CaseStatus.CLOSED:
            raise DomainValidationError("No se puede cambiar estado de caso cerrado")

        self.status = CaseStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def mark_as_resolved(self) -> None:
        """Marca el caso como resuelto"""
        if self.status not in [CaseStatus.OPEN, CaseStatus.IN_PROGRESS]:
            raise DomainValidationError("Solo se pueden resolver casos abiertos o en progreso")

        self.status = CaseStatus.RESOLVED
        self.updated_at = datetime.utcnow()

    def close(self) -> None:
        """Cierra el caso"""
        if self.status != CaseStatus.RESOLVED:
            raise DomainValidationError("Solo se pueden cerrar casos resueltos")

        self.status = CaseStatus.CLOSED
        self.updated_at = datetime.utcnow()
```

**Ejemplo de Value Object:**

```python
# app/domain/value_objects/case_status.py
from enum import Enum

class CaseStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

    def can_transition_to(self, new_status: "CaseStatus") -> bool:
        """Define transiciones válidas de estado"""
        transitions = {
            self.OPEN: [self.IN_PROGRESS, self.CLOSED],
            self.IN_PROGRESS: [self.RESOLVED, self.CLOSED],
            self.RESOLVED: [self.CLOSED],
            self.CLOSED: []
        }
        return new_status in transitions.get(self, [])
```

**Ejemplo de Repository Interface:**

```python
# app/domain/repositories/case_repository.py
from abc import ABC, abstractmethod
from uuid import UUID
from typing import List, Optional
from app.domain.entities.case import SupportCase

class CaseRepository(ABC):
    """Interface del repositorio de casos (Port)"""

    @abstractmethod
    async def save(self, case: SupportCase) -> None:
        """Guarda un caso (solo INSERT, no UPDATE)"""
        pass

    @abstractmethod
    async def get_by_id(self, case_id: UUID) -> Optional[SupportCase]:
        """Obtiene un caso por ID"""
        pass

    @abstractmethod
    async def get_all(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        case_type: Optional[str] = None,
        created_by: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[List[SupportCase], int]:
        """Obtiene casos con filtros y paginación"""
        pass
```

### 4. Capa de Infraestructura

**Responsabilidades:**
- Implementación de repositorios
- Acceso a base de datos
- Servicios externos (email, cache, etc.)
- Logging, métricas

**Ejemplo de Repository Implementation:**

```python
# app/infrastructure/database/repositories/case_repository_impl.py
from uuid import UUID
from typing import List, Optional, Tuple
import asyncpg
from app.domain.entities.case import SupportCase
from app.domain.repositories.case_repository import CaseRepository
from app.domain.value_objects.case_status import CaseStatus
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.infrastructure.database.connection import DatabaseConnection

class CaseRepositoryImpl(CaseRepository):
    def __init__(self, db: DatabaseConnection):
        self._db = db

    async def save(self, case: SupportCase) -> None:
        """Guarda un caso (solo INSERT)"""
        query = """
            INSERT INTO support_cases (
                id, title, description, case_type, priority,
                status, created_by, created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """

        await self._db.execute(
            query,
            case.id,
            case.title,
            case.description,
            case.case_type.value,
            case.priority.value,
            case.status.value,
            case.created_by,
            case.created_at,
            case.updated_at
        )

    async def get_by_id(self, case_id: UUID) -> Optional[SupportCase]:
        """Obtiene un caso por ID"""
        query = """
            SELECT
                id, title, description, case_type, priority,
                status, created_by, created_at, updated_at
            FROM support_cases
            WHERE id = $1
        """

        row = await self._db.fetchrow(query, case_id)

        if not row:
            return None

        return self._map_to_entity(row)

    async def get_all(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        case_type: Optional[str] = None,
        created_by: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[SupportCase], int]:
        """Obtiene casos con filtros y paginación"""
        offset = (page - 1) * page_size
        conditions = []
        params = []
        param_idx = 1

        if status:
            conditions.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        if priority:
            conditions.append(f"priority = ${param_idx}")
            params.append(priority)
            param_idx += 1

        if case_type:
            conditions.append(f"case_type = ${param_idx}")
            params.append(case_type)
            param_idx += 1

        if created_by:
            conditions.append(f"created_by = ${param_idx}")
            params.append(created_by)
            param_idx += 1

        if search:
            conditions.append(f"(title ILIKE ${param_idx} OR description ILIKE ${param_idx})")
            search_term = f"%{search}%"
            params.append(search_term)
            params.append(search_term)
            param_idx += 2

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Query para datos
        query = f"""
            SELECT
                id, title, description, case_type, priority,
                status, created_by, created_at, updated_at
            FROM support_cases
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([page_size, offset])

        rows = await self._db.fetch(query, *params)

        # Query para total
        count_query = f"""
            SELECT COUNT(*) FROM support_cases
            WHERE {where_clause}
        """
        total = await self._db.fetchval(count_query, *params[:-2])  # Excluir LIMIT y OFFSET

        cases = [self._map_to_entity(row) for row in rows]
        return cases, total

    def _map_to_entity(self, row: asyncpg.Record) -> SupportCase:
        """Mapea un registro de DB a una entidad de dominio"""
        return SupportCase(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            case_type=CaseType(row["case_type"]),
            priority=CasePriority(row["priority"]),
            status=CaseStatus(row["status"]),
            created_by=row["created_by"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )
```

---

## Flujo de Request

```
HTTP Request
    ↓
[FastAPI Router] ← Valida con Pydantic
    ↓
[Dependencies] ← Inyecta Use Case
    ↓
[Use Case] ← Orquesta flujo
    ↓
[Domain Service] ← Lógica compleja (opcional)
    ↓
[Entity] ← Aplica reglas de negocio
    ↓
[Repository Interface] ← Abstracción
    ↓
[Repository Implementation] ← Acceso a DB
    ↓
[PostgreSQL]
```

**Ejemplo completo del flujo:**

```python
# 1. Router recibe request
@router.get("/cases/{case_id}")
async def get_case(
    case_id: UUID,
    use_case: GetCaseByIdUseCase = Depends(get_case_by_id_use_case)
):
    case = await use_case.execute(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Caso no encontrado")
    return CaseResponse.from_entity(case)

# 2. Use Case orquesta
class GetCaseByIdUseCase:
    async def execute(self, case_id: UUID) -> Optional[SupportCase]:
        case = await self._case_repository.get_by_id(case_id)
        if case:
            # Obtener queries asociadas
            queries = await self._query_repository.get_by_case_id(case_id)
            case.queries = queries
        return case
```


## Acceso a Datos (sin ORM)

### Connection Pool

```python
# app/infrastructure/database/connection.py
import asyncpg
from typing import Optional
from app.config import settings

class DatabaseConnection:
    """Gestiona el pool de conexiones a PostgreSQL"""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """Crea el pool de conexiones"""
        self._pool = await asyncpg.create_pool(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            min_size=10,
            max_size=20,
            command_timeout=60,
            # Configuración de performance
            max_queries=50000,
            max_inactive_connection_lifetime=300
        )

    async def disconnect(self) -> None:
        """Cierra el pool de conexiones"""
        if self._pool:
            await self._pool.close()

    async def fetch(self, query: str, *args) -> list:
        """Ejecuta query que retorna múltiples registros"""
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Ejecuta query que retorna un registro"""
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args) -> str:
        """Ejecuta query sin retorno (INSERT, UPDATE, DELETE)"""
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def executemany(self, query: str, args_list: list) -> None:
        """Ejecuta múltiples queries en batch"""
        async with self._pool.acquire() as conn:
            await conn.executemany(query, args_list)

    def transaction(self):
        """Retorna un context manager para transacciones"""
        return self._pool.acquire()
```

### Prevención de SQL Injection

**✅ CORRECTO - Usar parámetros:**

```python
# Siempre usar placeholders ($1, $2, etc.)
async def get_case_by_id(self, case_id: UUID) -> Optional[SupportCase]:
    query = "SELECT * FROM support_cases WHERE id = $1"
    row = await self._db.fetchrow(query, case_id)
    return self._map_to_entity(row) if row else None

# Para múltiples parámetros
async def get_cases_by_status_and_priority(
    self,
    status: str,
    priority: str
) -> List[SupportCase]:
    query = """
        SELECT * FROM support_cases
        WHERE status = $1 AND priority = $2
        ORDER BY created_at DESC
    """
    rows = await self._db.fetch(query, status, priority)
    return [self._map_to_entity(row) for row in rows]
```

**❌ INCORRECTO - NUNCA concatenar strings:**

```python
# ¡PELIGRO! Vulnerable a SQL injection
async def get_case_by_id(self, case_id: UUID):
    query = f"SELECT * FROM support_cases WHERE id = '{case_id}'"  # ❌ NO HACER
    return await self._db.fetchrow(query)

# ¡PELIGRO! Incluso con format()
query = "SELECT * FROM support_cases WHERE id = '{}'".format(case_id)  # ❌ NO HACER
```

**Casos especiales - Identificadores dinámicos:**

```python
from asyncpg import sql

# Para nombres de tabla o columna dinámicos (usar con extremo cuidado)
async def get_by_dynamic_column(
    self,
    column_name: str,
    value: str
) -> Optional[SupportCase]:
    # Whitelist de columnas permitidas
    allowed_columns = {"status", "priority", "case_type", "created_by", "id"}
    if column_name not in allowed_columns:
        raise ValueError(f"Columna no permitida: {column_name}")

    # Usar asyncpg.sql para identificadores
    query = f"SELECT * FROM support_cases WHERE {column_name} = $1"
    return await self._db.fetchrow(query, value)
```

**Búsquedas LIKE seguras:**

```python
async def search_cases(self, search_term: str) -> List[SupportCase]:
    # Escapar caracteres especiales de LIKE
    safe_term = search_term.replace("%", "\\%").replace("_", "\\_")

    query = """
        SELECT * FROM support_cases
        WHERE title ILIKE $1 || '%' OR description ILIKE $1 || '%'
        ESCAPE '\\'
    """
    rows = await self._db.fetch(query, safe_term)
    return [self._map_to_entity(row) for row in rows]
```

**IN clauses con array parameters:**

```python
async def get_cases_by_ids(self, case_ids: List[UUID]) -> List[SupportCase]:
    query = """
        SELECT * FROM support_cases
        WHERE id = ANY($1::uuid[])
    """
    rows = await self._db.fetch(query, case_ids)
    return [self._map_to_entity(row) for row in rows]
```

---

## Manejo de Transacciones

### Unit of Work Pattern

```python
# app/application/interfaces/unit_of_work.py
from abc import ABC, abstractmethod
from typing import Any

class UnitOfWork(ABC):
    """Interface del patrón Unit of Work"""

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        """Inicia una transacción"""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finaliza la transacción (commit o rollback)"""
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Confirma los cambios"""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Deshace los cambios"""
        pass
```

```python
# app/infrastructure/database/unit_of_work.py
from typing import Optional
import asyncpg
from app.application.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.database.connection import DatabaseConnection

class PostgreSQLUnitOfWork(UnitOfWork):
    """Implementación de Unit of Work para PostgreSQL"""

    def __init__(self, db: DatabaseConnection):
        self._db = db
        self._connection: Optional[asyncpg.Connection] = None
        self._transaction: Optional[asyncpg.Transaction] = None

    async def __aenter__(self) -> "PostgreSQLUnitOfWork":
        """Inicia una transacción"""
        self._connection = await self._db._pool.acquire()
        self._transaction = self._connection.transaction()
        await self._transaction.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finaliza la transacción"""
        try:
            if exc_type is not None:
                # Hubo una excepción, hacer rollback
                await self.rollback()
            else:
                # No hubo excepciones, hacer commit
                await self.commit()
        finally:
            if self._connection:
                await self._db._pool.release(self._connection)
                self._connection = None
                self._transaction = None

    async def commit(self) -> None:
        """Confirma la transacción"""
        if self._transaction:
            await self._transaction.commit()

    async def rollback(self) -> None:
        """Deshace la transacción"""
        if self._transaction:
            await self._transaction.rollback()

    def get_connection(self) -> asyncpg.Connection:
        """Obtiene la conexión actual para uso en repositorios"""
        return self._connection
```

**Uso en Use Cases:**

```python
class CreateCaseUseCase:
    """Use case que necesita atomicidad para crear caso y queries"""

    async def execute(
        self,
        title: str,
        description: str | None,
        case_type: str,
        priority: str,
        queries: List[dict],
        created_by: str
    ) -> SupportCase:
        async with self._uow:
            # Crear caso
            case = SupportCase.create(
                title=title,
                description=description,
                case_type=CaseType(case_type),
                priority=CasePriority(priority),
                created_by=created_by
            )

            # Persistir caso
            await self._case_repository.save(case)

            # Crear y persistir queries asociadas (atómico)
            for query_data in queries:
                query = CaseQuery.create(
                    case_id=case.id,
                    database_name=query_data["database_name"],
                    schema_name=query_data["schema_name"],
                    query_text=query_data["query_text"],
                    executed_by=created_by
                )
                await self._query_repository.save(query)
                case.add_query(query)

            # Commit automático al salir del context manager
            # Si hay error, rollback automático de caso y queries
            await self._uow.commit()

            return case
```

### Savepoints para transacciones anidadas

```python
async def complex_operation(self) -> None:
    async with self._uow:
        # Operación principal
        await self._repository.save(entity1)

        # Savepoint para sub-operación
        async with self._connection.transaction():
            try:
                await self._repository.save(entity2)
                # Si falla aquí, solo se deshace entity2
            except Exception:
                # El savepoint se deshace automáticamente
                logger.error("Sub-operación falló")

        # Continuar con operación principal
        await self._repository.save(entity3)

        # Commit de todo
        await self._uow.commit()
```

---

## Versionado de API

### Estrategia: Versionado por URL

```python
# app/main.py
from fastapi import FastAPI
from app.api.v1.routers import cases as cases_v1
from app.api.v2.routers import cases as cases_v2

app = FastAPI(title="Tracker API", version="2.0.0")

# API v1
api_v1 = FastAPI(title="API v1")
api_v1.include_router(cases_v1.router)

# API v2
api_v2 = FastAPI(title="API v2")
api_v2.include_router(cases_v2.router)

# Mount versiones
app.mount("/api/v1", api_v1)
app.mount("/api/v2", api_v2)

# Healthcheck sin versión
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Deprecación de versiones

```python
# app/api/v1/routers/cases.py
from fastapi import APIRouter, Header
import warnings

router = APIRouter()

@router.get(
    "/cases/{case_id}",
    deprecated=True,
    description="⚠️ Esta versión será eliminada el 2026-06-01. Usar /api/v2/cases/{case_id}"
)
async def get_case_v1(case_id: UUID):
    # Agregar header de deprecación
    return {
        "data": {...},
        "warning": "Esta API está deprecada. Migrar a v2 antes del 2026-06-01"
    }
```

### Versionado de schemas

```python
# app/api/v1/schemas/cases.py
class CaseResponseV1(BaseModel):
    id: UUID
    title: str
    case_type: str
    priority: str
    status: str
    created_by: str

# app/api/v2/schemas/cases.py
class CaseResponseV2(BaseModel):
    id: UUID
    title: str
    description: str  # Nuevo campo
    case_type: str
    priority: str
    status: str
    created_by: str
    created_at: datetime  # Nuevo campo
    queries_count: int  # Nuevo campo agregado
```

---

## Migraciones

### Sistema de migraciones sin ORM

```python
# migrations/migration_manager.py
import asyncpg
from pathlib import Path
from typing import List
import re

class MigrationManager:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.migrations_dir = Path("migrations")
        self.rollback_dir = self.migrations_dir / "rollback"

    async def init_migrations_table(self) -> None:
        """Crea la tabla de control de migraciones"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    checksum VARCHAR(64) NOT NULL
                )
            """)
        finally:
            await conn.close()

    def get_migration_files(self) -> List[tuple]:
        """Obtiene lista de archivos de migración ordenados"""
        pattern = re.compile(r'^(\d{3})_(.+)\.sql$')
        migrations = []

        for file in sorted(self.migrations_dir.glob("*.sql")):
            match = pattern.match(file.name)
            if match:
                version = int(match.group(1))
                name = match.group(2)
                migrations.append((version, name, file))

        return migrations

    async def get_applied_migrations(self, conn) -> set:
        """Obtiene versiones ya aplicadas"""
        rows = await conn.fetch(
            "SELECT version FROM schema_migrations ORDER BY version"
        )
        return {row['version'] for row in rows}

    async def migrate(self) -> None:
        """Aplica migraciones pendientes"""
        await self.init_migrations_table()

        conn = await asyncpg.connect(self.connection_string)
        try:
            applied = await self.get_applied_migrations(conn)
            migrations = self.get_migration_files()

            for version, name, file_path in migrations:
                if version in applied:
                    print(f"✓ Migración {version}_{name} ya aplicada")
                    continue

                print(f"Aplicando migración {version}_{name}...")

                # Leer SQL
                sql = file_path.read_text()
                checksum = self._calculate_checksum(sql)

                # Ejecutar en transacción
                async with conn.transaction():
                    await conn.execute(sql)
                    await conn.execute("""
                        INSERT INTO schema_migrations (version, name, checksum)
                        VALUES ($1, $2, $3)
                    """, version, name, checksum)

                print(f"✓ Migración {version}_{name} aplicada correctamente")

        finally:
            await conn.close()

    async def rollback(self, steps: int = 1) -> None:
        """Deshace las últimas N migraciones"""
        conn = await asyncpg.connect(self.connection_string)
        try:
            # Obtener últimas migraciones aplicadas
            rows = await conn.fetch("""
                SELECT version, name FROM schema_migrations
                ORDER BY version DESC
                LIMIT $1
            """, steps)

            for row in rows:
                version = row['version']
                name = row['name']
                rollback_file = self.rollback_dir / f"{version:03d}_{name}.sql"

                if not rollback_file.exists():
                    raise FileNotFoundError(
                        f"Archivo de rollback no encontrado: {rollback_file}"
                    )

                print(f"Deshaciendo migración {version}_{name}...")

                sql = rollback_file.read_text()

                async with conn.transaction():
                    await conn.execute(sql)
                    await conn.execute(
                        "DELETE FROM schema_migrations WHERE version = $1",
                        version
                    )

                print(f"✓ Migración {version}_{name} deshecha")

        finally:
            await conn.close()

    def _calculate_checksum(self, content: str) -> str:
        """Calcula checksum de una migración"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
```

### Ejemplo de migración

```sql
-- migrations/001_initial_schema.sql
BEGIN;

-- Tabla de casos de soporte
CREATE TABLE support_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    case_type VARCHAR(20) NOT NULL CHECK (case_type IN ('support', 'requirement', 'investigation')),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_support_cases_status ON support_cases(status);
CREATE INDEX idx_support_cases_priority ON support_cases(priority);
CREATE INDEX idx_support_cases_type ON support_cases(case_type);
CREATE INDEX idx_support_cases_created_by ON support_cases(created_by);
CREATE INDEX idx_support_cases_created_at ON support_cases(created_at DESC);
CREATE INDEX idx_support_cases_title_search ON support_cases USING gin(to_tsvector('spanish', title));
CREATE INDEX idx_support_cases_status_priority ON support_cases(status, priority);

-- Tabla de consultas SQL ejecutadas
CREATE TABLE case_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES support_cases(id) ON DELETE CASCADE,
    database_name VARCHAR(255) NOT NULL,
    schema_name VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,
    execution_time_ms INTEGER,
    rows_affected INTEGER,
    executed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    executed_by VARCHAR(255) NOT NULL
);

CREATE INDEX idx_case_queries_case_id ON case_queries(case_id);
CREATE INDEX idx_case_queries_executed_at ON case_queries(executed_at DESC);
CREATE INDEX idx_case_queries_executed_by ON case_queries(executed_by);

COMMIT;
```

```sql
-- migrations/rollback/001_initial_schema.sql
BEGIN;

DROP TABLE IF EXISTS case_queries CASCADE;
DROP TABLE IF EXISTS support_cases CASCADE;

COMMIT;
```

### CLI para migraciones

```python
# manage.py
import asyncio
import sys
from migrations.migration_manager import MigrationManager
from app.config import settings

async def main():
    manager = MigrationManager(settings.DATABASE_URL)

    if len(sys.argv) < 2:
        print("Uso: python manage.py [migrate|rollback|status]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "migrate":
        await manager.migrate()
    elif command == "rollback":
        steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        await manager.rollback(steps)
    elif command == "status":
        await manager.show_status()
    else:
        print(f"Comando desconocido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Performance

### Índices en PostgreSQL

```sql
-- Índices básicos
CREATE INDEX idx_support_cases_status ON support_cases(status);
CREATE INDEX idx_support_cases_priority ON support_cases(priority);
CREATE INDEX idx_support_cases_created_by ON support_cases(created_by);

-- Índice compuesto para queries frecuentes
CREATE INDEX idx_support_cases_status_priority ON support_cases(status, priority);
CREATE INDEX idx_support_cases_type_status ON support_cases(case_type, status);

-- Índice parcial (solo casos abiertos)
CREATE INDEX idx_support_cases_open ON support_cases(priority, created_at)
WHERE status = 'open';

-- Índice para búsquedas de texto
CREATE INDEX idx_support_cases_title_gin ON support_cases USING gin(to_tsvector('spanish', title));
CREATE INDEX idx_support_cases_description_gin ON support_cases USING gin(to_tsvector('spanish', description));

-- Índices para case_queries
CREATE INDEX idx_case_queries_case_id ON case_queries(case_id);
CREATE INDEX idx_case_queries_executed_at ON case_queries(executed_at DESC);
```

### Query Optimization

```python
# ✅ BUENO: Select solo columnas necesarias
async def get_case_summaries(self) -> List[dict]:
    query = """
        SELECT id, title, status, priority, case_type, created_by
        FROM support_cases
        WHERE status != 'closed'
        ORDER BY created_at DESC
        LIMIT 100
    """
    return await self._db.fetch(query)

# ❌ MALO: Select *
async def get_all_cases(self):
    query = "SELECT * FROM support_cases"  # Trae todas las columnas
    return await self._db.fetch(query)
```

### Paginación eficiente

```python
# app/api/v1/schemas/common.py
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

# Repository
async def get_cases_paginated(
    self,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> tuple[List[SupportCase], int]:
    """Paginación con filtros"""
    offset = (page - 1) * page_size
    conditions = []
    params = []
    param_idx = 1

    if status:
        conditions.append(f"status = ${param_idx}")
        params.append(status)
        param_idx += 1

    if priority:
        conditions.append(f"priority = ${param_idx}")
        params.append(priority)
        param_idx += 1

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Query para datos
    query = f"""
        SELECT id, title, description, case_type, priority, status, created_by, created_at, updated_at
        FROM support_cases
        WHERE {where_clause}
        ORDER BY created_at DESC
        LIMIT ${param_idx} OFFSET ${param_idx + 1}
    """
    params.extend([page_size, offset])
    rows = await self._db.fetch(query, *params)

    # Query para total (puede ser cacheado)
    count_query = f"SELECT COUNT(*) FROM support_cases WHERE {where_clause}"
    total = await self._db.fetchval(count_query, *params[:-2])  # Excluir LIMIT y OFFSET

    cases = [self._map_to_entity(row) for row in rows]
    return cases, total
```

### Batch Operations

```python
async def save_many_queries(self, queries: List[CaseQuery]) -> None:
    """Guarda múltiples queries en batch"""
    query = """
        INSERT INTO case_queries (
            id, case_id, database_name, schema_name, query_text,
            execution_time_ms, rows_affected, executed_at, executed_by
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    """

    values = [
        (
            q.id,
            q.case_id,
            q.database_name,
            q.schema_name,
            q.query_text,
            q.execution_time_ms,
            q.rows_affected,
            q.executed_at,
            q.executed_by
        )
        for q in queries
    ]

    await self._db.executemany(query, values)
```

---

## Observabilidad

### Structured Logging

```python
# app/infrastructure/logging/setup.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configura logging estructurado"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)

    # Formato JSON
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

# Uso
logger = setup_logging()

logger.info(
    "Case created",
    extra={
        "case_id": str(case.id),
        "created_by": case.created_by,
        "action": "case.created"
    }
)
```

### Request ID Tracking

```python
# app/api/middleware/request_id.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import logging

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generar o extraer request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Agregar a contexto de logging
        with logging.LoggerAdapter(logger, {"request_id": request_id}):
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
```

### Métricas

```python
# app/infrastructure/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps

# Definir métricas
request_count = Counter(
    'http_requests_total',
    'Total de requests HTTP',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'Duración de requests HTTP',
    ['method', 'endpoint']
)

active_cases = Gauge(
    'active_cases_total',
    'Total de casos activos'
)

# Decorator para medir duración
def track_time(metric: Histogram, labels: dict):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.time() - start
                metric.labels(**labels).observe(duration)
        return wrapper
    return decorator

# Uso en routers
@router.post("/cases")
@track_time(
    request_duration,
    {"method": "POST", "endpoint": "/cases"}
)
async def create_case(...):
    request_count.labels(
        method="POST",
        endpoint="/cases",
        status=201
    ).inc()
    # ...
```

### Health Checks

```python
# app/api/health.py
from fastapi import APIRouter, status
from app.infrastructure.database.connection import DatabaseConnection

router = APIRouter()

@router.get("/health")
async def health():
    """Health check básico"""
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness(db: DatabaseConnection):
    """Readiness check - verifica dependencias"""
    try:
        # Verificar DB
        await db.execute("SELECT 1")

        return {
            "status": "ready",
            "checks": {
                "database": "healthy"
            }
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "checks": {
                "database": "unhealthy",
                "error": str(e)
            }
        }

@router.get("/health/live")
async def liveness():
    """Liveness check - verifica que el proceso esté vivo"""
    return {"status": "alive"}
```

---

## Testing

### Estructura de tests

```python
# tests/conftest.py
import pytest
import asyncio
from typing import AsyncGenerator
import asyncpg
from app.infrastructure.database.connection import DatabaseConnection
from app.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """Event loop para toda la sesión de tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_connection():
    """Conexión a DB de test"""
    conn = DatabaseConnection()
    await conn.connect()
    yield conn
    await conn.disconnect()

@pytest.fixture(autouse=True)
async def clean_database(db_connection):
    """Limpia la DB antes de cada test"""
    await db_connection.execute("TRUNCATE case_queries, support_cases CASCADE")
    yield
```

### Tests Unitarios (Domain)

```python
# tests/unit/domain/entities/test_case.py
import pytest
from uuid import uuid4
from app.domain.entities.case import SupportCase
from app.domain.value_objects.case_status import CaseStatus
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.domain.exceptions import DomainValidationError

class TestSupportCase:
    def test_create_case_with_valid_data(self):
        """Debe crear un caso válido"""
        case = SupportCase.create(
            title="Test case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="test@example.com",
            description="Description"
        )

        assert case.title == "Test case"
        assert case.status == CaseStatus.OPEN
        assert case.description == "Description"
        assert case.case_type == CaseType.SUPPORT
        assert case.priority == CasePriority.HIGH

    def test_create_case_with_empty_title_raises_error(self):
        """No debe permitir título vacío"""
        with pytest.raises(DomainValidationError, match="título no puede estar vacío"):
            SupportCase.create(
                title="",
                case_type=CaseType.SUPPORT,
                priority=CasePriority.MEDIUM,
                created_by="test@example.com"
            )

    def test_create_case_with_invalid_email_raises_error(self):
        """No debe permitir email inválido"""
        with pytest.raises(DomainValidationError, match="email del creador no es válido"):
            SupportCase.create(
                title="Test",
                case_type=CaseType.SUPPORT,
                priority=CasePriority.MEDIUM,
                created_by="invalid-email"
            )

    def test_mark_as_resolved_from_in_progress(self):
        """Debe permitir resolver caso en progreso"""
        case = SupportCase.create(
            title="Test",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.MEDIUM,
            created_by="test@example.com"
        )
        case.mark_as_in_progress()
        case.mark_as_resolved()

        assert case.status == CaseStatus.RESOLVED

    def test_close_case_from_resolved(self):
        """Debe permitir cerrar caso resuelto"""
        case = SupportCase.create(
            title="Test",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.MEDIUM,
            created_by="test@example.com"
        )
        case.mark_as_in_progress()
        case.mark_as_resolved()
        case.close()

        assert case.status == CaseStatus.CLOSED
```

### Tests de Integración (Repository)

```python
# tests/integration/infrastructure/repositories/test_case_repository.py
import pytest
from uuid import uuid4
from app.domain.entities.case import SupportCase
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.infrastructure.database.repositories.case_repository_impl import CaseRepositoryImpl

@pytest.mark.asyncio
class TestCaseRepository:
    async def test_save_and_retrieve_case(self, db_connection):
        """Debe guardar y recuperar un caso"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear caso
        case = SupportCase.create(
            title="Test case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="test@example.com"
        )

        # Guardar
        await repo.save(case)

        # Recuperar
        retrieved = await repo.get_by_id(case.id)

        assert retrieved is not None
        assert retrieved.id == case.id
        assert retrieved.title == case.title
        assert retrieved.status == case.status

    async def test_get_by_created_by_returns_user_cases(self, db_connection):
        """Debe retornar solo los casos del usuario creador"""
        repo = CaseRepositoryImpl(db_connection)

        user_email = "user1@example.com"
        other_user_email = "user2@example.com"

        # Crear casos
        case1 = SupportCase.create(
            title="Case 1",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by=user_email
        )
        case2 = SupportCase.create(
            title="Case 2",
            case_type=CaseType.REQUIREMENT,
            priority=CasePriority.MEDIUM,
            created_by=user_email
        )
        case3 = SupportCase.create(
            title="Case 3",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.LOW,
            created_by=other_user_email
        )

        await repo.save(case1)
        await repo.save(case2)
        await repo.save(case3)

        # Obtener casos del usuario
        user_cases, total = await repo.get_all(created_by=user_email)

        assert len(user_cases) == 2
        assert total == 2
        assert all(c.created_by == user_email for c in user_cases)
```

### Tests de Use Cases

```python
# tests/unit/application/use_cases/test_create_case.py
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock
from app.application.use_cases.create_case import CreateCaseUseCase
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.domain.exceptions import DomainValidationError

@pytest.mark.asyncio
class TestCreateCaseUseCase:
    async def test_create_case_successfully(self):
        """Debe crear caso exitosamente"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()
        uow = AsyncMock()

        # Use case
        use_case = CreateCaseUseCase(case_repo, query_repo, uow)

        # Ejecutar
        case = await use_case.execute(
            title="New case",
            description="Description",
            case_type="support",
            priority="high",
            queries=[
                {
                    "database_name": "test_db",
                    "schema_name": "public",
                    "query_text": "SELECT * FROM test"
                }
            ],
            created_by="test@example.com"
        )

        # Verificar
        assert case.title == "New case"
        assert case.created_by == "test@example.com"
        case_repo.save.assert_called_once()
        query_repo.save.assert_called_once()
        uow.commit.assert_called_once()

    async def test_create_case_with_invalid_type_raises_error(self):
        """Debe fallar si el tipo de caso es inválido"""
        case_repo = AsyncMock()
        query_repo = AsyncMock()
        uow = AsyncMock()

        use_case = CreateCaseUseCase(case_repo, query_repo, uow)

        with pytest.raises(ValueError):  # CaseType enum validation
            await use_case.execute(
                title="New case",
                description="Description",
                case_type="invalid_type",
                priority="high",
                queries=[],
                created_by="test@example.com"
            )
```

### Tests E2E

```python
# tests/e2e/test_case_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
class TestCaseAPI:
    async def test_create_case_endpoint(self, auth_token):
        """Test completo del endpoint de crear caso"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/cases",
                json={
                    "title": "Test case",
                    "description": "Description",
                    "case_type": "support",
                    "priority": "high",
                    "queries": [
                        {
                            "database_name": "test_db",
                            "schema_name": "public",
                            "query_text": "SELECT * FROM test"
                        }
                    ],
                    "created_by": "test@example.com"
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )

            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test case"
            assert data["status"] == "open"
            assert data["case_type"] == "support"
```

---

## Anti-patterns

### ❌ 1. Anemic Domain Model

**Problema:** Entidades sin comportamiento, solo datos.

```python
# ❌ MALO
@dataclass
class SupportCase:
    id: UUID
    title: str
    status: str
    # Solo getters/setters, sin lógica

# Lógica en servicio externo
class CaseService:
    def resolve_case(self, case: SupportCase):
        if case.status != "in_progress":
            raise ValueError("...")
        case.status = "resolved"  # ❌ Lógica de negocio fuera de la entidad
```

```python
# ✅ BUENO
@dataclass
class SupportCase:
    id: UUID
    title: str
    status: CaseStatus

    def mark_as_resolved(self):  # ✅ Comportamiento en la entidad
        if self.status not in [CaseStatus.OPEN, CaseStatus.IN_PROGRESS]:
            raise DomainValidationError("...")
        self.status = CaseStatus.RESOLVED
```

### ❌ 2. God Object / Fat Controller

**Problema:** Un controller que hace todo.

```python
# ❌ MALO
@router.post("/cases")
async def create_case(request: CreateCaseRequest, db: Database):
    # Validación
    if not request.title:
        raise ValueError("...")

    # Lógica de negocio
    if len(request.queries) > 10:
        raise ValueError("Demasiadas queries")

    # Persistencia
    await db.execute("INSERT INTO support_cases (...) VALUES (...)")
    for query in request.queries:
        await db.execute("INSERT INTO case_queries (...) VALUES (...)")

    # Notificación
    await send_email(...)

    return {"status": "ok"}
```

```python
# ✅ BUENO: Cada capa con su responsabilidad
@router.post("/cases")
async def create_case(
    request: CreateCaseRequest,
    use_case: CreateCaseUseCase = Depends()
):
    case = await use_case.execute(...)  # Use case orquesta
    return CaseResponse.from_entity(case)
```

### ❌ 3. Leaky Abstractions

**Problema:** Detalles de infraestructura en el dominio.

```python
# ❌ MALO: Entidad depende de asyncpg
from asyncpg import Record

@dataclass
class SupportCase:
    @classmethod
    def from_record(cls, record: Record):  # ❌ Dependencia de infraestructura
        return cls(...)
```

```python
# ✅ BUENO: Mapeo en la capa de infraestructura
class CaseRepositoryImpl:
    def _map_to_entity(self, row: Record) -> SupportCase:  # ✅ Mapeo en repo
        return SupportCase(
            id=row["id"],
            title=row["title"],
            ...
        )
```

### ❌ 4. Service Layer Bypass

**Problema:** Controllers acceden directamente a repositorios.

```python
# ❌ MALO
@router.get("/cases")
async def get_cases(repo: CaseRepository = Depends()):
    return await repo.get_all()  # ❌ Saltea la capa de aplicación
```

```python
# ✅ BUENO
@router.get("/cases")
async def get_cases(use_case: GetCasesUseCase = Depends()):
    return await use_case.execute()  # ✅ Pasa por use case
```

### ❌ 5. Transaction Script

**Problema:** Procedural, sin encapsulación de dominio.

```python
# ❌ MALO: Script procedural
async def create_case_with_queries(case_data, queries_data, db):
    case = await db.insert_case(case_data)
    for query_data in queries_data:
        query_data['case_id'] = case['id']
        await db.insert_query(query_data)
    return case
```

```python
# ✅ BUENO: Use case + entidades ricas
class CreateCaseUseCase:
    async def execute(self, title, description, case_type, priority, queries, created_by):
        async with self._uow:
            # Crear entidad de dominio
            case = SupportCase.create(
                title=title,
                description=description,
                case_type=CaseType(case_type),
                priority=CasePriority(priority),
                created_by=created_by
            )

            # Persistir caso
            await self._case_repo.save(case)

            # Crear y persistir queries
            for query_data in queries:
                query = CaseQuery.create(
                    case_id=case.id,
                    database_name=query_data["database_name"],
                    schema_name=query_data["schema_name"],
                    query_text=query_data["query_text"],
                    executed_by=created_by
                )
                await self._query_repo.save(query)
                case.add_query(query)

            await self._uow.commit()
            return case
```

### ❌ 6. Primitive Obsession

**Problema:** Usar primitivos en lugar de Value Objects.

```python
# ❌ MALO
@dataclass
class User:
    email: str  # ❌ Sin validación

user = User(email="invalid-email")  # ❌ Acepta valores inválidos
```

```python
# ✅ BUENO: Value Object
@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError("Email inválido")

@dataclass
class User:
    email: Email  # ✅ Validación garantizada

user = User(email=Email("test@example.com"))  # ✅ Válido
user = User(email=Email("invalid"))  # ❌ Raises ValueError
```

---

## 12 Factor App

### I. Codebase

Un codebase rastreado en control de versiones, múltiples deploys.

```bash
git init
git remote add origin https://github.com/user/tracker-backend.git
```

### II. Dependencies

Declarar y aislar dependencias explícitamente.

```toml
# pyproject.toml
[tool.poetry]
name = "tracker-backend"
version = "1.0.0"

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "0.111.0"
asyncpg = "^0.29.0"
pydantic = "^2.0"
pydantic-settings = "^2.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
bcrypt = "^4.0"

[tool.poetry.dev-dependencies]
pytest = "^7.4"
pytest-asyncio = "^0.21"
httpx = "^0.25"
```

### III. Config

Almacenar configuración en el entorno.

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Database
    DB_HOST: str
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    APP_NAME: str = "Tracker API"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

settings = Settings()
```

```bash
# .env
DB_HOST=localhost
DB_PORT=5432
DB_USER=tracker_user
DB_PASSWORD=secret_password
DB_NAME=tracker_db
SECRET_KEY=your-secret-key-here
DEBUG=false
```

### IV. Backing Services

Tratar servicios externos como recursos adjuntos.

```python
# Fácil de cambiar de PostgreSQL local a RDS
DATABASE_URL=postgresql://user:pass@localhost:5432/db  # Local
DATABASE_URL=postgresql://user:pass@rds.aws.com:5432/db  # AWS RDS

```

### V. Build, Release, Run

Separar estrictamente las etapas de build y run.

```dockerfile
# docker/Dockerfile
# Build stage
FROM python:3.12-slim as builder
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

# Run stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app ./app
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### VI. Processes

Ejecutar la app como uno o más procesos stateless.


### VII. Port Binding

Exportar servicios via port binding.

```python
# app/main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,  # Port binding
        reload=settings.DEBUG
    )
```

### VIII. Concurrency

Escalar mediante el modelo de procesos.

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    image: tracker-api:latest
    deploy:
      replicas: 3  # Múltiples procesos
    ports:
      - "8000:8000"
```

### IX. Disposability

Maximizar robustez con fast startup y graceful shutdown.

```python
# app/main.py
@app.on_event("startup")
async def startup():
    """Fast startup"""
    await db.connect()
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown():
    """Graceful shutdown"""
    await db.disconnect()
    logger.info("Application stopped")
```

### X. Dev/Prod Parity

Mantener desarrollo y producción lo más similares posible.

```yaml
# docker-compose.yml (mismo para dev y prod)
version: '3.8'
services:
  api:
    build: .
    environment:
      - DATABASE_URL=${DATABASE_URL}
    depends_on:
      - db

  db:
    image: postgres:16.3  # Misma versión en dev y prod
```

### XI. Logs

Tratar logs como streams de eventos.

```python
# ❌ MALO: Escribir a archivo
logging.basicConfig(filename='app.log')

# ✅ BUENO: Escribir a stdout
logging.basicConfig(stream=sys.stdout)

# El orquestador (Docker, K8s) maneja la agregación
```

### XII. Admin Processes

Ejecutar tareas admin/management como procesos one-off.

```python
# manage.py
import asyncio
from app.infrastructure.database.connection import DatabaseConnection

async def create_initial_case():
    """Proceso administrativo one-off para crear caso inicial"""
    db = DatabaseConnection()
    await db.connect()

    # Crear caso inicial de ejemplo
    await db.execute("""
        INSERT INTO support_cases (title, description, case_type, priority, status, created_by)
        VALUES ('Caso inicial', 'Caso de ejemplo para testing', 'support', 'medium', 'open', 'admin@example.com')
    """)

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
```

---

## Configuración de Docker

```dockerfile
# docker/Dockerfile
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Instalar Poetry
RUN pip install poetry

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock ./

# Instalar dependencias
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copiar código
COPY app ./app
COPY migrations ./migrations

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://tracker_user:tracker_pass@db:5432/tracker_db
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - backend

  db:
    image: postgres:16.3-alpine
    environment:
      - POSTGRES_USER=tracker_user
      - POSTGRES_PASSWORD=tracker_pass
      - POSTGRES_DB=tracker_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tracker_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

volumes:
  postgres_data:

networks:
  backend:
    driver: bridge
```

---

## Resumen de Principios

1. **Separación de responsabilidades**: Cada capa tiene un propósito claro
2. **Dependency Inversion**: Las dependencias apuntan hacia el dominio
3. **Independencia de frameworks**: La lógica de negocio no depende de FastAPI o PostgreSQL
4. **Testeable**: Cada capa puede testearse independientemente
5. **Seguridad primero**: SQL injection prevention, JWT, rate limiting
6. **Observabilidad**: Logs estructurados, métricas, health checks
7. **Configuración por entorno**: 12 Factor App
8. **Performance**: Índices, caching, paginación, batch operations
9. **Transacciones ACID**: Unit of Work pattern
10. **Clean Code**: No duplicación, naming claro, funciones pequeñas

---

## Checklist de Implementación

### Al crear una nueva feature:

- [ ] ¿La entidad de dominio tiene toda la lógica de negocio?
- [ ] ¿Los repositorios son interfaces en el dominio?
- [ ] ¿El use case orquesta sin lógica de negocio?
- [ ] ¿Las queries usan parámetros (no concatenación)?
- [ ] ¿Hay tests unitarios para entidades?
- [ ] ¿Hay tests de integración para repositorios?
- [ ] ¿Se usa Unit of Work para transacciones?
- [ ] ¿Los logs son estructurados?
- [ ] ¿Hay validación de entrada con Pydantic?
- [ ] ¿Los errores tienen manejo apropiado?
- [ ] ¿Se consideró el performance (índices, N+1)?
- [ ] ¿La configuración viene del entorno?

---

Este documento es una referencia viva. Actualízalo conforme evolucione el proyecto.
