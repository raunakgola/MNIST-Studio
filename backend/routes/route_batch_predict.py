# routes/route_batch_predict.py
import time
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from schema.input_schema import BatchImageData
from schema.response_schema import BatchPredictionResponse, PredictionResponse
from saved_models.predict import predict_batch_images, update_metrics
from middleware.middlewares import get_current_user
from logger.logging import logger

router = APIRouter()

@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    batch_data: BatchImageData,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user = Depends(get_current_user)
):
    """
    Batch prediction endpoint for processing multiple images efficiently.
    
    This endpoint accepts multiple sets of normalized pixel values and processes
    them together for improved efficiency. Each image should be a list of 784
    normalized pixel values representing a 28x28 grayscale image.
    """
    request_id = str(uuid.uuid4())
    batch_start_time = time.time()
    
    try:
        # Validate batch size
        if len(batch_data.images) > 10:
            raise HTTPException(
                status_code=400,
                detail="Batch size too large. Maximum 10 images per batch."
            )
        
        if len(batch_data.images) == 0:
            raise HTTPException(
                status_code=400,
                detail="Batch cannot be empty. Please provide at least one image."
            )
        
        # Run batch inference
        results = predict_batch_images(batch_data.images, request_id)
        
        predictions = []
        for i, result in enumerate(results["predictions"]):
            individual_prediction = PredictionResponse(
                prediction=result["prediction"],
                confidence=result["confidence"],
                probabilities=result["probabilities"],
                inference_time_ms=result["inference_time_ms"],
                request_id=f"{request_id}-{i}"
            )
            predictions.append(individual_prediction)
            
            # Update metrics for each successful prediction
            background_tasks.add_task(
                update_metrics,
                result["prediction"],
                0,  # Individual timing not tracked in batch
                success=True
            )
        
        # Log successful batch prediction
        logger.info(f"Batch prediction {request_id}: processed {len(batch_data.images)} images in {results['total_inference_time_ms']:.2f}ms")
        
        return BatchPredictionResponse(
            predictions=predictions,
            batch_size=len(batch_data.images),
            total_inference_time_ms=results["total_inference_time_ms"],
            average_inference_time_ms=results["average_inference_time_ms"],
            request_id=request_id
        )
        
    except ValueError as e:
        # Handle preprocessing errors
        for _ in range(len(batch_data.images)):
            background_tasks.add_task(update_metrics, -1, 0, success=False)
        logger.error(f"Batch preprocessing error for request {request_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Handle unexpected errors
        for _ in range(len(batch_data.images)):
            background_tasks.add_task(update_metrics, -1, 0, success=False)
        logger.error(f"Batch prediction error for request {request_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch prediction failed due to internal error")