import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime
from app.application.use_cases.get_case_by_id import GetCaseByIdUseCase
from app.domain.entities.case import SupportCase, CaseQuery
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.domain.value_objects.case_status import CaseStatus


@pytest.mark.asyncio
class TestGetCaseByIdUseCase:
    async def test_get_case_by_id_successfully(self):
        """Debe obtener un caso por ID exitosamente"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()

        # Caso de ejemplo
        case_id = uuid4()
        case = SupportCase(
            id=case_id,
            title="Test Case",
            description="Test Description",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            status=CaseStatus.OPEN,
            created_by="user@test.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Queries de ejemplo
        query1 = CaseQuery(
            id=uuid4(),
            case_id=case_id,
            database_name="test_db",
            schema_name="public",
            query_text="SELECT * FROM test",
            execution_time_ms=100,
            rows_affected=10,
            executed_at=datetime.utcnow(),
            executed_by="user@test.com",
        )
        query2 = CaseQuery(
            id=uuid4(),
            case_id=case_id,
            database_name="test_db",
            schema_name="public",
            query_text="SELECT COUNT(*) FROM test",
            execution_time_ms=50,
            rows_affected=1,
            executed_at=datetime.utcnow(),
            executed_by="user@test.com",
        )

        # Configurar mocks
        case_repo.get_by_id.return_value = case
        query_repo.get_by_case_id.return_value = [query1, query2]

        # Use case
        use_case = GetCaseByIdUseCase(case_repo, query_repo)

        # Ejecutar
        result = await use_case.execute(case_id)

        # Verificar
        assert result is not None
        assert result.id == case_id
        assert result.title == "Test Case"
        assert len(result.queries) == 2
        assert result.queries[0].id == query1.id
        assert result.queries[1].id == query2.id
        case_repo.get_by_id.assert_called_once_with(case_id)
        query_repo.get_by_case_id.assert_called_once_with(case_id)

    async def test_get_case_by_id_not_found(self):
        """Debe retornar None cuando el caso no existe"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()

        # Configurar mocks para caso no encontrado
        case_id = uuid4()
        case_repo.get_by_id.return_value = None

        # Use case
        use_case = GetCaseByIdUseCase(case_repo, query_repo)

        # Ejecutar
        result = await use_case.execute(case_id)

        # Verificar
        assert result is None
        case_repo.get_by_id.assert_called_once_with(case_id)
        query_repo.get_by_case_id.assert_not_called()

    async def test_get_case_by_id_without_queries(self):
        """Debe obtener un caso sin queries"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()

        # Caso de ejemplo
        case_id = uuid4()
        case = SupportCase(
            id=case_id,
            title="Test Case",
            description="Test Description",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            status=CaseStatus.OPEN,
            created_by="user@test.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Configurar mocks (sin queries)
        case_repo.get_by_id.return_value = case
        query_repo.get_by_case_id.return_value = []

        # Use case
        use_case = GetCaseByIdUseCase(case_repo, query_repo)

        # Ejecutar
        result = await use_case.execute(case_id)

        # Verificar
        assert result is not None
        assert result.id == case_id
        assert len(result.queries) == 0
        case_repo.get_by_id.assert_called_once_with(case_id)
        query_repo.get_by_case_id.assert_called_once_with(case_id)
