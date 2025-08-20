"""
Hybrid recommender system that combines multiple recommendation approaches.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging
from collections import defaultdict
import time

from .base import BaseRecommender
from .als_recommender import ALSRecommender
from .baseline import BaselineRecommender
from ..monitoring.metrics import get_metrics_collector
from ..monitoring.ab_testing import get_ab_test_manager, ExperimentConfig
from datetime import datetime

logger = logging.getLogger(__name__)


class HybridRecommender(BaseRecommender):
    """Hybrid recommender that combines multiple recommendation strategies."""
    
    def __init__(self, 
                 als_model: Optional[ALSRecommender] = None,
                 baseline_model: Optional[BaselineRecommender] = None,
                 default_weights: Optional[Dict[str, float]] = None,
                 enable_ab_testing: bool = True):
        """
        Initialize the hybrid recommender.
        
        Args:
            als_model: Pre-trained ALS model
            baseline_model: Pre-trained baseline model (for content-based and popularity)
            default_weights: Default weights for combining recommendations
            enable_ab_testing: Whether to enable A/B testing capabilities
        """
        super().__init__(name="HybridRecommender")
        
        self.als_model = als_model
        self.baseline_model = baseline_model
        self.enable_ab_testing = enable_ab_testing
        
        # Default weights for combining different approaches
        self.default_weights = default_weights or {
            "als": 0.7,
            "content": 0.2,
            "pop": 0.1
        }
        
        # Normalize weights to sum to 1
        total_weight = sum(self.default_weights.values())
        if total_weight > 0:
            self.default_weights = {k: round(v / total_weight, 10) for k, v in self.default_weights.items()}
        
        # Data for explanations
        self.courses_df = None
        self.interactions_df = None
        
        # Explanation templates
        self.explanation_templates = {
            "als": "similar_users_enrolled",
            "content": "skill_match",
            "pop": "popular"
        }
        
        # Initialize monitoring
        self.metrics_collector = get_metrics_collector()
        self.ab_test_manager = get_ab_test_manager() if enable_ab_testing else None
        
        # A/B testing experiment configurations
        self.experiments = {
            "new_algorithm_v1": {
                "name": "new_algorithm_v1",
                "description": "Testing new hybrid algorithm with adjusted weights",
                "traffic_split": {"control": 0.9, "treatment": 0.1},
                "treatment_weights": {
                    "als": 0.6,
                    "content": 0.3,
                    "pop": 0.1
                }
            },
            "content_boost": {
                "name": "content_boost",
                "description": "Testing increased content-based filtering weight",
                "traffic_split": {"control": 0.9, "treatment": 0.1},
                "treatment_weights": {
                    "als": 0.5,
                    "content": 0.4,
                    "pop": 0.1
                }
            }
        }
        
        # Initialize experiments if A/B testing is enabled
        if self.enable_ab_testing and self.ab_test_manager:
            self._initialize_experiments()
    
    def _initialize_experiments(self):
        """Initialize A/B testing experiments."""
        try:
            for exp_name, exp_config in self.experiments.items():
                config = ExperimentConfig(
                    name=exp_config["name"],
                    description=exp_config["description"],
                    variants=["control", "treatment"],
                    traffic_split=exp_config["traffic_split"],
                    start_date=datetime.now(),
                    is_active=True
                )
                self.ab_test_manager.create_experiment(config)
                logger.info(f"Initialized A/B test experiment: {exp_name}")
        except Exception as e:
            logger.error(f"Failed to initialize experiments: {e}")
    
    def set_data(self, courses_df: pd.DataFrame, interactions_df: pd.DataFrame):
        """Set data for explanation generation."""
        self.courses_df = courses_df.copy() if courses_df is not None else None
        self.interactions_df = interactions_df.copy() if interactions_df is not None else None
    
    def hybrid_recommend(self, 
                        user_id: str, 
                        N: int = 10, 
                        weights: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Generate hybrid recommendations combining multiple approaches.
        
        Args:
            user_id: ID of the user to recommend for
            N: Number of recommendations to generate
            weights: Weights for combining different approaches
            
        Returns:
            List of recommendation dictionaries with explanations
        """
        start_time = time.time()
        
        # A/B testing: Get user variant and adjust weights
        experiment_name = "new_algorithm_v1"  # Default experiment
        variant = "control"
        
        if self.enable_ab_testing and self.ab_test_manager:
            variant = self.ab_test_manager.get_user_variant(user_id, experiment_name)
            
            # Use treatment weights if user is in treatment group
            if variant == "treatment" and experiment_name in self.experiments:
                treatment_weights = self.experiments[experiment_name]["treatment_weights"]
                weights = treatment_weights.copy()
                logger.info(f"User {user_id} assigned to {variant} group, using treatment weights: {weights}")
        
        if weights is None:
            weights = self.default_weights.copy()
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: round(v / total_weight, 10) for k, v in weights.items()}
        
        logger.info(f"Generating hybrid recommendations for user {user_id} with weights: {weights} (variant: {variant})")
        
        # Get recommendations from different approaches
        recommendations = {}
        
        # ALS recommendations
        if self.als_model and self.als_model.is_fitted and "als" in weights:
            try:
                als_recs = self.als_model.recommend(user_id, n_recommendations=N * 2)
                if als_recs:
                    recommendations["als"] = als_recs
                    logger.debug(f"ALS recommendations: {len(als_recs)} items")
            except Exception as e:
                logger.warning(f"Failed to get ALS recommendations: {e}")
                recommendations["als"] = []
        
        # Content-based recommendations
        if self.baseline_model and self.baseline_model.is_fitted and "content" in weights:
            try:
                # Get user's enrolled courses for content-based recommendations
                user_courses = self._get_user_courses(user_id)
                if user_courses:
                    # Use the first enrolled course as reference
                    reference_course = user_courses[0]
                    content_recs = self.baseline_model.get_similar_items(reference_course, n_similar=N * 2)
                    if content_recs:
                        recommendations["content"] = content_recs
                        logger.debug(f"Content-based recommendations: {len(content_recs)} items")
                else:
                    # If no enrolled courses, use popularity as fallback
                    content_recs = self.baseline_model.recommend(user_id, n_recommendations=N * 2)
                    if content_recs:
                        recommendations["content"] = content_recs
                        logger.debug(f"Content-based fallback (popularity): {len(content_recs)} items")
            except Exception as e:
                logger.warning(f"Failed to get content-based recommendations: {e}")
                recommendations["content"] = []
        
        # Popularity-based recommendations
        if self.baseline_model and self.baseline_model.is_fitted and "pop" in weights:
            try:
                pop_recs = self.baseline_model.recommend(user_id, n_recommendations=N * 2)
                if pop_recs:
                    recommendations["pop"] = pop_recs
                    logger.debug(f"Popularity recommendations: {len(pop_recs)} items")
            except Exception as e:
                logger.warning(f"Failed to get popularity recommendations: {e}")
                recommendations["pop"] = []
        
        # If no recommendations from any model, create fallback recommendations
        if not any(recommendations.values()):
            logger.info("No models available, creating fallback recommendations")
            fallback_recs = self._create_fallback_recommendations(user_id, N)
            recommendations["fallback"] = fallback_recs
        
        # Combine recommendations
        combined_scores = self._combine_recommendations(recommendations, weights)
        
        # Get top-N recommendations
        top_recommendations = self._get_top_recommendations(combined_scores, N)
        
        # Generate explanations
        final_recommendations = self._add_explanations(top_recommendations, recommendations, weights)
        
        # Record metrics
        end_time = time.time()
        duration = end_time - start_time
        
        # Record recommendation metrics
        self.metrics_collector.record_recommendation(
            algorithm=f"hybrid_{variant}",
            user_id=user_id,
            count=len(final_recommendations)
        )
        
        # Record recommendation scores
        for rec in final_recommendations:
            self.metrics_collector.record_recommendation_score(
                algorithm=f"hybrid_{variant}",
                score=rec.get("score", 0.0)
            )
        
        # Record model prediction time
        self.metrics_collector.record_model_prediction_time(
            model_name=f"hybrid_{variant}",
            duration=duration
        )
        
        logger.info(f"Generated {len(final_recommendations)} hybrid recommendations for {variant} variant in {duration:.3f}s")
        return final_recommendations
    
    def record_conversion(self, user_id: str, conversion_type: str, experiment_name: str = "new_algorithm_v1"):
        """
        Record a conversion event for A/B testing.
        
        Args:
            user_id: User identifier
            conversion_type: Type of conversion (e.g., "enroll", "complete")
            experiment_name: Name of the experiment
        """
        if self.enable_ab_testing and self.ab_test_manager:
            self.ab_test_manager.record_conversion(user_id, experiment_name, conversion_type)
            logger.info(f"Recorded conversion: {user_id} -> {conversion_type} for experiment {experiment_name}")
    
    def get_experiment_stats(self, experiment_name: str = "new_algorithm_v1") -> Dict[str, Any]:
        """
        Get statistics for an A/B test experiment.
        
        Args:
            experiment_name: Name of the experiment
            
        Returns:
            Dictionary with experiment statistics
        """
        if self.enable_ab_testing and self.ab_test_manager:
            return self.ab_test_manager.get_experiment_stats(experiment_name)
        return {}
    
    def _get_user_courses(self, user_id: str) -> List[str]:
        """Get courses that the user has enrolled in."""
        if self.interactions_df is None:
            return []
        
        user_interactions = self.interactions_df[
            (self.interactions_df['student_id'] == user_id) & 
            (self.interactions_df['event_type'].isin(['enroll', 'complete']))
        ]
        
        return user_interactions['course_id'].unique().tolist()
    
    def _combine_recommendations(self, 
                                recommendations: Dict[str, List], 
                                weights: Dict[str, float]) -> Dict[str, float]:
        """Combine scores from different recommendation approaches."""
        combined_scores = defaultdict(float)
        
        for approach, recs in recommendations.items():
            if not recs:  # Skip empty recommendation lists
                continue
            
            # For fallback recommendations, use a default weight if not in weights
            if approach == "fallback":
                weight = weights.get(approach, 1.0)  # Default weight for fallback
            elif approach not in weights:
                continue
            else:
                weight = weights[approach]
            
            for rec in recs:
                item_id = rec.get('item_id')
                if not item_id:
                    continue
                
                # Get score based on approach
                if approach == "als":
                    score = rec.get('score', 0.0)
                elif approach == "content":
                    score = rec.get('similarity_score', 0.0)
                elif approach == "fallback":
                    score = rec.get('score', 0.0)
                else:  # popularity
                    score = rec.get('score', 0.0)
                
                # Normalize score to 0-1 range and apply weight
                normalized_score = self._normalize_score(score, approach)
                combined_scores[item_id] += normalized_score * weight
        
        return dict(combined_scores)
    
    def _normalize_score(self, score: float, approach: str) -> float:
        """Normalize scores to 0-1 range based on approach."""
        if approach == "als":
            # ALS scores can be negative, normalize to 0-1
            return max(0.0, min(1.0, (score + 1) / 2))
        elif approach == "content":
            # Content similarity scores are typically 0-1
            return max(0.0, min(1.0, score))
        else:  # popularity
            # Popularity scores are typically 0-1
            return max(0.0, min(1.0, score))
    
    def _get_top_recommendations(self, combined_scores: Dict[str, float], N: int) -> List[Tuple[str, float]]:
        """Get top-N recommendations based on combined scores."""
        # Sort by score (descending) and take top N
        sorted_items = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:N]
    
    def _add_explanations(self, 
                          top_recommendations: List[Tuple[str, float]], 
                          recommendations: Dict[str, List], 
                          weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Add explanations to recommendations."""
        final_recommendations = []
        
        for rank, (item_id, combined_score) in enumerate(top_recommendations, 1):
            # Generate explanations
            explanations = self._generate_explanations(item_id, recommendations, weights)
            
            # Get top 2 reasons
            top_reasons = explanations[:2] if len(explanations) >= 2 else explanations
            
            recommendation = {
                "item_id": item_id,
                "score": float(combined_score),
                "rank": rank,
                "model": "Hybrid",
                "explanations": top_reasons,
                "all_explanations": explanations
            }
            
            final_recommendations.append(recommendation)
        
        return final_recommendations
    
    def _generate_explanations(self, 
                              item_id: str, 
                              recommendations: Dict[str, List], 
                              weights: Dict[str, float]) -> List[str]:
        """Generate explanations for a recommendation."""
        explanations = []
        
        # Check ALS explanations
        if "als" in recommendations and weights.get("als", 0) > 0:
            als_recs = recommendations["als"]
            als_item = next((rec for rec in als_recs if rec.get('item_id') == item_id), None)
            if als_item:
                explanations.append("similar_users_enrolled")
        
        # Check content-based explanations
        if "content" in recommendations and weights.get("content", 0) > 0:
            content_recs = recommendations["content"]
            content_item = next((rec for rec in content_recs if rec.get('item_id') == item_id), None)
            if content_item:
                # Get skill match explanation
                skill_explanation = self._get_skill_match_explanation(item_id)
                if skill_explanation:
                    explanations.append(f"skill_match: {skill_explanation}")
                else:
                    explanations.append("similar_course_content")
        
        # Check popularity explanations
        if "pop" in recommendations and weights.get("pop", 0) > 0:
            pop_recs = recommendations["pop"]
            pop_item = next((rec for rec in pop_recs if rec.get('item_id') == item_id), None)
            if pop_item:
                explanations.append("popular")
        
        # Check fallback explanations
        if "fallback" in recommendations and weights.get("fallback", 0) > 0:
            fallback_recs = recommendations["fallback"]
            fallback_item = next((rec for rec in fallback_recs if rec.get('item_id') == item_id), None)
            if fallback_item:
                explanations.append("recommended_for_you")
        
        # Add fallback explanations if none generated
        if not explanations:
            if self.courses_df is not None:
                # Try to get course info for explanation
                course_info = self._get_course_info(item_id)
                if course_info:
                    explanations.append(f"course_match: {course_info}")
                else:
                    explanations.append("recommended_for_you")
            else:
                explanations.append("recommended_for_you")
        
        return explanations
    
    def _get_skill_match_explanation(self, item_id: str) -> Optional[str]:
        """Get skill match explanation for a course."""
        if self.courses_df is None:
            return None
        
        course_row = self.courses_df[self.courses_df['course_id'] == item_id]
        if course_row.empty:
            return None
        
        # Extract skill tags or course title
        skill_tags = course_row.iloc[0].get('skill_tags', '')
        title = course_row.iloc[0].get('title', '')
        
        if pd.notna(skill_tags) and skill_tags:
            # Take first skill tag
            skills = str(skill_tags).split(',')
            if skills:
                return skills[0].strip()
        
        if pd.notna(title) and title:
            # Extract key terms from title
            words = str(title).split()
            if words:
                return words[0].lower()
        
        return None
    
    def _get_course_info(self, item_id: str) -> Optional[str]:
        """Get course information for explanation."""
        if self.courses_df is None:
            return None
        
        course_row = self.courses_df[self.courses_df['course_id'] == item_id]
        if course_row.empty:
            return None
        
        # Get course title or category
        title = course_row.iloc[0].get('title', '')
        category = course_row.iloc[0].get('category', '')
        
        if pd.notna(title) and title:
            return str(title)[:30] + "..." if len(str(title)) > 30 else str(title)
        elif pd.notna(category) and category:
            return str(category)
        
        return None
    
    def get_explanation_summary(self, user_id: str, N: int = 10, weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Get a summary of explanations for recommendations."""
        recommendations = self.hybrid_recommend(user_id, N, weights)
        
        # Count explanation types
        explanation_counts = defaultdict(int)
        for rec in recommendations:
            for explanation in rec.get('explanations', []):
                explanation_counts[explanation] += 1
        
        # Get top explanations
        top_explanations = sorted(explanation_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "user_id": user_id,
            "total_recommendations": len(recommendations),
            "explanation_summary": dict(top_explanations),
            "top_explanations": [exp for exp, count in top_explanations[:5]]
        }
    
    def fit(self, interactions_df: pd.DataFrame, courses_df: pd.DataFrame = None, 
            users_df: pd.DataFrame = None, **kwargs) -> 'HybridRecommender':
        """
        Fit the hybrid recommender (not needed for this implementation).
        
        Args:
            interactions_df: DataFrame with user-item interactions
            courses_df: DataFrame with course information
            users_df: DataFrame with user information
            **kwargs: Additional fitting parameters
            
        Returns:
            Self for method chaining
        """
        logger.info("Hybrid recommender does not require fitting")
        self.is_fitted = True
        return self
    
    def recommend(self, user_id: str, n_recommendations: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """
        Generate recommendations using the hybrid approach.
        
        Args:
            user_id: ID of the user to recommend for
            n_recommendations: Number of recommendations to generate
            **kwargs: Additional recommendation parameters
            
        Returns:
            List of recommendation dictionaries
        """
        return self.hybrid_recommend(user_id, n_recommendations)
    
    def predict_rating(self, user_id: str, item_id: str) -> float:
        """
        Predict rating using hybrid approach.
        
        Args:
            user_id: ID of the user
            item_id: ID of the item
            
        Returns:
            Predicted rating
        """
        # Simple fallback rating prediction
        return 3.5  # Neutral rating

    def _create_fallback_recommendations(self, user_id: str, N: int) -> List[Dict[str, Any]]:
        """Create fallback recommendations when no models are available."""
        # Create dummy recommendations with fallback explanations
        fallback_recs = []
        for i in range(N):
            rec = {
                "item_id": f"fallback_course_{i+1:03d}",
                "score": 0.5,  # Neutral score
                "rank": i + 1,
                "model": "fallback"
            }
            fallback_recs.append(rec)
        
        return fallback_recs


def hybrid_recommend(user_id: str, 
                    N: int = 10, 
                    weights: Optional[Dict[str, float]] = None,
                    als_model: Optional[ALSRecommender] = None,
                    baseline_model: Optional[BaselineRecommender] = None,
                    courses_df: Optional[pd.DataFrame] = None,
                    interactions_df: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
    """
    Standalone function for hybrid recommendations.
    
    Args:
        user_id: ID of the user to recommend for
        N: Number of recommendations to generate
        weights: Weights for combining different approaches
        als_model: Pre-trained ALS model
        baseline_model: Pre-trained baseline model
        courses_df: Course information DataFrame
        interactions_df: Interactions DataFrame
        
    Returns:
        List of recommendation dictionaries with explanations
    """
    # Create hybrid recommender
    hybrid_rec = HybridRecommender(
        als_model=als_model,
        baseline_model=baseline_model,
        default_weights=weights
    )
    
    # Set data for explanations
    if courses_df is not None and interactions_df is not None:
        hybrid_rec.set_data(courses_df, interactions_df)
    
    # Generate recommendations
    return hybrid_rec.recommend(user_id, n_recommendations=N) 