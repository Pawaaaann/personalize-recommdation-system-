"""
Tests for the ALS recommender model.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import os

from ..models.als_recommender import ALSRecommender


class TestALSRecommender:
    """Test cases for ALSRecommender class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def small_interactions_data(self):
        """Create a small synthetic interactions dataset for testing."""
        np.random.seed(42)
        
        # Create small dataset: 10 users, 8 courses, 25 interactions
        n_users = 10
        n_courses = 8
        n_interactions = 25
        
        # Generate user and course IDs - ensure we get exactly the expected numbers
        user_ids = [f"user_{i:03d}" for i in range(1, n_users + 1)]
        course_ids = [f"course_{i:03d}" for i in range(1, n_courses + 1)]
        
        # Generate interactions with different event types
        interactions = []
        event_types = ['view', 'enroll', 'complete', 'quiz_attempt']
        
        # Ensure we have at least one interaction for each user and course
        for user_id in user_ids:
            interactions.append({
                'user_id': user_id,
                'course_id': np.random.choice(course_ids),
                'event_type': np.random.choice(event_types),
                'rating': np.random.choice([1, 2, 3, 4, 5]) if np.random.random() > 0.3 else np.nan,
                'timestamp': np.random.randint(1600000000, 1700000000)
            })
        
        for course_id in course_ids:
            interactions.append({
                'user_id': np.random.choice(user_ids),
                'course_id': course_id,
                'event_type': np.random.choice(event_types),
                'rating': np.random.choice([1, 2, 3, 4, 5]) if np.random.random() > 0.3 else np.nan,
                'timestamp': np.random.randint(1600000000, 1700000000)
            })
        
        # Fill remaining interactions randomly
        remaining_interactions = n_interactions - len(interactions)
        for _ in range(remaining_interactions):
            user_id = np.random.choice(user_ids)
            course_id = np.random.choice(course_ids)
            event_type = np.random.choice(event_types)
            rating = np.random.choice([1, 2, 3, 4, 5]) if np.random.random() > 0.3 else np.nan
            
            interactions.append({
                'user_id': user_id,
                'course_id': course_id,
                'event_type': event_type,
                'rating': rating,
                'timestamp': np.random.randint(1600000000, 1700000000)
            })
        
        df = pd.DataFrame(interactions)
        
        # Verify we have the expected number of unique users and courses
        assert df['user_id'].nunique() == n_users, f"Expected {n_users} users, got {df['user_id'].nunique()}"
        assert df['course_id'].nunique() == n_courses, f"Expected {n_courses} courses, got {df['course_id'].nunique()}"
        
        return df
    
    def test_init_default_params(self):
        """Test ALSRecommender initialization with default parameters."""
        als = ALSRecommender()
        
        assert als.factors == 64
        assert als.regularization == 0.01
        assert als.iterations == 20
        assert als.alpha == 40.0
        assert als.name == "ALSRecommender"
        assert not als.is_fitted
        assert als.interaction_weights == {
            'view': 1, 'enroll': 3, 'complete': 5, 'rating': 4, 'quiz_attempt': 2, 'default': 1
        }
    
    def test_init_custom_params(self):
        """Test ALSRecommender initialization with custom parameters."""
        als = ALSRecommender(
            factors=128,
            regularization=0.1,
            iterations=50,
            alpha=60.0
        )
        
        assert als.factors == 128
        assert als.regularization == 0.1
        assert als.iterations == 50
        assert als.alpha == 60.0
    
    def test_fit_creates_interaction_matrix(self, small_interactions_data):
        """Test that fit method creates proper interaction matrix."""
        als = ALSRecommender(factors=32, iterations=5)  # Use small factors and iterations for speed
        
        # Fit the model
        als.fit(small_interactions_data)
        
        # Check that model is fitted
        assert als.is_fitted
        
        # Check interaction matrix shape
        assert als.interaction_matrix.shape == (10, 8)  # 10 users, 8 courses
        
        # Check ID mappings
        assert len(als.user_id_to_index) == 10
        assert len(als.item_id_to_index) == 8
        assert len(als.index_to_user_id) == 10
        assert len(als.index_to_item_id) == 8
        
        # Check that factors are created
        assert als.user_factors is not None
        assert als.item_factors is not None
        assert als.user_factors.shape == (10, 32)  # 10 users, 32 factors
        assert als.item_factors.shape == (8, 32)   # 8 courses, 32 factors
    
    def test_confidence_weighting(self, small_interactions_data):
        """Test that confidence weighting is applied correctly."""
        als = ALSRecommender(factors=16, iterations=5)
        
        # Fit the model
        als.fit(small_interactions_data)
        
        # Check that interaction matrix has non-binary values due to weighting
        matrix_values = als.interaction_matrix.data
        
        # Should have different values due to confidence weighting
        unique_values = np.unique(matrix_values)
        assert len(unique_values) > 1  # More than just 0s and 1s
        
        # Check that weights are applied correctly
        # The actual values will be modulated by ratings, so we check for the base weights
        # view=1, enroll=3, complete=5, quiz_attempt=2
        base_weights = [1, 2, 3, 5]
        
        # Check that at least some of the base weights are present (scaled by alpha)
        found_weights = 0
        for weight in base_weights:
            scaled_weight = weight * als.alpha
            if any(np.isclose(matrix_values, scaled_weight, atol=1e-6)):
                found_weights += 1
        
        # Should find at least some of the base weights
        assert found_weights >= 2, f"Expected to find at least 2 base weights, found {found_weights}"
        
        # All values should be positive and reasonable
        assert np.all(matrix_values > 0)
        assert np.all(matrix_values <= 200)  # Max should be 5 * 40 = 200
    
    def test_recommend_output_format(self, small_interactions_data):
        """Test that recommend method returns correct output format."""
        als = ALSRecommender(factors=16, iterations=5)
        als.fit(small_interactions_data)
        
        # Get recommendations for a user
        user_id = small_interactions_data['user_id'].iloc[0]
        recommendations = als.recommend(user_id, n_recommendations=5)
        
        # Check output format
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5
        
        for rec in recommendations:
            assert isinstance(rec, dict)
            assert 'item_id' in rec
            assert 'score' in rec
            assert 'rank' in rec
            assert 'model' in rec
            
            assert rec['model'] == 'ALS'
            assert isinstance(rec['score'], float)
            assert isinstance(rec['rank'], int)
            assert rec['rank'] > 0
    
    def test_similar_items_output_format(self, small_interactions_data):
        """Test that similar_items method returns correct output format."""
        als = ALSRecommender(factors=16, iterations=5)
        als.fit(small_interactions_data)
        
        # Get similar items for a course
        course_id = small_interactions_data['course_id'].iloc[0]
        similar_items = als.similar_items(course_id, n_similar=3)
        
        # Check output format
        assert isinstance(similar_items, list)
        assert len(similar_items) <= 3
        
        for item in similar_items:
            assert isinstance(item, dict)
            assert 'item_id' in item
            assert 'similarity_score' in item
            assert 'rank' in item
            assert 'reference_item' in item
            
            assert item['reference_item'] == course_id
            assert isinstance(item['similarity_score'], float)
            assert isinstance(item['rank'], int)
            assert item['rank'] > 0
    
    def test_save_and_load(self, small_interactions_data, temp_dir):
        """Test save and load functionality."""
        als = ALSRecommender(factors=16, iterations=5)
        als.fit(small_interactions_data)
        
        # Save the model
        save_path = os.path.join(temp_dir, "test_als_model.pkl")
        als.save(save_path)
        
        # Check that file was created
        assert os.path.exists(save_path)
        
        # Create new instance and load
        als_loaded = ALSRecommender()
        als_loaded.load(save_path)
        
        # Check that model is fitted
        assert als_loaded.is_fitted
        
        # Check that all attributes are restored
        assert als_loaded.factors == als.factors
        assert als_loaded.regularization == als.regularization
        assert als_loaded.iterations == als.iterations
        assert als_loaded.alpha == als.alpha
        assert als_loaded.interaction_weights == als.interaction_weights
        
        # Check that matrices are restored
        assert als_loaded.interaction_matrix.shape == als.interaction_matrix.shape
        assert als_loaded.user_factors.shape == als.user_factors.shape
        assert als_loaded.item_factors.shape == als.item_factors.shape
        
        # Check that ID mappings are restored
        assert als_loaded.user_id_to_index == als.user_id_to_index
        assert als_loaded.item_id_to_index == als.item_id_to_index
    
    def test_recommendations_consistency(self, small_interactions_data):
        """Test that recommendations are consistent for the same user."""
        als = ALSRecommender(factors=16, iterations=5)
        als.fit(small_interactions_data)
        
        user_id = small_interactions_data['user_id'].iloc[0]
        
        # Get recommendations twice
        rec1 = als.recommend(user_id, n_recommendations=5)
        rec2 = als.recommend(user_id, n_recommendations=5)
        
        # Should be identical (deterministic)
        assert rec1 == rec2
    
    def test_edge_cases(self, small_interactions_data):
        """Test edge cases and error handling."""
        als = ALSRecommender(factors=16, iterations=5)
        
        # Test recommending before fitting
        with pytest.raises(RuntimeError):
            als.recommend("user_001")
        
        # Test similar items before fitting
        with pytest.raises(RuntimeError):
            als.similar_items("course_001")
        
        # Fit the model
        als.fit(small_interactions_data)
        
        # Test recommending for unknown user
        unknown_user_recs = als.recommend("unknown_user")
        assert unknown_user_recs == []
        
        # Test similar items for unknown course
        unknown_course_similar = als.similar_items("unknown_course")
        assert unknown_course_similar == []
    
    def test_model_info(self, small_interactions_data):
        """Test that get_model_info returns correct information."""
        als = ALSRecommender(factors=16, iterations=5)
        
        # Before fitting
        info_before = als.get_model_info()
        assert info_before['is_fitted'] == False
        
        # After fitting
        als.fit(small_interactions_data)
        info_after = als.get_model_info()
        
        assert info_after['is_fitted'] == True
        assert info_after['factors'] == 16
        assert info_after['regularization'] == 0.01
        assert info_after['iterations'] == 5
        assert info_after['alpha'] == 40.0
        assert info_after['n_users'] == 10
        assert info_after['n_items'] == 8
        assert info_after['matrix_shape'] == (10, 8)
        assert 'sparsity' in info_after
    
    def test_rating_prediction(self, small_interactions_data):
        """Test rating prediction functionality."""
        als = ALSRecommender(factors=16, iterations=5)
        als.fit(small_interactions_data)
        
        # Test prediction for known user-item pair
        user_id = small_interactions_data['user_id'].iloc[0]
        course_id = small_interactions_data['course_id'].iloc[0]
        
        rating = als.predict_rating(user_id, course_id)
        assert isinstance(rating, float)
        assert 1.0 <= rating <= 5.0
        
        # Test prediction for unknown user/item
        unknown_rating = als.predict_rating("unknown_user", "unknown_course")
        assert unknown_rating == 0.0
    
    def test_embedding_retrieval(self, small_interactions_data):
        """Test user and item embedding retrieval."""
        als = ALSRecommender(factors=16, iterations=5)
        als.fit(small_interactions_data)
        
        user_id = small_interactions_data['user_id'].iloc[0]
        course_id = small_interactions_data['course_id'].iloc[0]
        
        # Get user embedding
        user_embedding = als.get_user_embeddings(user_id)
        assert isinstance(user_embedding, np.ndarray)
        assert user_embedding.shape == (16,)  # 16 factors
        
        # Get item embedding
        item_embedding = als.get_item_embeddings(course_id)
        assert isinstance(item_embedding, np.ndarray)
        assert item_embedding.shape == (16,)  # 16 factors
        
        # Test error for unknown user/item
        with pytest.raises(ValueError):
            als.get_user_embeddings("unknown_user")
        
        with pytest.raises(ValueError):
            als.get_item_embeddings("unknown_course")
    
    def test_save_unfitted_model_error(self):
        """Test that saving unfitted model raises error."""
        als = ALSRecommender()
        
        with pytest.raises(RuntimeError):
            als.save("test.pkl")
    
    def test_interaction_matrix_sparsity(self, small_interactions_data):
        """Test that interaction matrix sparsity is calculated correctly."""
        als = ALSRecommender(factors=16, iterations=5)
        als.fit(small_interactions_data)
        
        # Get sparsity from model info
        info = als.get_model_info()
        sparsity = info['sparsity']
        
        # Should be a float between 0 and 1
        assert isinstance(sparsity, float)
        assert 0.0 <= sparsity <= 1.0
        
        # For our small test data, sparsity should be reasonable
        # 10 users * 8 courses = 80 total elements, 25 interactions
        expected_sparsity = 1 - (25 / 80)  # ≈ 0.6875
        assert abs(sparsity - expected_sparsity) < 0.1  # Allow some tolerance
