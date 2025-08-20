"""
ALS (Alternating Least Squares) recommender using implicit library.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix
import logging
import pickle
from pathlib import Path

from .base import BaseRecommender

logger = logging.getLogger(__name__)


class ALSRecommender(BaseRecommender):
    """Alternating Least Squares recommender for collaborative filtering."""
    
    def __init__(self, factors: int = 64, regularization: float = 0.01, 
                 iterations: int = 20, alpha: float = 40.0):
        """
        Initialize the ALS recommender.
        
        Args:
            factors: Number of latent factors (default: 64)
            regularization: Regularization parameter (default: 0.01)
            iterations: Number of iterations for training (default: 20)
            alpha: Confidence parameter for implicit feedback (default: 40.0)
        """
        super().__init__(name="ALSRecommender")
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.alpha = alpha
        
        # Model components
        self.model = None
        self.user_factors = None
        self.item_factors = None
        
        # Data mappings
        self.user_id_to_index = {}
        self.item_id_to_index = {}
        self.index_to_user_id = {}
        self.index_to_item_id = {}
        
        # Interaction matrix
        self.interaction_matrix = None
        
        # Confidence weights for different interaction types
        self.interaction_weights = {
            'view': 1,
            'enroll': 3,
            'complete': 5,
            'rating': 4,
            'quiz_attempt': 2,
            'default': 1
        }
        
    def fit(self, interactions_df: pd.DataFrame, **kwargs) -> 'ALSRecommender':
        """
        Fit the ALS model.
        
        Args:
            interactions_df: DataFrame with user-item interactions
            **kwargs: Additional fitting parameters
            
        Returns:
            Self for method chaining
        """
        logger.info("Fitting ALS model...")
        
        # Create user-item matrix with confidence weighting
        self._create_interaction_matrix(interactions_df)
        
        # Initialize and fit the model
        self.model = AlternatingLeastSquares(
            factors=self.factors,
            regularization=self.regularization,
            iterations=self.iterations,
            random_state=42
        )
        
        # Fit the model
        self.model.fit(self.interaction_matrix.T)  # Note: implicit expects items x users
        
        # Store the learned factors
        # Note: implicit returns user_factors and item_factors in the order they were fitted
        # Since we fitted with items x users, user_factors corresponds to items and item_factors to users
        # We need to swap them back to match our original matrix dimensions
        self.item_factors = self.model.user_factors  # This is actually item factors
        self.user_factors = self.model.item_factors  # This is actually user factors
        
        self.is_fitted = True
        logger.info("ALS model fitting complete!")
        
        return self
    
    def _create_interaction_matrix(self, interactions_df: pd.DataFrame):
        """Create sparse interaction matrix with confidence weighting and ID mappings."""
        # Create user and item ID mappings
        unique_users = sorted(interactions_df['student_id'].unique())
        unique_items = sorted(interactions_df['course_id'].unique())
        
        self.user_id_to_index = {user_id: idx for idx, user_id in enumerate(unique_users)}
        self.item_id_to_index = {item_id: idx for idx, item_id in enumerate(unique_items)}
        self.index_to_user_id = {idx: user_id for user_id, idx in self.user_id_to_index.items()}
        self.index_to_item_id = {idx: item_id for item_id, idx in self.item_id_to_index.items()}
        
        # Create sparse matrix with confidence weighting
        rows = [self.user_id_to_index[user_id] for user_id in interactions_df['student_id']]
        cols = [self.item_id_to_index[item_id] for item_id in interactions_df['course_id']]
        
        # Apply confidence weighting based on interaction type
        data = []
        for _, row in interactions_df.iterrows():
            # Get interaction type and apply weight
            interaction_type = row.get('event_type', 'default')
            base_weight = self.interaction_weights.get(interaction_type, self.interaction_weights['default'])
            
            # If rating exists, use it to modulate the weight
            if 'rating' in row and pd.notna(row['rating']):
                rating_weight = row['rating'] / 5.0  # Normalize rating to 0-1
                final_weight = base_weight * rating_weight
            else:
                final_weight = base_weight
            
            data.append(final_weight)
        
        # Apply alpha scaling for implicit feedback
        data = np.array(data) * self.alpha
        
        self.interaction_matrix = csr_matrix(
            (data, (rows, cols)), 
            shape=(len(unique_users), len(unique_items))
        )
        
        logger.info(f"Created interaction matrix: {self.interaction_matrix.shape}")
        logger.info(f"Applied confidence weighting: {self.interaction_weights}")
    
    def recommend(self, user_id: str, n_recommendations: int = 10, 
                  filter_interacted: bool = True, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a user.
        
        Args:
            user_id: ID of the user to recommend for
            n_recommendations: Number of recommendations to generate
            filter_interacted: Whether to filter out already interacted items
            **kwargs: Additional recommendation parameters
            
        Returns:
            List of recommendation dictionaries
        """
        self._check_is_fitted()
        
        if user_id not in self.user_id_to_index:
            logger.warning(f"User {user_id} not found in training data")
            return []
        
        user_idx = self.user_id_to_index[user_id]
        
        # Get recommendations from the model
        item_scores = self.model.recommend(
            user_idx, 
            self.interaction_matrix[user_idx], 
            N=n_recommendations + 100  # Get more to account for filtering
        )
        
        # Convert to list of (item_idx, score) tuples
        item_scores = list(zip(item_scores[0], item_scores[1]))
        
        # Filter out already interacted items if requested
        if filter_interacted:
            user_interactions = self.interaction_matrix[user_idx].nonzero()[1]
            item_scores = [(idx, score) for idx, score in item_scores if idx not in user_interactions]
        
        # Take top recommendations
        top_item_scores = item_scores[:n_recommendations]
        
        # Format recommendations
        recommendations = []
        for i, (item_idx, score) in enumerate(top_item_scores):
            # Check if item_idx is within bounds
            if item_idx not in self.index_to_item_id:
                logger.warning(f"Item index {item_idx} out of bounds, skipping")
                continue
                
            item_id = self.index_to_item_id[item_idx]
            
            rec = {
                "item_id": item_id,
                "score": float(score),
                "rank": i + 1,
                "model": "ALS"
            }
            
            recommendations.append(rec)
        
        return recommendations
    
    def similar_items(self, item_id: str, n_similar: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar items to a given item.
        
        Args:
            item_id: ID of the item to find similar items for
            n_similar: Number of similar items to return (default: 5)
            
        Returns:
            List of similar item dictionaries
        """
        return self.get_similar_items(item_id, n_similar)
    
    def save(self, path: str) -> None:
        """
        Save the trained model to disk.
        
        Args:
            path: Path to save the model
        """
        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted model")
        
        # Create directory if it doesn't exist
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare data for saving
        save_data = {
            'model': self.model,
            'user_factors': self.user_factors,
            'item_factors': self.item_factors,
            'user_id_to_index': self.user_id_to_index,
            'item_id_to_index': self.item_id_to_index,
            'index_to_user_id': self.index_to_user_id,
            'index_to_item_id': self.index_to_item_id,
            'interaction_matrix': self.interaction_matrix,
            'factors': self.factors,
            'regularization': self.regularization,
            'iterations': self.iterations,
            'alpha': self.alpha,
            'interaction_weights': self.interaction_weights
        }
        
        with open(path, 'wb') as f:
            pickle.dump(save_data, f)
        
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str) -> 'ALSRecommender':
        """
        Load a trained model from disk.
        
        Args:
            path: Path to load the model from
            
        Returns:
            Self for method chaining
        """
        with open(path, 'rb') as f:
            save_data = pickle.load(f)
        
        # Restore model components
        self.model = save_data['model']
        self.user_factors = save_data['user_factors']
        self.item_factors = save_data['item_factors']
        self.user_id_to_index = save_data['user_id_to_index']
        self.item_id_to_index = save_data['item_id_to_index']
        self.index_to_user_id = save_data['index_to_user_id']
        self.index_to_item_id = save_data['index_to_item_id']
        self.interaction_matrix = save_data['interaction_matrix']
        self.factors = save_data['factors']
        self.regularization = save_data['regularization']
        self.iterations = save_data['iterations']
        self.alpha = save_data['alpha']
        self.interaction_weights = save_data['interaction_weights']
        
        self.is_fitted = True
        logger.info(f"Model loaded from {path}")
        
        return self
    
    def predict_rating(self, user_id: str, item_id: str) -> float:
        """
        Predict rating for a user-item pair.
        
        Args:
            user_id: ID of the user
            item_id: ID of the item
            
        Returns:
            Predicted rating
        """
        self._check_is_fitted()
        
        if (user_id not in self.user_id_to_index or 
            item_id not in self.item_id_to_index):
            return 0.0
        
        user_idx = self.user_id_to_index[user_id]
        item_idx = self.item_id_to_index[item_id]
        
        # Get user and item factors
        user_factors = self.user_factors[user_idx]
        item_factors = self.item_factors[item_idx]
        
        # Calculate dot product
        predicted_score = np.dot(user_factors, item_factors)
        
        # Convert to rating scale (1-5)
        # This is a rough conversion - you might want to tune this
        predicted_rating = max(1.0, min(5.0, predicted_score / 10 + 3.0))
        
        return float(predicted_rating)
    
    def get_similar_items(self, item_id: str, n_similar: int = 10) -> List[Dict[str, Any]]:
        """
        Find similar items to a given item.
        
        Args:
            item_id: ID of the item to find similar items for
            n_similar: Number of similar items to return
            
        Returns:
            List of similar item dictionaries
        """
        self._check_is_fitted()
        
        if item_id not in self.item_id_to_index:
            return []
        
        item_idx = self.item_id_to_index[item_id]
        
        # Get similar items from the model
        similar_items = self.model.similar_items(item_idx, n_similar + 1)
        
        # Handle different return formats from implicit library
        if isinstance(similar_items, tuple) and len(similar_items) == 2:
            # Format: (indices, scores)
            indices, scores = similar_items
            similar_items = list(zip(indices, scores))
        elif isinstance(similar_items, list):
            # Format: list of (index, score) tuples
            pass
        else:
            # Unknown format, return empty list
            logger.warning(f"Unknown similar_items format: {type(similar_items)}")
            return []
        
        # Format results (skip the first item as it's the same item)
        similar_items = similar_items[1:]
        
        recommendations = []
        for i, (similar_idx, score) in enumerate(similar_items):
            # Check if similar_idx is within bounds
            if similar_idx not in self.index_to_item_id:
                logger.warning(f"Similar item index {similar_idx} out of bounds, skipping")
                continue
                
            similar_item_id = self.index_to_item_id[similar_idx]
            
            rec = {
                "item_id": similar_item_id,
                "similarity_score": float(score),
                "rank": i + 1,
                "reference_item": item_id
            }
            
            recommendations.append(rec)
        
        return recommendations
    
    def get_user_embeddings(self, user_id: str) -> np.ndarray:
        """
        Get user embedding vector.
        
        Args:
            user_id: ID of the user
            
        Returns:
            User embedding vector
        """
        self._check_is_fitted()
        
        if user_id not in self.user_id_to_index:
            raise ValueError(f"User {user_id} not found in training data")
        
        user_idx = self.user_id_to_index[user_id]
        return self.user_factors[user_idx].copy()
    
    def get_item_embeddings(self, item_id: str) -> np.ndarray:
        """
        Get item embedding vector.
        
        Args:
            item_id: ID of the item
            
        Returns:
            Item embedding vector
        """
        self._check_is_fitted()
        
        if item_id not in self.item_id_to_index:
            raise ValueError(f"Item {item_id} not found in training data")
        
        item_idx = self.item_id_to_index[item_id]
        return self.item_factors[item_idx].copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the fitted model."""
        info = super().get_model_info()
        info.update({
            "factors": self.factors,
            "regularization": self.regularization,
            "iterations": self.iterations,
            "alpha": self.alpha,
            "n_users": len(self.user_id_to_index),
            "n_items": len(self.item_id_to_index),
            "matrix_shape": self.interaction_matrix.shape if self.interaction_matrix is not None else None,
            "sparsity": self._calculate_sparsity()
        })
        return info
    
    def _calculate_sparsity(self) -> float:
        """Calculate sparsity of the interaction matrix."""
        if self.interaction_matrix is None:
            return 0.0
        
        total_elements = self.interaction_matrix.shape[0] * self.interaction_matrix.shape[1]
        non_zero_elements = self.interaction_matrix.nnz
        
        return 1 - (non_zero_elements / total_elements) 