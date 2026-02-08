from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.domain.entities.case import CaseQuery


class QueryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    database_name: str
    schema_name: str
    query_text: str
    execution_time_ms: int | None
    rows_affected: int | None
    executed_at: datetime
    executed_by: str

    @classmethod
    def from_entity(cls, query: CaseQuery) -> "QueryResponse":
        return cls(
            id=query.id,
            case_id=query.case_id,
            database_name=query.database_name,
            schema_name=query.schema_name,
            query_text=query.query_text,
            execution_time_ms=query.execution_time_ms,
            rows_affected=query.rows_affected,
            executed_at=query.executed_at,
            executed_by=query.executed_by
        )


class QueryRequest(BaseModel):
    database_name: str
    schema_name: str
    query_text: str
