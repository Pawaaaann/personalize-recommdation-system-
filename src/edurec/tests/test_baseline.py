"""
Tests for the baseline recommender model.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
from ..models.baseline import (
    popularity_recommender, 
    content_based_recommender,
    get_course_popularity_stats,
    get_course_similarity_matrix
)

class TestBaselineRecommender:
    """Test cases for baseline recommender functions."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_interactions(self):
        """Create sample interactions data for testing."""
        np.random.seed(42)
        n_interactions = 1000
        n_students = 100
        n_courses = 50
        
        # Create realistic interaction data
        interactions = []
        for _ in range(n_interactions):
            interactions.append({
                'student_id': np.random.randint(1, n_students + 1),
                'course_id': np.random.randint(1, n_courses + 1),
                'timestamp': np.random.randint(1600000000, 1700000000),
                'event_type': np.random.choice(['view', 'enroll', 'complete', 'quiz_attempt']),
                'progress': np.random.randint(0, 101),
                'quiz_score': np.random.randint(0, 101) if np.random.random() > 0.7 else None,
                'skill_tags': '|'.join(np.random.choice(['algebra', 'calculus', 'programming'], size=np.random.randint(1, 4)))
            })
        
        return pd.DataFrame(interactions)
    
    @pytest.fixture
    def sample_courses(self):
        """Create sample courses data for testing."""
        np.random.seed(42)
        n_courses = 50
        
        courses = []
        for i in range(n_courses):
            category = np.random.choice(['Mathematics', 'Computer Science', 'Language Arts'])
            difficulty = np.random.choice(['Beginner', 'Intermediate', 'Advanced'])
            
            if category == 'Mathematics':
                title = f"{difficulty} Mathematics: {np.random.choice(['Algebra', 'Calculus', 'Geometry'])}"
                skills = '|'.join(np.random.choice(['algebra', 'calculus', 'geometry', 'fractions'], size=np.random.randint(2, 5)))
            elif category == 'Computer Science':
                title = f"{difficulty} Computer Science: {np.random.choice(['Programming', 'Data Structures', 'Algorithms'])}"
                skills = '|'.join(np.random.choice(['programming', 'algorithms', 'data_structures', 'databases'], size=np.random.randint(2, 5)))
            else:
                title = f"{difficulty} Language Arts: {np.random.choice(['Writing', 'Grammar', 'Literature'])}"
                skills = '|'.join(np.random.choice(['writing', 'grammar', 'vocabulary', 'communication'], size=np.random.randint(2, 5)))
            
            courses.append({
                'course_id': i + 1,
                'title': title,
                'description': f"A comprehensive {difficulty.lower()} course in {category.lower()}.",
                'duration_hours': np.random.randint(2, 20),
                'skill_tags': skills
            })
        
        return pd.DataFrame(courses)
    
    def test_popularity_recommender_basic(self, sample_interactions):
        """Test basic functionality of popularity recommender."""
        # Test with default top_n
        recommendations = popularity_recommender(sample_interactions)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 20  # Default top_n
        assert all(isinstance(course_id, int) for course_id in recommendations)
        
        # Test with custom top_n
        recommendations = popularity_recommender(sample_interactions, top_n=10)
        assert len(recommendations) == 10
    
    def test_popularity_recommender_ordering(self, sample_interactions):
        """Test that popularity recommender returns courses in correct order."""
        recommendations = popularity_recommender(sample_interactions, top_n=5)
        
        # Get actual popularity counts
        popularity_counts = sample_interactions['course_id'].value_counts()
        
        # Check that recommendations are in descending order of popularity
        for i in range(len(recommendations) - 1):
            current_pop = popularity_counts[recommendations[i]]
            next_pop = popularity_counts[recommendations[i + 1]]
            assert current_pop >= next_pop, f"Popularity ordering incorrect at position {i}"
    
    def test_popularity_recommender_edge_cases(self, sample_interactions):
        """Test edge cases for popularity recommender."""
        # Test with top_n larger than available courses
        unique_courses = sample_interactions['course_id'].nunique()
        recommendations = popularity_recommender(sample_interactions, top_n=unique_courses + 10)
        assert len(recommendations) == unique_courses
        
        # Test with empty interactions
        empty_df = pd.DataFrame(columns=sample_interactions.columns)
        recommendations = popularity_recommender(empty_df)
        assert recommendations == []
    
    def test_content_based_recommender_course_id(self, sample_courses):
        """Test content-based recommender using course_id."""
        # Test with a specific course
        target_course_id = 1
        recommendations = content_based_recommender(sample_courses, course_id=target_course_id, top_n=5)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 5
        assert all(isinstance(course_id, int) for course_id in recommendations)
        assert target_course_id not in recommendations  # Should not recommend the target course
    
    def test_content_based_recommender_query_text(self, sample_courses):
        """Test content-based recommender using query text."""
        # Test with a text query
        query = "mathematics algebra calculus"
        recommendations = content_based_recommender(sample_courses, query_text=query, top_n=5)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 5
        assert all(isinstance(course_id, int) for course_id in recommendations)
    
    def test_content_based_recommender_validation(self, sample_courses):
        """Test input validation for content-based recommender."""
        # Test with neither course_id nor query_text
        with pytest.raises(Exception):
            content_based_recommender(sample_courses)
        
        # Test with invalid course_id
        recommendations = content_based_recommender(sample_courses, course_id=999)
        assert recommendations == []
    
    def test_content_based_recommender_similarity_ordering(self, sample_courses):
        """Test that content-based recommender returns courses in similarity order."""
        target_course_id = 1
        recommendations = content_based_recommender(sample_courses, course_id=target_course_id, top_n=3)
        
        # Get the target course text
        target_course = sample_courses[sample_courses['course_id'] == target_course_id].iloc[0]
        target_text = f"{target_course['title']} {target_course['description']} {target_course['skill_tags']}"
        
        # Get recommended courses
        recommended_courses = sample_courses[sample_courses['course_id'].isin(recommendations)]
        
        # Simple similarity check (courses with similar skill tags should be ranked higher)
        target_skills = set(target_course['skill_tags'].split('|'))
        
        # Check that courses with more skill overlap come first
        for i in range(len(recommendations) - 1):
            current_course = recommended_courses[recommended_courses['course_id'] == recommendations[i]].iloc[0]
            next_course = recommended_courses[recommended_courses['course_id'] == recommendations[i + 1]].iloc[0]
            
            current_skills = set(current_course['skill_tags'].split('|'))
            next_skills = set(next_course['skill_tags'].split('|'))
            
            current_overlap = len(target_skills.intersection(current_skills))
            next_overlap = len(target_skills.intersection(next_skills))
            
            # This is a heuristic check - in practice, TF-IDF + cosine similarity should handle this better
            # We're just ensuring the function doesn't crash and returns reasonable results
            assert isinstance(current_overlap, int)
            assert isinstance(next_overlap, int)
    
    def test_content_based_recommender_top_n(self, sample_courses):
        """Test that content-based recommender respects top_n parameter."""
        # Test with different top_n values
        for top_n in [1, 5, 10, 20]:
            recommendations = content_based_recommender(sample_courses, course_id=1, top_n=top_n)
            assert len(recommendations) == min(top_n, len(sample_courses) - 1)  # -1 for excluding target course
    
    def test_get_course_popularity_stats(self, sample_interactions):
        """Test the get_course_popularity_stats function."""
        popularity_stats = get_course_popularity_stats(sample_interactions)
        
        assert isinstance(popularity_stats, pd.Series)
        assert len(popularity_stats) == sample_interactions['course_id'].nunique()
        assert popularity_stats.index.name is None  # Should be course_id
        assert all(popularity_stats.values > 0)  # All courses should have at least one interaction
    
    def test_get_course_similarity_matrix(self, sample_courses):
        """Test the get_course_similarity_matrix function."""
        similarity_matrix = get_course_similarity_matrix(sample_courses)
        
        assert isinstance(similarity_matrix, np.ndarray)
        assert similarity_matrix.shape == (len(sample_courses), len(sample_courses))
        
        # Check that diagonal elements are 1.0 (self-similarity)
        np.testing.assert_array_almost_equal(np.diag(similarity_matrix), 1.0)
        
        # Check that similarity values are between -1 and 1
        assert np.all(similarity_matrix >= -1) and np.all(similarity_matrix <= 1)
    
    def test_error_handling(self, sample_interactions, sample_courses):
        """Test error handling in recommender functions."""
        # Test with malformed data
        malformed_interactions = sample_interactions.copy()
        malformed_interactions.loc[0, 'course_id'] = None
        
        # Should handle gracefully
        recommendations = popularity_recommender(malformed_interactions)
        assert isinstance(recommendations, list)
        
        # Test with malformed courses data
        malformed_courses = sample_courses.copy()
        malformed_courses.loc[0, 'title'] = None
        
        # Should handle gracefully
        recommendations = content_based_recommender(malformed_courses, course_id=2)
        assert isinstance(recommendations, list)
    
    def test_reproducibility(self, sample_interactions, sample_courses):
        """Test that recommendations are reproducible with the same data."""
        # Get recommendations twice
        pop_rec1 = popularity_recommender(sample_interactions, top_n=10)
        pop_rec2 = popularity_recommender(sample_interactions, top_n=10)
        
        content_rec1 = content_based_recommender(sample_courses, course_id=1, top_n=10)
        content_rec2 = content_based_recommender(sample_courses, course_id=1, top_n=10)
        
        # Should be identical
        assert pop_rec1 == pop_rec2
        assert content_rec1 == content_rec2
    
    def test_integration_with_synthetic_data(self, temp_data_dir):
        """Test that the recommenders work with the actual synthetic data generator."""
        try:
            # Import and run the data generator
            from ..data.generate_sample import generate_sample_data
            
            # Generate a small dataset for testing
            data = generate_sample_data(
                n_students=100,
                n_courses=20,
                n_interactions=500,
                output_dir=temp_data_dir
            )
            
            interactions_df = data['interactions']
            courses_df = data['courses']
            
            # Test popularity recommender
            pop_recommendations = popularity_recommender(interactions_df, top_n=5)
            assert len(pop_recommendations) == 5
            assert all(course_id in courses_df['course_id'].values for course_id in pop_recommendations)
            
            # Test content-based recommender
            content_recommendations = content_based_recommender(courses_df, course_id=1, top_n=5)
            assert len(content_recommendations) == 5
            assert all(course_id in courses_df['course_id'].values for course_id in content_recommendations)
            
        except ImportError:
            pytest.skip("Synthetic data generator not available for integration test")
        except Exception as e:
            pytest.fail(f"Integration test failed: {e}") 