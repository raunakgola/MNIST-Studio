# routes/route_health.py
import time
from fastapi import APIRouter
from schema.response_schema import HealthResponse
# Fixed import path
import global_variables.global_variable as gv

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint.
    This endpoint allows monitoring systems to verify the API is functioning correctly.
    """
    return HealthResponse(
        status="healthy" if gv.model is not None else "unhealthy",
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        model_loaded=gv.model is not None,
        model_info=gv.model_info
    )
