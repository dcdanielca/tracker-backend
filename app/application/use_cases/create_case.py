from typing import List
from app.domain.entities.case import SupportCase, CaseQuery
from app.domain.repositories.case_repository import CaseRepository
from app.domain.repositories.query_repository import QueryRepository
from app.domain.value_objects.case_type import CaseType
from app.domain.value_objects.case_priority import CasePriority
from app.application.interfaces.unit_of_work import UnitOfWork
from app.infrastructure.database.repositories.case_repository_impl import CaseRepositoryImpl
from app.infrastructure.database.repositories.query_repository_impl import QueryRepositoryImpl
import logging

logger = logging.getLogger(__name__)


class CreateCaseUseCase:
    def __init__(
        self,
        case_repository: CaseRepository,
        query_repository: QueryRepository,
        uow: UnitOfWork
    ):
        self._case_repository = case_repository
        self._query_repository = query_repository
        self._uow = uow

    async def execute(
        self,
        title: str,
        description: str | None,
        case_type: str,
        priority: str,
        queries: List[dict],
        created_by: str
    ) -> SupportCase:
        """Crea un nuevo caso con sus queries asociadas"""
        async with self._uow:
            # Obtener conexión de la transacción
            connection = self._uow.get_connection()
            
            # Crear repositorios con la conexión de transacción
            case_repo = CaseRepositoryImpl(self._case_repository._db, connection)
            query_repo = QueryRepositoryImpl(self._query_repository._db, connection)
            
            # Crear entidad de dominio
            case = SupportCase.create(
                title=title,
                description=description,
                case_type=CaseType(case_type),
                priority=CasePriority(priority),
                created_by=created_by
            )

            # Persistir caso
            await case_repo.save(case)
            logger.info(f"Case created: {case.id}")

            # Crear todas las queries primero
            case_queries = []
            for query_data in queries:
                query = CaseQuery.create(
                    case_id=case.id,
                    database_name=query_data["database_name"],
                    schema_name=query_data["schema_name"],
                    query_text=query_data["query_text"],
                    executed_by=created_by
                )
                case_queries.append(query)
                case.add_query(query)

            # Guardar todas las queries en batch (bulk create)
            if case_queries:
                await query_repo.save_many(case_queries)
                logger.debug(f"Saved {len(case_queries)} queries in batch for case {case.id}")

            return case
