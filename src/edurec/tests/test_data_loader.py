"""
Tests for the data loader module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil

from ..data.data_loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        users_data = {
            'user_id': ['user_001', 'user_002', 'user_003'],
            'age_group': ['25-34', '18-24', '35-44'],
            'education_level': ['Bachelor\'s', 'High School', 'Master\'s'],
            'primary_interest': ['Computer Science', 'Mathematics', 'Physics']
        }
        
        courses_data = {
            'course_id': ['course_001', 'course_002', 'course_003'],
            'title': ['Python Basics', 'Linear Algebra', 'Quantum Mechanics'],
            'category': ['Computer Science', 'Mathematics', 'Physics'],
            'difficulty_level': ['Beginner', 'Intermediate', 'Advanced']
        }
        
        interactions_data = {
            'user_id': ['user_001', 'user_001', 'user_002', 'user_003'],
            'course_id': ['course_001', 'course_002', 'course_001', 'course_003'],
            'rating': [4.5, 3.0, 5.0, 4.0],
            'interaction_type': ['enrollment', 'completion', 'rating', 'enrollment']
        }
        
        return {
            'users': pd.DataFrame(users_data),
            'courses': pd.DataFrame(courses_data),
            'interactions': pd.DataFrame(interactions_data)
        }
    
    def test_init(self, temp_data_dir):
        """Test DataLoader initialization."""
        loader = DataLoader(temp_data_dir)
        assert loader.data_dir == Path(temp_data_dir)
        assert loader.users_df is None
        assert loader.courses_df is None
        assert loader.interactions_df is None
    
    def test_load_users(self, temp_data_dir, sample_data):
        """Test loading users data."""
        loader = DataLoader(temp_data_dir)
        
        # Save sample users data
        sample_data['users'].to_csv(Path(temp_data_dir) / "users.csv", index=False)
        
        # Load users
        users_df = loader.load_users()
        
        assert not users_df.empty
        assert len(users_df) == 3
        assert 'user_id' in users_df.columns
        assert 'primary_interest' in users_df.columns
    
    def test_load_courses(self, temp_data_dir, sample_data):
        """Test loading courses data."""
        loader = DataLoader(temp_data_dir)
        
        # Save sample courses data
        sample_data['courses'].to_csv(Path(temp_data_dir) / "courses.csv", index=False)
        
        # Load courses
        courses_df = loader.load_courses()
        
        assert not courses_df.empty
        assert len(courses_df) == 3
        assert 'course_id' in courses_df.columns
        assert 'category' in courses_df.columns
    
    def test_load_interactions(self, temp_data_dir, sample_data):
        """Test loading interactions data."""
        loader = DataLoader(temp_data_dir)
        
        # Save sample interactions data
        sample_data['interactions'].to_csv(Path(temp_data_dir) / "interactions.csv", index=False)
        
        # Load interactions
        interactions_df = loader.load_interactions()
        
        assert not interactions_df.empty
        assert len(interactions_df) == 4
        assert 'user_id' in interactions_df.columns
        assert 'rating' in interactions_df.columns
    
    def test_load_all_data(self, temp_data_dir, sample_data):
        """Test loading all data at once."""
        loader = DataLoader(temp_data_dir)
        
        # Save all sample data
        sample_data['users'].to_csv(Path(temp_data_dir) / "users.csv", index=False)
        sample_data['courses'].to_csv(Path(temp_data_dir) / "courses.csv", index=False)
        sample_data['interactions'].to_csv(Path(temp_data_dir) / "interactions.csv", index=False)
        
        # Load all data
        data = loader.load_all_data()
        
        assert 'users' in data
        assert 'courses' in data
        assert 'interactions' in data
        assert len(data['users']) == 3
        assert len(data['courses']) == 3
        assert len(data['interactions']) == 4
    
    def test_get_user_item_matrix(self, temp_data_dir, sample_data):
        """Test creating user-item interaction matrix."""
        loader = DataLoader(temp_data_dir)
        
        # Save sample data
        sample_data['interactions'].to_csv(Path(temp_data_dir) / "interactions.csv", index=False)
        loader.load_interactions()
        
        # Get user-item matrix
        matrix, user_ids, item_ids = loader.get_user_item_matrix()
        
        assert isinstance(matrix, np.ndarray)
        assert len(user_ids) == 3  # 3 unique users
        assert len(item_ids) == 3  # 3 unique courses
        assert matrix.shape == (3, 3)
        
        # Check that ratings are correctly placed
        assert matrix[0, 0] == 4.5  # user_001, course_001
        assert matrix[0, 1] == 3.0  # user_001, course_002
    
    def test_save_data(self, temp_data_dir, sample_data):
        """Test saving data."""
        loader = DataLoader(temp_data_dir)
        
        # Save data
        loader.save_data(
            users=sample_data['users'],
            courses=sample_data['courses'],
            interactions=sample_data['interactions']
        )
        
        # Check that files were created
        assert (Path(temp_data_dir) / "users.csv").exists()
        assert (Path(temp_data_dir) / "courses.csv").exists()
        assert (Path(temp_data_dir) / "interactions.csv").exists()
    
    def test_get_data_summary(self, temp_data_dir, sample_data):
        """Test getting data summary."""
        loader = DataLoader(temp_data_dir)
        
        # Save and load sample data
        loader.save_data(
            users=sample_data['users'],
            courses=sample_data['courses'],
            interactions=sample_data['interactions']
        )
        loader.load_all_data()
        
        # Get summary
        summary = loader.get_data_summary()
        
        assert 'users' in summary
        assert 'courses' in summary
        assert 'interactions' in summary
        
        assert summary['users']['count'] == 3
        assert summary['courses']['count'] == 3
        assert summary['interactions']['count'] == 4
        assert 'sparsity' in summary['interactions']
    
    def test_handle_missing_files(self, temp_data_dir):
        """Test handling of missing data files."""
        loader = DataLoader(temp_data_dir)
        
        # Try to load non-existent files
        users_df = loader.load_users()
        courses_df = loader.load_courses()
        interactions_df = loader.load_interactions()
        
        assert users_df.empty
        assert courses_df.empty
        assert interactions_df.empty
    
    def test_calculate_sparsity(self, temp_data_dir, sample_data):
        """Test sparsity calculation."""
        loader = DataLoader(temp_data_dir)
        
        # Save and load sample data
        loader.save_data(
            users=sample_data['users'],
            courses=sample_data['courses'],
            interactions=sample_data['interactions']
        )
        loader.load_all_data()
        
        # Get summary to trigger sparsity calculation
        summary = loader.get_data_summary()
        sparsity = summary['interactions']['sparsity']
        
        # With 3 users, 3 courses, and 4 interactions, sparsity should be:
        # 1 - (4 / (3 * 3)) = 1 - (4/9) ≈ 0.556
        expected_sparsity = 1 - (4 / (3 * 3))
        assert abs(sparsity - expected_sparsity) < 1e-6 