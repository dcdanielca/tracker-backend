from abc import ABC, abstractmethod
from uuid import UUID
from typing import List
from app.domain.entities.case import CaseQuery


class QueryRepository(ABC):
    """Interface del repositorio de queries (Port)"""

    @abstractmethod
    async def save(self, query: CaseQuery) -> None:
        """Guarda una query"""
        pass

    @abstractmethod
    async def save_many(self, queries: List[CaseQuery]) -> None:
        """Guarda múltiples queries en batch (más eficiente)"""
        pass

    @abstractmethod
    async def get_by_case_id(self, case_id: UUID) -> List[CaseQuery]:
        """Obtiene todas las queries de un caso"""
        pass
