from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from app.domain.entities.case import SupportCase
from app.api.v1.schemas.queries import QueryResponse, QueryRequest


class CreateCaseRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    case_type: str = Field(..., pattern="^(support|requirement|investigation)$")
    priority: str = Field(..., pattern="^(low|medium|high|critical)$")
    queries: List[QueryRequest] = Field(default_factory=list)
    created_by: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")  # Email validation


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    case_type: str
    priority: str
    status: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    queries: List[QueryResponse] = Field(default_factory=list)

    @classmethod
    def from_entity(cls, case: SupportCase) -> "CaseResponse":
        return cls(
            id=case.id,
            title=case.title,
            description=case.description,
            case_type=case.case_type.value,
            priority=case.priority.value,
            status=case.status.value,
            created_by=case.created_by,
            created_at=case.created_at,
            updated_at=case.updated_at,
            queries=[QueryResponse.from_entity(q) for q in case.queries]
        )
