import React, { useState, useRef, useCallback } from 'react';
import { RotateCcw, Download, Send, Github } from 'lucide-react';

const MNISTDrawingGrid = () => {
  const [grid, setGrid] = useState(() => Array(28).fill().map(() => Array(28).fill(0)));
  const [isDrawing, setIsDrawing] = useState(false);
  const [pixelValues, setPixelValues] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasDrawing, setHasDrawing] = useState(false);
  const gridRef = useRef(null);

  const getPixelFromPosition = useCallback((clientX, clientY) => {
    if (!gridRef.current) return null;
    
    const rect = gridRef.current.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;
    
    const cellWidth = rect.width / 28;
    const cellHeight = rect.height / 28;
    
    const col = Math.floor(x / cellWidth);
    const row = Math.floor(y / cellHeight);
    
    if (row >= 0 && row < 28 && col >= 0 && col < 28) {
      return { row, col, x: x % cellWidth, y: y % cellHeight, cellWidth, cellHeight };
    }
    return null;
  }, []);

  const calculatePixelIntensity = useCallback((x, y, cellWidth, cellHeight) => {
    // Calculate distance from center of the cell
    const centerX = cellWidth / 2;
    const centerY = cellHeight / 2;
    const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
    const maxDistance = Math.sqrt(Math.pow(centerX, 2) + Math.pow(centerY, 2));
    
    // Invert distance so closer to center = higher value
    const intensity = Math.max(0, 1 - (distance / maxDistance));
    return Math.round(intensity * 255);
  }, []);

  const drawOnGrid = useCallback((clientX, clientY) => {
    const pixel = getPixelFromPosition(clientX, clientY);
    if (!pixel) return;

    const { row, col, x, y, cellWidth, cellHeight } = pixel;
    const intensity = calculatePixelIntensity(x, y, cellWidth, cellHeight);
    
    setGrid(prevGrid => {
      const newGrid = [...prevGrid];
      newGrid[row] = [...newGrid[row]];
      // Use maximum value to allow building up intensity
      newGrid[row][col] = Math.max(newGrid[row][col], intensity);
      return newGrid;
    });
    
    // Mark that user has drawn something
    setHasDrawing(true);
  }, [getPixelFromPosition, calculatePixelIntensity]);

  // Mouse event handlers
  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDrawing(true);
    drawOnGrid(e.clientX, e.clientY);
  };

  const handleMouseMove = (e) => {
    e.preventDefault();
    if (isDrawing) {
      drawOnGrid(e.clientX, e.clientY);
    }
  };

  const handleMouseUp = (e) => {
    e.preventDefault();
    setIsDrawing(false);
  };

  // Touch event handlers
  const handleTouchStart = (e) => {
    e.preventDefault();
    setIsDrawing(true);
    const touch = e.touches[0];
    drawOnGrid(touch.clientX, touch.clientY);
  };

  const handleTouchMove = (e) => {
    e.preventDefault();
    if (isDrawing && e.touches.length > 0) {
      const touch = e.touches[0];
      drawOnGrid(touch.clientX, touch.clientY);
    }
  };

  const handleTouchEnd = (e) => {
    e.preventDefault();
    setIsDrawing(false);
  };

  const clearGrid = () => {
    setGrid(Array(28).fill().map(() => Array(28).fill(0)));
    setPixelValues(null);
    setPrediction(null);
    setError(null);
    setHasDrawing(false);
  };

    // Function to handle GitHub button click
  const openGitHub = () => {
    window.open('https://github.com/raunakgola/MNIST-Studio', '_blank', 'noopener,noreferrer');
  };

  const getPixelValues = () => {
    // Flatten the 2D array and normalize values to 0-1 range (like MNIST)
    const flatValues = grid.flat().map(val => parseFloat((val / 255).toFixed(3)));
    setPixelValues(flatValues);
    setPrediction(null);
    setError(null);
  };

  const sendToServer = async () => {
    if (!pixelValues) {
      setError('Please extract pixel values first');
      return;
    }

    setIsLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const serverUrl = import.meta.env.VITE_PREDICTION_SERVER_URL;
      
      const response = await fetch(serverUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pixel_values: pixelValues
        })
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const result = await response.json();
      setPrediction(result);
    } catch (err) {
      setError(`Failed to send data to server: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getGrayscaleValue = (intensity) => {
    return `rgb(${intensity}, ${intensity}, ${intensity})`;
  };

  const formatConfidence = (confidence) => {
    return (confidence * 100).toFixed(1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-4 sm:py-8 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-6 sm:mb-8">
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-2">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-800">MNIST Drawing Canvas</h1>
            <button
              onClick={openGitHub}
              className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition-all duration-200 shadow-md hover:shadow-lg text-sm sm:text-base"
              title="View source code on GitHub"
            >
              <Github size={18} />
              Source Code
            </button>
          </div>
          <p className="text-sm sm:text-base lg:text-lg text-gray-600">Draw digits on the 28×28 grid to generate MNIST-compatible data</p>
        </div>
        
        <div className="flex flex-col xl:flex-row gap-6 lg:gap-8 items-start">
          {/* Drawing Area */}
          <div className="w-full xl:flex-1 bg-white rounded-xl shadow-lg p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-3">
              <h2 className="text-lg sm:text-xl font-semibold text-gray-800">Drawing Grid</h2>
              <div className="flex gap-2 sm:gap-3 w-full sm:w-auto">
                <button
                  onClick={clearGrid}
                  className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-3 sm:px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-all duration-200 shadow-md hover:shadow-lg text-sm sm:text-base"
                >
                  <RotateCcw size={16} />
                  Clear
                </button>
                <button
                  onClick={getPixelValues}
                  disabled={!hasDrawing}
                  className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-3 sm:px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg text-sm sm:text-base"
                >
                  <Download size={16} />
                  Extract Data
                </button>
                <button
                  onClick={sendToServer}
                  disabled={!pixelValues || isLoading}
                  className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-3 sm:px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg text-sm sm:text-base"
                >
                  <Send size={16} />
                  {isLoading ? 'Predicting...' : 'Predict'}
                </button>
              </div>
            </div>

            <div className="flex justify-center">
              <div 
                ref={gridRef}
                className="border-2 border-gray-300 cursor-crosshair select-none rounded-lg overflow-hidden shadow-inner w-full max-w-[280px] sm:max-w-[400px] md:max-w-[500px] lg:max-w-[560px] aspect-square touch-none"
                style={{ 
                  display: 'grid',
                  gridTemplateColumns: 'repeat(28, 1fr)',
                  gridTemplateRows: 'repeat(28, 1fr)'
                }}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                onTouchStart={handleTouchStart}
                onTouchMove={handleTouchMove}
                onTouchEnd={handleTouchEnd}
                onTouchCancel={handleTouchEnd}
              >
                {grid.map((row, rowIndex) =>
                  row.map((cell, colIndex) => (
                    <div
                      key={`${rowIndex}-${colIndex}`}
                      className="border-r border-b border-gray-100 last:border-r-0 [&:nth-child(28n)]:border-r-0"
                      style={{
                        backgroundColor: getGrayscaleValue(cell),
                        width: '100%',
                        height: '100%'
                      }}
                    />
                  ))
                )}
              </div>
            </div>

            <div className="mt-4 text-center text-xs sm:text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
              <p><strong>How to use:</strong> Click and drag to draw digits on desktop, or touch and drag on mobile. Pixel intensity varies based on distance from cell center.</p>
            </div>
          </div>

          {/* Information Panel */}
          <div className="w-full xl:w-80 2xl:w-96 space-y-4 sm:space-y-6">
            {/* Instructions */}
            <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-3">Instructions</h3>
              <div className="space-y-2 text-xs sm:text-sm text-gray-600">
                <p>• Draw digits (0-9) by clicking and dragging on desktop or touching and dragging on mobile</p>
                <p>• Pixel intensity is calculated based on position within each cell</p>
                <p>• Use "Clear" to start over with a blank canvas</p>
                <p>• Click "Extract Data" to get the 784 pixel values in MNIST format</p>
                <p>• Click "Predict" to send data to the ML server for digit recognition</p>
              </div>
            </div>

            {/* Grid Info */}
            <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-3">Grid Information</h3>
              <div className="space-y-2 text-xs sm:text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Dimensions:</span>
                  <span className="font-medium">28 × 28 pixels</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total pixels:</span>
                  <span className="font-medium">784</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Value range:</span>
                  <span className="font-medium">0.0 - 1.0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Format:</span>
                  <span className="font-medium">MNIST compatible</span>
                </div>
              </div>
            </div>

            {/* Prediction Results */}
            {prediction && (
              <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-3">Prediction Result</h3>
                
                {/* Main Prediction */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                  <div className="text-center">
                    <div className="text-4xl font-bold text-green-700 mb-2">{prediction.prediction}</div>
                    <div className="text-sm text-green-600">
                      Confidence: {formatConfidence(prediction.confidence)}%
                    </div>
                  </div>
                </div>

                {/* All Probabilities */}
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">All Probabilities:</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(prediction.probabilities).map(([digit, prob]) => (
                      <div 
                        key={digit}
                        className={`flex justify-between items-center p-2 rounded text-xs ${
                          parseInt(digit) === prediction.prediction 
                            ? 'bg-green-100 border border-green-300' 
                            : 'bg-gray-50'
                        }`}
                      >
                        <span className="font-medium">Digit {digit}:</span>
                        <span>{formatConfidence(prob)}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Additional Info */}
                <div className="mt-4 pt-3 border-t border-gray-200 text-xs text-gray-500">
                  <div className="flex justify-between">
                    <span>Inference Time:</span>
                    <span>{prediction.inference_time_ms}ms</span>
                  </div>
                  <div className="flex justify-between mt-1">
                    <span>Request ID:</span>
                    <span className="font-mono text-xs truncate ml-2">{prediction.request_id}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-white rounded-xl shadow-lg p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold text-gray-800 mb-3">Error</h3>
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Pixel Values Display */}
        {pixelValues && (
          <div className="mt-6 lg:mt-8 bg-white rounded-xl shadow-lg p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-2">
              <h2 className="text-lg sm:text-xl font-semibold text-gray-800">Extracted Pixel Values</h2>
              <span className="text-xs sm:text-sm text-gray-600">784 values (28×28 grid)</span>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-3 sm:p-4 max-h-48 sm:max-h-64 overflow-y-auto">
              <pre className="text-xs font-mono text-gray-700 whitespace-pre-wrap break-all">
                [{pixelValues.join(', ')}]
              </pre>
            </div>
            
            <div className="mt-3 text-xs sm:text-sm text-gray-600 bg-blue-50 rounded-lg p-3">
              <p><strong>Note:</strong> Values are normalized to [0, 1] range where 0 = black and 1 = white, matching MNIST dataset format.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MNISTDrawingGrid;