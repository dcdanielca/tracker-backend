import asyncpg
from typing import Optional, List, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Gestiona el pool de conexiones a PostgreSQL"""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """Crea el pool de conexiones"""
        try:
            self._pool = await asyncpg.create_pool(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=settings.DB_NAME,
                min_size=10,
                max_size=20,
                command_timeout=60,
                max_queries=50000,
                max_inactive_connection_lifetime=300
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise

    async def disconnect(self) -> None:
        """Cierra el pool de conexiones"""
        if self._pool:
            await self._pool.close()
            logger.info("Database connection pool closed")

    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """Ejecuta query que retorna múltiples registros"""
        if not self._pool:
            raise RuntimeError("Database pool not initialized")
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Ejecuta query que retorna un registro"""
        if not self._pool:
            raise RuntimeError("Database pool not initialized")
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args) -> Any:
        """Ejecuta query que retorna un valor único"""
        if not self._pool:
            raise RuntimeError("Database pool not initialized")
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def execute(self, query: str, *args) -> str:
        """Ejecuta query sin retorno (INSERT, UPDATE, DELETE)"""
        if not self._pool:
            raise RuntimeError("Database pool not initialized")
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def executemany(self, query: str, args_list: List[tuple]) -> None:
        """Ejecuta múltiples queries en batch"""
        if not self._pool:
            raise RuntimeError("Database pool not initialized")
        async with self._pool.acquire() as conn:
            await conn.executemany(query, args_list)

    def transaction(self):
        """Retorna un context manager para transacciones"""
        if not self._pool:
            raise RuntimeError("Database pool not initialized")
        return self._pool.acquire()
