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

# from ..models.hybrid import hybrid_recommend
# from ..models.als_recommender import ALSRecommender
from ..models.baseline import BaselineRecommender
from ..data.data_loader import DataLoader
from ..monitoring.metrics import get_metrics_collector
from ..monitoring.ab_testing import get_ab_test_manager
from ..gamification.engine import GamificationEngine
from ..gamification.badge_definitions import get_all_badges as get_all_badge_definitions

# FastAPI app will be initialized later with lifespan

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
    n_recommendations: int = Field(10, ge=4, le=20, description="Number of recommendations (default 10, minimum 4)")

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

# Gamification Models
class UserStatsResponse(BaseModel):
    user_id: str = Field(..., description="User identifier")
    total_xp: int = Field(..., description="Total experience points")
    level: int = Field(..., description="User level")
    current_streak: int = Field(..., description="Current consecutive days streak")
    longest_streak: int = Field(..., description="Longest streak achieved")
    earned_badges: List[str] = Field(..., description="List of earned badge IDs")
    courses_completed: int = Field(..., description="Number of courses completed")
    courses_liked: int = Field(..., description="Number of courses liked")
    domains_explored: List[str] = Field(..., description="Domains the user has explored")

class ActivityUpdateResponse(BaseModel):
    xp_gained: int = Field(..., description="XP points gained from this activity")
    badges_earned: List[str] = Field(..., description="New badges earned")
    level_up: bool = Field(..., description="Whether user leveled up")
    streak_updated: bool = Field(..., description="Whether streak was updated")
    current_stats: UserStatsResponse = Field(..., description="Updated user stats")

class BadgeResponse(BaseModel):
    id: str = Field(..., description="Badge identifier")
    name: str = Field(..., description="Badge name")
    description: str = Field(..., description="Badge description")
    type: str = Field(..., description="Badge type")
    rarity: str = Field(..., description="Badge rarity")
    icon: str = Field(..., description="Badge icon")
    points: int = Field(..., description="XP points for earning this badge")
    color: str = Field(..., description="Badge color class")

class LeaderboardResponse(BaseModel):
    user_id: str = Field(..., description="User identifier")
    username: str = Field(..., description="Display name")
    total_xp: int = Field(..., description="Total experience points")
    level: int = Field(..., description="User level")
    current_streak: int = Field(..., description="Current streak")
    badges_count: int = Field(..., description="Number of badges earned")
    rank: int = Field(..., description="Leaderboard rank")

# Assessment Models
class UserAssessmentRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    interests: List[str] = Field(..., description="List of user interests")
    skill_level: str = Field(..., description="User's skill level (beginner, intermediate, advanced)")
    career_goals: List[str] = Field(..., description="List of career goals")
    domain: Optional[str] = Field(None, description="Primary domain of interest")
    subdomain: Optional[str] = Field(None, description="Specific subdomain of interest")
    experience_level: Optional[str] = Field(None, description="Years of experience")

class UserAssessmentResponse(BaseModel):
    user_id: str = Field(..., description="User identifier")
    interests: List[str] = Field(..., description="List of user interests")
    skill_level: str = Field(..., description="User's skill level")
    career_goals: List[str] = Field(..., description="List of career goals")
    domain: Optional[str] = Field(None, description="Primary domain of interest")
    subdomain: Optional[str] = Field(None, description="Specific subdomain of interest")
    experience_level: Optional[str] = Field(None, description="Years of experience")
    completed_at: datetime = Field(..., description="Assessment completion timestamp")
    recommendations: Optional[List[RecommendationResponse]] = Field(None, description="Personalized recommendations")

# Global variables for models and data
models_loaded = False
als_model: Optional[Any] = None  # ALSRecommender
baseline_model: Optional[BaselineRecommender] = None
courses_df: Optional[pd.DataFrame] = None
interactions_df: Optional[pd.DataFrame] = None

