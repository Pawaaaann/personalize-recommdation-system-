#!/usr/bin/env python3
"""
FastAPI backend for the educational recommendation system.
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..models.hybrid import hybrid_recommend
from ..models.als_recommender import ALSRecommender
from ..models.baseline import BaselineRecommender
from ..data.data_loader import DataLoader
from ..monitoring.metrics import get_metrics_collector
from ..monitoring.ab_testing import get_ab_test_manager

# Initialize FastAPI app
app = FastAPI(
    title="Educational Recommendation System API",
    description="API for personalized course recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request monitoring middleware
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Middleware to monitor request latencies and counts."""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    endpoint = request.url.path
    method = request.method
    status = str(response.status_code)
    
    # Record metrics
    metrics_collector.record_request(endpoint, method, duration, status)
    
    return response

# Pydantic models
class InteractionEvent(BaseModel):
    student_id: str = Field(..., description="Student identifier")
    course_id: str = Field(..., description="Course identifier")
    event_type: str = Field(..., description="Type of interaction (view, enroll, complete)")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Event timestamp")

class RecommendationResponse(BaseModel):
    course_id: str = Field(..., description="Course identifier")
    score: float = Field(..., description="Recommendation score")
    explanation: List[str] = Field(..., description="List of explanation reasons")

class CourseMetadata(BaseModel):
    course_id: str = Field(..., description="Course identifier")
    title: str = Field(..., description="Course title")
    description: Optional[str] = Field(None, description="Course description")
    skill_tags: Optional[str] = Field(None, description="Comma-separated skill tags")
    difficulty: Optional[str] = Field(None, description="Course difficulty level")
    duration: Optional[str] = Field(None, description="Course duration")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    models_loaded: bool = Field(..., description="Whether recommendation models are loaded")

class ExperimentStatsResponse(BaseModel):
    name: str = Field(..., description="Experiment name")
    description: str = Field(..., description="Experiment description")
    is_active: bool = Field(..., description="Whether experiment is active")
    traffic_split: Dict[str, float] = Field(..., description="Traffic split configuration")
    assignments: Dict[str, int] = Field(..., description="User assignments per variant")
    conversions: Dict[str, Dict[str, int]] = Field(..., description="Conversion counts per variant")
    precision_at_10: Dict[str, float] = Field(..., description="Precision@10 scores per variant")

# Global variables for models and data
models_loaded = False
als_model: Optional[ALSRecommender] = None
baseline_model: Optional[BaselineRecommender] = None
courses_df: Optional[pd.DataFrame] = None
interactions_df: Optional[pd.DataFrame] = None

# Initialize monitoring
metrics_collector = get_metrics_collector()
ab_test_manager = get_ab_test_manager()

# Paths for data and models
DATA_DIR = Path("data")
MODELS_DIR = Path("models")
INTERACTIONS_QUEUE_FILE = Path("data/interactions_queue.jsonl")

def load_models_and_data():
    """Load pre-trained models and data."""
    global models_loaded, als_model, baseline_model, courses_df, interactions_df
    
    try:
        start_time = time.time()
        
        # Load data
        data_loader = DataLoader()
        courses_df = data_loader.load_courses()
        interactions_df = data_loader.load_interactions()
        
        # Update system metrics
        if courses_df is not None:
            metrics_collector.set_total_courses(len(courses_df))
        if interactions_df is not None:
            unique_users = interactions_df['student_id'].nunique()
            metrics_collector.set_active_users(unique_users)
        
        # Load ALS model if available
        als_model_path = MODELS_DIR / "als_model.pkl"
        if als_model_path.exists():
            als_start_time = time.time()
            als_model = ALSRecommender()
            als_model.load(str(als_model_path))
            als_duration = time.time() - als_start_time
            metrics_collector.record_model_load_time("als_model", als_duration)
            print(f"Loaded ALS model from {als_model_path} in {als_duration:.3f}s")
        else:
            print(f"ALS model not found at {als_model_path}")
        
        # Load baseline model
        baseline_start_time = time.time()
        baseline_model = BaselineRecommender(strategy="hybrid")
        baseline_model.fit(interactions_df, courses_df)
        baseline_duration = time.time() - baseline_start_time
        metrics_collector.record_model_load_time("baseline_model", baseline_duration)
        print("Loaded and fitted baseline model")
        
        models_loaded = True
        total_duration = time.time() - start_time
        print(f"Models and data loaded successfully in {total_duration:.3f}s")
        
    except Exception as e:
        print(f"Error loading models and data: {e}")
        models_loaded = False

