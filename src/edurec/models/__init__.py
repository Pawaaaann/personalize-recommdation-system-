"""
Recommendation models for EduRec.
"""
from .base import BaseRecommender
from .baseline import (
    BaselineRecommender,
    popularity_recommender,
    content_based_recommender,
    get_course_popularity_stats,
    get_course_similarity_matrix
)
# from .als_recommender import ALSRecommender
# from .hybrid import HybridRecommender

__all__ = [
    "BaseRecommender",
    "BaselineRecommender",
    "popularity_recommender",
    "content_based_recommender", 
    "get_course_popularity_stats",
    "get_course_similarity_matrix",
    # "ALSRecommender",
    # "HybridRecommender"
] 