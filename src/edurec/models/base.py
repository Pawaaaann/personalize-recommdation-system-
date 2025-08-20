"""
Base recommender interface for EduRec.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


class BaseRecommender(ABC):
    """Abstract base class for all recommendation models."""
    
    def __init__(self, name: str = "BaseRecommender"):
        """
        Initialize the base recommender.
        
        Args:
            name: Name of the recommender
        """
        self.name = name
        self.is_fitted = False
        
    @abstractmethod
    def fit(self, interactions_df: pd.DataFrame, **kwargs) -> 'BaseRecommender':
        """
        Fit the recommendation model.
        
        Args:
            interactions_df: DataFrame with user-item interactions
            **kwargs: Additional fitting parameters
            
        Returns:
            Self for method chaining
        """
        pass
    
    @abstractmethod
    def recommend(self, user_id: str, n_recommendations: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a user.
        
        Args:
            user_id: ID of the user to recommend for
            n_recommendations: Number of recommendations to generate
            **kwargs: Additional recommendation parameters
            
        Returns:
            List of recommendation dictionaries
        """
        pass
    
    @abstractmethod
    def predict_rating(self, user_id: str, item_id: str) -> float:
        """
        Predict rating for a user-item pair.
        
        Args:
            user_id: ID of the user
            item_id: ID of the item
            
        Returns:
            Predicted rating
        """
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the fitted model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "name": self.name,
            "is_fitted": self.is_fitted,
            "type": self.__class__.__name__
        }
    
    def validate_user_id(self, user_id: str, available_users: List[str]) -> bool:
        """
        Validate if a user ID exists in the available users.
        
        Args:
            user_id: User ID to validate
            available_users: List of available user IDs
            
        Returns:
            True if user ID is valid, False otherwise
        """
        return user_id in available_users
    
    def validate_item_id(self, item_id: str, available_items: List[str]) -> bool:
        """
        Validate if an item ID exists in the available items.
        
        Args:
            item_id: Item ID to validate
            available_items: List of available item IDs
            
        Returns:
            True if item ID is valid, False otherwise
        """
        return item_id in available_items
    
    def _check_is_fitted(self):
        """Check if the model has been fitted."""
        if not self.is_fitted:
            raise RuntimeError(f"{self.name} must be fitted before making predictions")
    
    def _format_recommendations(self, item_ids: List[str], scores: List[float], 
                               metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Format recommendations into a standard format.
        
        Args:
            item_ids: List of recommended item IDs
            scores: List of recommendation scores
            metadata: Optional metadata for items
            
        Returns:
            List of formatted recommendation dictionaries
        """
        recommendations = []
        for i, (item_id, score) in enumerate(zip(item_ids, scores)):
            rec = {
                "item_id": item_id,
                "score": float(score),
                "rank": i + 1
            }
            
            if metadata and item_id in metadata:
                rec.update(metadata[item_id])
            
            recommendations.append(rec)
        
        return recommendations 