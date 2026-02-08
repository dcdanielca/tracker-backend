import pytest
from uuid import uuid4
from app.domain.entities.case import SupportCase, CaseQuery
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.infrastructure.database.repositories.case_repository_impl import CaseRepositoryImpl
from app.infrastructure.database.repositories.query_repository_impl import QueryRepositoryImpl


@pytest.mark.asyncio
class TestQueryRepositoryBulk:
    async def test_save_many_queries(self, db_connection):
        """Debe guardar múltiples queries en batch"""
        case_repo = CaseRepositoryImpl(db_connection)
        query_repo = QueryRepositoryImpl(db_connection)

        # Crear caso
        case = SupportCase.create(
            title="Test case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="test@example.com"
        )
        await case_repo.save(case)

        # Crear múltiples queries
        queries = [
            CaseQuery.create(
                case_id=case.id,
                database_name=f"db{i}",
                schema_name="public",
                query_text=f"SELECT * FROM table{i}",
                executed_by="test@example.com"
            )
            for i in range(5)
        ]

        # Guardar todas en batch
        await query_repo.save_many(queries)

        # Verificar que se guardaron todas
        retrieved_queries = await query_repo.get_by_case_id(case.id)
        assert len(retrieved_queries) == 5
        
        # Verificar que todas tienen el case_id correcto
        assert all(q.case_id == case.id for q in retrieved_queries)

    async def test_save_many_with_empty_list(self, db_connection):
        """Debe manejar lista vacía sin errores"""
        query_repo = QueryRepositoryImpl(db_connection)
        
        # No debe lanzar error
        await query_repo.save_many([])
