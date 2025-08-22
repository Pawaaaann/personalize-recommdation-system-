#!/usr/bin/env python3
"""
Test script for the new interest-based recommendations endpoint.
"""

import requests
import json

def test_interest_based_recommendations():
    """Test the new interest-based recommendations endpoint."""
    
    # Test data
    test_request = {
        "interests": ["Problem Solving", "Technical Skills", "Data Analysis"],
        "domain": "Technology & Software",
        "subdomain": "data-science",
        "experience_level": "beginner",
        "n_recommendations": 5
    }
    
    try:
        # Make request to the new endpoint
        response = requests.post(
            "http://localhost:8000/recommendations/interest-based",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"\n✅ Success! Received {len(recommendations)} recommendations:")
            
            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. Course ID: {rec['course_id']}")
                print(f"   Score: {rec['score']}")
                print(f"   Explanations: {rec['explanation']}")
                
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the backend server is running on port 8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("Testing Interest-Based Recommendations Endpoint")
    print("=" * 50)
    test_interest_based_recommendations()
