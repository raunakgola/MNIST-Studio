# middleware/middlewares.py
import time
import uuid
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from logger.logging import logger

# Security configuration
security = HTTPBearer(auto_error=False)

def add_middleware(app):
    """Add all middleware to the FastAPI app"""
    # Add CORS middleware for cross-origin requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add trusted host middleware for additional security
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # In production, specify exact hosts
    )

    # Middleware for request logging and timing
    @app.middleware("http")
    async def log_requests(request, call_next):
        """
        Middleware to log all requests and measure response times.
        This is crucial for monitoring and debugging in production.
        """
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Log incoming request
        logger.info(f"Request {request_id}: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"Request {request_id} completed in {process_time:.3f}s - Status: {response.status_code}")
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        return response

def add_exception_handlers(app):
    """Add custom exception handlers to the FastAPI app"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        """Custom HTTP exception handler with detailed logging."""
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """General exception handler for unexpected errors."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

# Security dependency (optional authentication)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Optional authentication dependency.
    In production, implement proper JWT or API key validation here.
    """
    if credentials is None:
        return None  # Allow unauthenticated access for demo
    
    # Example: validate token (implement your authentication logic)
    # if not validate_token(credentials.credentials):
    #     raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    return {"user": "authenticated"}