from app.infrastructure.database.db import db
from app.infrastructure.database.repositories.case_repository_impl import CaseRepositoryImpl
from app.infrastructure.database.repositories.query_repository_impl import QueryRepositoryImpl
from app.infrastructure.database.unit_of_work import PostgreSQLUnitOfWork
from app.application.use_cases.create_case import CreateCaseUseCase


def get_case_repository() -> CaseRepositoryImpl:
    """Dependency para obtener el repositorio de casos"""
    return CaseRepositoryImpl(db)


def get_query_repository() -> QueryRepositoryImpl:
    """Dependency para obtener el repositorio de queries"""
    return QueryRepositoryImpl(db)


def get_unit_of_work() -> PostgreSQLUnitOfWork:
    """Dependency para obtener Unit of Work"""
    return PostgreSQLUnitOfWork(db)


def get_create_case_use_case() -> CreateCaseUseCase:
    """Dependency para obtener el use case de crear caso"""
    case_repo = get_case_repository()
    query_repo = get_query_repository()
    uow = get_unit_of_work()
    return CreateCaseUseCase(case_repo, query_repo, uow)
