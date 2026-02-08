import pytest
from httpx import AsyncClient
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
