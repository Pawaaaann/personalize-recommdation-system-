# EduRec Frontend

This directory will contain the React frontend application for the EduRec education recommendation system.

## Planned Features

- **User Dashboard**: Personalized course recommendations and learning progress
- **Course Browser**: Browse and search available courses
- **Recommendation Engine**: View and interact with AI-generated course suggestions
- **User Profile**: Manage preferences and learning history
- **Responsive Design**: Mobile-first approach for all devices

## Technology Stack

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand or Redux Toolkit
- **HTTP Client**: Axios or React Query
- **UI Components**: Headless UI + custom components

## Development

This frontend will be scaffolded in a future update. For now, the backend API is available at:

- **Local Development**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Integration

The frontend will integrate with the following backend endpoints:

- `GET /recommend/{user_id}` - Get course recommendations
- `POST /recommend` - Get recommendations with custom parameters
- `GET /models` - List available recommendation models
- `GET /data/summary` - Get data statistics
- `GET /users/{user_id}/profile` - Get user profile
- `GET /courses/{course_id}/similar` - Get similar courses

## Getting Started

Once scaffolded, the frontend can be started with:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:5173 