# Server.py
import os
import uvicorn

if __name__ == "__main__":
    # Set model path via environment or default
    model_path = os.environ.get("MODEL_PATH", "saved_models/mnist_cnn_pruned_only.pth")
    
    # Ensure the model path is set as environment variable
    os.environ["MODEL_PATH"] = model_path
    
    # Verify model file exists before starting server
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        print("Please ensure the model file exists or set the correct MODEL_PATH environment variable")
        exit(1)
    
    print(f"Starting server with model: {model_path}")
    
    # Run the FastAPI server
    # Import the app directly since we're in the same directory
    from App import app
    
    uvicorn.run(
        app,  # Pass the app object directly
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        reload=False  # Set to True for development
    )