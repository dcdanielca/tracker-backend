import pytest
from datetime import datetime, timedelta
from app.domain.entities.case import SupportCase
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.domain.value_objects.case_status import CaseStatus
from app.infrastructure.database.repositories.case_repository_impl import CaseRepositoryImpl


@pytest.mark.asyncio
class TestCaseRepositoryGetAll:
    async def test_get_all_without_filters(self, db_connection):
        """Debe obtener todos los casos sin filtros"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear múltiples casos
        case1 = SupportCase.create(
            title="Case 1",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="user1@test.com",
            description="Description 1",
        )
        case2 = SupportCase.create(
            title="Case 2",
            case_type=CaseType.REQUIREMENT,
            priority=CasePriority.MEDIUM,
            created_by="user2@test.com",
            description="Description 2",
        )
        case3 = SupportCase.create(
            title="Case 3",
            case_type=CaseType.INVESTIGATION,
            priority=CasePriority.LOW,
            created_by="user3@test.com",
            description="Description 3",
        )

        await repo.save(case1)
        await repo.save(case2)
        await repo.save(case3)

        # Obtener todos
        cases, total = await repo.get_all(page=1, page_size=10)

        # Verificar
        assert len(cases) == 3
        assert total == 3

    async def test_get_all_with_status_filter(self, db_connection):
        """Debe filtrar por estado correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear casos con diferentes estados
        case1 = SupportCase.create(
            title="Case 1",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="user@test.com",
        )
        case1.status = CaseStatus.OPEN

        case2 = SupportCase.create(
            title="Case 2",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="user@test.com",
        )
        case2.status = CaseStatus.IN_PROGRESS

        await repo.save(case1)
        await repo.save(case2)

        # Filtrar por estado "open"
        cases, total = await repo.get_all(status="open", page=1, page_size=10)

        # Verificar
        assert len(cases) == 1
        assert total == 1
        assert cases[0].status == CaseStatus.OPEN

    async def test_get_all_with_priority_filter(self, db_connection):
        """Debe filtrar por prioridad correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear casos con diferentes prioridades
        case1 = SupportCase.create(
            title="High Priority",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="user@test.com",
        )
        case2 = SupportCase.create(
            title="Low Priority",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.LOW,
            created_by="user@test.com",
        )

        await repo.save(case1)
        await repo.save(case2)

        # Filtrar por prioridad "high"
        cases, total = await repo.get_all(priority="high", page=1, page_size=10)

        # Verificar
        assert len(cases) == 1
        assert total == 1
        assert cases[0].priority == CasePriority.HIGH

    async def test_get_all_with_case_type_filter(self, db_connection):
        """Debe filtrar por tipo de caso correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear casos con diferentes tipos
        case1 = SupportCase.create(
            title="Support Case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.MEDIUM,
            created_by="user@test.com",
        )
        case2 = SupportCase.create(
            title="Requirement Case",
            case_type=CaseType.REQUIREMENT,
            priority=CasePriority.MEDIUM,
            created_by="user@test.com",
        )

        await repo.save(case1)
        await repo.save(case2)

        # Filtrar por tipo "requirement"
        cases, total = await repo.get_all(case_type="requirement", page=1, page_size=10)

        # Verificar
        assert len(cases) == 1
        assert total == 1
        assert cases[0].case_type == CaseType.REQUIREMENT

    async def test_get_all_with_created_by_filter(self, db_connection):
        """Debe filtrar por creador correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear casos con diferentes creadores
        case1 = SupportCase.create(
            title="Case 1",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.MEDIUM,
            created_by="user1@test.com",
        )
        case2 = SupportCase.create(
            title="Case 2",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.MEDIUM,
            created_by="user2@test.com",
        )

        await repo.save(case1)
        await repo.save(case2)

        # Filtrar por creador
        cases, total = await repo.get_all(created_by="user1@test.com", page=1, page_size=10)

        # Verificar
        assert len(cases) == 1
        assert total == 1
        assert cases[0].created_by == "user1@test.com"

    async def test_get_all_with_search_filter(self, db_connection):
        """Debe buscar en título y descripción correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear casos
        case1 = SupportCase.create(
            title="Database Query Issue",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="user@test.com",
            description="Problem with SQL query",
        )
        case2 = SupportCase.create(
            title="API Enhancement",
            case_type=CaseType.REQUIREMENT,
            priority=CasePriority.MEDIUM,
            created_by="user@test.com",
            description="Add new endpoint",
        )

        await repo.save(case1)
        await repo.save(case2)

        # Buscar por "query"
        cases, total = await repo.get_all(search="query", page=1, page_size=10)

        # Verificar - debe encontrar case1 (en title y description)
        assert len(cases) == 1
        assert total == 1
        assert "query" in cases[0].title.lower() or "query" in (cases[0].description or "").lower()

    async def test_get_all_with_date_range_filter(self, db_connection):
        """Debe filtrar por rango de fechas correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear casos con fechas diferentes
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)

        case1 = SupportCase.create(
            title="Old Case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.MEDIUM,
            created_by="user@test.com",
        )
        case1.created_at = yesterday

        case2 = SupportCase.create(
            title="New Case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.MEDIUM,
            created_by="user@test.com",
        )

        await repo.save(case1)
        await repo.save(case2)

        # Filtrar casos desde hoy
        cases, total = await repo.get_all(date_gte=now - timedelta(hours=1), page=1, page_size=10)

        # Verificar - solo debe encontrar case2
        assert len(cases) == 1
        assert cases[0].title == "New Case"

    async def test_get_all_with_pagination(self, db_connection):
        """Debe paginar correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear 15 casos
        for i in range(15):
            case = SupportCase.create(
                title=f"Case {i+1}",
                case_type=CaseType.SUPPORT,
                priority=CasePriority.MEDIUM,
                created_by="user@test.com",
            )
            await repo.save(case)

        # Página 1 (10 elementos)
        cases_page1, total_page1 = await repo.get_all(page=1, page_size=10)
        assert len(cases_page1) == 10
        assert total_page1 == 15

        # Página 2 (5 elementos restantes)
        cases_page2, total_page2 = await repo.get_all(page=2, page_size=10)
        assert len(cases_page2) == 5
        assert total_page2 == 15

    async def test_get_all_with_sorting(self, db_connection):
        """Debe ordenar correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear casos
        case1 = SupportCase.create(
            title="AAA Case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.LOW,
            created_by="user@test.com",
        )
        case2 = SupportCase.create(
            title="ZZZ Case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="user@test.com",
        )

        await repo.save(case1)
        await repo.save(case2)

        # Ordenar por título ascendente
        cases_asc, _ = await repo.get_all(sort_by="title", sort_order="asc", page=1, page_size=10)
        assert cases_asc[0].title == "AAA Case"
        assert cases_asc[1].title == "ZZZ Case"

        # Ordenar por título descendente
        cases_desc, _ = await repo.get_all(sort_by="title", sort_order="desc", page=1, page_size=10)
        assert cases_desc[0].title == "ZZZ Case"
        assert cases_desc[1].title == "AAA Case"

    async def test_get_all_with_multiple_filters(self, db_connection):
        """Debe combinar múltiples filtros correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear casos variados
        case1 = SupportCase.create(
            title="High Priority Support",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="user1@test.com",
        )
        case2 = SupportCase.create(
            title="Low Priority Support",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.LOW,
            created_by="user1@test.com",
        )
        case3 = SupportCase.create(
            title="High Priority Requirement",
            case_type=CaseType.REQUIREMENT,
            priority=CasePriority.HIGH,
            created_by="user2@test.com",
        )

        await repo.save(case1)
        await repo.save(case2)
        await repo.save(case3)

        # Filtrar: tipo=support, prioridad=high, creador=user1
        cases, total = await repo.get_all(
            case_type="support", priority="high", created_by="user1@test.com", page=1, page_size=10
        )

        # Verificar - solo debe encontrar case1
        assert len(cases) == 1
        assert total == 1
        assert cases[0].title == "High Priority Support"

    async def test_get_all_empty_result(self, db_connection):
        """Debe manejar resultado vacío correctamente"""
        repo = CaseRepositoryImpl(db_connection)

        # No crear ningún caso

        # Obtener todos
        cases, total = await repo.get_all(page=1, page_size=10)

        # Verificar
        assert len(cases) == 0
        assert total == 0
