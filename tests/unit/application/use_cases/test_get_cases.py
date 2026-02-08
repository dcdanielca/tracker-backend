import pytest
from unittest.mock import AsyncMock, Mock
from uuid import uuid4
from datetime import datetime
from app.application.use_cases.get_cases import GetCasesUseCase
from app.domain.entities.case import SupportCase
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.domain.value_objects.case_status import CaseStatus


@pytest.mark.asyncio
class TestGetCasesUseCase:
    async def test_get_cases_without_filters(self):
        """Debe obtener casos sin filtros"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()

        # Casos de ejemplo
        case1 = SupportCase(
            id=uuid4(),
            title="Case 1",
            description="Description 1",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            status=CaseStatus.OPEN,
            created_by="user1@test.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        case2 = SupportCase(
            id=uuid4(),
            title="Case 2",
            description="Description 2",
            case_type=CaseType.REQUIREMENT,
            priority=CasePriority.MEDIUM,
            status=CaseStatus.IN_PROGRESS,
            created_by="user2@test.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Configurar mocks
        case_repo.get_all.return_value = ([case1, case2], 2)
        query_repo.get_by_case_id.return_value = []

        # Use case
        use_case = GetCasesUseCase(case_repo, query_repo)

        # Ejecutar
        cases_with_count, total = await use_case.execute(
            page=1,
            page_size=10
        )

        # Verificar
        assert len(cases_with_count) == 2
        assert total == 2
        assert cases_with_count[0][0].id == case1.id
        assert cases_with_count[0][1] == 0  # queries_count
        assert cases_with_count[1][0].id == case2.id
        assert cases_with_count[1][1] == 0  # queries_count
        case_repo.get_all.assert_called_once()
        assert query_repo.get_by_case_id.call_count == 2

    async def test_get_cases_with_filters(self):
        """Debe obtener casos con filtros aplicados"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()

        # Casos de ejemplo
        case1 = SupportCase(
            id=uuid4(),
            title="Case 1",
            description="Description 1",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            status=CaseStatus.OPEN,
            created_by="user1@test.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Configurar mocks
        case_repo.get_all.return_value = ([case1], 1)
        query_repo.get_by_case_id.return_value = []

        # Use case
        use_case = GetCasesUseCase(case_repo, query_repo)

        # Ejecutar con filtros
        cases_with_count, total = await use_case.execute(
            status="open",
            priority="high",
            case_type="support",
            created_by="user1@test.com",
            search="Case",
            page=1,
            page_size=10
        )

        # Verificar
        assert len(cases_with_count) == 1
        assert total == 1
        assert cases_with_count[0][0].id == case1.id
        case_repo.get_all.assert_called_once_with(
            status="open",
            priority="high",
            case_type="support",
            created_by="user1@test.com",
            search="Case",
            date_gte=None,
            date_lte=None,
            sort_by="created_at",
            sort_order="desc",
            page=1,
            page_size=10
        )

    async def test_get_cases_with_queries_count(self):
        """Debe obtener casos con el conteo de queries correcto"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()

        # Casos de ejemplo
        case1 = SupportCase(
            id=uuid4(),
            title="Case 1",
            description="Description 1",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            status=CaseStatus.OPEN,
            created_by="user1@test.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Configurar mocks
        case_repo.get_all.return_value = ([case1], 1)
        # Simular 3 queries para el caso
        query_repo.get_by_case_id.return_value = [Mock(), Mock(), Mock()]

        # Use case
        use_case = GetCasesUseCase(case_repo, query_repo)

        # Ejecutar
        cases_with_count, total = await use_case.execute(page=1, page_size=10)

        # Verificar
        assert len(cases_with_count) == 1
        assert cases_with_count[0][1] == 3  # queries_count debe ser 3

    async def test_get_cases_with_pagination(self):
        """Debe paginar correctamente"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()

        # Casos de ejemplo (página 2)
        case1 = SupportCase(
            id=uuid4(),
            title="Case 11",
            description="Description 11",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            status=CaseStatus.OPEN,
            created_by="user1@test.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Configurar mocks
        case_repo.get_all.return_value = ([case1], 25)  # 25 total, página 2
        query_repo.get_by_case_id.return_value = []

        # Use case
        use_case = GetCasesUseCase(case_repo, query_repo)

        # Ejecutar página 2 con 10 elementos por página
        cases_with_count, total = await use_case.execute(
            page=2,
            page_size=10
        )

        # Verificar
        assert len(cases_with_count) == 1
        assert total == 25
        case_repo.get_all.assert_called_once_with(
            status=None,
            priority=None,
            case_type=None,
            created_by=None,
            search=None,
            date_gte=None,
            date_lte=None,
            sort_by="created_at",
            sort_order="desc",
            page=2,
            page_size=10
        )

    async def test_get_cases_empty_result(self):
        """Debe manejar resultado vacío correctamente"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()

        # Configurar mocks con resultado vacío
        case_repo.get_all.return_value = ([], 0)

        # Use case
        use_case = GetCasesUseCase(case_repo, query_repo)

        # Ejecutar
        cases_with_count, total = await use_case.execute(page=1, page_size=10)

        # Verificar
        assert len(cases_with_count) == 0
        assert total == 0
        query_repo.get_by_case_id.assert_not_called()
