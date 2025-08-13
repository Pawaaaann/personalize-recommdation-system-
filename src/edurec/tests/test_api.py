#!/usr/bin/env python3
"""
Tests for the FastAPI backend.
"""

import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import pytest
import httpx
import pandas as pd
from fastapi.testclient import TestClient

from ..api.main import app, load_models_and_data, store_interaction
from ..models.als_recommender import ALSRecommender
from ..models.baseline import BaselineRecommender

# Create test client
client = TestClient(app)

class TestAPIEndpoints:
    """Test class for API endpoints."""
    
    @pytest.fixture
    def mock_models_and_data(self):
        """Mock models and data for testing."""
        # Create mock data
        courses_data = {
            "course_id": ["course_001", "course_002", "course_003"],
            "title": ["Python Basics", "Data Science", "Machine Learning"],
            "description": ["Learn Python", "Learn Data Science", "Learn ML"],
            "skill_tags": ["python,programming", "data,python", "ml,python"],
            "difficulty": ["beginner", "intermediate", "advanced"],
            "duration": ["4 weeks", "6 weeks", "8 weeks"]
        }
        courses_df = pd.DataFrame(courses_data)
        
        interactions_data = {
            "user_id": ["user_001", "user_002", "user_001"],
            "course_id": ["course_001", "course_002", "course_003"],
            "rating": [5, 4, 3],
            "event_type": ["complete", "enroll", "view"]
        }
        interactions_df = pd.DataFrame(interactions_data)
        
        # Create mock models
        mock_als = Mock(spec=ALSRecommender)
        mock_als.is_fitted = True
        mock_als.recommend.return_value = [
            {"item_id": "course_002", "score": 0.9, "rank": 1},
            {"item_id": "course_003", "score": 0.8, "rank": 2}
        ]
        
        mock_baseline = Mock(spec=BaselineRecommender)
        mock_baseline.is_fitted = True
        mock_baseline.recommend.return_value = [
            {"item_id": "course_001", "score": 0.95, "rank": 1},
            {"item_id": "course_002", "score": 0.85, "rank": 2}
        ]
        mock_baseline.get_similar_items.return_value = [
            {"item_id": "course_003", "similarity_score": 0.9, "rank": 1}
        ]
        
        return {
            "courses_df": courses_df,
            "interactions_df": interactions_df,
            "als_model": mock_als,
            "baseline_model": mock_baseline
        }
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @patch('edurec.api.main.load_models_and_data')
    def test_health_endpoint(self, mock_load):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "models_loaded" in data
        assert data["status"] == "healthy"
        assert isinstance(data["models_loaded"], bool)
    
    @patch('edurec.api.main.hybrid_recommend')
    @patch('edurec.api.main.models_loaded', True)
    def test_recommendations_endpoint(self, mock_hybrid, mock_models_and_data):
        """Test the recommendations endpoint."""
        # Mock hybrid_recommend to return test data
        mock_hybrid.return_value = [
            {"item_id": "course_001", "score": 0.95, "explanations": ["popular", "skill_match"]},
            {"item_id": "course_002", "score": 0.85, "explanations": ["similar_users_enrolled"]}
        ]
        
        response = client.get("/recommend/user_001?k=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["course_id"] == "course_001"
        assert data[0]["score"] == 0.95
        assert "popular" in data[0]["explanation"]
        assert data[1]["course_id"] == "course_002"
        assert data[1]["score"] == 0.85
    
    @patch('edurec.api.main.models_loaded', False)
    def test_recommendations_endpoint_models_not_loaded(self):
        """Test recommendations endpoint when models are not loaded."""
        response = client.get("/recommend/user_001")
        assert response.status_code == 503
        assert "Models not loaded" in response.json()["detail"]
    
    @patch('edurec.api.main.courses_df')
    def test_course_metadata_endpoint(self, mock_courses_df, mock_models_and_data):
        """Test the course metadata endpoint."""
        # Set up mock courses_df
        courses_df = mock_models_and_data["courses_df"]
        with patch('edurec.api.main.courses_df', courses_df):
            response = client.get("/course/course_001")
            assert response.status_code == 200
            
            data = response.json()
            assert data["course_id"] == "course_001"
            assert data["title"] == "Python Basics"
            assert data["description"] == "Learn Python"
            assert data["skill_tags"] == "python,programming"
            assert data["difficulty"] == "beginner"
            assert data["duration"] == "4 weeks"
    
    @patch('edurec.api.main.courses_df', None)
    def test_course_metadata_endpoint_data_not_loaded(self):
        """Test course metadata endpoint when data is not loaded."""
        response = client.get("/course/course_001")
        assert response.status_code == 503
        assert "Course data not loaded" in response.json()["detail"]
    
    def test_course_metadata_endpoint_course_not_found(self, mock_models_and_data):
        """Test course metadata endpoint for non-existent course."""
        courses_df = mock_models_and_data["courses_df"]
        with patch('edurec.api.main.courses_df', courses_df):
            response = client.get("/course/nonexistent_course")
            assert response.status_code == 404
            assert "Course not found" in response.json()["detail"]
    
    def test_interactions_endpoint_valid_event(self, temp_data_dir):
        """Test the interactions endpoint with valid event."""
        # Mock the interactions queue file path
        with patch('edurec.api.main.INTERACTIONS_QUEUE_FILE', temp_data_dir / "interactions_queue.jsonl"):
            event_data = {
                "student_id": "user_001",
                "course_id": "course_001",
                "event_type": "enroll",
                "timestamp": "2024-01-01T10:00:00"
            }
            
            response = client.post("/interactions", json=event_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Interaction recorded successfully"
            assert data["event"]["student_id"] == "user_001"
            assert data["event"]["course_id"] == "course_001"
            assert data["event"]["event_type"] == "enroll"
    
    def test_interactions_endpoint_invalid_event_type(self):
        """Test interactions endpoint with invalid event type."""
        event_data = {
            "student_id": "user_001",
            "course_id": "course_001",
            "event_type": "invalid_event",
            "timestamp": "2024-01-01T10:00:00"
        }
        
        response = client.post("/interactions", json=event_data)
        assert response.status_code == 400
        assert "Invalid event_type" in response.json()["detail"]
    
    def test_interactions_endpoint_missing_required_fields(self):
        """Test interactions endpoint with missing required fields."""
        event_data = {
            "student_id": "user_001"
            # Missing course_id and event_type
        }
        
        response = client.post("/interactions", json=event_data)
        assert response.status_code == 422  # Validation error
    
    def test_interactions_queue_endpoint(self, temp_data_dir):
        """Test the interactions queue endpoint."""
        # Create a test interactions queue file
        queue_file = temp_data_dir / "interactions_queue.jsonl"
        test_interactions = [
            {"student_id": "user_001", "course_id": "course_001", "event_type": "view", "timestamp": "2024-01-01T10:00:00"},
            {"student_id": "user_002", "course_id": "course_002", "event_type": "enroll", "timestamp": "2024-01-01T11:00:00"}
        ]
        
        with open(queue_file, "w") as f:
            for interaction in test_interactions:
                f.write(json.dumps(interaction) + "\n")
        
        with patch('edurec.api.main.INTERACTIONS_QUEUE_FILE', queue_file):
            response = client.get("/interactions/queue")
            assert response.status_code == 200
            
            data = response.json()
            assert data["count"] == 2
            assert len(data["interactions"]) == 2
            assert data["interactions"][0]["student_id"] == "user_001"
            assert data["interactions"][1]["student_id"] == "user_002"
    
    def test_interactions_queue_endpoint_empty(self, temp_data_dir):
        """Test interactions queue endpoint when queue is empty."""
        with patch('edurec.api.main.INTERACTIONS_QUEUE_FILE', temp_data_dir / "nonexistent.jsonl"):
            response = client.get("/interactions/queue")
            assert response.status_code == 200
            
            data = response.json()
            assert data["count"] == 0
            assert data["interactions"] == []
    
    def test_clear_interactions_queue_endpoint(self, temp_data_dir):
        """Test the clear interactions queue endpoint."""
        # Create a test interactions queue file
        queue_file = temp_data_dir / "interactions_queue.jsonl"
        queue_file.write_text("test interaction data\n")
        
        with patch('edurec.api.main.INTERACTIONS_QUEUE_FILE', queue_file):
            response = client.delete("/interactions/queue")
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Interactions queue cleared successfully"
            
            # Verify file was deleted
            assert not queue_file.exists()
    
    def test_clear_interactions_queue_endpoint_nonexistent(self, temp_data_dir):
        """Test clear interactions queue endpoint when queue doesn't exist."""
        with patch('edurec.api.main.INTERACTIONS_QUEUE_FILE', temp_data_dir / "nonexistent.jsonl"):
            response = client.delete("/interactions/queue")
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Interactions queue cleared successfully"
    
    @patch('edurec.api.main.hybrid_recommend')
    @patch('edurec.api.main.models_loaded', True)
    def test_recommendations_with_custom_k(self, mock_hybrid, mock_models_and_data):
        """Test recommendations endpoint with custom k parameter."""
        # Mock hybrid_recommend to return test data
        mock_hybrid.return_value = [
            {"item_id": f"course_{i:03d}", "score": 0.9 - i*0.1, "explanations": ["popular"]}
            for i in range(1, 6)
        ]
        
        response = client.get("/recommend/user_001?k=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5
        assert all("course_" in rec["course_id"] for rec in data)
    
    def test_recommendations_parameter_validation(self):
        """Test recommendations endpoint parameter validation."""
        # Test k too small
        response = client.get("/recommend/user_001?k=0")
        assert response.status_code == 422
        
        # Test k too large
        response = client.get("/recommend/user_001?k=51")
        assert response.status_code == 422
        
        # Test valid k
        response = client.get("/recommend/user_001?k=25")
        assert response.status_code == 503  # Models not loaded, but parameter validation passed
    
    @patch('edurec.api.main.hybrid_recommend')
    @patch('edurec.api.main.models_loaded', True)
    def test_recommendations_error_handling(self, mock_hybrid):
        """Test recommendations endpoint error handling."""
        # Mock hybrid_recommend to raise an exception
        mock_hybrid.side_effect = Exception("Test error")
        
        response = client.get("/recommend/user_001")
        assert response.status_code == 500
        assert "Failed to generate recommendations" in response.json()["detail"]
    
    def test_course_metadata_error_handling(self, mock_models_and_data):
        """Test course metadata endpoint error handling."""
        courses_df = mock_models_and_data["courses_df"]
        with patch('edurec.api.main.courses_df', courses_df):
            # Test with invalid course_id that might cause other errors
            response = client.get("/course/")  # Empty course_id
            assert response.status_code == 404  # FastAPI routing error
    
    def test_interactions_error_handling(self, temp_data_dir):
        """Test interactions endpoint error handling."""
        # Mock the store_interaction function to raise an exception
        with patch('edurec.api.main.store_interaction') as mock_store:
            mock_store.side_effect = Exception("Test error")
            
            event_data = {
                "student_id": "user_001",
                "course_id": "course_001",
                "event_type": "enroll"
            }
            
            response = client.post("/interactions", json=event_data)
            assert response.status_code == 500
            assert "Failed to record interaction" in response.json()["detail"]

class TestAPIUtilities:
    """Test class for API utility functions."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @patch('edurec.api.main.als_model', None)
    @patch('edurec.api.main.baseline_model', None)
    @patch('edurec.api.main.courses_df', None)
    @patch('edurec.api.main.interactions_df', None)
    def test_load_models_and_data_no_models(self):
        """Test load_models_and_data when no models are available."""
        with patch('edurec.api.main.DataLoader') as mock_loader:
            mock_loader_instance = Mock()
            mock_loader.return_value = mock_loader_instance
            mock_loader_instance.load_courses_data.return_value = pd.DataFrame()
            mock_loader_instance.load_interactions_data.return_value = pd.DataFrame()
            
            load_models_and_data()
            
            # Verify that models_loaded is False when no ALS model exists
            from edurec.api.main import models_loaded
            assert not models_loaded
    
    def test_store_interaction_success(self, temp_data_dir):
        """Test successful interaction storage."""
        queue_file = temp_data_dir / "test_queue.jsonl"
        
        with patch('edurec.api.main.INTERACTIONS_QUEUE_FILE', queue_file):
            event = Mock()
            event.model_dump.return_value = {
                "student_id": "user_001",
                "course_id": "course_001",
                "event_type": "view",
                "timestamp": None
            }
            event.student_id = "user_001"
            event.course_id = "course_001"
            event.event_type = "view"
            
            store_interaction(event)
            
            # Verify file was created and contains the interaction
            assert queue_file.exists()
            with open(queue_file, "r") as f:
                content = f.read().strip()
                assert "user_001" in content
                assert "course_001" in content
                assert "view" in content
    
    def test_store_interaction_directory_creation(self, temp_data_dir):
        """Test that store_interaction creates directories if they don't exist."""
        nested_dir = temp_data_dir / "nested" / "deep"
        queue_file = nested_dir / "queue.jsonl"
        
        with patch('edurec.api.main.INTERACTIONS_QUEUE_FILE', queue_file):
            event = Mock()
            event.model_dump.return_value = {
                "student_id": "user_001",
                "course_id": "course_001",
                "event_type": "view",
                "timestamp": None
            }
            event.student_id = "user_001"
            event.course_id = "course_001"
            event.event_type = "view"
            
            store_interaction(event)
            
            # Verify nested directory was created
            assert nested_dir.exists()
            assert queue_file.exists()

if __name__ == "__main__":
    pytest.main([__file__])
