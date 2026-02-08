from uuid import UUID
from typing import Optional, List, Tuple
from datetime import datetime
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

    async def get_all(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        case_type: Optional[str] = None,
        created_by: Optional[str] = None,
        search: Optional[str] = None,
        date_gte: Optional[datetime] = None,
        date_lte: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[SupportCase], int]:
        """Obtiene casos con filtros y paginación"""
        offset = (page - 1) * page_size
        conditions = []
        params = []
        param_idx = 1

        # Construir condiciones dinámicamente
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
            param_idx += 1

        if date_gte:
            conditions.append(f"created_at >= ${param_idx}")
            params.append(date_gte)
            param_idx += 1

        if date_lte:
            conditions.append(f"created_at <= ${param_idx}")
            params.append(date_lte)
            param_idx += 1

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Validar sort_by para prevenir SQL injection
        allowed_sort_fields = ["status", "priority", "case_type", "created_by", "created_at", "title"]
        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        # Validar sort_order
        sort_order_sql = "DESC" if sort_order.lower() == "desc" else "ASC"

        # Query para datos
        query = f"""
            SELECT
                id, title, description, case_type, priority,
                status, created_by, created_at, updated_at
            FROM support_cases
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order_sql}
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([page_size, offset])

        # Ejecutar query
        if self._connection:
            rows = await self._connection.fetch(query, *params)
        else:
            rows = await self._db.fetch(query, *params)

        # Query para total (sin LIMIT y OFFSET)
        count_query = f"""
            SELECT COUNT(*) FROM support_cases
            WHERE {where_clause}
        """
        count_params = params[:-2]  # Excluir LIMIT y OFFSET

        if self._connection:
            total = await self._connection.fetchval(count_query, *count_params)
        else:
            total = await self._db.fetchval(count_query, *count_params)

        cases = [self._map_to_entity(row) for row in rows]
        logger.debug(f"Retrieved {len(cases)} cases (total: {total})")

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
