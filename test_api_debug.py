#!/usr/bin/env python3
"""
Test script that mimics the API endpoint to debug the issue.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from edurec.models.hybrid import hybrid_recommend
from edurec.models.baseline import BaselineRecommender
from edurec.data.data_loader import DataLoader

def test_api_endpoint():
    """Test the API endpoint logic."""
    print("Testing API endpoint logic...")
    
    # Load data (same as API)
    data_loader = DataLoader()
    courses_df = data_loader.load_courses()
    interactions_df = data_loader.load_interactions()
    
    # Create baseline model (same as API)
    baseline_model = BaselineRecommender(strategy="hybrid")
    baseline_model.fit(interactions_df, courses_df)
    
    # Test student_id
    student_id = "2574"
    k = 5
    
    print(f"Testing recommendations for student {student_id} with k={k}")
    
    try:
        # Get recommendations using hybrid approach (same as API)
        recommendations = hybrid_recommend(
            user_id=student_id,
            N=k,
            als_model=None,  # No ALS model in API
            baseline_model=baseline_model,
            courses_df=courses_df,
            interactions_df=interactions_df
        )
        
        print(f"✅ Got {len(recommendations)} recommendations")
        
        # Convert to response format (same as API)
        response = []
        for rec in recommendations:
            print(f"Processing recommendation: {rec}")
            response_item = {
                "course_id": rec["item_id"],
                "score": round(rec["score"], 4),
                "explanation": rec.get("explanations", [])
            }
            response.append(response_item)
            print(f"Created response item: {response_item}")
        
        print(f"✅ Created {len(response)} response items")
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = test_api_endpoint()
    if result:
        print(f"\nFinal result: {result}")
