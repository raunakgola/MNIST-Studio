# saved_models/model_architecture.py
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any
from logger.logging import logger

class CNNModel(nn.Module):
    """
    Recreation of the CNN model architecture from your training code.
    This must match exactly the architecture you used during training.
    """
    def __init__(self, num_classes=10, dropout_rate=0.25):  # Fixed: was 'init' instead of '__init__'
        super(CNNModel, self).__init__()  # Fixed: was 'init' instead of '__init__'
        
        # First convolutional block
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Second convolutional block
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Dropout for regularization
        self.dropout1 = nn.Dropout(dropout_rate)
        
        # Fully connected layers
        self.fc1 = nn.Linear(64 * 7 * 7, 128)
        self.dropout2 = nn.Dropout(dropout_rate)
        self.fc2 = nn.Linear(128, num_classes)
        
    def forward(self, x):
        # First conv block with ReLU activation and pooling
        x = self.pool1(F.relu(self.conv1(x)))
        
        # Second conv block with ReLU activation and pooling
        x = self.pool2(F.relu(self.conv2(x)))
        
        # Flatten the tensor for fully connected layers
        x = x.view(-1, 64 * 7 * 7)
        
        # Apply dropout and first fully connected layer
        x = self.dropout1(x)
        x = F.relu(self.fc1(x))
        
        # Apply dropout and final classification layer
        x = self.dropout2(x)
        x = self.fc2(x)
        
        return x

def load_model(model_path: str) -> torch.nn.Module:
    """
    Load the trained model with comprehensive error handling.
    This function ensures the model loads correctly and is ready for inference.
    """
    try:
        logger.info(f"Loading model from {model_path}")
        
        # Initialize model architecture
        model = CNNModel()
        
        # Load the state dictionary
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        # Load with map_location to handle CPU/GPU differences
        state_dict = torch.load(model_path, map_location=torch.device('cpu'))
        model.load_state_dict(state_dict)
        
        # Set to evaluation mode - crucial for inference
        model.eval()
        
        logger.info("Model loaded successfully")
        return model
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise RuntimeError(f"Model loading failed: {str(e)}")

def get_model_info(model: torch.nn.Module) -> Dict[str, Any]:
    """
    Extract useful information about the loaded model.
    This helps with API documentation and debugging.
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # Calculate approximate model size in MB
    model_size_mb = sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 * 1024)
    
    return {
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "model_size_mb": round(model_size_mb, 2),
        "architecture": "CNN with 2 Conv layers + 2 FC layers",
        "input_shape": [1, 28, 28],
        "output_classes": 10
    }