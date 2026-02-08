import pytest
from uuid import uuid4
from app.domain.entities.case import SupportCase, CaseQuery
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.infrastructure.database.repositories.case_repository_impl import CaseRepositoryImpl
from app.infrastructure.database.repositories.query_repository_impl import QueryRepositoryImpl


@pytest.mark.asyncio
class TestQueryRepository:
    async def test_save_and_retrieve_queries(self, db_connection):
        """Debe guardar y recuperar queries"""
        case_repo = CaseRepositoryImpl(db_connection)
        query_repo = QueryRepositoryImpl(db_connection)

        # Crear caso
        case = SupportCase.create(
            title="Test case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="test@example.com",
        )
        await case_repo.save(case)

        # Crear queries
        query1 = CaseQuery.create(
            case_id=case.id,
            database_name="db1",
            schema_name="public",
            query_text="SELECT * FROM table1",
            executed_by="test@example.com",
        )

        query2 = CaseQuery.create(
            case_id=case.id,
            database_name="db2",
            schema_name="schema2",
            query_text="SELECT * FROM table2",
            executed_by="test@example.com",
        )

        await query_repo.save(query1)
        await query_repo.save(query2)

        # Recuperar queries del caso
        queries = await query_repo.get_by_case_id(case.id)

        assert len(queries) == 2
        assert queries[0].database_name in ["db1", "db2"]
        assert queries[1].database_name in ["db1", "db2"]

    async def test_get_by_case_id_returns_empty_list_for_nonexistent_case(self, db_connection):
        """Debe retornar lista vacía para caso sin queries"""
        query_repo = QueryRepositoryImpl(db_connection)
        non_existent_id = uuid4()

        queries = await query_repo.get_by_case_id(non_existent_id)
        assert queries == []
