import pytest
from httpx import AsyncClient
from uuid import uuid4
from app.main import app


@pytest.mark.asyncio
class TestCaseAPI:
    async def test_create_case_endpoint_success(self):
        """Test completo del endpoint de crear caso"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/cases/",
                json={
                    "title": "Test case",
                    "description": "Description",
                    "case_type": "support",
                    "priority": "high",
                    "queries": [
                        {
                            "database_name": "test_db",
                            "schema_name": "public",
                            "query_text": "SELECT * FROM test"
                        }
                    ],
                    "created_by": "test@example.com"
                }
            )

            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test case"
            assert data["status"] == "open"
            assert data["case_type"] == "support"
            assert data["priority"] == "high"
            assert data["created_by"] == "test@example.com"
            assert len(data["queries"]) == 1
            assert data["queries"][0]["database_name"] == "test_db"

    async def test_create_case_endpoint_without_queries(self):
        """Test crear caso sin queries"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/cases/",
                json={
                    "title": "Test case without queries",
                    "case_type": "requirement",
                    "priority": "medium",
                    "queries": [],
                    "created_by": "user@example.com"
                }
            )

            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test case without queries"
            assert len(data["queries"]) == 0

    async def test_create_case_endpoint_validation_error(self):
        """Test validación de campos requeridos"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/cases/",
                json={
                    "title": "",  # Título vacío
                    "case_type": "support",
                    "priority": "high",
                    "created_by": "test@example.com"
                }
            )

            assert response.status_code == 422

    async def test_create_case_endpoint_invalid_email(self):
        """Test validación de email inválido"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/cases/",
                json={
                    "title": "Test case",
                    "case_type": "support",
                    "priority": "high",
                    "created_by": "invalid-email"  # Email inválido
                }
            )

            assert response.status_code == 422

    async def test_get_cases_endpoint_without_filters(self):
        """Test obtener lista de casos sin filtros"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Crear algunos casos primero
            for i in range(3):
                await client.post(
                    "/api/v1/cases/",
                    json={
                        "title": f"Test case {i+1}",
                        "case_type": "support",
                        "priority": "medium",
                        "created_by": "test@example.com",
                        "queries": []
                    }
                )

            # Obtener lista
            response = await client.get("/api/v1/cases/")

            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert "page" in data
            assert "page_size" in data
            assert "pages" in data
            assert len(data["items"]) >= 3
            assert data["total"] >= 3

    async def test_get_cases_endpoint_with_filters(self):
        """Test obtener lista de casos con filtros"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Crear casos con diferentes atributos
            await client.post(
                "/api/v1/cases/",
                json={
                    "title": "High priority case",
                    "case_type": "support",
                    "priority": "high",
                    "created_by": "user1@example.com",
                    "queries": []
                }
            )
            await client.post(
                "/api/v1/cases/",
                json={
                    "title": "Low priority case",
                    "case_type": "requirement",
                    "priority": "low",
                    "created_by": "user2@example.com",
                    "queries": []
                }
            )

            # Filtrar por prioridad alta
            response = await client.get("/api/v1/cases/?priority=high")

            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) >= 1
            # Verificar que todos los casos tengan prioridad alta
            for item in data["items"]:
                if "High priority" in item["title"]:
                    assert item["priority"] == "high"

    async def test_get_cases_endpoint_with_search(self):
        """Test buscar casos por texto"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Crear caso con texto específico
            await client.post(
                "/api/v1/cases/",
                json={
                    "title": "Database connection issue",
                    "description": "Cannot connect to PostgreSQL",
                    "case_type": "support",
                    "priority": "critical",
                    "created_by": "test@example.com",
                    "queries": []
                }
            )

            # Buscar por "database"
            response = await client.get("/api/v1/cases/?search=database")

            assert response.status_code == 200
            data = response.json()
            # Debe encontrar al menos el caso que creamos
            found = any("database" in item["title"].lower() for item in data["items"])
            assert found

    async def test_get_cases_endpoint_with_pagination(self):
        """Test paginación de casos"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Crear varios casos
            for i in range(15):
                await client.post(
                    "/api/v1/cases/",
                    json={
                        "title": f"Pagination test case {i+1}",
                        "case_type": "support",
                        "priority": "medium",
                        "created_by": "test@example.com",
                        "queries": []
                    }
                )

            # Página 1 con 10 elementos
            response_page1 = await client.get("/api/v1/cases/?page=1&page_size=10")
            assert response_page1.status_code == 200
            data_page1 = response_page1.json()
            assert data_page1["page"] == 1
            assert data_page1["page_size"] == 10
            assert len(data_page1["items"]) == 10

            # Página 2 con 10 elementos
            response_page2 = await client.get("/api/v1/cases/?page=2&page_size=10")
            assert response_page2.status_code == 200
            data_page2 = response_page2.json()
            assert data_page2["page"] == 2
            assert len(data_page2["items"]) >= 5

    async def test_get_cases_endpoint_queries_count(self):
        """Test que queries_count se retorne correctamente"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Crear caso con queries
            await client.post(
                "/api/v1/cases/",
                json={
                    "title": "Case with queries",
                    "case_type": "support",
                    "priority": "medium",
                    "created_by": "test@example.com",
                    "queries": [
                        {
                            "database_name": "db1",
                            "schema_name": "public",
                            "query_text": "SELECT 1"
                        },
                        {
                            "database_name": "db2",
                            "schema_name": "public",
                            "query_text": "SELECT 2"
                        }
                    ]
                }
            )

            # Obtener lista
            response = await client.get("/api/v1/cases/?search=Case with queries")

            assert response.status_code == 200
            data = response.json()
            # Buscar el caso creado
            case = next(
                (item for item in data["items"] if "Case with queries" in item["title"]),
                None
            )
            assert case is not None
            assert "queries_count" in case
            assert case["queries_count"] == 2

    async def test_get_case_by_id_endpoint_success(self):
        """Test obtener caso por ID exitosamente"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Crear un caso
            create_response = await client.post(
                "/api/v1/cases/",
                json={
                    "title": "Test case for get by id",
                    "description": "Test description",
                    "case_type": "investigation",
                    "priority": "high",
                    "created_by": "test@example.com",
                    "queries": [
                        {
                            "database_name": "test_db",
                            "schema_name": "public",
                            "query_text": "SELECT * FROM users"
                        }
                    ]
                }
            )

            assert create_response.status_code == 201
            created_case = create_response.json()
            case_id = created_case["id"]

            # Obtener el caso por ID
            get_response = await client.get(f"/api/v1/cases/{case_id}")

            assert get_response.status_code == 200
            data = get_response.json()
            assert data["id"] == case_id
            assert data["title"] == "Test case for get by id"
            assert data["description"] == "Test description"
            assert data["case_type"] == "investigation"
            assert data["priority"] == "high"
            assert data["status"] == "open"
            assert data["created_by"] == "test@example.com"
            assert len(data["queries"]) == 1
            assert data["queries"][0]["database_name"] == "test_db"
            assert data["queries"][0]["query_text"] == "SELECT * FROM users"

    async def test_get_case_by_id_endpoint_not_found(self):
        """Test obtener caso con ID inexistente"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # ID aleatorio que no existe
            non_existent_id = str(uuid4())

            # Intentar obtener caso inexistente
            response = await client.get(f"/api/v1/cases/{non_existent_id}")

            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert non_existent_id in data["detail"]

    async def test_get_case_by_id_endpoint_invalid_uuid(self):
        """Test obtener caso con UUID inválido"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # UUID inválido
            invalid_id = "not-a-uuid"

            # Intentar obtener caso con UUID inválido
            response = await client.get(f"/api/v1/cases/{invalid_id}")

            # FastAPI valida automáticamente el UUID y retorna 422
            assert response.status_code == 422
