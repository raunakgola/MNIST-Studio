# routes/route_root.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "message": "MNIST CNN Prediction API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/predict/batch",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }