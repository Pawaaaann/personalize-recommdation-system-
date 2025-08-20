"""
Data loading and generation utilities for EduRec.
"""

from .data_loader import DataLoader
from .generate_sample import generate_sample_data, main

__all__ = ["DataLoader", "generate_sample_data", "main"] 