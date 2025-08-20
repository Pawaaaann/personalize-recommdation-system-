"""
Baseline recommendation models for EduRec.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

from .base import BaseRecommender

logger = logging.getLogger(__name__)

def popularity_recommender(interactions_df: pd.DataFrame, top_n: int = 20) -> List[int]:
    """
    Generate course recommendations based on popularity (most interactions).
    
    Args:
        interactions_df: DataFrame with columns ['student_id', 'course_id', 'event_type', ...]
        top_n: Number of top courses to recommend
        
    Returns:
        List of course_ids sorted by popularity (most popular first)
    """
    try:
        # Count interactions per course
        course_popularity = interactions_df['course_id'].value_counts()
        
        # Get top N most popular courses
        top_courses = course_popularity.head(top_n)
        
        # Return list of course_ids
        return top_courses.index.tolist()
        
    except Exception as e:
        logger.error(f"Error in popularity recommender: {e}")
        return []

def content_based_recommender(
    courses_df: pd.DataFrame, 
    course_id: Optional[int] = None, 
    query_text: Optional[str] = None, 
    top_n: int = 20
) -> List[int]:
    """
    Generate course recommendations based on content similarity using TF-IDF and cosine similarity.
    
    Args:
        courses_df: DataFrame with columns ['course_id', 'title', 'description', 'skill_tags']
        course_id: ID of course to find similar courses for (if None, uses query_text)
        query_text: Text query to find similar courses for (if None, uses course_id)
        top_n: Number of top similar courses to recommend
        
    Returns:
        List of course_ids sorted by similarity (most similar first)
    """
    if course_id is None and query_text is None:
        raise ValueError("Either course_id or query_text must be provided")
    
    try:
        # Combine title, description, and skill_tags into a single text field
        courses_df = courses_df.copy()
        courses_df['combined_text'] = (
            courses_df['title'].fillna('') + ' ' + 
            courses_df['description'].fillna('') + ' ' + 
            courses_df['skill_tags'].fillna('')
        )
        
        # Create TF-IDF vectorizer
        tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        # Fit and transform the combined text
        tfidf_matrix = tfidf.fit_transform(courses_df['combined_text'])
        
        if course_id is not None:
            # Find similar courses based on course_id
            if course_id not in courses_df['course_id'].values:
                logger.error(f"Course ID {course_id} not found in courses dataframe")
                return []
            
            # Get the index of the target course
            target_idx = courses_df[courses_df['course_id'] == course_id].index[0]
            target_vector = tfidf_matrix[target_idx]
            
            # Calculate cosine similarity with all other courses
            similarities = cosine_similarity(target_vector, tfidf_matrix).flatten()
            
        else:
            # Find similar courses based on query_text
            # Transform the query text
            query_vector = tfidf.transform([query_text])
            
            # Calculate cosine similarity with all courses
            similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
        
        # Get indices of top similar courses (excluding the target course if using course_id)
        if course_id is not None:
            # Exclude the target course from recommendations
            similarities[target_idx] = -1
        
        # Get top N similar courses
        top_indices = np.argsort(similarities)[::-1][:top_n]
        
        # Return list of course_ids
        recommended_course_ids = courses_df.iloc[top_indices]['course_id'].tolist()
        
        return recommended_course_ids
        
    except Exception as e:
        logger.error(f"Error in content-based recommender: {e}")
        return []

def get_course_popularity_stats(interactions_df: pd.DataFrame) -> pd.Series:
    """
    Get popularity statistics for all courses.
    
    Args:
        interactions_df: DataFrame with interaction data
        
    Returns:
        Series with course_id as index and interaction count as values
    """
    popularity_stats = interactions_df['course_id'].value_counts()
    popularity_stats.index.name = None  # Remove the index name
    return popularity_stats

def get_course_similarity_matrix(courses_df: pd.DataFrame) -> np.ndarray:
    """
    Get the full similarity matrix for all courses.
    
    Args:
        courses_df: DataFrame with course data
        
    Returns:
        NxN similarity matrix where N is the number of courses
    """
    try:
        # Combine text fields
        courses_df = courses_df.copy()
        courses_df['combined_text'] = (
            courses_df['title'].fillna('') + ' ' + 
            courses_df['description'].fillna('') + ' ' + 
            courses_df['skill_tags'].fillna('')
        )
        
        # Create TF-IDF vectors
        tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8
        )
        
        tfidf_matrix = tfidf.fit_transform(courses_df['combined_text'])
        
        # Calculate full similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Ensure values are properly bounded between -1 and 1
        # Cosine similarity should already be in this range, but let's clip to be safe
        similarity_matrix = np.clip(similarity_matrix, -1.0, 1.0)
        
        return similarity_matrix
        
    except Exception as e:
        logger.error(f"Error creating similarity matrix: {e}")
        return np.array([]) 

class BaselineRecommender(BaseRecommender):
    """Baseline recommender that combines popularity and content-based approaches."""
    
    def __init__(self, strategy: str = "popularity"):
        """
        Initialize the baseline recommender.
        
        Args:
            strategy: Strategy to use ('popularity', 'content_based', or 'hybrid')
        """
        super().__init__(name=f"BaselineRecommender_{strategy}")
        self.strategy = strategy
        self.interactions_df = None
        self.courses_df = None
        self.users_df = None
        self.course_popularity = None
        self.course_similarity_matrix = None
        self.tfidf_vectorizer = None
        
    def fit(self, interactions_df: pd.DataFrame, courses_df: pd.DataFrame = None,
            users_df: pd.DataFrame = None, **kwargs) -> 'BaselineRecommender':
        """
        Fit the baseline recommender.
        
        Args:
            interactions_df: DataFrame with user-item interactions
            courses_df: DataFrame with course information
            users_df: DataFrame with user information
            **kwargs: Additional fitting parameters
            
        Returns:
            Self for method chaining
        """
        logger.info(f"Fitting baseline recommender with strategy: {self.strategy}")
        
        self.interactions_df = interactions_df.copy()
        self.courses_df = courses_df.copy() if courses_df is not None else None
        self.users_df = users_df.copy() if users_df is not None else None
        
        # Fit popularity-based components
        if self.strategy in ["popularity", "hybrid"]:
            self.course_popularity = get_course_popularity_stats(interactions_df)
        
        # Fit content-based components
        if self.strategy in ["content_based", "hybrid"] and self.courses_df is not None:
            self.course_similarity_matrix = get_course_similarity_matrix(self.courses_df)
            
            # Create TF-IDF vectorizer for content-based recommendations
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.8
            )
            
            # Combine text fields for TF-IDF
            combined_text = (
                self.courses_df['title'].fillna('') + ' ' + 
                self.courses_df['description'].fillna('') + ' ' + 
                self.courses_df['skill_tags'].fillna('')
            )
            self.tfidf_vectorizer.fit(combined_text)
        
        self.is_fitted = True
        return self
    
    def recommend(self, user_id: str, n_recommendations: int = 10, 
                  user_interests: Optional[List[str]] = None, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate recommendations for a user.
        
        Args:
            user_id: ID of the user to recommend for
            n_recommendations: Number of recommendations to generate
            user_interests: Optional list of user interests for content-based filtering
            **kwargs: Additional recommendation parameters
            
        Returns:
            List of recommendation dictionaries
        """
        self._check_is_fitted()
        
        if self.strategy == "popularity":
            recommendations = popularity_recommender(self.interactions_df, n_recommendations)
            scores = [1.0 - (i / len(recommendations)) for i in range(len(recommendations))]
            
        elif self.strategy == "content_based":
            if user_interests:
                query_text = " ".join(user_interests)
                recommendations = content_based_recommender(
                    self.courses_df, query_text=query_text, top_n=n_recommendations
                )
            else:
                # Use a default course for content-based recommendations
                default_course_id = self.courses_df['course_id'].iloc[0]
                recommendations = content_based_recommender(
                    self.courses_df, course_id=default_course_id, top_n=n_recommendations
                )
            scores = [1.0 - (i / len(recommendations)) for i in range(len(recommendations))]
            
        elif self.strategy == "hybrid":
            # Combine popularity and content-based approaches
            pop_recs = popularity_recommender(self.interactions_df, n_recommendations // 2)
            content_recs = content_based_recommender(
                self.courses_df, course_id=self.courses_df['course_id'].iloc[0], 
                top_n=n_recommendations // 2
            )
            
            # Combine and deduplicate
            all_recs = list(dict.fromkeys(pop_recs + content_recs))[:n_recommendations]
            recommendations = all_recs
            scores = [1.0 - (i / len(recommendations)) for i in range(len(recommendations))]
        
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        # Format recommendations
        return self._format_recommendations(recommendations, scores)
    
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
        
        # For baseline recommender, return popularity-based score
        if self.course_popularity is not None and item_id in self.course_popularity.index:
            # Normalize popularity score to 1-5 scale
            max_popularity = self.course_popularity.max()
            normalized_score = self.course_popularity[item_id] / max_popularity
            return 1.0 + (normalized_score * 4.0)  # Scale to 1-5
        
        return 3.0  # Default neutral rating
    
    def get_similar_items(self, item_id: str, n_similar: int = 10) -> List[Dict[str, Any]]:
        """
        Get similar items to a given item.
        
        Args:
            item_id: ID of the item to find similar items for
            n_similar: Number of similar items to return
            
        Returns:
            List of similar item dictionaries
        """
        self._check_is_fitted()
        
        if self.course_similarity_matrix is None:
            return []
        
        try:
            # Find the index of the target item
            item_idx = self.courses_df[self.courses_df['course_id'] == item_id].index[0]
            
            # Get similarities for this item
            similarities = self.course_similarity_matrix[item_idx]
            
            # Get top similar items (excluding self)
            similarities[item_idx] = -1  # Exclude self
            top_indices = np.argsort(similarities)[::-1][:n_similar]
            
            # Format results
            similar_items = []
            for i, idx in enumerate(top_indices):
                if similarities[idx] > 0:  # Only include positive similarities
                    course_id = self.courses_df.iloc[idx]['course_id']
                    similar_items.append({
                        "item_id": course_id,
                        "similarity_score": float(similarities[idx]),
                        "rank": i + 1
                    })
            
            return similar_items
            
        except (IndexError, KeyError):
            logger.warning(f"Item {item_id} not found in courses data")
            return [] 