from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.api.v1.schemas.cases import (
    CreateCaseRequest,
    CaseResponse,
    CaseSummaryResponse,
    PaginatedResponse
)
from app.api.dependencies import (
    get_create_case_use_case,
    get_get_cases_use_case,
    get_get_case_by_id_use_case
)
from app.application.use_cases.create_case import CreateCaseUseCase
from app.application.use_cases.get_cases import GetCasesUseCase
from app.application.use_cases.get_case_by_id import GetCaseByIdUseCase
from app.domain.exceptions import DomainValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get(
    "/",
    response_model=PaginatedResponse[CaseSummaryResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar casos",
    description="Lista casos con filtros y paginación"
)
async def get_cases(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=50, description="Elementos por página"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filtrar por estado"),
    priority: Optional[str] = Query(None, description="Filtrar por prioridad"),
    case_type: Optional[str] = Query(None, description="Filtrar por tipo de caso"),
    created_by: Optional[str] = Query(None, description="Filtrar por email de usuario creador"),
    search: Optional[str] = Query(None, description="Búsqueda en título y descripción"),
    date_gte: Optional[datetime] = Query(None, description="Casos desde esta fecha"),
    date_lte: Optional[datetime] = Query(None, description="Casos hasta esta fecha"),
    sort_by: str = Query("created_at", description="Campo para ordenar"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Orden ascendente o descendente"),
    use_case: GetCasesUseCase = Depends(get_get_cases_use_case)
):
    """Endpoint para listar casos con filtros y paginación"""
    try:
        logger.info(
            f"Listing cases: page={page}, page_size={page_size}",
            extra={
                "page": page,
                "filters": {
                    "status": status_filter,
                    "priority": priority,
                    "case_type": case_type,
                    "created_by": created_by,
                    "search": search
                }
            }
        )

        cases_with_count, total = await use_case.execute(
            status=status_filter,
            priority=priority,
            case_type=case_type,
            created_by=created_by,
            search=search,
            date_gte=date_gte,
            date_lte=date_lte,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size
        )

        # Convertir a response models
        items = [
            CaseSummaryResponse.from_entity(case, queries_count)
            for case, queries_count in cases_with_count
        ]

        return PaginatedResponse.create(
            items=items,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Unexpected error listing cases: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener caso por ID",
    description="Obtiene el detalle completo de un caso incluyendo todas sus consultas SQL"
)
async def get_case_by_id(
    case_id: UUID,
    use_case: GetCaseByIdUseCase = Depends(get_get_case_by_id_use_case)
):
    """Endpoint para obtener el detalle de un caso específico"""
    try:
        logger.info(f"Getting case by ID: {case_id}")

        case = await use_case.execute(case_id)

        if not case:
            logger.info(f"Case not found: {case_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Caso con ID {case_id} no encontrado"
            )

        logger.info(f"Case retrieved successfully: {case_id}")
        return CaseResponse.from_entity(case)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting case {case_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post(
    "/",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo caso",
    description="Crea un nuevo caso de soporte con sus consultas SQL asociadas"
)
async def create_case(
    request: CreateCaseRequest,
    use_case: CreateCaseUseCase = Depends(get_create_case_use_case)
):
    """Endpoint para crear un nuevo caso de soporte"""
    try:
        logger.info(f"Creating case: {request.title} by {request.created_by}")

        case = await use_case.execute(
            title=request.title,
            description=request.description,
            case_type=request.case_type,
            priority=request.priority,
            queries=[q.model_dump() for q in request.queries],
            created_by=request.created_by
        )

        logger.info(f"Case created successfully: {case.id}")
        return CaseResponse.from_entity(case)

    except DomainValidationError as e:
        logger.warning(f"Validation error creating case: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except ValueError as e:
        logger.warning(f"Value error creating case: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating case: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
