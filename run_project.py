#!/usr/bin/env python3
"""
Simplified startup script to run the EduRec project with error handling.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "fastapi", "uvicorn[standard]", "pandas", "numpy", "scipy", 
            "scikit-learn", "pydantic", "prometheus_client", "redis", "requests"
        ])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_data_files():
    """Check if data files exist."""
    data_dir = project_root / "data"
    courses_file = data_dir / "courses.csv"
    interactions_file = data_dir / "interactions.csv"
    
    if courses_file.exists() and interactions_file.exists():
        print("✅ Data files found")
        return True
    else:
        print("❌ Data files missing")
        return False

def create_minimal_api():
    """Create a minimal API that works without complex dependencies."""
    api_content = '''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd
import json
from datetime import datetime

app = FastAPI(
    title="EduRec API",
    description="Educational Recommendation System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data storage
courses_data = None
interactions_data = None

def load_data():
    """Load data files."""
    global courses_data, interactions_data
    try:
        data_dir = Path(__file__).parent.parent.parent / "data"
        courses_file = data_dir / "courses.csv"
        interactions_file = data_dir / "interactions.csv"
        
        if courses_file.exists():
            courses_data = pd.read_csv(courses_file)
            print(f"Loaded {len(courses_data)} courses")
        
        if interactions_file.exists():
            interactions_data = pd.read_csv(interactions_file)
            print(f"Loaded {len(interactions_data)} interactions")
            
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Load data on startup."""
    load_data()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "EduRec API is running!", "timestamp": datetime.now()}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "data_loaded": courses_data is not None and interactions_data is not None
    }

@app.get("/courses")
async def get_courses():
    """Get all courses."""
    if courses_data is None:
        raise HTTPException(status_code=503, detail="Courses data not loaded")
    
    return {
        "courses": courses_data.head(10).to_dict("records"),
        "total_count": len(courses_data)
    }

@app.get("/recommend/{student_id}")
async def get_recommendations(student_id: str, k: int = 10):
    """Get simple popularity-based recommendations."""
    if courses_data is None or interactions_data is None:
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    try:
        # Simple popularity-based recommendations
        popular_courses = interactions_data['course_id'].value_counts().head(k)
        
        recommendations = []
        for i, (course_id, count) in enumerate(popular_courses.items()):
            course_info = courses_data[courses_data['course_id'] == course_id]
            if not course_info.empty:
                rec = {
                    "course_id": course_id,
                    "score": float(count / popular_courses.max()),
                    "rank": i + 1,
                    "title": course_info.iloc[0].get('title', 'Unknown'),
                    "explanation": ["popular_course"]
                }
                recommendations.append(rec)
        
        return {"recommendations": recommendations, "user_id": student_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
'''
    
    api_file = project_root / "simple_api.py"
    with open(api_file, 'w') as f:
        f.write(api_content)
    
    print("✅ Created simplified API")
    return api_file

def main():
    """Main function to run the project."""
    print("🚀 Starting EduRec project...")
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check data files
    if not check_data_files():
        print("⚠️ Data files missing, but continuing with simplified API...")
    
    # Create and run simplified API
    api_file = create_minimal_api()
    
    print(f"🎯 Starting API server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    
    try:
        subprocess.run([sys.executable, str(api_file)])
    except KeyboardInterrupt:
        print("\\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error running server: {e}")

if __name__ == "__main__":
    main()
