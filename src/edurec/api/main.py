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

class InterestBasedRecommendationRequest(BaseModel):
    interests: List[str] = Field(..., description="List of user interests")
    domain: Optional[str] = Field(None, description="User's selected domain")
    subdomain: Optional[str] = Field(None, description="User's selected subdomain")
    experience_level: Optional[str] = Field(None, description="User's experience level")
    n_recommendations: int = Field(5, ge=4, le=20, description="Number of recommendations (minimum 4)")

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
        
        # Debug logging for data loading
        print(f"Data loading debug:")
        print(f"- courses_df type: {type(courses_df)}")
        print(f"- courses_df shape: {courses_df.shape if courses_df is not None else 'None'}")
        if courses_df is not None:
            print(f"- courses_df columns: {courses_df.columns.tolist()}")
            print(f"- First 5 course IDs: {courses_df['course_id'].head(5).tolist()}")
            print(f"- Last 5 course IDs: {courses_df['course_id'].tail(5).tolist()}")
            print(f"- Course ID 499 exists: {499 in courses_df['course_id'].values}")
        
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
        import traceback
        traceback.print_exc()
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

@app.post("/recommendations/interest-based", response_model=List[RecommendationResponse])
async def get_interest_based_recommendations(request: InterestBasedRecommendationRequest):
    """Get personalized course recommendations based on user interests."""
    if not models_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Ensure minimum of 4 recommendations
        n_recs = max(4, request.n_recommendations)
        
        # Use baseline model with content-based strategy for interest-based recommendations
        if baseline_model is None:
            raise HTTPException(status_code=503, detail="Baseline model not loaded")
        
        all_recommendations = []
        seen_courses = set()
        
        # Strategy 1: Try content-based filtering with user interests
        try:
            print(f"Attempting content-based recommendations with interests: {request.interests}")
            
            # Import the content-based recommender directly
            from ..models.baseline import content_based_recommender
            
            # Use content-based recommender directly with user interests
            query_text = " ".join(request.interests)
            content_course_ids = content_based_recommender(
                courses_df, query_text=query_text, top_n=n_recs * 3
            )
            
            print(f"Content-based recommender returned {len(content_course_ids)} course IDs")
            
            # Convert course IDs to recommendation format
            for i, course_id in enumerate(content_course_ids):
                if course_id not in seen_courses and len(all_recommendations) < n_recs:
                    # Calculate score based on position (higher position = higher score)
                    score = 1.0 - (i / len(content_course_ids))
                    
                    content_rec = {
                        "item_id": course_id,
                        "score": score,
                        "explanations": ["Based on your interests", "Content-based match"]
                    }
                    all_recommendations.append(content_rec)
                    seen_courses.add(course_id)
                    
        except Exception as e:
            print(f"Content-based recommendations failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Strategy 2: If we still need more, try popularity-based recommendations
        if len(all_recommendations) < n_recs:
            try:
                print(f"Attempting popularity-based recommendations to get {n_recs - len(all_recommendations)} more")
                
                # Import the popularity recommender directly
                from ..models.baseline import popularity_recommender
                
                # Use popularity recommender directly
                pop_course_ids = popularity_recommender(interactions_df, n_recs * 2)
                print(f"Popularity-based recommender returned {len(pop_course_ids)} course IDs")
                
                # Add unique popularity-based recommendations
                for i, course_id in enumerate(pop_course_ids):
                    if course_id not in seen_courses and len(all_recommendations) < n_recs:
                        # Calculate score based on popularity position
                        score = 1.0 - (i / len(pop_course_ids))
                        
                        pop_rec = {
                            "item_id": course_id,
                            "score": score,
                            "explanations": ["Popular course", "Widely taken by students"]
                        }
                        all_recommendations.append(pop_rec)
                        seen_courses.add(course_id)
                        
            except Exception as e:
                print(f"Popularity-based recommendations failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Strategy 3: If we still don't have enough, get random courses from the dataset
        if len(all_recommendations) < n_recs:
            try:
                print(f"Attempting to get {n_recs - len(all_recommendations)} random courses from dataset")
                # Get random courses from the dataset
                available_courses = courses_df[~courses_df['course_id'].isin(seen_courses)]
                if len(available_courses) > 0:
                    sample_size = min(n_recs - len(all_recommendations), len(available_courses))
                    sample_courses = available_courses.sample(sample_size)
                    
                    for _, course_row in sample_courses.iterrows():
                        if len(all_recommendations) < n_recs:
                            synthetic_rec = {
                                "item_id": course_row['course_id'],
                                "score": 0.5,  # Default score for random recommendations
                                "explanations": ["Course from your field", "Available in our catalog"]
                            }
                            all_recommendations.append(synthetic_rec)
                            seen_courses.add(course_row['course_id'])
                    
                    print(f"Added {len(sample_courses)} random courses from dataset")
            except Exception as e:
                print(f"Random course sampling failed: {e}")
        
        # Strategy 4: Ultimate fallback - create generic recommendations only if we have less than 4
        if len(all_recommendations) < 4:
            print(f"Using generic fallback for {4 - len(all_recommendations)} recommendations")
            generic_courses = [
                {
                    "item_id": "generic_1",
                    "score": 0.7,
                    "explanations": ["Foundation course for beginners", "Essential skills development"]
                },
                {
                    "item_id": "generic_2", 
                    "score": 0.6,
                    "explanations": ["Popular starting point", "Industry standard course"]
                },
                {
                    "item_id": "generic_3",
                    "score": 0.5,
                    "explanations": ["Recommended for your level", "Good introduction to the field"]
                },
                {
                    "item_id": "generic_4",
                    "score": 0.4,
                    "explanations": ["Widely taken course", "Builds fundamental knowledge"]
                }
            ]
            
            for rec in generic_courses:
                if len(all_recommendations) < 4:
                    all_recommendations.append(rec)
        
        # Ensure we have exactly the requested number of recommendations
        final_recommendations = all_recommendations[:n_recs]
        
        print(f"Final recommendations breakdown:")
        print(f"- Total generated: {len(all_recommendations)}")
        print(f"- Final count: {len(final_recommendations)}")
        print(f"- Real course IDs: {[r['item_id'] for r in final_recommendations if not str(r['item_id']).startswith('generic_')]}")
        print(f"- Generic fallbacks: {[r['item_id'] for r in final_recommendations if str(r['item_id']).startswith('generic_')]}")
        
        # Convert to response format
        response = []
        for rec in final_recommendations:
            response.append(RecommendationResponse(
                course_id=str(rec["item_id"]),
                score=round(rec["score"], 4),
                explanation=rec.get("explanations", ["Based on your interests", "Popular in your field"])
            ))
        
        # Record recommendation metrics
        metrics_collector.record_recommendation(
            algorithm="interest_based",
            user_id="interest_based_user",
            count=len(response)
        )
        
        # Record recommendation scores
        for rec in response:
            metrics_collector.record_recommendation_score(
                algorithm="interest_based",
                score=rec.score
            )
        
        print(f"Generated {len(response)} interest-based recommendations")
        return response
        
    except Exception as e:
        print(f"Error getting interest-based recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate interest-based recommendations")

@app.get("/debug/recommendations")
async def debug_recommendations():
    """Debug endpoint to check recommendation system status."""
    try:
        debug_info = {
            "models_loaded": models_loaded,
            "baseline_model_available": baseline_model is not None,
            "courses_df_available": courses_df is not None,
            "interactions_df_available": interactions_df is not None,
            "total_courses": len(courses_df) if courses_df is not None else 0,
            "total_interactions": len(interactions_df) if interactions_df is not None else 0,
            "sample_courses": []
        }
        
        if courses_df is not None and len(courses_df) > 0:
            sample_courses = courses_df.head(3)[['course_id', 'title', 'skill_tags']].to_dict('records')
            debug_info["sample_courses"] = sample_courses
        
        return debug_info
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/course/{course_id}", response_model=CourseMetadata)
async def get_course_metadata(course_id: str):
    """Get metadata for a specific course."""
    if courses_df is None:
        raise HTTPException(status_code=503, detail="Course data not loaded")
    
    try:
        # Convert course_id to int for comparison with DataFrame
        try:
            course_id_int = int(course_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid course ID format")
        
        # Debug logging
        print(f"Looking for course ID: {course_id_int}")
        print(f"Available course IDs (first 10): {courses_df['course_id'].head(10).tolist()}")
        print(f"Available course IDs (last 10): {courses_df['course_id'].tail(10).tolist()}")
        print(f"Course ID {course_id_int} exists: {course_id_int in courses_df['course_id'].values}")
        
        # Look up the course by integer ID
        course_data = courses_df[courses_df["course_id"] == course_id_int]
        if course_data.empty:
            raise HTTPException(status_code=404, detail="Course not found")
        
        course_row = course_data.iloc[0]
        return CourseMetadata(
            course_id=str(course_row["course_id"]),  # Convert back to string for response
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