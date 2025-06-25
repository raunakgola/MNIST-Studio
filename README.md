# ⚡ MNIST-Studio

A full-stack MNIST digit visualization and prediction tool built with React frontend and FastAPI backend. This interactive application allows users to draw digits on a 28×28 pixel grid and get real-time predictions using a trained deep learning model.

## 🌟 Features

**Interactive Drawing Interface**
- 28×28 pixel drawing grid that mirrors the MNIST dataset format
- Real-time pixel value extraction and visualization
- Responsive design optimized for both mobile and desktop devices
- Intuitive drawing controls with clear and reset functionality

**Deep Learning Pipeline**
- Containerized deep learning inference system
- FastAPI backend for high-performance model serving
- Real-time digit classification with confidence scores
- Optimized model architecture for quick predictions

**Full-Stack Architecture**
- Modern React frontend with component-based design
- RESTful API backend built with FastAPI
- Docker containerization for easy deployment
- Cross-platform compatibility

## 🚀 Quick Start

### Prerequisites

Before running the application, ensure you have the following installed:
- Node.js (v14 or higher)
- Python (v3.8 or higher)
- Docker (optional, for containerized deployment)

### Frontend Setup

Navigate to the frontend directory and install the required dependencies:

```bash
cd frontend
npm install
```

Configure the server URL by updating the environment file with your backend endpoint, then start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` (or the port specified by your development server).

### Backend Setup

The backend requires a Python virtual environment to manage dependencies effectively. First, create and activate a virtual environment:

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

Install the required packages from the requirements file:

```bash
pip install -r api_requirements.txt
```

Start the FastAPI server using the following command:

```bash
python -u "c:\Users\Raunak Gola\test\Server.py"
```

The API will be accessible at `http://localhost:8000` with automatic documentation available at `http://localhost:8000/docs`.

## 🐳 Docker Deployment

For a streamlined deployment experience, pre-built Docker containers are available on Docker Hub. This approach eliminates the need for local environment setup and ensures consistent performance across different systems.

### Pull Docker Images

First, pull the pre-built images from Docker Hub:

```bash
docker pull raunakgola123/mnist-frontend:latest
docker pull raunakgola123/mnist-backend:latest
```

### Run Frontend Container

Launch the frontend container with port mapping:

```bash
docker run -p 8080:80 raunakgola123/mnist-frontend:latest
```

The frontend will be accessible at `http://localhost:8080`.

### Run Backend Container

Start the backend container with logging configuration and port mapping:

```bash
docker run -d --name mnist-api-container \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  -p 8000:8000 \
  raunakgola123/mnist-backend:latest
```

The API will be available at `http://localhost:8000`.

## 📁 Project Structure

```
MNIST-Studio/
├── backend/          # FastAPI backend application
├── frontend/         # React frontend application
├── .gitignore        # Git ignore patterns
├── LICENSE           # Project license
└── README.md         # Project documentation
```

## 🎥 Demo Video

A demonstration video is included in the repository that showcases the application's features and functionality. Download the video file to see the interactive drawing interface and real-time prediction capabilities in action.

## 🛠️ Technical Architecture

**Frontend Technologies**
- React for component-based UI development
- Modern JavaScript (ES6+) for interactive functionality
- Responsive CSS for cross-device compatibility

**Backend Technologies**
- FastAPI for high-performance API development
- Python machine learning stack for model inference
- Asynchronous request handling for optimal performance
- RESTful API design for clean client-server communication

**Deployment Strategy**
- Docker containerization for consistent environments
- Multi-stage builds for optimized image sizes
- Configurable logging for production monitoring
- Port mapping for flexible deployment options

## 🤝 Contributing

Contributions are welcome! Whether you're interested in improving the machine learning model, enhancing the user interface, or optimizing the deployment process, your input helps make this project better for everyone.

## 📄 License

This project is licensed under the terms specified in the LICENSE file. Please review the license before using or contributing to this project.

## 🔗 Links

- **Frontend Container**: `raunakgola123/mnist-frontend:latest`
- **Backend Container**: `raunakgola123/mnist-backend:latest`
- **API Documentation**: Available at `/docs` endpoint when running the backend
