from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from app.domain.entities.case import SupportCase


class CaseRepository(ABC):
    """Interface del repositorio de casos (Port)"""

    @abstractmethod
    async def save(self, case: SupportCase) -> None:
        """Guarda un caso (solo INSERT, no UPDATE)"""
        pass

    @abstractmethod
    async def get_by_id(self, case_id: UUID) -> Optional[SupportCase]:
        """Obtiene un caso por ID"""
        pass
