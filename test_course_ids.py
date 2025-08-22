#!/usr/bin/env python3
"""
Test script to check course IDs and content-based recommendations.
"""

import requests

def test_course_ids():
    """Test what course IDs are available and what recommendations are returned."""
    
    try:
        # Get debug info
        debug_response = requests.get("http://localhost:8000/debug/recommendations")
        debug_data = debug_response.json()
        
        print("=== Debug Information ===")
        print(f"Total courses: {debug_data['total_courses']}")
        print(f"Sample courses:")
        for course in debug_data['sample_courses']:
            print(f"  ID: {course['course_id']}, Title: {course['title']}")
        
        # Test interest-based recommendations
        test_request = {
            "interests": ["Problem Solving", "Technical Skills", "Data Analysis"],
            "domain": "Technology & Software",
            "subdomain": "data-science",
            "experience_level": "beginner",
            "n_recommendations": 5
        }
        
        print("\n=== Testing Interest-Based Recommendations ===")
        rec_response = requests.post(
            "http://localhost:8000/recommendations/interest-based",
            json=test_request
        )
        
        if rec_response.status_code == 200:
            recommendations = rec_response.json()
            print(f"Received {len(recommendations)} recommendations:")
            
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. Course ID: {rec['course_id']}, Score: {rec['score']}")
                
                # Try to get course metadata
                try:
                    course_response = requests.get(f"http://localhost:8000/course/{rec['course_id']}")
                    if course_response.status_code == 200:
                        course_data = course_response.json()
                        print(f"     Title: {course_data['title']}")
                        print(f"     Description: {course_data.get('description', 'No description')[:100]}...")
                    else:
                        print(f"     Course metadata not found (Status: {course_response.status_code})")
                except Exception as e:
                    print(f"     Error fetching course metadata: {e}")
        else:
            print(f"Error: {rec_response.status_code}")
            print(f"Response: {rec_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_course_ids()
