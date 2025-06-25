# Global variables for model and metrics
#global_variables/global_variable.py
model = None
model_info = {}
prediction_metrics = {
    "total_predictions": 0,
    "successful_predictions": 0,
    "failed_predictions": 0,
    "average_inference_time": 0.0,
    "predictions_by_class": {str(i): 0 for i in range(10)}
}