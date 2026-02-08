import pytest
from app.domain.entities.case import SupportCase, CaseQuery
from app.domain.value_objects.case_status import CaseStatus
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.domain.exceptions import DomainValidationError


class TestSupportCase:
    def test_create_case_with_valid_data(self):
        """Debe crear un caso válido"""
        case = SupportCase.create(
            title="Test case",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.HIGH,
            created_by="test@example.com",
            description="Description"
        )

        assert case.title == "Test case"
        assert case.status == CaseStatus.OPEN
        assert case.description == "Description"
        assert case.case_type == CaseType.SUPPORT
        assert case.priority == CasePriority.HIGH
        assert case.created_by == "test@example.com"

    def test_create_case_with_empty_title_raises_error(self):
        """No debe permitir título vacío"""
        with pytest.raises(DomainValidationError, match="título no puede estar vacío"):
            SupportCase.create(
                title="",
                case_type=CaseType.SUPPORT,
                priority=CasePriority.MEDIUM,
                created_by="test@example.com"
            )

    def test_create_case_with_invalid_email_raises_error(self):
        """No debe permitir email inválido"""
        with pytest.raises(DomainValidationError, match="email del creador no es válido"):
            SupportCase.create(
                title="Test",
                case_type=CaseType.SUPPORT,
                priority=CasePriority.MEDIUM,
                created_by="invalid-email"
            )

    def test_create_case_with_title_too_long_raises_error(self):
        """No debe permitir título muy largo"""
        long_title = "a" * 201
        with pytest.raises(DomainValidationError, match="título no puede exceder 200 caracteres"):
            SupportCase.create(
                title=long_title,
                case_type=CaseType.SUPPORT,
                priority=CasePriority.MEDIUM,
                created_by="test@example.com"
            )

    def test_add_query_to_case(self):
        """Debe permitir agregar queries al caso"""
        case = SupportCase.create(
            title="Test",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.MEDIUM,
            created_by="test@example.com"
        )
        
        query = CaseQuery.create(
            case_id=case.id,
            database_name="test_db",
            schema_name="public",
            query_text="SELECT * FROM test",
            executed_by="test@example.com"
        )
        
        case.add_query(query)
        assert len(case.queries) == 1
        assert case.queries[0].id == query.id

    def test_add_query_with_wrong_case_id_raises_error(self):
        """No debe permitir agregar query de otro caso"""
        case = SupportCase.create(
            title="Test",
            case_type=CaseType.SUPPORT,
            priority=CasePriority.MEDIUM,
            created_by="test@example.com"
        )
        
        from uuid import uuid4
        query = CaseQuery.create(
            case_id=uuid4(),  # Diferente al case.id
            database_name="test_db",
            schema_name="public",
            query_text="SELECT * FROM test",
            executed_by="test@example.com"
        )
        
        with pytest.raises(DomainValidationError, match="La query no pertenece a este caso"):
            case.add_query(query)


class TestCaseQuery:
    def test_create_query_with_valid_data(self):
        """Debe crear una query válida"""
        from uuid import uuid4
        case_id = uuid4()
        
        query = CaseQuery.create(
            case_id=case_id,
            database_name="test_db",
            schema_name="public",
            query_text="SELECT * FROM test",
            executed_by="test@example.com"
        )
        
        assert query.database_name == "test_db"
        assert query.schema_name == "public"
        assert query.query_text == "SELECT * FROM test"
        assert query.executed_by == "test@example.com"
        assert query.case_id == case_id

    def test_create_query_with_empty_database_name_raises_error(self):
        """No debe permitir database_name vacío"""
        from uuid import uuid4
        with pytest.raises(DomainValidationError, match="nombre de la base de datos no puede estar vacío"):
            CaseQuery.create(
                case_id=uuid4(),
                database_name="",
                schema_name="public",
                query_text="SELECT * FROM test",
                executed_by="test@example.com"
            )

    def test_create_query_with_invalid_email_raises_error(self):
        """No debe permitir email inválido"""
        from uuid import uuid4
        with pytest.raises(DomainValidationError, match="email del ejecutor no es válido"):
            CaseQuery.create(
                case_id=uuid4(),
                database_name="test_db",
                schema_name="public",
                query_text="SELECT * FROM test",
                executed_by="invalid-email"
            )
