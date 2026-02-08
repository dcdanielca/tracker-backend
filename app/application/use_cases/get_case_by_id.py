from uuid import UUID
from typing import Optional
from app.domain.entities.case import SupportCase
from app.domain.repositories.case_repository import CaseRepository
from app.domain.repositories.query_repository import QueryRepository
import logging

logger = logging.getLogger(__name__)


class GetCaseByIdUseCase:
    def __init__(
        self,
        case_repository: CaseRepository,
        query_repository: QueryRepository
    ):
        self._case_repository = case_repository
        self._query_repository = query_repository

    async def execute(self, case_id: UUID) -> Optional[SupportCase]:
        """Obtiene un caso por su ID con todas sus queries"""
        # Obtener caso
        case = await self._case_repository.get_by_id(case_id)

        if not case:
            logger.info(f"Case not found: {case_id}")
            return None

        # Obtener queries asociadas
        queries = await self._query_repository.get_by_case_id(case_id)
        case.queries = queries

        logger.info(f"Case retrieved: {case_id} with {len(queries)} queries")
        return case
