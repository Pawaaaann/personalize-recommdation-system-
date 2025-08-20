#!/usr/bin/env python3
"""
Demonstration script for the hybrid recommender system.
Shows how to use the hybrid_recommend function with different weights and models.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add the src directory to the path so we can import edurec modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from edurec.models.hybrid import hybrid_recommend
from edurec.models.als_recommender import ALSRecommender
from edurec.models.baseline import BaselineRecommender


def create_demo_data():
    """Create demo data for demonstration."""
    # Create sample courses
    courses_data = {
        'course_id': [
            'course_001', 'course_002', 'course_003', 'course_004', 'course_005',
            'course_006', 'course_007', 'course_008', 'course_009', 'course_010'
        ],
        'title': [
            'Python Basics', 'Advanced Python', 'Data Science', 'Machine Learning', 'Web Development',
            'JavaScript Fundamentals', 'React.js', 'Node.js', 'Database Design', 'API Development'
        ],
        'description': [
            'Learn the fundamentals of Python programming language',
            'Advanced Python concepts and best practices',
            'Introduction to data science with Python',
            'Machine learning algorithms and techniques',
            'Build modern web applications',
            'JavaScript programming fundamentals',
            'React.js frontend development',
            'Node.js backend development',
            'Database design and SQL',
            'RESTful API development'
        ],
        'skill_tags': [
            'python,programming', 'python,advanced', 'python,data,ml', 'python,ml,ai', 'javascript,web',
            'javascript,frontend', 'javascript,react,frontend', 'javascript,node,backend', 'database,sql', 'api,rest'
        ],
        'category': [
            'Programming', 'Programming', 'Data Science', 'Machine Learning', 'Web Development',
            'Programming', 'Web Development', 'Web Development', 'Database', 'Web Development'
        ]
    }
    
    # Create sample interactions
    interactions_data = {
        'user_id': [
            'user_001', 'user_001', 'user_001', 'user_002', 'user_002', 'user_002',
            'user_003', 'user_003', 'user_004', 'user_004', 'user_005', 'user_005'
        ],
        'course_id': [
            'course_001', 'course_002', 'course_003', 'course_001', 'course_004', 'course_005',
            'course_006', 'course_007', 'course_008', 'course_009', 'course_010', 'course_001'
        ],
        'event_type': [
            'enroll', 'complete', 'enroll', 'enroll', 'complete', 'enroll',
            'enroll', 'complete', 'enroll', 'enroll', 'enroll', 'complete'
        ],
        'rating': [
            5.0, 5.0, 4.0, 4.0, 5.0, 4.0,
            4.0, 5.0, 4.0, 3.0, 4.0, 5.0
        ],
        'timestamp': [
            1600000000, 1600000001, 1600000002, 1600000003, 1600000004, 1600000005,
            1600000006, 1600000007, 1600000008, 1600000009, 1600000010, 1600000011
        ]
    }
    
    courses_df = pd.DataFrame(courses_data)
    interactions_df = pd.DataFrame(interactions_data)
    
    return courses_df, interactions_df


def train_models(courses_df, interactions_df):
    """Train the ALS and baseline models."""
    print("Training ALS model...")
    als_model = ALSRecommender(factors=16, iterations=10)
    als_model.fit(interactions_df)
    
    print("Training baseline model...")
    baseline_model = BaselineRecommender(strategy="hybrid")
    baseline_model.fit(interactions_df, courses_df)
    
    return als_model, baseline_model


def demonstrate_hybrid_recommendations():
    """Demonstrate the hybrid recommender system."""
    print("=" * 60)
    print("HYBRID RECOMMENDER SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Create demo data
    courses_df, interactions_df = create_demo_data()
    print(f"\nCreated demo data:")
    print(f"- {len(courses_df)} courses")
    print(f"- {len(interactions_df)} interactions")
    print(f"- {interactions_df['user_id'].nunique()} users")
    
    # Train models
    als_model, baseline_model = train_models(courses_df, interactions_df)
    print("\nModels trained successfully!")
    
    # Test user
    test_user = "user_001"
    print(f"\nGenerating recommendations for user: {test_user}")
    
    # Different weight combinations
    weight_configs = [
        {"als": 0.7, "content": 0.2, "pop": 0.1},
        {"als": 0.5, "content": 0.3, "pop": 0.2},
        {"als": 0.2, "content": 0.6, "pop": 0.2},
        {"als": 0.1, "content": 0.2, "pop": 0.7},
        {"als": 1.0, "content": 0.0, "pop": 0.0},
        {"als": 0.0, "content": 1.0, "pop": 0.0},
        {"als": 0.0, "content": 0.0, "pop": 1.0}
    ]
    
    for i, weights in enumerate(weight_configs, 1):
        print(f"\n--- Configuration {i}: {weights} ---")
        
        recommendations = hybrid_recommend(
            user_id=test_user,
            N=5,
            weights=weights,
            als_model=als_model,
            baseline_model=baseline_model,
            courses_df=courses_df,
            interactions_df=interactions_df
        )
        
        print(f"Top 5 recommendations:")
        for rec in recommendations:
            explanations = rec.get('explanations', [])
            print(f"  {rec['rank']}. {rec['item_id']} (score: {rec['score']:.3f})")
            print(f"     Explanations: {explanations}")
    
    # Test with no models (fallback)
    print(f"\n--- Fallback Configuration (no models) ---")
    fallback_recommendations = hybrid_recommend(
        user_id=test_user,
        N=3
    )
    
    print(f"Fallback recommendations:")
    for rec in fallback_recommendations:
        explanations = rec.get('explanations', [])
        print(f"  {rec['rank']}. {rec['item_id']} (score: {rec['score']:.3f})")
        print(f"     Explanations: {explanations}")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_hybrid_recommendations()
