#!/usr/bin/env python3
"""
Debug script to test the recommendation system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from edurec.models.hybrid import hybrid_recommend
from edurec.models.baseline import BaselineRecommender

def test_recommendations():
    """Test the recommendation system step by step."""
    print("Loading data...")
    
    # Load data
    interactions_df = pd.read_csv('data/interactions.csv')
    courses_df = pd.read_csv('data/courses.csv')
    
    print(f"Loaded {len(interactions_df)} interactions and {len(courses_df)} courses")
    
    # Test baseline model
    print("\nTesting baseline model...")
    try:
        baseline_model = BaselineRecommender(strategy="hybrid")
        baseline_model.fit(interactions_df, courses_df)
        print("✅ Baseline model fitted successfully")
        
        # Test baseline recommendations
        baseline_recs = baseline_model.recommend("2574", n_recommendations=5)
        print(f"✅ Baseline recommendations: {len(baseline_recs)} items")
        print("Baseline recommendation structure:")
        if baseline_recs:
            print(f"Keys: {list(baseline_recs[0].keys())}")
            print(f"Sample: {baseline_recs[0]}")
            
    except Exception as e:
        print(f"❌ Baseline model error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test hybrid recommendations
    print("\nTesting hybrid recommendations...")
    try:
        recommendations = hybrid_recommend(
            user_id="2574",
            N=5,
            baseline_model=baseline_model,
            courses_df=courses_df,
            interactions_df=interactions_df
        )
        print(f"✅ Hybrid recommendations: {len(recommendations)} items")
        print("Hybrid recommendation structure:")
        if recommendations:
            print(f"Keys: {list(recommendations[0].keys())}")
            print(f"Sample: {recommendations[0]}")
            
    except Exception as e:
        print(f"❌ Hybrid recommendations error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_recommendations()
