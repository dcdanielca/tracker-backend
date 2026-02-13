# Claude Conversation Log

Session ID: 0cb4063d-8d09-4656-832b-38e981f96b00
Date: 2026-02-08 14:13:32

---

## 👤 User

Actúa como un Senior Backend Engineer.

Crea un archivo `claude.md` con guía de estilos y arquitectura
basado en:

- Django Style Guide
- Clean Architecture
- Domain Driven Design (light)
- 12 Factor App
- Best practices de microservicios

Stack:
- Python 3.12
- FastAPI 0.111.0
- PostgreSQL 16.3
- Sin ORM (sanitizar queries para evitar SQL injection)
- Pydantic
- Pytest
- Docker

Incluye:

- Arquitectura por capas
- Flujo request → domain → db
- Manejo de transacciones
- Versionado
- Migraciones sin ORM
- Performance
- Seguridad
- Observabilidad
- Testing
- Anti-patterns

Formato: Markdown
Idioma: Español
Nivel: Senior
Con ejemplos.


---

## 🤖 Claude

Voy a crear una guía completa de arquitectura y estilos para tu proyecto backend con FastAPI.

---

## 🤖 Claude

Primero verificaré si el archivo ya existe.

---

## 🤖 Claude

El archivo existe pero está vacío. Ahora lo escribiré con el contenido completo de la guía.

---

## 🤖 Claude

He creado exitosamente el archivo `claude.md` con una guía completa de arquitectura y estilos para tu proyecto backend con FastAPI.

La guía incluye:

**Fundamentos:**
- Principios de Clean Architecture y DDD
- Estructura completa del proyecto por capas
- Flujo detallado de requests

**Implementación:**
- Ejemplos de Entidades, Value Objects y Repositories
- Acceso a PostgreSQL sin ORM con prevención de SQL injection
- Unit of Work pattern para transacciones
- Sistema de migraciones SQL personalizado

**Calidad y Seguridad:**
- Autenticación JWT, password hashing, rate limiting
- Testing (unitarios, integración, E2E)
- Observabilidad (logs estructurados, métricas, health checks)

**Performance:**
- Índices de PostgreSQL
- Caching con Redis
- Paginación eficiente
- Batch operations

**Buenas Prácticas:**
- Versionado de API
- 12 Factor App
- Anti-patterns a evitar
- Docker configuration

Todos los ejemplos están en español y a nivel senior, con código completo y funcional que puedes usar como referencia durante el desarrollo del proyecto.

---

