import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.create_case import CreateCaseUseCase
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority


@pytest.mark.asyncio
class TestCreateCaseUseCase:
    async def test_create_case_successfully(self):
        """Debe crear caso exitosamente"""
        # Mocks
        case_repo = AsyncMock()
        query_repo = AsyncMock()
        uow = AsyncMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)

        # Mock de conexión
        mock_connection = AsyncMock()
        uow.get_connection = AsyncMock(return_value=mock_connection)

        # Mock de repositorios que se crearán internamente
        from unittest.mock import patch

        with patch(
            "app.application.use_cases.create_case.CaseRepositoryImpl"
        ) as MockCaseRepo, patch(
            "app.application.use_cases.create_case.QueryRepositoryImpl"
        ) as MockQueryRepo:
            mock_case_repo_instance = AsyncMock()
            mock_query_repo_instance = AsyncMock()
            MockCaseRepo.return_value = mock_case_repo_instance
            MockQueryRepo.return_value = mock_query_repo_instance

            # Use case
            use_case = CreateCaseUseCase(case_repo, query_repo, uow)

            # Ejecutar
            case = await use_case.execute(
                title="New case",
                description="Description",
                case_type="support",
                priority="high",
                queries=[
                    {
                        "database_name": "test_db",
                        "schema_name": "public",
                        "query_text": "SELECT * FROM test",
                    }
                ],
                created_by="test@example.com",
            )

            # Verificar
            assert case.title == "New case"
            assert case.created_by == "test@example.com"
            assert case.case_type == CaseType.SUPPORT
            assert case.priority == CasePriority.HIGH
            mock_case_repo_instance.save.assert_called_once()
            mock_query_repo_instance.save_many.assert_called_once()
            # Verificar que se guardó una lista con 1 query
            call_args = mock_query_repo_instance.save_many.call_args[0][0]
            assert len(call_args) == 1

    async def test_create_case_with_multiple_queries(self):
        """Debe crear caso con múltiples queries"""
        case_repo = AsyncMock()
        query_repo = AsyncMock()
        uow = AsyncMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)

        # Mock de conexión
        mock_connection = AsyncMock()
        uow.get_connection = AsyncMock(return_value=mock_connection)

        from unittest.mock import patch

        with patch(
            "app.application.use_cases.create_case.CaseRepositoryImpl"
        ) as MockCaseRepo, patch(
            "app.application.use_cases.create_case.QueryRepositoryImpl"
        ) as MockQueryRepo:
            mock_case_repo_instance = AsyncMock()
            mock_query_repo_instance = AsyncMock()
            MockCaseRepo.return_value = mock_case_repo_instance
            MockQueryRepo.return_value = mock_query_repo_instance

            use_case = CreateCaseUseCase(case_repo, query_repo, uow)

            case = await use_case.execute(
                title="New case",
                description="Description",
                case_type="support",
                priority="high",
                queries=[
                    {
                        "database_name": "db1",
                        "schema_name": "public",
                        "query_text": "SELECT * FROM table1",
                    },
                    {
                        "database_name": "db2",
                        "schema_name": "schema2",
                        "query_text": "SELECT * FROM table2",
                    },
                ],
                created_by="test@example.com",
            )

            assert len(case.queries) == 2
            mock_query_repo_instance.save_many.assert_called_once()
            # Verificar que se guardaron 2 queries en batch
            call_args = mock_query_repo_instance.save_many.call_args[0][0]
            assert len(call_args) == 2

    async def test_create_case_with_invalid_type_raises_error(self):
        """Debe fallar si el tipo de caso es inválido"""
        case_repo = AsyncMock()
        query_repo = AsyncMock()
        uow = AsyncMock()
        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)

        use_case = CreateCaseUseCase(case_repo, query_repo, uow)

        with pytest.raises(ValueError):  # CaseType enum validation
            await use_case.execute(
                title="New case",
                description="Description",
                case_type="invalid_type",
                priority="high",
                queries=[],
                created_by="test@example.com",
            )
