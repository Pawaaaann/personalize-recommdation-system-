# EduRec - Education Recommendation System

A personalized education recommendation system built with Python, featuring collaborative filtering, content-based filtering, and hybrid approaches.

## Features

- **Collaborative Filtering**: User-based and item-based recommendations using ALS (Alternating Least Squares)
- **Content-Based Filtering**: Course similarity based on features and metadata
- **Hybrid Recommendations**: Combines multiple approaches for better accuracy
- **RESTful API**: FastAPI-based API for easy integration
- **Synthetic Data Generation**: Tools for generating sample educational data
- **Comprehensive Testing**: Unit tests for all components
- **Monitoring & Observability**: Prometheus metrics collection and health monitoring
- **A/B Testing Framework**: Experiment management with traffic splitting and conversion tracking
- **Performance Metrics**: Request latency, recommendation counts, and model performance tracking

## Project Structure

```
edurec/
├── src/edurec/
│   ├── data/           # Data loaders and synthetic data generators
│   ├── models/         # Recommendation algorithms
│   ├── api/            # FastAPI application
│   └── tests/          # Unit tests
├── frontend/           # React frontend (to be scaffolded)
├── docker/             # Docker configuration
├── pyproject.toml      # Poetry dependencies
└── dev_setup.sh        # Development setup script
```

## Requirements

- Python 3.10+
- Poetry (recommended) or pip

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Build and run all services
docker-compose up --build

# Access the application:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
# - Health Check: http://localhost:8000/health
# - Metrics: http://localhost:8000/metrics
# - Prometheus: http://localhost:9090
# - Redis: localhost:6379
```

### Option 2: Development Environment

```bash
# Run the setup script
./dev_setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Generate Sample Data

```bash
python -m src.edurec.data.generate_sample
```

### Run the API Server

```bash
python -m uvicorn src.edurec.api.main:app --reload
```

The API will be available at `http://localhost:8000`

### Run Tests

```bash
pytest src/edurec/tests/
```

## API Documentation

Once the server is running, visit:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Monitoring & A/B Testing

### Health Check
- **Endpoint**: `GET /health`
- **Description**: Service health status and model loading status

### Metrics
- **Endpoint**: `GET /metrics`
- **Description**: Prometheus-formatted metrics including:
  - Request latencies and counts
  - Recommendation generation metrics
  - Model performance metrics
  - A/B testing metrics
  - System metrics (active users, total courses)

### A/B Testing
- **List Experiments**: `GET /experiments`
- **Experiment Stats**: `GET /experiments/{experiment_name}`
- **Record Conversion**: `POST /experiments/{experiment_name}/conversion`

### Prometheus Dashboard
- **URL**: `http://localhost:9090`
- **Description**: Time-series metrics visualization and alerting

### Testing Monitoring Features
```bash
# Run the monitoring test script
python src/edurec/monitoring/test_monitoring.py
```

## Development

### Adding New Models

1. Create a new file in `src/edurec/models/`
2. Implement the `BaseRecommender` interface
3. Add tests in `src/edurec/tests/models/`
4. Update the API to include the new model

### Data Format

The system expects educational data in the following format:
- **Users**: User IDs and optional demographic information
- **Courses**: Course IDs, titles, descriptions, and metadata
- **Interactions**: User-course interactions (enrollments, ratings, completions)

## Docker

### Services

The application consists of three main services:

- **Backend** (`Dockerfile.backend`): Python FastAPI application
- **Frontend** (`frontend/Dockerfile`): React application served by Nginx
- **Redis** (`redis:7-alpine`): In-memory data store for caching and job queues

### Development with Docker

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build
```

### Production Deployment

```bash
# Build production images
docker build -f Dockerfile.backend -t edurec-backend .
docker build -f frontend/Dockerfile -t edurec-frontend ./frontend

# Run with production settings
docker-compose -f docker-compose.yml up -d
```

## CI/CD

The project includes GitHub Actions CI/CD pipeline that:

- Runs linting (flake8) and type checking (mypy)
- Executes unit tests with pytest
- Builds and pushes Docker images to Docker Hub (on main branch)

### Required Secrets

For the CI/CD pipeline to work, add these secrets to your GitHub repository:

- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details 