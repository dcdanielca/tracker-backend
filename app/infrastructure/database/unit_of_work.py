from typing import Optional
import asyncpg
from app.application.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class PostgreSQLUnitOfWork(UnitOfWork):
    """Implementación de Unit of Work para PostgreSQL"""

    def __init__(self, db: DatabaseConnection):
        self._db = db
        self._connection: Optional[asyncpg.Connection] = None
        self._transaction: Optional[asyncpg.Transaction] = None

    async def __aenter__(self) -> "PostgreSQLUnitOfWork":
        """Inicia una transacción"""
        pool = getattr(self._db, '_pool', None)
        if not pool:
            raise RuntimeError("Database pool not initialized")
        
        self._connection = await pool.acquire()
        self._transaction = self._connection.transaction()
        await self._transaction.start()
        logger.debug("Transaction started")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Finaliza la transacción"""
        try:
            if exc_type is not None:
                # Hubo una excepción, hacer rollback
                await self.rollback()
                logger.debug("Transaction rolled back due to exception")
            else:
                # No hubo excepciones, hacer commit
                await self.commit()
                logger.debug("Transaction committed")
        finally:
            if self._connection:
                pool = getattr(self._db, '_pool', None)
                if pool:
                    await pool.release(self._connection)
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
        if not self._connection:
            raise RuntimeError("No active transaction")
        return self._connection
