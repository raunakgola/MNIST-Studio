# App.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from logger.logging import logger
# Fixed import path to match actual file name
import global_variables.global_variable as gv
from saved_models.model_architecture import load_model, get_model_info
from middleware.middlewares import add_middleware, add_exception_handlers

# Import routers
from routes.route_root import router as root_router
from routes.route_health import router as health_router
from routes.route_metrics import router as metrics_router
from routes.route_predict import router as predict_router
from routes.route_batch_predict import router as batch_router

def _load_model(model_path: str):
    """Load the model and update global variables."""
    if not model_path or not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    try:
        # Load model and update global variables
        gv.model = load_model(model_path)
        gv.model_info = get_model_info(gv.model)
        logger.info(f"Model loaded successfully from {model_path}")
        logger.info(f"Model info: {gv.model_info}")
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle events."""
    logger.info("Starting MNIST API application")
    try:
        model_path = os.environ.get("MODEL_PATH")
        if not model_path:
            raise ValueError("MODEL_PATH environment variable is required")
        
        _load_model(model_path)
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise RuntimeError(f"Application startup failed: {str(e)}")
    
    yield
    
    logger.info("Shutting down MNIST API application")

# Initialize FastAPI app
app = FastAPI(
    title="MNIST CNN Prediction API",
    description="Industrial-level API for MNIST digit classification using CNN",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware and exception handlers
add_middleware(app)
add_exception_handlers(app)

# Include routes
app.include_router(root_router)
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(predict_router)
app.include_router(batch_router)