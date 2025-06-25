# routes/route_metrics.py
from fastapi import APIRouter
from schema.response_schema import MetricsResponse
# Fixed import path
import global_variables.global_variable as gv

router = APIRouter()

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Endpoint to retrieve API usage metrics.
    Essential for monitoring performance and usage patterns in production.
    """
    success_rate = (
        gv.prediction_metrics["successful_predictions"] / gv.prediction_metrics["total_predictions"]
        if gv.prediction_metrics["total_predictions"] > 0 else 0.0
    )
    
    return MetricsResponse(
        total_predictions=gv.prediction_metrics["total_predictions"],
        successful_predictions=gv.prediction_metrics["successful_predictions"],
        failed_predictions=gv.prediction_metrics["failed_predictions"],
        success_rate=round(success_rate, 4),
        average_inference_time=round(gv.prediction_metrics["average_inference_time"], 3),
        predictions_by_class=gv.prediction_metrics["predictions_by_class"]
    )