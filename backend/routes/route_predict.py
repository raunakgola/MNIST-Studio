# routes/route_predict.py
import time
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from schema.input_schema import ImageData
from schema.response_schema import PredictionResponse
from saved_models.predict import predict_single_image, update_metrics
from middleware.middlewares import get_current_user
from logger.logging import logger

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_digit(
    image_data: ImageData,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user = Depends(get_current_user)
):
    """
    Main prediction endpoint for digit classification.
    
    This endpoint accepts normalized pixel values for a 28x28 grayscale image,
    runs inference using a trained neural network, and returns prediction
    results with confidence scores.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Run inference
        result = predict_single_image(image_data.pixel_values, request_id)
        
        # Update metrics in background
        background_tasks.add_task(
            update_metrics,
            result["prediction"],
            result["inference_time_ms"],
            success=True
        )
        
        # Log successful prediction
        logger.info(f"Prediction {request_id}: digit={result['prediction']}, confidence={result['confidence']:.4f}")
        
        return PredictionResponse(
            prediction=result["prediction"],
            confidence=result["confidence"],
            probabilities=result["probabilities"],
            inference_time_ms=result["inference_time_ms"],
            request_id=request_id
        )
        
    except ValueError as e:
        # Handle preprocessing errors
        background_tasks.add_task(update_metrics, -1, 0, success=False)
        logger.error(f"Preprocessing error for request {request_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Handle unexpected errors
        background_tasks.add_task(update_metrics, -1, 0, success=False)
        logger.error(f"Prediction error for request {request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed due to internal error")