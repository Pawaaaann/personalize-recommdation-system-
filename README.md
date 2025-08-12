# EduRec - Education Recommendation System

A personalized education recommendation system built with Python, featuring collaborative filtering, content-based filtering, and hybrid approaches.

## Features

- **Collaborative Filtering**: User-based and item-based recommendations using ALS (Alternating Least Squares)
- **Content-Based Filtering**: Course similarity based on features and metadata
- **Hybrid Recommendations**: Combines multiple approaches for better accuracy
- **RESTful API**: FastAPI-based API for easy integration
- **Synthetic Data Generation**: Tools for generating sample educational data
- **Comprehensive Testing**: Unit tests for all components

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

### 1. Setup Development Environment

```bash
# Run the setup script
./dev_setup.sh

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Generate Sample Data

```bash
python -m src.edurec.data.generate_sample
```

### 3. Run the API Server

```bash
python -m uvicorn src.edurec.api.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Run Tests

```bash
pytest src/edurec/tests/
```

## API Documentation

Once the server is running, visit:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details 