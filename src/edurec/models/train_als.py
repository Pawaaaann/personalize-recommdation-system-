#!/usr/bin/env python3
"""
Training script for ALS recommender model.
Reads data/interactions.csv and saves trained model to models/als_model.pkl
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import argparse
import sys
import os

# Add the src directory to the path so we can import edurec modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from edurec.models.als_recommender import ALSRecommender
from edurec.data.data_loader import DataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_interactions_data(data_path: str) -> pd.DataFrame:
    """
    Load interactions data from CSV file.
    
    Args:
        data_path: Path to the interactions CSV file
        
    Returns:
        DataFrame with interactions data
    """
    try:
        logger.info(f"Loading interactions data from {data_path}")
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Interactions file not found: {data_path}")
        
        # Load the data
        interactions_df = pd.read_csv(data_path)
        
        # Validate required columns
        required_columns = ['user_id', 'course_id']
        missing_columns = [col for col in required_columns if col not in interactions_df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Add event_type column if it doesn't exist (for backward compatibility)
        if 'event_type' not in interactions_df.columns:
            logger.info("No event_type column found, adding default 'interaction' type")
            interactions_df['event_type'] = 'interaction'
        
        # Add rating column if it doesn't exist
        if 'rating' not in interactions_df.columns:
            logger.info("No rating column found, adding default rating of 3.0")
            interactions_df['rating'] = 3.0
        
        logger.info(f"Loaded {len(interactions_df)} interactions for {interactions_df['user_id'].nunique()} users and {interactions_df['course_id'].nunique()} courses")
        
        return interactions_df
        
    except Exception as e:
        logger.error(f"Error loading interactions data: {e}")
        raise


def train_als_model(interactions_df: pd.DataFrame, 
                   factors: int = 64,
                   regularization: float = 0.01,
                   iterations: int = 20,
                   alpha: float = 40.0) -> ALSRecommender:
    """
    Train the ALS recommender model.
    
    Args:
        interactions_df: DataFrame with interactions data
        factors: Number of latent factors
        regularization: Regularization parameter
        iterations: Number of iterations for training
        alpha: Confidence parameter for implicit feedback
        
    Returns:
        Trained ALSRecommender instance
    """
    logger.info("Initializing ALS recommender...")
    
    # Initialize the model with specified hyperparameters
    als_model = ALSRecommender(
        factors=factors,
        regularization=regularization,
        iterations=iterations,
        alpha=alpha
    )
    
    logger.info(f"Training ALS model with factors={factors}, regularization={regularization}, iterations={iterations}, alpha={alpha}")
    
    # Fit the model
    als_model.fit(interactions_df)
    
    logger.info("ALS model training completed successfully!")
    
    # Log model information
    model_info = als_model.get_model_info()
    logger.info(f"Model info: {model_info}")
    
    return als_model


def save_model(model: ALSRecommender, output_path: str) -> None:
    """
    Save the trained model to disk.
    
    Args:
        model: Trained ALSRecommender instance
        output_path: Path to save the model
    """
    try:
        logger.info(f"Saving model to {output_path}")
        
        # Create output directory if it doesn't exist
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the model
        model.save(output_path)
        
        logger.info(f"Model successfully saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        raise


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description='Train ALS recommender model')
    parser.add_argument('--data-path', type=str, default='data/interactions.csv',
                       help='Path to interactions CSV file (default: data/interactions.csv)')
    parser.add_argument('--output-path', type=str, default='models/als_model.pkl',
                       help='Path to save the trained model (default: models/als_model.pkl)')
    parser.add_argument('--factors', type=int, default=64,
                       help='Number of latent factors (default: 64)')
    parser.add_argument('--regularization', type=float, default=0.01,
                       help='Regularization parameter (default: 0.01)')
    parser.add_argument('--iterations', type=int, default=20,
                       help='Number of training iterations (default: 20)')
    parser.add_argument('--alpha', type=float, default=40.0,
                       help='Confidence parameter for implicit feedback (default: 40.0)')
    
    args = parser.parse_args()
    
    try:
        # Load interactions data
        interactions_df = load_interactions_data(args.data_path)
        
        # Train the model
        als_model = train_als_model(
            interactions_df,
            factors=args.factors,
            regularization=args.regularization,
            iterations=args.iterations,
            alpha=args.alpha
        )
        
        # Save the model
        save_model(als_model, args.output_path)
        
        logger.info("ALS model training and saving completed successfully!")
        
        # Print summary
        print("\n" + "="*50)
        print("ALS MODEL TRAINING SUMMARY")
        print("="*50)
        print(f"Data loaded: {args.data_path}")
        print(f"Interactions: {len(interactions_df)}")
        print(f"Users: {interactions_df['user_id'].nunique()}")
        print(f"Courses: {interactions_df['course_id'].nunique()}")
        print(f"Model saved: {args.output_path}")
        print(f"Hyperparameters: factors={args.factors}, regularization={args.regularization}, iterations={args.iterations}, alpha={args.alpha}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
