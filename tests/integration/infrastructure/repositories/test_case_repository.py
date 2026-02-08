import pytest
from uuid import uuid4
from app.domain.entities.case import SupportCase
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.infrastructure.database.repositories.case_repository_impl import CaseRepositoryImpl


@pytest.mark.asyncio
class TestCaseRepository:
    async def test_save_and_retrieve_case(self, db_connection):
        """Debe guardar y recuperar un caso"""
        repo = CaseRepositoryImpl(db_connection)

        # Crear caso
        case = SupportCase.create(
            title="Test case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="test@example.com",
        )

        # Guardar
        await repo.save(case)

        # Recuperar
        retrieved = await repo.get_by_id(case.id)

        assert retrieved is not None
        assert retrieved.id == case.id
        assert retrieved.title == case.title
        assert retrieved.status == case.status
        assert retrieved.case_type == case.case_type
        assert retrieved.priority == case.priority
        assert retrieved.created_by == case.created_by

    async def test_get_by_id_returns_none_for_nonexistent_case(self, db_connection):
        """Debe retornar None para caso inexistente"""
        repo = CaseRepositoryImpl(db_connection)
        non_existent_id = uuid4()

        result = await repo.get_by_id(non_existent_id)
        assert result is None
