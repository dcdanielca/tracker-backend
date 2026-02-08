from uuid import UUID
from typing import List, Optional
import asyncpg
from app.domain.entities.case import CaseQuery
from app.domain.repositories.query_repository import QueryRepository
from app.infrastructure.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class QueryRepositoryImpl(QueryRepository):
    def __init__(self, db: DatabaseConnection, connection: Optional[asyncpg.Connection] = None):
        self._db = db
        self._connection = connection  # Conexión de transacción si está disponible

    async def save(self, query: CaseQuery) -> None:
        """Guarda una query"""
        sql = """
            INSERT INTO case_queries (
                id, case_id, database_name, schema_name, query_text,
                execution_time_ms, rows_affected, executed_at, executed_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """

        if self._connection:
            # Usar conexión de transacción
            await self._connection.execute(
                sql,
                query.id,
                query.case_id,
                query.database_name,
                query.schema_name,
                query.query_text,
                query.execution_time_ms,
                query.rows_affected,
                query.executed_at,
                query.executed_by,
            )
        else:
            # Usar pool normal
            await self._db.execute(
                sql,
                query.id,
                query.case_id,
                query.database_name,
                query.schema_name,
                query.query_text,
                query.execution_time_ms,
                query.rows_affected,
                query.executed_at,
                query.executed_by,
            )
        logger.debug(f"Query saved: {query.id}")

    async def save_many(self, queries: List[CaseQuery]) -> None:
        """Guarda múltiples queries en batch"""
        if not queries:
            return

        sql = """
            INSERT INTO case_queries (
                id, case_id, database_name, schema_name, query_text,
                execution_time_ms, rows_affected, executed_at, executed_by
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """

        # Preparar valores para bulk insert
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
                q.executed_by,
            )
            for q in queries
        ]

        if self._connection:
            # Usar conexión de transacción
            await self._connection.executemany(sql, values)
        else:
            # Usar pool normal
            await self._db.executemany(sql, values)

        logger.debug(f"Saved {len(queries)} queries in batch")

    async def get_by_case_id(self, case_id: UUID) -> List[CaseQuery]:
        """Obtiene todas las queries de un caso"""
        query = """
            SELECT
                id, case_id, database_name, schema_name, query_text,
                execution_time_ms, rows_affected, executed_at, executed_by
            FROM case_queries
            WHERE case_id = $1
            ORDER BY executed_at ASC
        """

        if self._connection:
            rows = await self._connection.fetch(query, case_id)
        else:
            rows = await self._db.fetch(query, case_id)

        return [self._map_to_entity(row) for row in rows]

    def _map_to_entity(self, row: asyncpg.Record) -> CaseQuery:
        """Mapea un registro de DB a una entidad de dominio"""
        return CaseQuery(
            id=row["id"],
            case_id=row["case_id"],
            database_name=row["database_name"],
            schema_name=row["schema_name"],
            query_text=row["query_text"],
            execution_time_ms=row["execution_time_ms"],
            rows_affected=row["rows_affected"],
            executed_at=row["executed_at"],
            executed_by=row["executed_by"],
        )
