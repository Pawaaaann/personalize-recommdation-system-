#!/usr/bin/env python3
"""
Simplified server to run EduRec with minimal dependencies.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize data on startup."""
    logger.info("🚀 Starting EduRec API...")
    load_data()
    yield

app = FastAPI(title="EduRec API", description="Educational Recommendation System API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class RecommendationResponse(BaseModel):
    course_id: str
    score: float
    title: str
    explanation: List[str]

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    models_loaded: bool
    data_loaded: bool

# Global data
courses_df = None
interactions_df = None

def load_data():
    """Load course and interaction data."""
    global courses_df, interactions_df
    
    try:
        data_dir = Path("data")
        
        # Load courses
        courses_file = data_dir / "courses.csv"
        if courses_file.exists():
            courses_df = pd.read_csv(courses_file)
            logger.info(f"✅ Loaded {len(courses_df)} courses")
        else:
            logger.warning("❌ courses.csv not found")
            
        # Load interactions
        interactions_file = data_dir / "interactions.csv"
        if interactions_file.exists():
            interactions_df = pd.read_csv(interactions_file)
            logger.info(f"✅ Loaded {len(interactions_df)} interactions")
        else:
            logger.warning("❌ interactions.csv not found")
            
        return True
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        return False

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "EduRec API is running!",
        "timestamp": datetime.now(),
        "endpoints": ["/health", "/courses", "/recommend/{student_id}", "/docs"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "models_loaded": courses_df is not None and interactions_df is not None,
        "data_loaded": courses_df is not None and interactions_df is not None
    }

@app.get("/courses")
async def get_courses(limit: int = 20):
    """Get courses with optional limit."""
    if courses_df is None:
        raise HTTPException(status_code=503, detail="Courses data not loaded")
    
    courses_sample = courses_df.head(limit).to_dict("records")
    return {
        "courses": courses_sample,
        "total_count": len(courses_df),
        "showing": min(limit, len(courses_df))
    }

@app.get("/recommend/{student_id}", response_model=List[RecommendationResponse])
async def get_recommendations(student_id: str, k: int = 10):
    """Get personalized recommendations for a student."""
    if courses_df is None or interactions_df is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        # Simple popularity-based recommendations
        course_popularity = interactions_df['course_id'].value_counts()
        
        # Get user's previous interactions to filter out
        user_interactions = set()
        if 'student_id' in interactions_df.columns:
            user_courses = interactions_df[interactions_df['student_id'] == student_id]['course_id'].unique()
            user_interactions = set(user_courses)
        
        # Filter out user's previous courses and get top recommendations
        available_courses = course_popularity[~course_popularity.index.isin(user_interactions)]
        top_courses = available_courses.head(k)
        
        recommendations = []
        max_popularity = top_courses.max() if len(top_courses) > 0 else 1
        
        for i, (course_id, popularity) in enumerate(top_courses.items()):
            # Get course info
            course_info = courses_df[courses_df['course_id'] == course_id]
            title = "Unknown Course"
            if not course_info.empty:
                title = course_info.iloc[0].get('title', 'Unknown Course')
            
            # Calculate normalized score
            score = popularity / max_popularity if max_popularity > 0 else 0.5
            
            rec = RecommendationResponse(
                course_id=str(course_id),
                score=round(score, 3),
                title=title,
                explanation=["popular_course", "recommended_for_you"]
            )
            recommendations.append(rec)
        
        logger.info(f"Generated {len(recommendations)} recommendations for {student_id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@app.get("/course/{course_id}")
async def get_course_metadata(course_id: str):
    """Get metadata for a specific course."""
    if courses_df is None:
        raise HTTPException(status_code=503, detail="Courses data not loaded")
    
    try:
        course_data = courses_df[courses_df['course_id'] == course_id]
        if course_data.empty:
            raise HTTPException(status_code=404, detail="Course not found")
        
        course_row = course_data.iloc[0]
        return {
            "course_id": course_row["course_id"],
            "title": course_row.get("title", "Unknown"),
            "description": course_row.get("description", ""),
            "skill_tags": course_row.get("skill_tags", ""),
            "difficulty": course_row.get("difficulty", ""),
            "duration": course_row.get("duration", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting course metadata: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get system statistics."""
    if courses_df is None or interactions_df is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        stats = {
            "total_courses": len(courses_df),
            "total_interactions": len(interactions_df),
            "unique_students": interactions_df['student_id'].nunique() if 'student_id' in interactions_df.columns else 0,
            "unique_courses_with_interactions": interactions_df['course_id'].nunique(),
            "data_loaded": True
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.post("/interactions")
async def record_interaction(interaction: dict):
    """Record a new interaction event."""
    try:
        # Simple interaction recording - just log it
        logger.info(f"Recorded interaction: {interaction}")
        return {"message": "Interaction recorded successfully", "event": interaction}
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")

@app.get("/interactions/queue")
async def get_interactions_queue():
    """Get interactions queue (simplified)."""
    return {"interactions": [], "count": 0}

if __name__ == "__main__":
    import uvicorn
    print("🎯 Starting EduRec API server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("❤️ Health check at: http://localhost:8000/health")
    print("📊 Statistics at: http://localhost:8000/stats")
    print("\\nPress Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
