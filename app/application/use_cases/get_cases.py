from typing import List, Tuple, Optional
from datetime import datetime
from app.domain.entities.case import SupportCase
from app.domain.repositories.case_repository import CaseRepository
from app.domain.repositories.query_repository import QueryRepository
import logging

logger = logging.getLogger(__name__)


class GetCasesUseCase:
    def __init__(self, case_repository: CaseRepository, query_repository: QueryRepository):
        self._case_repository = case_repository
        self._query_repository = query_repository

    async def execute(
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
        page_size: int = 10,
    ) -> Tuple[List[Tuple[SupportCase, int]], int]:
        """
        Obtiene casos con filtros y paginación.

        Returns:
            Tuple con lista de (caso, queries_count) y total de casos
        """
        # Obtener casos con filtros
        cases, total = await self._case_repository.get_all(
            status=status,
            priority=priority,
            case_type=case_type,
            created_by=created_by,
            search=search,
            date_gte=date_gte,
            date_lte=date_lte,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

        # Para cada caso, obtener el conteo de queries
        # Esto es más eficiente que obtener todas las queries
        cases_with_count = []
        for case in cases:
            queries = await self._query_repository.get_by_case_id(case.id)
            queries_count = len(queries)
            cases_with_count.append((case, queries_count))

        logger.info(
            f"Retrieved {len(cases)} cases (page {page}, total {total})",
            extra={
                "page": page,
                "page_size": page_size,
                "total": total,
                "filters": {
                    "status": status,
                    "priority": priority,
                    "case_type": case_type,
                    "created_by": created_by,
                    "search": search,
                },
            },
        )

        return cases_with_count, total
