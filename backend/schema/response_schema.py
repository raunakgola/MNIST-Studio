#schema/response_schema.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PredictionResponse(BaseModel):
    """
    Structured response model for predictions.
    This ensures consistent API responses and automatic documentation.
    """
    prediction: int = Field(..., description="Predicted digit (0-9)")
    confidence: float = Field(..., description="Confidence score (0-1)")
    probabilities: Dict[str, float] = Field(..., description="Probability for each digit")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")
    request_id: str = Field(..., description="Unique request identifier")

class BatchPredictionResponse(BaseModel):
    """
    Response model for batch predictions.
    """
    predictions: List[PredictionResponse] = Field(..., description="List of individual predictions")
    batch_size: int = Field(..., description="Number of images processed")
    total_inference_time_ms: float = Field(..., description="Total time for batch processing")
    average_inference_time_ms: float = Field(..., description="Average time per image")
    request_id: str = Field(..., description="Unique batch request identifier")

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str
    timestamp: str
    model_loaded: bool
    model_info: Dict[str, Any]

class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""
    total_predictions: int
    successful_predictions: int
    failed_predictions: int
    success_rate: float
    average_inference_time: float
    predictions_by_class: Dict[str, int]