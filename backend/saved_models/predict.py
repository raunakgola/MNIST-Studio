# saved_models/prediction.py
import time
import torch
import torch.nn.functional as F
from typing import List, Dict, Any
# Fixed import path to use global_variable instead of global_variables
import global_variables.global_variable as gv
from logger.logging import logger

def preprocess_image(pixel_values: List[float]) -> torch.Tensor:
    """
    Preprocess pixel values for model inference.
    
    This function takes a list of pixel values and converts them into
    the tensor format expected by your trained model.
    """
    try:
        # Validate input length
        if len(pixel_values) != 784:
            raise ValueError(f"Expected 784 pixel values, got {len(pixel_values)}")
        
        # Convert list to tensor and reshape for MNIST (28x28 grayscale)
        tensor = torch.tensor(pixel_values, dtype=torch.float32).reshape(1, 1, 28, 28)  # Add batch dimension
        
        return tensor
        
    except Exception as e:
        logger.error(f"Image preprocessing failed: {str(e)}")
        raise ValueError(f"Image preprocessing failed: {str(e)}")

def preprocess_batch_images(batch_pixel_values: List[List[float]]) -> torch.Tensor:
    """
    Preprocess multiple sets of pixel values for batch inference.
    
    This function takes a list of pixel value lists and converts them into
    a batch tensor format expected by your trained model.
    """
    try:
        # Convert each list to tensor and stack them into a batch
        tensors = []
        for pixel_values in batch_pixel_values:
            if len(pixel_values) != 784:
                raise ValueError(f"Each image must have exactly 784 pixel values, got {len(pixel_values)}")
            
            # Reshape to (1, 28, 28) for single image
            tensor = torch.tensor(pixel_values, dtype=torch.float32).reshape(1, 28, 28)
            tensors.append(tensor)
        
        # Stack all tensors into a batch (batch_size, 1, 28, 28)
        batch_tensor = torch.stack(tensors)
        
        return batch_tensor
        
    except Exception as e:
        logger.error(f"Batch image preprocessing failed: {str(e)}")
        raise ValueError(f"Batch image preprocessing failed: {str(e)}")

def predict_single_image(pixel_values: List[float], request_id: str) -> Dict[str, Any]:
    """
    Predict a single image and return results.
    """
    # Check if model is loaded
    if gv.model is None:
        raise RuntimeError("Model not loaded. Please check server startup logs.")
    
    # Read and preprocess image
    processed_tensor = preprocess_image(pixel_values)
    
    # Run inference
    inference_start = time.time()
    with torch.no_grad():
        logits = gv.model(processed_tensor)
        probabilities = F.softmax(logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_class].item()
    
    inference_time = (time.time() - inference_start) * 1000  # Convert to milliseconds
    
    # Create probability dictionary
    prob_dict = {str(i): float(probabilities[0][i]) for i in range(10)}
    
    return {
        "prediction": predicted_class,
        "confidence": round(confidence, 4),
        "probabilities": prob_dict,
        "inference_time_ms": round(inference_time, 2)
    }

def predict_batch_images(batch_pixel_values: List[List[float]], request_id: str) -> Dict[str, Any]:
    """
    Predict multiple images in batch and return results.
    """
    # Check if model is loaded
    if gv.model is None:
        raise RuntimeError("Model not loaded. Please check server startup logs.")
        
    # Preprocess all images into a batch tensor
    batch_tensor = preprocess_batch_images(batch_pixel_values)
    
    # Run batch inference
    inference_start = time.time()
    predictions = []
    
    with torch.no_grad():
        # Process the entire batch at once for efficiency
        logits = gv.model(batch_tensor)
        probabilities = F.softmax(logits, dim=1)
        predicted_classes = torch.argmax(probabilities, dim=1)
        
        # Extract results for each image in the batch
        for i in range(len(batch_pixel_values)):
            predicted_class = predicted_classes[i].item()
            confidence = probabilities[i][predicted_class].item()
            
            # Create probability dictionary for this image
            prob_dict = {str(j): float(probabilities[i][j]) for j in range(10)}
            
            # Create individual prediction result
            individual_result = {
                "prediction": predicted_class,
                "confidence": round(confidence, 4),
                "probabilities": prob_dict,
                "inference_time_ms": 0  # Will be calculated after batch processing
            }
            
            predictions.append(individual_result)
    
    # Calculate timing information
    total_inference_time = (time.time() - inference_start) * 1000  # Convert to milliseconds
    average_inference_time = total_inference_time / len(batch_pixel_values)
    
    # Update individual prediction timing
    for prediction in predictions:
        prediction["inference_time_ms"] = round(average_inference_time, 2)
    
    return {
        "predictions": predictions,
        "total_inference_time_ms": round(total_inference_time, 2),
        "average_inference_time_ms": round(average_inference_time, 2)
    }

def update_metrics(predicted_class: int, inference_time: float, success: bool):
    """
    Background task to update prediction metrics.
    This runs asynchronously to avoid impacting response times.
    """
    gv.prediction_metrics["total_predictions"] += 1
    
    if success:
        gv.prediction_metrics["successful_predictions"] += 1
        
        # Update average inference time (only if inference_time > 0)
        if inference_time > 0:
            current_avg = gv.prediction_metrics["average_inference_time"]
            total_successful = gv.prediction_metrics["successful_predictions"]
            gv.prediction_metrics["average_inference_time"] = (
                (current_avg * (total_successful - 1) + inference_time) / total_successful
            )
        
        # Update class-specific metrics
        if 0 <= predicted_class <= 9:
            gv.prediction_metrics["predictions_by_class"][str(predicted_class)] += 1
    else:
        gv.prediction_metrics["failed_predictions"] += 1
