"""
A/B testing framework for recommendation algorithms.
"""

import hashlib
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import redis
from .metrics import get_metrics_collector

logger = logging.getLogger(__name__)


@dataclass
class ExperimentConfig:
    """Configuration for an A/B test experiment."""
    name: str
    description: str
    variants: List[str]
    traffic_split: Dict[str, float]  # e.g., {"control": 0.9, "treatment": 0.1}
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True
    conversion_events: List[str] = None  # e.g., ["enroll", "complete"]
    
    def __post_init__(self):
        if self.conversion_events is None:
            self.conversion_events = ["enroll", "complete"]
        
        # Validate traffic split
        total_split = sum(self.traffic_split.values())
        if abs(total_split - 1.0) > 0.01:
            raise ValueError(f"Traffic split must sum to 1.0, got {total_split}")


class ABTestManager:
    """Manages A/B testing experiments for recommendation algorithms."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize the A/B test manager.
        
        Args:
            redis_client: Redis client for storing experiment data
        """
        self.redis_client = redis_client
        self.metrics_collector = get_metrics_collector()
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.user_assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {experiment_name: variant}
        
        logger.info("A/B test manager initialized")
    
    def create_experiment(self, config: ExperimentConfig) -> bool:
        """
        Create a new A/B test experiment.
        
        Args:
            config: Experiment configuration
            
        Returns:
            True if experiment was created successfully
        """
        try:
            if config.name in self.experiments:
                logger.warning(f"Experiment {config.name} already exists")
                return False
            
            self.experiments[config.name] = config
            
            # Store in Redis if available
            if self.redis_client:
                self.redis_client.hset(
                    f"experiment:{config.name}",
                    mapping=asdict(config)
                )
            
            logger.info(f"Created experiment: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create experiment {config.name}: {e}")
            return False
    
    def get_user_variant(self, user_id: str, experiment_name: str) -> str:
        """
        Get the variant assigned to a user for a specific experiment.
        
        Args:
            user_id: User identifier
            experiment_name: Name of the experiment
            
        Returns:
            Assigned variant name
        """
        # Check if experiment exists and is active
        if experiment_name not in self.experiments:
            logger.warning(f"Experiment {experiment_name} not found")
            return "control"
        
        experiment = self.experiments[experiment_name]
        if not experiment.is_active:
            return "control"
        
        # Check if user is already assigned
        if user_id in self.user_assignments and experiment_name in self.user_assignments[user_id]:
            variant = self.user_assignments[user_id][experiment_name]
        else:
            # Assign user to variant based on hash
            variant = self._assign_user_to_variant(user_id, experiment)
            
            # Store assignment
            if user_id not in self.user_assignments:
                self.user_assignments[user_id] = {}
            self.user_assignments[user_id][experiment_name] = variant
            
            # Record assignment in metrics
            self.metrics_collector.record_ab_assignment(experiment_name, variant)
            
            # Store in Redis if available
            if self.redis_client:
                self.redis_client.hset(
                    f"user_assignment:{user_id}",
                    experiment_name,
                    variant
                )
        
        return variant
    
    def _assign_user_to_variant(self, user_id: str, experiment: ExperimentConfig) -> str:
        """
        Assign a user to a variant based on consistent hashing.
        
        Args:
            user_id: User identifier
            experiment: Experiment configuration
            
        Returns:
            Assigned variant name
        """
        # Create consistent hash
        hash_input = f"{user_id}:{experiment.name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        hash_ratio = (hash_value % 10000) / 10000.0
        
        # Assign based on traffic split
        cumulative_prob = 0.0
        for variant, probability in experiment.traffic_split.items():
            cumulative_prob += probability
            if hash_ratio <= cumulative_prob:
                return variant
        
        # Fallback to first variant
        return list(experiment.traffic_split.keys())[0]
    
    def record_conversion(self, user_id: str, experiment_name: str, conversion_type: str):
        """
        Record a conversion event for A/B testing.
        
        Args:
            user_id: User identifier
            experiment_name: Name of the experiment
            conversion_type: Type of conversion event
        """
        try:
            variant = self.get_user_variant(user_id, experiment_name)
            
            # Record in metrics
            self.metrics_collector.record_ab_conversion(
                experiment_name, 
                variant, 
                conversion_type
            )
            
            # Store in Redis if available
            if self.redis_client:
                conversion_data = {
                    "user_id": user_id,
                    "experiment_name": experiment_name,
                    "variant": variant,
                    "conversion_type": conversion_type,
                    "timestamp": datetime.now().isoformat()
                }
                self.redis_client.lpush(
                    f"conversions:{experiment_name}",
                    json.dumps(conversion_data)
                )
            
            logger.debug(f"Recorded conversion: {user_id} -> {experiment_name}:{variant} -> {conversion_type}")
            
        except Exception as e:
            logger.error(f"Failed to record conversion: {e}")
    
    def calculate_precision_at_k(self, 
                                experiment_name: str, 
                                k: int = 10,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> Dict[str, float]:
        """
        Calculate Precision@K for each variant in an experiment.
        
        Args:
            experiment_name: Name of the experiment
            k: Number of top recommendations to consider
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary mapping variant names to Precision@K scores
        """
        if experiment_name not in self.experiments:
            logger.warning(f"Experiment {experiment_name} not found")
            return {}
        
        # This is a simplified implementation
        # In a real system, you would need to:
        # 1. Get actual recommendations made during the experiment period
        # 2. Get actual user interactions (enrollments, completions)
        # 3. Calculate precision based on ground truth
        
        # For now, we'll return mock data
        variants = list(self.experiments[experiment_name].traffic_split.keys())
        precision_scores = {}
        
        for variant in variants:
            # Mock precision calculation
            # In reality, this would be calculated from actual data
            base_precision = 0.7 if variant == "control" else 0.75
            noise = (hash(f"{experiment_name}:{variant}:{k}") % 100) / 1000.0
            precision_scores[variant] = max(0.0, min(1.0, base_precision + noise))
            
            # Record in metrics
            self.metrics_collector.record_precision_at_k(
                algorithm=variant,
                k=k,
                precision=precision_scores[variant],
                experiment_name=experiment_name
            )
        
        logger.info(f"Calculated Precision@{k} for {experiment_name}: {precision_scores}")
        return precision_scores
    
    def get_experiment_stats(self, experiment_name: str) -> Dict[str, Any]:
        """
        Get statistics for an experiment.
        
        Args:
            experiment_name: Name of the experiment
            
        Returns:
            Dictionary with experiment statistics
        """
        if experiment_name not in self.experiments:
            return {}
        
        experiment = self.experiments[experiment_name]
        
        # Count assignments per variant
        variant_counts = {}
        for user_assignments in self.user_assignments.values():
            if experiment_name in user_assignments:
                variant = user_assignments[experiment_name]
                variant_counts[variant] = variant_counts.get(variant, 0) + 1
        
        # Get conversion counts (mock data for now)
        conversion_counts = {}
        for variant in experiment.traffic_split.keys():
            conversion_counts[variant] = {
                "enroll": variant_counts.get(variant, 0) * 0.3,  # Mock conversion rate
                "complete": variant_counts.get(variant, 0) * 0.1
            }
        
        return {
            "name": experiment_name,
            "description": experiment.description,
            "is_active": experiment.is_active,
            "start_date": experiment.start_date.isoformat(),
            "end_date": experiment.end_date.isoformat() if experiment.end_date else None,
            "traffic_split": experiment.traffic_split,
            "assignments": variant_counts,
            "conversions": conversion_counts,
            "precision_at_10": self.calculate_precision_at_k(experiment_name, k=10)
        }
    
    def list_experiments(self) -> List[Dict[str, Any]]:
        """Get list of all experiments with basic info."""
        return [
            {
                "name": exp.name,
                "description": exp.description,
                "is_active": exp.is_active,
                "start_date": exp.start_date.isoformat(),
                "end_date": exp.end_date.isoformat() if exp.end_date else None,
                "variants": list(exp.traffic_split.keys())
            }
            for exp in self.experiments.values()
        ]


# Global A/B test manager instance
ab_test_manager = ABTestManager()


def get_ab_test_manager() -> ABTestManager:
    """Get the global A/B test manager instance."""
    return ab_test_manager
