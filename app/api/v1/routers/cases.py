from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.schemas.cases import CreateCaseRequest, CaseResponse
from app.api.dependencies import get_create_case_use_case
from app.application.use_cases.create_case import CreateCaseUseCase
from app.domain.exceptions import DomainValidationError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cases", tags=["cases"])


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
