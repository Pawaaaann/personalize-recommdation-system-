#!/usr/bin/env python3
"""
Quick start server for EduRec with minimal setup.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import uvicorn
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EduRec API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # Load interactions
        interactions_file = data_dir / "interactions.csv"
        if interactions_file.exists():
            interactions_df = pd.read_csv(interactions_file)
            logger.info(f"✅ Loaded {len(interactions_df)} interactions")
            
        return True
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup."""
    logger.info("🚀 Starting EduRec API...")
    load_data()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "EduRec API is running!",
        "status": "healthy",
        "endpoints": ["/health", "/courses", "/recommend/{student_id}"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
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
        "total": len(courses_df)
    }

@app.get("/recommend/{student_id}")
async def get_recommendations(student_id: str, limit: int = 10):
    """Get course recommendations for a student."""
    if courses_df is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        # Simple popularity-based recommendations
        popular_courses = courses_df.head(limit)
        
        recommendations = []
        for _, course in popular_courses.iterrows():
            rec = {
                "course_id": course["course_id"],
                "title": course.get("title", "Unknown Course"),
                "score": 0.8,
                "explanation": ["Popular course", "High enrollment"]
            }
            recommendations.append(rec)
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@app.get("/course/{course_id}")
async def get_course_metadata(course_id: int):
    """Get metadata for a specific course."""
    if courses_df is None:
        raise HTTPException(status_code=503, detail="Courses data not loaded")
    
    try:
        course_data = courses_df[courses_df['course_id'] == course_id]
        if course_data.empty:
            raise HTTPException(status_code=404, detail="Course not found")
        
        course_row = course_data.iloc[0]
        return {
            "course_id": int(course_row["course_id"]),
            "title": str(course_row.get("title", "Unknown")),
            "description": str(course_row.get("description", "")),
            "skill_tags": str(course_row.get("skill_tags", "")),
            "difficulty": "Beginner",  # Default since not in CSV
            "duration_hours": int(course_row.get("duration_hours", 0))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting course metadata: {str(e)}")

@app.post("/interactions")
async def record_interaction(interaction: dict):
    """Record a new interaction event."""
    try:
        logger.info(f"Recorded interaction: {interaction}")
        return {"message": "Interaction recorded successfully", "event": interaction}
    except Exception as e:
        logger.error(f"Error recording interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")

if __name__ == "__main__":
    print("🎯 Starting EduRec API server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("❤️ Health check at: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
