#!/usr/bin/env python3
"""
Test script to demonstrate monitoring and A/B testing features.
"""

import time
import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Service status: {data['status']}")
        print(f"Models loaded: {data['models_loaded']}")
        print(f"Timestamp: {data['timestamp']}")
    print()

def test_metrics_endpoint():
    """Test the metrics endpoint."""
    print("Testing metrics endpoint...")
    response = requests.get(f"{BASE_URL}/metrics")
    print(f"Metrics status: {response.status_code}")
    if response.status_code == 200:
        print("Metrics content (first 500 chars):")
        print(response.text[:500])
    print()

def test_recommendations_with_monitoring():
    """Test recommendations and monitor metrics."""
    print("Testing recommendations with monitoring...")
    
    # Test multiple users to see A/B testing in action
    test_users = ["user_001", "user_002", "user_003", "user_004", "user_005"]
    
    for user_id in test_users:
        print(f"Getting recommendations for {user_id}...")
        response = requests.get(f"{BASE_URL}/recommend/{user_id}?k=5")
        
        if response.status_code == 200:
            recommendations = response.json()
            print(f"  Got {len(recommendations)} recommendations")
            if recommendations:
                print(f"  Top recommendation: {recommendations[0]['course_id']} (score: {recommendations[0]['score']})")
        else:
            print(f"  Error: {response.status_code} - {response.text}")
        
        time.sleep(0.1)  # Small delay between requests
    
    print()

def test_ab_testing_experiments():
    """Test A/B testing experiment endpoints."""
    print("Testing A/B testing experiments...")
    
    # List experiments
    response = requests.get(f"{BASE_URL}/experiments")
    print(f"List experiments status: {response.status_code}")
    if response.status_code == 200:
        experiments = response.json()
        print(f"Found {len(experiments)} experiments:")
        for exp in experiments:
            print(f"  - {exp['name']}: {exp['description']} (active: {exp['is_active']})")
    
    print()
    
    # Get experiment stats
    experiment_name = "new_algorithm_v1"
    response = requests.get(f"{BASE_URL}/experiments/{experiment_name}")
    print(f"Experiment stats status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"Experiment: {stats['name']}")
        print(f"Description: {stats['description']}")
        print(f"Traffic split: {stats['traffic_split']}")
        print(f"Assignments: {stats['assignments']}")
        print(f"Precision@10: {stats['precision_at_10']}")
    
    print()

def test_conversion_tracking():
    """Test conversion tracking for A/B testing."""
    print("Testing conversion tracking...")
    
    # Record some conversions
    test_conversions = [
        ("user_001", "enroll"),
        ("user_002", "complete"),
        ("user_003", "enroll"),
        ("user_004", "complete"),
    ]
    
    for user_id, conversion_type in test_conversions:
        print(f"Recording conversion: {user_id} -> {conversion_type}")
        response = requests.post(
            f"{BASE_URL}/experiments/new_algorithm_v1/conversion",
            params={"user_id": user_id, "conversion_type": conversion_type}
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
    
    print()

def test_interaction_recording():
    """Test interaction recording with monitoring."""
    print("Testing interaction recording...")
    
    # Record some interactions
    test_interactions = [
        {"student_id": "user_001", "course_id": "course_001", "event_type": "view"},
        {"student_id": "user_002", "course_id": "course_002", "event_type": "enroll"},
        {"student_id": "user_003", "course_id": "course_003", "event_type": "complete"},
        {"student_id": "user_004", "course_id": "course_004", "event_type": "rate"},
    ]
    
    for interaction in test_interactions:
        print(f"Recording interaction: {interaction}")
        response = requests.post(
            f"{BASE_URL}/interactions",
            json=interaction
        )
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
    
    print()

def main():
    """Run all monitoring tests."""
    print("=" * 60)
    print("MONITORING AND A/B TESTING DEMONSTRATION")
    print("=" * 60)
    print()
    
    try:
        # Test basic endpoints
        test_health_endpoint()
        test_metrics_endpoint()
        
        # Test recommendations with monitoring
        test_recommendations_with_monitoring()
        
        # Test A/B testing
        test_ab_testing_experiments()
        
        # Test conversion tracking
        test_conversion_tracking()
        
        # Test interaction recording
        test_interaction_recording()
        
        # Show final metrics
        print("Final metrics snapshot:")
        test_metrics_endpoint()
        
        print("=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print()
        print("You can now:")
        print("1. View metrics at: http://localhost:8000/metrics")
        print("2. Check health at: http://localhost:8000/health")
        print("3. View experiments at: http://localhost:8000/experiments")
        print("4. Access API docs at: http://localhost:8000/docs")
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
