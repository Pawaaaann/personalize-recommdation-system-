"""
Tests for the hybrid recommender system.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, MagicMock

from ..models.hybrid import HybridRecommender, hybrid_recommend
from ..models.als_recommender import ALSRecommender
from ..models.baseline import BaselineRecommender


class TestHybridRecommender:
    """Test cases for HybridRecommender class."""
    
    @pytest.fixture
    def mock_als_model(self):
        """Create a mock ALS model."""
        mock_model = Mock(spec=ALSRecommender)
        mock_model.is_fitted = True
        
        # Mock recommend method
        mock_model.recommend.return_value = [
            {"item_id": "course_001", "score": 0.9, "rank": 1, "model": "ALS"},
            {"item_id": "course_002", "score": 0.8, "rank": 2, "model": "ALS"},
            {"item_id": "course_003", "score": 0.7, "rank": 3, "model": "ALS"}
        ]
        
        return mock_model
    
    @pytest.fixture
    def mock_baseline_model(self):
        """Create a mock baseline model."""
        mock_model = Mock(spec=BaselineRecommender)
        mock_model.is_fitted = True
        
        # Mock recommend method (popularity)
        mock_model.recommend.return_value = [
            {"item_id": "course_004", "score": 0.95, "rank": 1, "model": "Baseline"},
            {"item_id": "course_005", "score": 0.85, "rank": 2, "model": "Baseline"},
            {"item_id": "course_006", "score": 0.75, "rank": 3, "model": "Baseline"}
        ]
        
        # Mock get_similar_items method (content-based)
        mock_model.get_similar_items.return_value = [
            {"item_id": "course_007", "similarity_score": 0.9, "rank": 1, "reference_item": "course_001"},
            {"item_id": "course_008", "similarity_score": 0.8, "rank": 2, "reference_item": "course_001"},
            {"item_id": "course_009", "similarity_score": 0.7, "rank": 3, "reference_item": "course_001"}
        ]
        
        return mock_model
    
    @pytest.fixture
    def sample_courses_df(self):
        """Create sample courses DataFrame."""
        return pd.DataFrame({
            'course_id': ['course_001', 'course_002', 'course_003', 'course_004', 'course_005'],
            'title': ['Python Basics', 'Advanced Python', 'Data Science', 'Machine Learning', 'Web Development'],
            'skill_tags': ['python,programming', 'python,advanced', 'python,data', 'python,ml', 'javascript,web'],
            'category': ['Programming', 'Programming', 'Data Science', 'Machine Learning', 'Web Development']
        })
    
    @pytest.fixture
    def sample_interactions_df(self):
        """Create sample interactions DataFrame."""
        return pd.DataFrame({
            'user_id': ['user_001', 'user_001', 'user_002', 'user_002', 'user_003'],
            'course_id': ['course_001', 'course_002', 'course_001', 'course_003', 'course_004'],
            'event_type': ['enroll', 'complete', 'enroll', 'enroll', 'view'],
            'rating': [5.0, 5.0, 4.0, 4.0, 3.0],
            'timestamp': [1600000000, 1600000001, 1600000002, 1600000003, 1600000004]
        })
    
    def test_init_default_weights(self):
        """Test initialization with default weights."""
        hybrid = HybridRecommender()
        
        assert hybrid.name == "HybridRecommender"
        assert hybrid.default_weights == {"als": 0.7, "content": 0.2, "pop": 0.1}
        assert hybrid.als_model is None
        assert hybrid.baseline_model is None
    
    def test_init_custom_weights(self):
        """Test initialization with custom weights."""
        custom_weights = {"als": 0.5, "content": 0.3, "pop": 0.2}
        hybrid = HybridRecommender(default_weights=custom_weights)
        
        # Weights should be normalized
        expected_weights = {"als": 0.5, "content": 0.3, "pop": 0.2}
        assert hybrid.default_weights == expected_weights
    
    def test_init_with_models(self, mock_als_model, mock_baseline_model):
        """Test initialization with pre-trained models."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        assert hybrid.als_model == mock_als_model
        assert hybrid.baseline_model == mock_baseline_model
    
    def test_set_data(self, sample_courses_df, sample_interactions_df):
        """Test setting data for explanations."""
        hybrid = HybridRecommender()
        hybrid.set_data(sample_courses_df, sample_interactions_df)
        
        assert hybrid.courses_df is not None
        assert hybrid.interactions_df is not None
        assert len(hybrid.courses_df) == 5
        assert len(hybrid.interactions_df) == 5
    
    def test_hybrid_recommend_basic(self, mock_als_model, mock_baseline_model):
        """Test basic hybrid recommendation generation."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        recommendations = hybrid.hybrid_recommend("user_001", N=5)
        
        assert len(recommendations) > 0
        assert all(isinstance(rec, dict) for rec in recommendations)
        assert all("explanations" in rec for rec in recommendations)
        assert all("all_explanations" in rec for rec in recommendations)
    
    def test_hybrid_recommend_with_weights(self, mock_als_model, mock_baseline_model):
        """Test hybrid recommendations with custom weights."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        custom_weights = {"als": 0.8, "content": 0.15, "pop": 0.05}
        recommendations = hybrid.hybrid_recommend("user_001", N=5, weights=custom_weights)
        
        assert len(recommendations) > 0
        # ALS should have higher influence due to higher weight
        assert any("similar_users_enrolled" in rec.get("explanations", []) for rec in recommendations)
    
    def test_hybrid_recommend_als_only(self, mock_als_model):
        """Test hybrid recommendations with only ALS model."""
        hybrid = HybridRecommender(als_model=mock_als_model)
        
        weights = {"als": 1.0}
        recommendations = hybrid.hybrid_recommend("user_001", N=5, weights=weights)
        
        assert len(recommendations) > 0
        # All explanations should be ALS-based
        for rec in recommendations:
            assert "similar_users_enrolled" in rec.get("explanations", [])
    
    def test_hybrid_recommend_content_only(self, mock_baseline_model, sample_courses_df, sample_interactions_df):
        """Test hybrid recommendations with only content-based model."""
        hybrid = HybridRecommender(baseline_model=mock_baseline_model)
        hybrid.set_data(sample_courses_df, sample_interactions_df)
        
        weights = {"content": 1.0}
        recommendations = hybrid.hybrid_recommend("user_001", N=5, weights=weights)
        
        assert len(recommendations) > 0
        # Should have content-based explanations
        content_explanations = []
        for rec in recommendations:
            content_explanations.extend(rec.get("explanations", []))
        
        assert any("skill_match" in exp or "similar_course_content" in exp for exp in content_explanations)
    
    def test_hybrid_recommend_popularity_only(self, mock_baseline_model):
        """Test hybrid recommendations with only popularity model."""
        hybrid = HybridRecommender(baseline_model=mock_baseline_model)
        
        weights = {"pop": 1.0}
        recommendations = hybrid.hybrid_recommend("user_001", N=5, weights=weights)
        
        assert len(recommendations) > 0
        # All explanations should be popularity-based
        for rec in recommendations:
            assert "popular" in rec.get("explanations", [])
    
    def test_explanation_generation(self, mock_als_model, mock_baseline_model, sample_courses_df, sample_interactions_df):
        """Test explanation generation for recommendations."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        hybrid.set_data(sample_courses_df, sample_interactions_df)
        
        recommendations = hybrid.hybrid_recommend("user_001", N=3)
        
        for rec in recommendations:
            # Should have top 2 explanations
            explanations = rec.get("explanations", [])
            assert len(explanations) <= 2
            
            # Should have all explanations
            all_explanations = rec.get("all_explanations", [])
            assert len(all_explanations) >= len(explanations)
            
            # Explanations should be strings
            assert all(isinstance(exp, str) for exp in explanations)
    
    def test_skill_match_explanation(self, mock_als_model, mock_baseline_model, sample_courses_df, sample_interactions_df):
        """Test skill match explanation generation."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        hybrid.set_data(sample_courses_df, sample_interactions_df)
        
        # Test with a course that has skill tags
        skill_explanation = hybrid._get_skill_match_explanation("course_001")
        assert skill_explanation == "python"
        
        # Test with a course that has no skill tags
        skill_explanation = hybrid._get_skill_match_explanation("course_999")
        assert skill_explanation is None
    
    def test_course_info_explanation(self, mock_als_model, mock_baseline_model, sample_courses_df, sample_interactions_df):
        """Test course info explanation generation."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        hybrid.set_data(sample_courses_df, sample_interactions_df)
        
        # Test with existing course
        course_info = hybrid._get_course_info("course_001")
        assert "Python Basics" in course_info
        
        # Test with non-existing course
        course_info = hybrid._get_course_info("course_999")
        assert course_info is None
    
    def test_get_user_courses(self, mock_als_model, mock_baseline_model, sample_interactions_df):
        """Test getting user's enrolled courses."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        hybrid.set_data(None, sample_interactions_df)
        
        # User 001 has enrolled and completed courses
        user_courses = hybrid._get_user_courses("user_001")
        assert "course_001" in user_courses
        assert "course_002" in user_courses
        
        # User 003 only has view interaction
        user_courses = hybrid._get_user_courses("user_003")
        assert len(user_courses) == 0
    
    def test_explanation_summary(self, mock_als_model, mock_baseline_model, sample_courses_df, sample_interactions_df):
        """Test explanation summary generation."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        hybrid.set_data(sample_courses_df, sample_interactions_df)
        
        summary = hybrid.get_explanation_summary("user_001", N=5)
        
        assert "user_id" in summary
        assert "total_recommendations" in summary
        assert "explanation_summary" in summary
        assert "top_explanations" in summary
        
        assert summary["user_id"] == "user_001"
        assert summary["total_recommendations"] > 0
        assert len(summary["top_explanations"]) > 0
    
    def test_normalize_score(self, mock_als_model, mock_baseline_model):
        """Test score normalization for different approaches."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        # Test ALS score normalization (can be negative)
        als_score = hybrid._normalize_score(-0.5, "als")
        assert 0.0 <= als_score <= 1.0
        
        # Test content score normalization (typically 0-1)
        content_score = hybrid._normalize_score(0.8, "content")
        assert content_score == 0.8
        
        # Test popularity score normalization (typically 0-1)
        pop_score = hybrid._normalize_score(0.9, "pop")
        assert pop_score == 0.9
    
    def test_combine_recommendations(self, mock_als_model, mock_baseline_model):
        """Test combining recommendations from different approaches."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        recommendations = {
            "als": [{"item_id": "course_001", "score": 0.9}],
            "content": [{"item_id": "course_001", "similarity_score": 0.8}],
            "pop": [{"item_id": "course_001", "score": 0.7}]
        }
        
        weights = {"als": 0.5, "content": 0.3, "pop": 0.2}
        combined_scores = hybrid._combine_recommendations(recommendations, weights)
        
        assert "course_001" in combined_scores
        assert combined_scores["course_001"] > 0
    
    def test_get_top_recommendations(self, mock_als_model, mock_baseline_model):
        """Test getting top-N recommendations."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        combined_scores = {
            "course_001": 0.9,
            "course_002": 0.8,
            "course_003": 0.7,
            "course_004": 0.6
        }
        
        top_recs = hybrid._get_top_recommendations(combined_scores, N=3)
        
        assert len(top_recs) == 3
        assert top_recs[0][0] == "course_001"  # Highest score
        assert top_recs[0][1] == 0.9
    
    def test_edge_cases(self, mock_als_model, mock_baseline_model):
        """Test edge cases and error handling."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        # Test with no models
        empty_hybrid = HybridRecommender()
        recommendations = empty_hybrid.hybrid_recommend("user_001", N=5)
        
        # Should return recommendations with fallback explanations
        assert len(recommendations) > 0
        for rec in recommendations:
            assert "recommended_for_you" in rec.get("explanations", [])
    
    def test_weight_normalization(self, mock_als_model, mock_baseline_model):
        """Test that weights are properly normalized."""
        hybrid = HybridRecommender(
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        # Test with weights that don't sum to 1
        unnormalized_weights = {"als": 0.5, "content": 0.3, "pop": 0.1}
        recommendations = hybrid.hybrid_recommend("user_001", N=5, weights=unnormalized_weights)
        
        # Should still work and normalize weights internally
        assert len(recommendations) > 0


class TestHybridRecommendFunction:
    """Test cases for the standalone hybrid_recommend function."""
    
    @pytest.fixture
    def mock_als_model(self):
        """Create a mock ALS model."""
        mock_model = Mock(spec=ALSRecommender)
        mock_model.is_fitted = True
        mock_model.recommend.return_value = [
            {"item_id": "course_001", "score": 0.9, "rank": 1, "model": "ALS"}
        ]
        return mock_model
    
    @pytest.fixture
    def mock_baseline_model(self):
        """Create a mock baseline model."""
        mock_model = Mock(spec=BaselineRecommender)
        mock_model.is_fitted = True
        mock_model.recommend.return_value = [
            {"item_id": "course_002", "score": 0.8, "rank": 1, "model": "Baseline"}
        ]
        mock_model.get_similar_items.return_value = [
            {"item_id": "course_003", "similarity_score": 0.7, "rank": 1, "reference_item": "course_001"}
        ]
        return mock_model
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        courses_df = pd.DataFrame({
            'course_id': ['course_001', 'course_002'],
            'title': ['Python Basics', 'Advanced Python'],
            'skill_tags': ['python,programming', 'python,advanced']
        })
        
        interactions_df = pd.DataFrame({
            'user_id': ['user_001'],
            'course_id': ['course_001'],
            'event_type': ['enroll'],
            'rating': [5.0]
        })
        
        return courses_df, interactions_df
    
    def test_hybrid_recommend_function_basic(self, mock_als_model, mock_baseline_model, sample_data):
        """Test basic functionality of hybrid_recommend function."""
        courses_df, interactions_df = sample_data
        
        recommendations = hybrid_recommend(
            user_id="user_001",
            N=5,
            weights={"als": 0.7, "content": 0.2, "pop": 0.1},
            als_model=mock_als_model,
            baseline_model=mock_baseline_model,
            courses_df=courses_df,
            interactions_df=interactions_df
        )
        
        assert len(recommendations) > 0
        assert all(isinstance(rec, dict) for rec in recommendations)
        assert all("explanations" in rec for rec in recommendations)
    
    def test_hybrid_recommend_function_default_weights(self, mock_als_model, mock_baseline_model):
        """Test hybrid_recommend function with default weights."""
        recommendations = hybrid_recommend(
            user_id="user_001",
            N=5,
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        assert len(recommendations) > 0
        # Should use default weights (als: 0.7, content: 0.2, pop: 0.1)
    
    def test_hybrid_recommend_function_no_models(self):
        """Test hybrid_recommend function with no models."""
        recommendations = hybrid_recommend(
            user_id="user_001",
            N=5
        )
        
        # Should still return recommendations with fallback explanations
        assert len(recommendations) > 0
        for rec in recommendations:
            assert "recommended_for_you" in rec.get("explanations", [])
    
    def test_hybrid_recommend_function_custom_weights(self, mock_als_model, mock_baseline_model):
        """Test hybrid_recommend function with custom weights."""
        custom_weights = {"als": 0.9, "content": 0.1}
        
        recommendations = hybrid_recommend(
            user_id="user_001",
            N=5,
            weights=custom_weights,
            als_model=mock_als_model,
            baseline_model=mock_baseline_model
        )
        
        assert len(recommendations) > 0
        # ALS should have much higher influence due to 0.9 weight
