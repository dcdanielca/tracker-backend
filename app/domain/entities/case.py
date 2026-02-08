from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import List, Optional
from app.domain.value_objects.case_status import CaseStatus
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.domain.exceptions import DomainValidationError


@dataclass
class CaseQuery:
    """Entidad que representa una consulta SQL ejecutada"""

    id: UUID = field(default_factory=uuid4)
    case_id: UUID = field(default_factory=uuid4)
    database_name: str = ""
    schema_name: str = ""
    query_text: str = ""
    execution_time_ms: Optional[int] = None
    rows_affected: Optional[int] = None
    executed_at: datetime = field(default_factory=datetime.utcnow)
    executed_by: str = ""

    @classmethod
    def create(
        cls,
        case_id: UUID,
        database_name: str,
        schema_name: str,
        query_text: str,
        executed_by: str,
        execution_time_ms: Optional[int] = None,
        rows_affected: Optional[int] = None,
    ) -> "CaseQuery":
        """Factory method para crear una query válida"""
        if not database_name or len(database_name.strip()) == 0:
            raise DomainValidationError("El nombre de la base de datos no puede estar vacío")

        if not schema_name or len(schema_name.strip()) == 0:
            raise DomainValidationError("El nombre del esquema no puede estar vacío")

        if not query_text or len(query_text.strip()) == 0:
            raise DomainValidationError("El texto de la consulta no puede estar vacío")

        if not executed_by or "@" not in executed_by:
            raise DomainValidationError("El email del ejecutor no es válido")

        return cls(
            case_id=case_id,
            database_name=database_name.strip(),
            schema_name=schema_name.strip(),
            query_text=query_text.strip(),
            executed_by=executed_by,
            execution_time_ms=execution_time_ms,
            rows_affected=rows_affected,
        )


@dataclass
class SupportCase:
    """Entidad que representa un caso de soporte"""

    id: UUID = field(default_factory=uuid4)
    title: str = ""
    description: Optional[str] = None
    case_type: CaseType = field(default=CaseType.SUPPORT)
    priority: CasePriority = field(default=CasePriority.MEDIUM)
    status: CaseStatus = field(default=CaseStatus.OPEN)
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    queries: List[CaseQuery] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        title: str,
        case_type: CaseType,
        priority: CasePriority,
        created_by: str,
        description: Optional[str] = None,
    ) -> "SupportCase":
        """Factory method para crear un caso válido"""
        if not title or len(title.strip()) == 0:
            raise DomainValidationError("El título no puede estar vacío")

        if len(title) > 200:
            raise DomainValidationError("El título no puede exceder 200 caracteres")

        if not created_by or "@" not in created_by:
            raise DomainValidationError("El email del creador no es válido")

        return cls(
            title=title.strip(),
            description=description,
            case_type=case_type,
            priority=priority,
            created_by=created_by,
            status=CaseStatus.OPEN,
        )

    def add_query(self, query: CaseQuery) -> None:
        """Agrega una query al caso"""
        if query.case_id != self.id:
            raise DomainValidationError("La query no pertenece a este caso")
        self.queries.append(query)
        self.updated_at = datetime.utcnow()

    def mark_as_in_progress(self) -> None:
        """Marca el caso como en progreso"""
        if self.status == CaseStatus.CLOSED:
            raise DomainValidationError("No se puede cambiar estado de caso cerrado")

        self.status = CaseStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def mark_as_resolved(self) -> None:
        """Marca el caso como resuelto"""
        if self.status not in [CaseStatus.OPEN, CaseStatus.IN_PROGRESS]:
            raise DomainValidationError("Solo se pueden resolver casos abiertos o en progreso")

        self.status = CaseStatus.RESOLVED
        self.updated_at = datetime.utcnow()

    def close(self) -> None:
        """Cierra el caso"""
        if self.status != CaseStatus.RESOLVED:
            raise DomainValidationError("Solo se pueden cerrar casos resueltos")

        self.status = CaseStatus.CLOSED
        self.updated_at = datetime.utcnow()
