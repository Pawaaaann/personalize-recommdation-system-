"""
Main FastAPI application for EduRec.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import pandas as pd
from pathlib import Path

from ..data.data_loader import DataLoader
from ..models import BaselineRecommender, ALSRecommender, HybridRecommender

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EduRec API",
    description="Education Recommendation System API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class RecommendationRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user to get recommendations for")
    n_recommendations: int = Field(10, ge=1, le=100, description="Number of recommendations to return")
    model_type: str = Field("hybrid", description="Type of recommender to use")
    user_interests: Optional[List[str]] = Field(None, description="User interests for content-based filtering")

class RecommendationResponse(BaseModel):
    user_id: str
    recommendations: List[Dict[str, Any]]
    model_info: Dict[str, Any]
    total_count: int

class ModelInfoResponse(BaseModel):
    model_type: str
    is_fitted: bool
    model_info: Dict[str, Any]

class DataSummaryResponse(BaseModel):
    users: Dict[str, Any]
    courses: Dict[str, Any]
    interactions: Dict[str, Any]

# Global variables for models and data
data_loader = None
models = {}
current_model = None

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global data_loader, models
    
    logger.info("Starting EduRec API...")
    
    # Initialize data loader
    data_dir = Path("data")
    if data_dir.exists():
        data_loader = DataLoader(str(data_dir))
        try:
            data_loader.load_all_data()
            logger.info("Data loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load existing data: {e}")
    else:
        logger.info("No existing data found, will use sample data when available")
        data_loader = DataLoader()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to EduRec API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": [
            "/health",
            "/data/summary",
            "/models",
            "/recommend",
            "/models/{model_type}/info"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": pd.Timestamp.now().isoformat()}

@app.get("/data/summary", response_model=DataSummaryResponse)
async def get_data_summary():
    """Get summary of loaded data."""
    if data_loader is None:
        raise HTTPException(status_code=500, detail="Data loader not initialized")
    
    try:
        summary = data_loader.get_data_summary()
        return DataSummaryResponse(**summary)
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting data summary: {str(e)}")

@app.post("/models/train")
async def train_models():
    """Train all recommendation models."""
    global models, current_model
    
    if data_loader is None:
        raise HTTPException(status_code=500, detail="Data loader not initialized")
    
    try:
        # Load data if not already loaded
        data = data_loader.load_all_data()
        
        if data["interactions"].empty:
            raise HTTPException(status_code=400, detail="No interaction data available")
        
        logger.info("Training models...")
        
        # Train baseline model
        baseline_model = BaselineRecommender(strategy="popularity")
        baseline_model.fit(data["interactions"], data["courses"], data["users"])
        models["baseline"] = baseline_model
        
        # Train ALS model
        als_model = ALSRecommender()
        als_model.fit(data["interactions"])
        models["als"] = als_model
        
        # Train hybrid model
        hybrid_model = HybridRecommender()
        hybrid_model.fit(data["interactions"], data["courses"], data["users"])
        models["hybrid"] = hybrid_model
        
        # Set hybrid as default
        current_model = "hybrid"
        
        logger.info("All models trained successfully")
        
        return {
            "message": "Models trained successfully",
            "trained_models": list(models.keys()),
            "current_model": current_model
        }
        
    except Exception as e:
        logger.error(f"Error training models: {e}")
        raise HTTPException(status_code=500, detail=f"Error training models: {str(e)}")

@app.get("/models")
async def list_models():
    """List available models and their status."""
    global models, current_model
    
    model_status = {}
    for name, model in models.items():
        model_status[name] = {
            "is_fitted": model.is_fitted,
            "type": model.__class__.__name__,
            "name": model.name
        }
    
    return {
        "available_models": list(models.keys()),
        "current_model": current_model,
        "model_status": model_status
    }

@app.get("/models/{model_type}/info", response_model=ModelInfoResponse)
async def get_model_info(model_type: str):
    """Get information about a specific model."""
    global models
    
    if model_type not in models:
        raise HTTPException(status_code=404, detail=f"Model {model_type} not found")
    
    model = models[model_type]
    return ModelInfoResponse(
        model_type=model_type,
        is_fitted=model.is_fitted,
        model_info=model.get_model_info()
    )

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get course recommendations for a user."""
    global models, current_model
    
    # Determine which model to use
    model_type = request.model_type if request.model_type in models else current_model
    
    if model_type is None:
        raise HTTPException(status_code=400, detail="No models available. Please train models first.")
    
    if model_type not in models:
        raise HTTPException(status_code=404, detail=f"Model {model_type} not found")
    
    model = models[model_type]
    
    if not model.is_fitted:
        raise HTTPException(status_code=400, detail=f"Model {model_type} is not fitted")
    
    try:
        # Get recommendations
        recommendations = model.recommend(
            user_id=request.user_id,
            n_recommendations=request.n_recommendations,
            user_interests=request.user_interests
        )
        
        return RecommendationResponse(
            user_id=request.user_id,
            recommendations=recommendations,
            model_info=model.get_model_info(),
            total_count=len(recommendations)
        )
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@app.get("/recommend/{user_id}")
async def get_recommendations_simple(
    user_id: str,
    n_recommendations: int = 10,
    model_type: str = None
):
    """Simple endpoint for getting recommendations."""
    request = RecommendationRequest(
        user_id=user_id,
        n_recommendations=n_recommendations,
        model_type=model_type or "hybrid"
    )
    return await get_recommendations(request)

@app.get("/courses/{course_id}/similar")
async def get_similar_courses(
    course_id: str,
    n_similar: int = 10,
    model_type: str = "als"
):
    """Get similar courses to a given course."""
    global models
    
    if model_type not in models:
        raise HTTPException(status_code=404, detail=f"Model {model_type} not found")
    
    model = models[model_type]
    
    if not model.is_fitted:
        raise HTTPException(status_code=400, detail=f"Model {model_type} is not fitted")
    
    try:
        if hasattr(model, 'get_similar_items'):
            similar_items = model.get_similar_items(course_id, n_similar)
            return {
                "course_id": course_id,
                "similar_courses": similar_items,
                "model_type": model_type
            }
        else:
            raise HTTPException(status_code=400, detail=f"Model {model_type} does not support similar items")
            
    except Exception as e:
        logger.error(f"Error getting similar courses: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting similar courses: {str(e)}")

@app.get("/users/{user_id}/profile")
async def get_user_profile(user_id: str):
    """Get user profile and interaction history."""
    if data_loader is None:
        raise HTTPException(status_code=500, detail="Data loader not initialized")
    
    try:
        # Get user data
        users_df = data_loader.users_df
        interactions_df = data_loader.interactions_df
        
        if users_df is None or users_df.empty:
            raise HTTPException(status_code=404, detail="No user data available")
        
        user_data = users_df[users_df['user_id'] == user_id]
        if user_data.empty:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Get user interactions
        user_interactions = []
        if interactions_df is not None and not interactions_df.empty:
            user_interactions = interactions_df[
                interactions_df['user_id'] == user_id
            ].to_dict('records')
        
        return {
            "user_id": user_id,
            "profile": user_data.iloc[0].to_dict(),
            "interactions": user_interactions,
            "interaction_count": len(user_interactions)
        }
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting user profile: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 