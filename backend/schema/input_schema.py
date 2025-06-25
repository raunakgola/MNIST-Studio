# schema/input_schema.py
from pydantic import BaseModel, Field
from typing import List

class ImageData(BaseModel):
    """
    Model for single image pixel data.
    """
    pixel_values: List[float] = Field(
        ..., 
        description="List containing normalized image pixel values (784 values for 28x28 MNIST images)",
        min_items=784,  # Additional validation - ensures exactly 784 values
        max_items=784,
        example=[0.1, 0.2, 0.3]  # Shows example in the API docs
    )

class BatchImageData(BaseModel):
    """
    Model for batch image pixel data.
    This allows you to send multiple images at once for efficient processing.
    """
    images: List[List[float]] = Field(
        ...,
        description="List of images, where each image is a list of 784 normalized pixel values",
        max_items=10,  # Limit batch size to prevent overwhelming the server
        example=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]  # Example showing format
    )