def store_interaction(event: InteractionEvent):
    """Store interaction event to local queue."""
    try:
        # Ensure directory exists
        INTERACTIONS_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to JSONL file
        with open(INTERACTIONS_QUEUE_FILE, "a", encoding="utf-8") as f:
            event_dict = event.model_dump()
            if event_dict["timestamp"]:
                event_dict["timestamp"] = event_dict["timestamp"].isoformat()
            f.write(json.dumps(event_dict) + "\n")
        
        print(f"Stored interaction: {event.student_id} -> {event.course_id} ({event.event_type})")
        
    except Exception as e:
        print(f"Error storing interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to store interaction")

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for loading models and data."""
    load_models_and_data()
    yield

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Educational Recommendation System API",
    description="API for personalized course recommendations",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        models_loaded=models_loaded
    )

@app.get("/recommend/{student_id}", response_model=List[RecommendationResponse])
async def get_recommendations(
    student_id: str,
    k: int = Query(10, ge=1, le=50, description="Number of recommendations")
):
    """Get personalized course recommendations for a student."""
    if not models_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Get recommendations using hybrid approach
        recommendations = hybrid_recommend(
            user_id=student_id,
            N=k,
            als_model=als_model,
            baseline_model=baseline_model,
            courses_df=courses_df,
            interactions_df=interactions_df
        )
        
        # Convert to response format
        response = []
        for rec in recommendations:
            response.append(RecommendationResponse(
                course_id=str(rec["item_id"]),  # Convert to string
                score=round(rec["score"], 4),
                explanation=rec.get("explanations", [])
            ))
        
        # Record recommendation metrics
        metrics_collector.record_recommendation(
            algorithm="hybrid",
            user_id=student_id,
            count=len(response)
        )
        
        # Record recommendation scores
        for rec in response:
            metrics_collector.record_recommendation_score(
                algorithm="hybrid",
                score=rec.score
            )
        
        return response
        
    except Exception as e:
        print(f"Error getting recommendations for {student_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

@app.get("/course/{course_id}", response_model=CourseMetadata)
async def get_course_metadata(course_id: str):
    """Get metadata for a specific course."""
    if courses_df is None:
        raise HTTPException(status_code=503, detail="Course data not loaded")
    
    try:
        course_data = courses_df[courses_df["course_id"] == course_id]
        if course_data.empty:
            raise HTTPException(status_code=404, detail="Course not found")
        
        course_row = course_data.iloc[0]
        return CourseMetadata(
            course_id=course_row["course_id"],
            title=course_row["title"],
            description=course_row.get("description"),
            skill_tags=course_row.get("skill_tags"),
            difficulty=course_row.get("difficulty"),
            duration=course_row.get("duration")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting course metadata for {course_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve course metadata")

@app.post("/interactions")
async def record_interaction(event: InteractionEvent):
    """Record a new interaction event."""
    try:
        # Validate event type
        valid_event_types = ["view", "enroll", "complete", "rate", "like"]
        if event.event_type not in valid_event_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid event_type. Must be one of: {valid_event_types}"
            )
        
        # Store interaction
        store_interaction(event)
        
        # Record interaction metrics
        metrics_collector.record_interaction(event.event_type)
        
        # Record conversion for A/B testing if it's a conversion event
        if event.event_type in ["enroll", "complete"]:
            ab_test_manager.record_conversion(event.student_id, "new_algorithm_v1", event.event_type)
        
        return {"message": "Interaction recorded successfully", "event": event.model_dump()}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error recording interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")

@app.get("/interactions/queue")
async def get_interactions_queue():
    """Get all stored interactions (for debugging/admin purposes)."""
    try:
        if not INTERACTIONS_QUEUE_FILE.exists():
            return {"interactions": [], "count": 0}
        
        interactions = []
        with open(INTERACTIONS_QUEUE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    interactions.append(json.loads(line))
        
        return {"interactions": interactions, "count": len(interactions)}
        
    except Exception as e:
        print(f"Error reading interactions queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to read interactions queue")

@app.delete("/interactions/queue")
async def clear_interactions_queue():
    """Clear the interactions queue (for debugging/admin purposes)."""
    try:
        if INTERACTIONS_QUEUE_FILE.exists():
            INTERACTIONS_QUEUE_FILE.unlink()
        return {"message": "Interactions queue cleared successfully"}
        
    except Exception as e:
        print(f"Error clearing interactions queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear interactions queue")

# Monitoring endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            models_loaded=models_loaded
        )
    except Exception as e:
        print(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def get_metrics():
    """Get Prometheus metrics."""
    try:
        metrics_data = metrics_collector.get_metrics()
        return Response(
            content=metrics_data,
            media_type=metrics_collector.get_metrics_content_type()
        )
    except Exception as e:
        print(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@app.get("/experiments", response_model=List[Dict[str, Any]])
async def list_experiments():
    """List all A/B test experiments."""
    try:
        return ab_test_manager.list_experiments()
    except Exception as e:
        print(f"Failed to list experiments: {e}")
        raise HTTPException(status_code=500, detail="Failed to list experiments")

@app.get("/experiments/{experiment_name}", response_model=ExperimentStatsResponse)
async def get_experiment_stats(experiment_name: str):
    """Get statistics for a specific A/B test experiment."""
    try:
        stats = ab_test_manager.get_experiment_stats(experiment_name)
        if not stats:
            raise HTTPException(status_code=404, detail="Experiment not found")
        
        return ExperimentStatsResponse(**stats)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to get experiment stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get experiment statistics")

@app.post("/experiments/{experiment_name}/conversion")
async def record_conversion(
    experiment_name: str,
    user_id: str = Query(..., description="User ID"),
    conversion_type: str = Query(..., description="Type of conversion event")
):
    """Record a conversion event for A/B testing."""
    try:
        ab_test_manager.record_conversion(user_id, experiment_name, conversion_type)
        return {"message": "Conversion recorded successfully"}
    except Exception as e:
        print(f"Failed to record conversion: {e}")
        raise HTTPException(status_code=500, detail="Failed to record conversion")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 