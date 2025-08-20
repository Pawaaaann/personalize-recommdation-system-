"""
Metrics collection using Prometheus client for monitoring recommendation system performance.
"""

import time
import logging
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry, multiprocess
import threading

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and exposes metrics for the recommendation system."""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        """
        Initialize the metrics collector.
        
        Args:
            registry: Prometheus registry to use (defaults to default registry)
        """
        self.registry = registry or CollectorRegistry()
        
        # Request metrics
        self.request_duration = Histogram(
            'recommendation_request_duration_seconds',
            'Time spent processing recommendation requests',
            ['endpoint', 'method'],
            registry=self.registry
        )
        
        self.request_total = Counter(
            'recommendation_requests_total',
            'Total number of recommendation requests',
            ['endpoint', 'method', 'status'],
            registry=self.registry
        )
        
        # Recommendation metrics
        self.recommendations_generated = Counter(
            'recommendations_generated_total',
            'Total number of recommendations generated',
            ['algorithm', 'user_id'],
            registry=self.registry
        )
        
        self.recommendation_scores = Histogram(
            'recommendation_scores',
            'Distribution of recommendation scores',
            ['algorithm'],
            registry=self.registry
        )
        
        # Model performance metrics
        self.model_load_time = Histogram(
            'model_load_duration_seconds',
            'Time spent loading recommendation models',
            ['model_name'],
            registry=self.registry
        )
        
        self.model_prediction_time = Histogram(
            'model_prediction_duration_seconds',
            'Time spent making predictions',
            ['model_name'],
            registry=self.registry
        )
        
        # System metrics
        self.active_users = Gauge(
            'active_users',
            'Number of active users in the system',
            registry=self.registry
        )
        
        self.total_courses = Gauge(
            'total_courses',
            'Total number of courses in the system',
            registry=self.registry
        )
        
        self.interactions_total = Counter(
            'interactions_total',
            'Total number of user interactions',
            ['event_type'],
            registry=self.registry
        )
        
        # A/B testing metrics
        self.ab_test_assignments = Counter(
            'ab_test_assignments_total',
            'Total number of A/B test assignments',
            ['experiment_name', 'variant'],
            registry=self.registry
        )
        
        self.ab_test_conversions = Counter(
            'ab_test_conversions_total',
            'Total number of A/B test conversions',
            ['experiment_name', 'variant', 'conversion_type'],
            registry=self.registry
        )
        
        # Precision@K metrics
        self.precision_at_k = Summary(
            'precision_at_k',
            'Precision@K for recommendations',
            ['algorithm', 'k', 'experiment_name'],
            registry=self.registry
        )
        
        logger.info("Metrics collector initialized")
    
    def record_request(self, endpoint: str, method: str, duration: float, status: str = "200"):
        """Record a request metric."""
        self.request_duration.labels(endpoint=endpoint, method=method).observe(duration)
        self.request_total.labels(endpoint=endpoint, method=method, status=status).inc()
    
    def record_recommendation(self, algorithm: str, user_id: str, count: int = 1):
        """Record a recommendation generation."""
        self.recommendations_generated.labels(algorithm=algorithm, user_id=user_id).inc(count)
    
    def record_recommendation_score(self, algorithm: str, score: float):
        """Record a recommendation score."""
        self.recommendation_scores.labels(algorithm=algorithm).observe(score)
    
    def record_model_load_time(self, model_name: str, duration: float):
        """Record model loading time."""
        self.model_load_time.labels(model_name=model_name).observe(duration)
    
    def record_model_prediction_time(self, model_name: str, duration: float):
        """Record model prediction time."""
        self.model_prediction_time.labels(model_name=model_name).observe(duration)
    
    def set_active_users(self, count: int):
        """Set the number of active users."""
        self.active_users.set(count)
    
    def set_total_courses(self, count: int):
        """Set the total number of courses."""
        self.total_courses.set(count)
    
    def record_interaction(self, event_type: str):
        """Record a user interaction."""
        self.interactions_total.labels(event_type=event_type).inc()
    
    def record_ab_assignment(self, experiment_name: str, variant: str):
        """Record an A/B test assignment."""
        self.ab_test_assignments.labels(experiment_name=experiment_name, variant=variant).inc()
    
    def record_ab_conversion(self, experiment_name: str, variant: str, conversion_type: str):
        """Record an A/B test conversion."""
        self.ab_test_conversions.labels(
            experiment_name=experiment_name, 
            variant=variant, 
            conversion_type=conversion_type
        ).inc()
    
    def record_precision_at_k(self, algorithm: str, k: int, precision: float, experiment_name: str = "default"):
        """Record Precision@K metric."""
        self.precision_at_k.labels(
            algorithm=algorithm, 
            k=k, 
            experiment_name=experiment_name
        ).observe(precision)
    
    def get_metrics(self) -> bytes:
        """Get the current metrics in Prometheus format."""
        return generate_latest(self.registry)
    
    def get_metrics_content_type(self) -> str:
        """Get the content type for metrics."""
        return CONTENT_TYPE_LATEST


# Global metrics collector instance
metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector instance."""
    return metrics_collector
