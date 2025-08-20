"""
Data loader for educational recommendation data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Loads and manages educational data for recommendations."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the data loader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.users_df: Optional[pd.DataFrame] = None
        self.courses_df: Optional[pd.DataFrame] = None
        self.interactions_df: Optional[pd.DataFrame] = None
        
    def load_users(self, filepath: str = "users.csv") -> pd.DataFrame:
        """Load user data from CSV file."""
        file_path = self.data_dir / filepath
        if file_path.exists():
            self.users_df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(self.users_df)} users from {file_path}")
        else:
            logger.warning(f"Users file not found: {file_path}")
            self.users_df = pd.DataFrame()
        return self.users_df
    
    def load_courses(self, filepath: str = "courses.csv") -> pd.DataFrame:
        """Load course data from CSV file."""
        file_path = self.data_dir / filepath
        if file_path.exists():
            self.courses_df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(self.courses_df)} courses from {file_path}")
        else:
            logger.warning(f"Courses file not found: {file_path}")
            self.courses_df = pd.DataFrame()
        return self.courses_df
    
    def load_interactions(self, filepath: str = "interactions.csv") -> pd.DataFrame:
        """Load user-course interactions from CSV file."""
        file_path = self.data_dir / filepath
        if file_path.exists():
            self.interactions_df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(self.interactions_df)} interactions from {file_path}")
        else:
            logger.warning(f"Interactions file not found: {file_path}")
            self.interactions_df = pd.DataFrame()
        return self.interactions_df
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all data files."""
        return {
            "users": self.load_users(),
            "courses": self.load_courses(),
            "interactions": self.load_interactions()
        }
    
    def get_user_item_matrix(self) -> Tuple[np.ndarray, List, List]:
        """
        Create a user-item interaction matrix.
        
        Returns:
            Tuple of (matrix, user_ids, item_ids)
        """
        if self.interactions_df is None or self.interactions_df.empty:
            raise ValueError("No interactions data loaded")
        
        # Create pivot table - use student_id instead of user_id
        pivot = self.interactions_df.pivot_table(
            index='student_id', 
            columns='course_id', 
            values='progress', 
            fill_value=0
        )
        
        matrix = pivot.values
        user_ids = pivot.index.tolist()
        item_ids = pivot.columns.tolist()
        
        return matrix, user_ids, item_ids
    
    def get_user_features(self) -> Optional[pd.DataFrame]:
        """Get user features for content-based filtering."""
        return self.users_df
    
    def get_course_features(self) -> Optional[pd.DataFrame]:
        """Get course features for content-based filtering."""
        return self.courses_df
    
    def save_data(self, users: pd.DataFrame = None, 
                  courses: pd.DataFrame = None, 
                  interactions: pd.DataFrame = None):
        """Save data to CSV files."""
        if users is not None:
            users.to_csv(self.data_dir / "users.csv", index=False)
            logger.info(f"Saved {len(users)} users")
        
        if courses is not None:
            courses.to_csv(self.data_dir / "courses.csv", index=False)
            logger.info(f"Saved {len(courses)} courses")
        
        if interactions is not None:
            interactions.to_csv(self.data_dir / "interactions.csv", index=False)
            logger.info(f"Saved {len(interactions)} interactions")
    
    def get_data_summary(self) -> Dict[str, Dict]:
        """Get summary statistics for all data."""
        summary = {}
        
        if self.users_df is not None:
            summary["users"] = {
                "count": len(self.users_df),
                "columns": list(self.users_df.columns)
            }
        
        if self.courses_df is not None:
            summary["courses"] = {
                "count": len(self.courses_df),
                "columns": list(self.courses_df.columns)
            }
        
        if self.interactions_df is not None:
            summary["interactions"] = {
                "count": len(self.interactions_df),
                "columns": list(self.interactions_df.columns),
                "sparsity": self._calculate_sparsity()
            }
        
        return summary
    
    def _calculate_sparsity(self) -> float:
        """Calculate sparsity of the interaction matrix."""
        if self.interactions_df is None:
            return 0.0
        
        total_possible = len(self.users_df) * len(self.courses_df) if self.users_df is not None and self.courses_df is not None else 0
        if total_possible == 0:
            return 0.0
        
        actual_interactions = len(self.interactions_df)
        return 1 - (actual_interactions / total_possible) 