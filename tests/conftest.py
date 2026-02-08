import pytest
import asyncio
from app.infrastructure.database.connection import DatabaseConnection
from app.infrastructure.database.db import db
from app.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Event loop para toda la sesión de tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def initialize_app_db():
    """Inicializa la conexión de base de datos de la app para tests"""
    await db.connect()
    yield
    await db.disconnect()


@pytest.fixture(scope="session")
async def db_connection():
    """Conexión a DB de test (reutiliza la conexión de la app)"""
    return db


@pytest.fixture(autouse=True)
async def clean_database(db_connection):
    """Limpia la DB antes de cada test"""
    try:
        await db_connection.execute("TRUNCATE case_queries, support_cases CASCADE")
    except Exception:
        # Si las tablas no existen, no hacer nada
        pass
    yield
