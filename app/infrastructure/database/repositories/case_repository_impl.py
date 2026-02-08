from uuid import UUID
from typing import Optional
import asyncpg
from app.domain.entities.case import SupportCase
from app.domain.repositories.case_repository import CaseRepository
from app.domain.value_objects.case_status import CaseStatus
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.infrastructure.database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class CaseRepositoryImpl(CaseRepository):
    def __init__(self, db: DatabaseConnection, connection: Optional[asyncpg.Connection] = None):
        self._db = db
        self._connection = connection  # Conexión de transacción si está disponible

    async def save(self, case: SupportCase) -> None:
        """Guarda un caso (solo INSERT)"""
        query = """
            INSERT INTO support_cases (
                id, title, description, case_type, priority,
                status, created_by, created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """

        if self._connection:
            # Usar conexión de transacción
            await self._connection.execute(
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
        else:
            # Usar pool normal
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
        logger.debug(f"Case saved: {case.id}")

    async def get_by_id(self, case_id: UUID) -> Optional[SupportCase]:
        """Obtiene un caso por ID"""
        query = """
            SELECT
                id, title, description, case_type, priority,
                status, created_by, created_at, updated_at
            FROM support_cases
            WHERE id = $1
        """

        if self._connection:
            row = await self._connection.fetchrow(query, case_id)
        else:
            row = await self._db.fetchrow(query, case_id)

        if not row:
            return None

        return self._map_to_entity(row)

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