# Initialize monitoring and gamification
metrics_collector = get_metrics_collector()
ab_test_manager = get_ab_test_manager()
gamification_engine = GamificationEngine()

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
            metrics_collector.set_active_users(int(unique_users))
        
        # Load ALS model if available
        # als_model_path = MODELS_DIR / "als_model.pkl"
        # if als_model_path.exists():
        #     als_start_time = time.time()
        #     als_model = ALSRecommender()
        #     als_model.load(str(als_model_path))
        #     als_duration = time.time() - als_start_time
        #     metrics_collector.record_model_load_time("als_model", als_duration)
        #     print(f"Loaded ALS model from {als_model_path} in {als_duration:.3f}s")
        # else:
        print(f"ALS model not available - using baseline model only")
        
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
        # Get recommendations using baseline model only
        if baseline_model is None:
            raise HTTPException(status_code=503, detail="Baseline model not loaded")
        
        recommendations = baseline_model.recommend(student_id, n_recommendations=k)
        
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
        
        # Strategy 1: Enhanced content-based filtering with diversity
        try:
            print(f"Attempting enhanced content-based recommendations with interests: {request.interests}")
            
            # Import the content-based recommender directly
            from ..models.baseline import content_based_recommender
            
            # Use content-based recommender directly with user interests
            if courses_df is None:
                raise ValueError("Courses data not loaded")
            
            query_text = " ".join(request.interests)
            content_course_ids = content_based_recommender(
                courses_df, query_text=query_text, top_n=n_recs * 4  # Get more for diversity
            )
            
            print(f"Content-based recommender returned {len(content_course_ids)} course IDs")
            
            # Add diversity by filtering for different difficulty levels and topics
            difficulty_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}
            
            # Convert course IDs to recommendation format with enhanced diversity
            for i, course_id in enumerate(content_course_ids):
                if course_id not in seen_courses and len(all_recommendations) < max(8, n_recs * 0.8):  # Take majority from content-based
                    # Get course metadata for diversity analysis
                    course_row = courses_df[courses_df['course_id'] == course_id]
                    if not course_row.empty:
                        course_data = course_row.iloc[0]
                        
                        # Determine difficulty level (basic heuristic based on course data)
                        skill_tags = str(course_data.get('skill_tags', '').lower())
                        if any(word in skill_tags for word in ['beginner', 'intro', 'basic', 'fundamental']):
                            difficulty = 'beginner'
                        elif any(word in skill_tags for word in ['advanced', 'expert', 'master', 'deep']):
                            difficulty = 'advanced'
                        else:
                            difficulty = 'intermediate'
                        
                        # Ensure diversity across difficulty levels
                        max_per_difficulty = max(2, n_recs // 4)  # At least 2 per level, or quarter of total
                        if difficulty_counts.get(difficulty, 0) < max_per_difficulty:
                            # Calculate enhanced score based on position and user level match
                            base_score = 1.0 - (i / len(content_course_ids))
                            
                            # Boost score if difficulty matches user experience level
                            if request.experience_level and difficulty.lower() in request.experience_level.lower():
                                base_score = min(1.0, base_score * 1.2)
                            
                            # Enhanced explanations
                            explanations = [f"Matches your interests: {', '.join(request.interests[:3])}"]
                            if difficulty == 'beginner':
                                explanations.append("Perfect for building foundational knowledge")
                            elif difficulty == 'advanced':
                                explanations.append("Advanced content to challenge your skills")
                            else:
                                explanations.append("Intermediate level to expand your expertise")
                            
                            content_rec = {
                                "item_id": course_id,
                                "score": base_score,
                                "explanations": explanations
                            }
                            all_recommendations.append(content_rec)
                            seen_courses.add(course_id)
                            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
                    
        except Exception as e:
            print(f"Content-based recommendations failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Strategy 2: Enhanced popularity-based recommendations with trending insights
        if len(all_recommendations) < n_recs:
            try:
                print(f"Attempting enhanced popularity-based recommendations to get {n_recs - len(all_recommendations)} more")
                
                # Import the popularity recommender directly
                from ..models.baseline import popularity_recommender
                
                # Use popularity recommender directly
                if interactions_df is None:
                    raise ValueError("Interactions data not loaded")
                
                pop_course_ids = popularity_recommender(interactions_df, n_recs * 3)
                print(f"Popularity-based recommender returned {len(pop_course_ids)} course IDs")
                
                # Add unique popularity-based recommendations with enhanced explanations
                for i, course_id in enumerate(pop_course_ids):
                    if course_id not in seen_courses and len(all_recommendations) < n_recs:
                        # Get interaction count for this course
                        if interactions_df is not None:
                            interaction_count = len(interactions_df[interactions_df['course_id'] == course_id])
                        else:
                            interaction_count = 100  # Default fallback
                        
                        # Calculate enhanced score
                        base_score = max(0.4, 0.8 - (i / len(pop_course_ids)))  # Ensure minimum score
                        
                        # Enhanced explanations based on popularity metrics
                        if i < 5:
                            explanations = ["Top-rated course in your field", f"Chosen by {interaction_count}+ students"]
                        elif i < 15:
                            explanations = ["Highly popular course", "Great student reviews and engagement"]
                        else:
                            explanations = ["Well-regarded course", "Trusted by the learning community"]
                        
                        # Add domain-specific context if available
                        if request.domain:
                            explanations.append(f"Relevant to {request.domain} field")
                        
                        pop_rec = {
                            "item_id": course_id,
                            "score": base_score,
                            "explanations": explanations
                        }
                        all_recommendations.append(pop_rec)
                        seen_courses.add(course_id)
                        
            except Exception as e:
                print(f"Popularity-based recommendations failed: {e}")
                import traceback
                traceback.print_exc()
        
        # Strategy 3: Curated exploration recommendations
        if len(all_recommendations) < n_recs:
            try:
                print(f"Attempting to get {n_recs - len(all_recommendations)} curated exploration courses")
                if courses_df is None:
                    raise ValueError("Courses data not loaded")
                
                # Get courses from the dataset that could expand user's horizons
                available_courses = courses_df[~courses_df['course_id'].isin(list(seen_courses))]
                if len(available_courses) > 0:
                    # Prioritize courses that might introduce new skills or concepts
                    domain_keywords = []
                    if request.domain:
                        domain_keywords = request.domain.lower().split()
                    if request.subdomain:
                        domain_keywords.extend(request.subdomain.lower().split())
                    
                    # Score courses based on potential learning value
                    sample_size = min(n_recs - len(all_recommendations), len(available_courses))
                    
                    if sample_size > 0:
                        sample_courses = available_courses.sample(min(sample_size * 3, len(available_courses)))
                        
                        # Select courses with learning value scoring
                        scored_courses = []
                        for _, course_row in sample_courses.iterrows():
                            skill_tags = str(course_row.get('skill_tags', '')).lower()
                            title = str(course_row.get('title', '')).lower()
                            
                            # Score based on relevance and learning potential
                            relevance_score = 0.3  # Base score
                            
                            # Boost score if related to user's domain
                            for keyword in domain_keywords:
                                if keyword in skill_tags or keyword in title:
                                    relevance_score += 0.2
                            
                            # Boost for fundamental/foundational courses
                            if any(word in skill_tags for word in ['fundamental', 'essential', 'core', 'foundation']):
                                relevance_score += 0.15
                            
                            scored_courses.append((course_row, relevance_score))
                        
                        # Sort by relevance and take the best ones
                        scored_courses.sort(key=lambda x: x[1], reverse=True)
                        
                        for course_row, relevance_score in scored_courses[:sample_size]:
                            if len(all_recommendations) < n_recs:
                                # Enhanced explanations for exploration courses
                                explanations = ["Expand your skillset", "Discover new learning opportunities"]
                                
                                if relevance_score > 0.5:
                                    explanations = ["Highly relevant to your goals", "Builds on your current interests"]
                                elif relevance_score > 0.4:
                                    explanations = ["Related to your field", "Could complement your skills"]
                                
                                exploration_rec = {
                                    "item_id": course_row['course_id'],
                                    "score": min(0.7, 0.3 + relevance_score),  # Cap at reasonable score
                                    "explanations": explanations
                                }
                                all_recommendations.append(exploration_rec)
                                seen_courses.add(course_row['course_id'])
                        
                        print(f"Added {len(scored_courses[:sample_size])} curated exploration courses")
            except Exception as e:
                print(f"Random course sampling failed: {e}")
        
        # Strategy 4: Ultimate fallback - create generic recommendations only if we have less than 6
        if len(all_recommendations) < 6:
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
            try:
                sample_courses = courses_df.head(3)[['course_id', 'title', 'skill_tags']].to_dict('records')
                debug_info["sample_courses"] = sample_courses
            except Exception as e:
                debug_info["sample_courses_error"] = str(e)
        
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
        
        # Process gamification for this activity
        gamification_updates = gamification_engine.process_user_activity(
            user_id=event.student_id,
            activity_type=event.event_type,
            metadata={
                "course_id": event.course_id,
                "timestamp": event.timestamp.isoformat() if event.timestamp else None
            }
        )
        
        # Get updated user stats for response
        user_stats = gamification_engine.get_user_stats(event.student_id)
        stats_response = UserStatsResponse(
            user_id=user_stats.user_id,
            total_xp=user_stats.total_xp,
            level=user_stats.level,
            current_streak=user_stats.current_streak,
            longest_streak=user_stats.longest_streak,
            earned_badges=user_stats.earned_badges,
            courses_completed=user_stats.courses_completed,
            courses_liked=user_stats.courses_liked,
            domains_explored=list(user_stats.domains_explored)
        )
        
        return {
            "message": "Interaction recorded successfully", 
            "event": event.model_dump(),
            "gamification": ActivityUpdateResponse(
                xp_gained=gamification_updates["xp_gained"],
                badges_earned=gamification_updates["badges_earned"],
                level_up=gamification_updates["level_up"],
                streak_updated=gamification_updates["streak_updated"],
                current_stats=stats_response
            ).model_dump()
        }
        
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

# Gamification endpoints
@app.get("/gamification/stats/{user_id}", response_model=UserStatsResponse)
async def get_user_stats(user_id: str):
    """Get user's gamification statistics."""
    try:
        stats = gamification_engine.get_user_stats(user_id)
        return UserStatsResponse(
            user_id=stats.user_id,
            total_xp=stats.total_xp,
            level=stats.level,
            current_streak=stats.current_streak,
            longest_streak=stats.longest_streak,
            earned_badges=stats.earned_badges,
            courses_completed=stats.courses_completed,
            courses_liked=stats.courses_liked,
            domains_explored=list(stats.domains_explored)
        )
    except Exception as e:
        print(f"Error getting user stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user stats")

@app.get("/gamification/badges", response_model=List[BadgeResponse])
async def get_all_badges_endpoint():
    """Get all available badges."""
    try:
        badges = get_all_badge_definitions()
        badge_list = []
        for badge_id, badge in badges.items():
            badge_list.append(BadgeResponse(
                id=badge.id,
                name=badge.name,
                description=badge.description,
                type=badge.type.value,
                rarity=badge.rarity.value,
                icon=badge.icon,
                points=badge.points,
                color=badge.color
            ))
        return badge_list
    except Exception as e:
        print(f"Error getting badges: {e}")
        raise HTTPException(status_code=500, detail="Failed to get badges")

@app.get("/gamification/badges/progress/{user_id}")
async def get_badge_progress(user_id: str):
    """Get user's badge progress."""
    try:
        progress = gamification_engine.get_badge_progress(user_id)
        return {"badge_progress": progress}
    except Exception as e:
        print(f"Error getting badge progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get badge progress")

@app.get("/gamification/leaderboard", response_model=List[LeaderboardResponse])
async def get_leaderboard(limit: int = Query(50, ge=1, le=100)):
    """Get the global leaderboard."""
    try:
        leaderboard = gamification_engine.get_leaderboard(limit)
        return [LeaderboardResponse(
            user_id=entry.user_id,
            username=entry.username,
            total_xp=entry.total_xp,
            level=entry.level,
            current_streak=entry.current_streak,
            badges_count=entry.badges_count,
            rank=entry.rank
        ) for entry in leaderboard]
    except Exception as e:
        print(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

@app.get("/gamification/rank/{user_id}")
async def get_user_rank(user_id: str):
    """Get user's rank on the leaderboard."""
    try:
        rank = gamification_engine.get_user_rank(user_id)
        return {"user_id": user_id, "rank": rank}
    except Exception as e:
        print(f"Error getting user rank: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user rank")

@app.post("/gamification/activity/{user_id}")
async def record_gamification_activity(
    user_id: str,
    activity_type: str = Query(..., description="Type of activity"),
    metadata: Optional[Dict[str, Any]] = None
):
    """Record a gamification activity directly (for testing/admin)."""
    try:
        updates = gamification_engine.process_user_activity(
            user_id=user_id,
            activity_type=activity_type,
            metadata=metadata or {}
        )
        
        user_stats = gamification_engine.get_user_stats(user_id)
        stats_response = UserStatsResponse(
            user_id=user_stats.user_id,
            total_xp=user_stats.total_xp,
            level=user_stats.level,
            current_streak=user_stats.current_streak,
            longest_streak=user_stats.longest_streak,
            earned_badges=user_stats.earned_badges,
            courses_completed=user_stats.courses_completed,
            courses_liked=user_stats.courses_liked,
            domains_explored=list(user_stats.domains_explored)
        )
        
        return ActivityUpdateResponse(
            xp_gained=updates["xp_gained"],
            badges_earned=updates["badges_earned"],
            level_up=updates["level_up"],
            streak_updated=updates["streak_updated"],
            current_stats=stats_response
        )
    except Exception as e:
        print(f"Error recording gamification activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to record activity")

# Assessment endpoints
@app.post("/users/{user_id}/assessment", response_model=UserAssessmentResponse)
async def save_user_assessment(user_id: str, assessment: UserAssessmentRequest):
    """Save user's assessment data and generate personalized recommendations."""
    try:
        # Ensure user_id matches the path parameter
        assessment.user_id = user_id
        
        # Generate personalized recommendations based on assessment
        recommendations = []
        if assessment.interests:
            try:
                # Use the interest-based recommendation system
                interest_request = InterestBasedRecommendationRequest(
                    interests=assessment.interests,
                    domain=assessment.domain,
                    subdomain=assessment.subdomain,
                    experience_level=assessment.experience_level,
                    n_recommendations=8  # Get more recommendations for assessment
                )
                
                # Call the existing recommendation logic
                rec_response = await get_interest_based_recommendations(interest_request)
                recommendations = rec_response[:6]  # Limit to 6 for assessment
                
            except Exception as e:
                print(f"Failed to generate recommendations for assessment: {e}")
        
        # Save assessment data to file storage (will be migrated to Firebase automatically via hybrid storage)
        assessment_data = {
            "user_id": user_id,
            "interests": assessment.interests,
            "skill_level": assessment.skill_level,
            "career_goals": assessment.career_goals,
            "domain": assessment.domain,
            "subdomain": assessment.subdomain,
            "experience_level": assessment.experience_level,
            "completed_at": datetime.now().isoformat(),
            "recommendations": [rec.model_dump() for rec in recommendations] if recommendations else []
        }
        
        # Create assessments directory if it doesn't exist
        assessments_dir = Path("data/assessments")
        assessments_dir.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        assessment_file = assessments_dir / f"{user_id}.json"
        with open(assessment_file, 'w') as f:
            json.dump(assessment_data, f, indent=2)
        
        # Record gamification activity for completing assessment
        gamification_engine.process_user_activity(
            user_id=user_id,
            activity_type="assessment",
            metadata={"assessment_completed": True}
        )
        
        print(f"Assessment saved for user: {user_id}")
        
        return UserAssessmentResponse(
            user_id=user_id,
            interests=assessment.interests,
            skill_level=assessment.skill_level,
            career_goals=assessment.career_goals,
            domain=assessment.domain,
            subdomain=assessment.subdomain,
            experience_level=assessment.experience_level,
            completed_at=datetime.now(),
            recommendations=recommendations
        )
        
    except Exception as e:
        print(f"Error saving user assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to save user assessment")

@app.get("/users/{user_id}/assessment", response_model=UserAssessmentResponse)
async def get_user_assessment(user_id: str):
    """Get user's assessment data and recommendations."""
    try:
        # Try to load from file storage
        assessment_file = Path("data/assessments") / f"{user_id}.json"
        
        if not assessment_file.exists():
            raise HTTPException(status_code=404, detail="Assessment data not found")
        
        with open(assessment_file, 'r') as f:
            data = json.load(f)
        
        # Convert recommendations back to response objects
        recommendations = []
        if data.get("recommendations"):
            for rec_data in data["recommendations"]:
                recommendations.append(RecommendationResponse(
                    course_id=rec_data["course_id"],
                    score=rec_data["score"],
                    explanation=rec_data["explanation"]
                ))
        
        return UserAssessmentResponse(
            user_id=data["user_id"],
            interests=data.get("interests", []),
            skill_level=data.get("skill_level", "beginner"),
            career_goals=data.get("career_goals", []),
            domain=data.get("domain"),
            subdomain=data.get("subdomain"),
            experience_level=data.get("experience_level"),
            completed_at=datetime.fromisoformat(data["completed_at"]),
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting user assessment: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user assessment")

@app.get("/users/{user_id}/assessment/exists")
async def check_assessment_exists(user_id: str):
    """Check if user has completed an assessment."""
    try:
        assessment_file = Path("data/assessments") / f"{user_id}.json"
        exists = assessment_file.exists()
        
        return {
            "user_id": user_id,
            "assessment_exists": exists,
            "completed_at": None if not exists else datetime.fromtimestamp(assessment_file.stat().st_mtime).isoformat()
        }
        
    except Exception as e:
        print(f"Error checking assessment existence: {e}")
        raise HTTPException(status_code=500, detail="Failed to check assessment")

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