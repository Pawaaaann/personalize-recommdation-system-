# EduRec - Education Recommendation System

## Overview

EduRec is a comprehensive AI-powered education recommendation platform that provides personalized course suggestions through multiple recommendation strategies. The system combines collaborative filtering (ALS), content-based filtering, and popularity-based approaches in a hybrid model. It features a Python FastAPI backend with comprehensive monitoring and A/B testing capabilities, paired with a React frontend that includes Firebase authentication, interest assessment flows, career path recommendations, and personalized learning roadmaps.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
The backend is built using FastAPI with a modular recommendation engine architecture:

**Recommendation Models:**
- **Hybrid Recommender**: Combines multiple approaches with configurable weights (ALS: 70%, content-based: 20%, popularity: 10%)
- **ALS (Alternating Least Squares)**: Uses the implicit library for collaborative filtering based on user-item interactions
- **Baseline Recommenders**: Includes popularity-based and content-based filtering using TF-IDF and cosine similarity
- **Interest-Based Recommendations**: Matches user interests, domains, and experience levels to course content

**Data Layer:**
- **DataLoader**: Handles CSV data loading for users, courses, and interactions
- **Synthetic Data Generator**: Creates realistic educational data for testing and development
- **Data Models**: Structured around users, courses, and interaction events (view, enroll, complete, rate)

**API Design:**
- RESTful endpoints for recommendations, course metadata, and user interactions
- CORS enabled for frontend integration
- Request/response models using Pydantic for validation
- Health check and metrics endpoints for monitoring

**Monitoring & Testing:**
- **Prometheus Metrics**: Tracks request latencies, recommendation counts, and model performance
- **A/B Testing Framework**: Supports traffic splitting and conversion tracking for algorithm experimentation
- **Redis Integration**: For caching experiment configurations and user assignments

### Frontend Architecture
The frontend uses React with TypeScript and modern development practices:

**Authentication System:**
- **Firebase Authentication**: Supports Google OAuth and email/password registration
- **User Context**: React context for managing authentication state across components
- **Persistent Sessions**: Maintains login state across browser sessions

**User Experience Flow:**
- **Interest Assessment**: 6-step guided process collecting domain preferences, experience level, and learning goals
- **Career Path Recommendations**: AI-powered matching with detailed career information, salary ranges, and skill requirements
- **Learning Roadmaps**: Structured weekly schedules with specific topics, courses, and project milestones
- **Course Discovery**: Integration with major learning platforms (Coursera, Udemy, edX, freeCodeCamp)

**State Management:**
- React hooks for local state management
- LocalStorage for persisting user assessments and preferences
- Context providers for global application state

**UI Framework:**
- Tailwind CSS for responsive design and component styling
- Lucide React for consistent iconography
- Custom component library with reusable UI elements

### Data Storage Strategy
The system uses file-based storage with plans for database integration:

**Current Implementation:**
- CSV files for courses, users, and interaction data
- LocalStorage for frontend user preferences and assessment data
- Redis for caching and A/B testing configurations

**Data Models:**
- **Courses**: ID, title, description, skill tags, difficulty, duration, category
- **Users**: ID, demographics, interests, experience level, learning goals
- **Interactions**: User-course pairs with event types (view, enroll, complete, rate) and timestamps

### Integration Architecture
The system is designed for scalability and external service integration:

**API Integration:**
- Proxy configuration for backend communication
- RESTful API design following OpenAPI specifications
- Error handling and retry mechanisms for external course platform APIs

**Deployment Strategy:**
- Docker containerization for consistent deployment
- Multi-stage builds separating development and production environments
- Environment-specific configuration management

## External Dependencies

### Core Python Libraries
- **FastAPI**: Web framework for building the REST API
- **Pandas & NumPy**: Data manipulation and numerical computing
- **Scikit-learn**: Machine learning utilities for content-based filtering
- **Implicit**: Collaborative filtering library for ALS implementation
- **Prometheus Client**: Metrics collection and monitoring
- **Redis**: Caching and session storage for A/B testing
- **Pydantic**: Data validation and settings management

### Frontend Dependencies
- **React & TypeScript**: Core frontend framework with type safety
- **Vite**: Build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Firebase**: Authentication and user management services
- **Lucide React**: Icon library for consistent UI elements

### External Services
- **Firebase Authentication**: User registration, login, and session management
- **Google OAuth**: Social login integration
- **Course Platform APIs**: Integration points for Coursera, Udemy, edX, and freeCodeCamp
- **Prometheus**: Metrics collection and monitoring infrastructure

### Development & Testing
- **Pytest**: Python testing framework with fixtures and mocking
- **Docker**: Containerization for development and deployment
- **Poetry**: Python dependency management (legacy, requirements.txt used)
- **ESLint & TypeScript**: Code quality and type checking for frontend

The architecture prioritizes modularity, allowing individual recommendation algorithms to be swapped or weighted differently, and supports both real-time recommendations and batch processing for model training and evaluation.