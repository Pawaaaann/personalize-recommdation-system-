"""
Generate synthetic educational data for testing and development.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List
import random
import argparse
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set reproducible random seed
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Sample data for realistic generation
COURSE_CATEGORIES = [
    "Mathematics", "Science", "Computer Science", "Language Arts", 
    "History", "Geography", "Literature", "Physics", "Chemistry", 
    "Biology", "Economics", "Psychology", "Philosophy", "Art", "Music"
]

DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced"]

EVENT_TYPES = ["view", "enroll", "complete", "quiz_attempt"]

SKILL_TAGS = [
    "algebra", "calculus", "geometry", "fractions", "statistics", "probability",
    "programming", "algorithms", "data_structures", "machine_learning", "databases",
    "web_development", "mobile_development", "cybersecurity", "networking",
    "writing", "grammar", "vocabulary", "reading_comprehension", "essay_writing",
    "research_methods", "critical_thinking", "problem_solving", "creativity",
    "communication", "leadership", "teamwork", "time_management", "organization"
]

def generate_course_data(n_courses: int = 500) -> pd.DataFrame:
    """Generate course data with realistic titles, descriptions, and skill tags."""
    logger.info(f"Generating {n_courses} courses...")
    
    courses = []
    for i in range(n_courses):
        # Generate course ID
        course_id = i + 1
        
        # Select category and difficulty
        category = random.choice(COURSE_CATEGORIES)
        difficulty = random.choice(DIFFICULTY_LEVELS)
        
        # Generate title
        if category == "Mathematics":
            title = f"{difficulty} {category}: {random.choice(['Algebra', 'Calculus', 'Geometry', 'Statistics'])}"
        elif category == "Computer Science":
            title = f"{difficulty} {category}: {random.choice(['Programming', 'Data Structures', 'Algorithms', 'Web Development'])}"
        elif category == "Language Arts":
            title = f"{difficulty} {category}: {random.choice(['Writing', 'Grammar', 'Literature', 'Communication'])}"
        else:
            title = f"{difficulty} {category}: {random.choice(['Fundamentals', 'Advanced Topics', 'Practical Applications', 'Theory'])}"
        
        # Generate description
        description = f"A comprehensive {difficulty.lower()} course covering essential concepts in {category.lower()}. Perfect for students looking to build strong foundations and develop practical skills."
        
        # Generate duration (2-20 hours)
        duration_hours = random.randint(2, 20)
        
        # Generate skill tags (2-5 tags per course)
        num_tags = random.randint(2, 5)
        course_skills = random.sample(SKILL_TAGS, num_tags)
        skill_tags = "|".join(course_skills)
        
        courses.append({
            'course_id': course_id,
            'title': title,
            'description': description,
            'duration_hours': duration_hours,
            'skill_tags': skill_tags
        })
    
    return pd.DataFrame(courses)

def generate_interaction_data(n_students: int = 10000, n_courses: int = 500, n_interactions: int = 200000) -> pd.DataFrame:
    """Generate interaction data with realistic patterns."""
    logger.info(f"Generating {n_interactions} interactions for {n_students} students and {n_courses} courses...")
    
    interactions = []
    
    # Generate base timestamp (last 2 years)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=730)
    
    # Generate interactions
    for _ in range(n_interactions):
        # Random student and course
        student_id = random.randint(1, n_students)
        course_id = random.randint(1, n_courses)
        
        # Random timestamp within the range
        random_days = random.uniform(0, 730)
        timestamp = int((start_time + timedelta(days=random_days)).timestamp())
        
        # Event type with realistic distribution
        event_weights = [0.4, 0.3, 0.2, 0.1]  # view, enroll, complete, quiz_attempt
        event_type = random.choices(EVENT_TYPES, weights=event_weights)[0]
        
        # Progress based on event type
        if event_type == "view":
            progress = random.randint(0, 30)
        elif event_type == "enroll":
            progress = random.randint(0, 10)
        elif event_type == "complete":
            progress = 100
        else:  # quiz_attempt
            progress = random.randint(20, 90)
        
        # Quiz score (only for quiz_attempt events, otherwise null)
        if event_type == "quiz_attempt":
            quiz_score = random.randint(0, 100)
        else:
            quiz_score = None
        
        # Skill tags (copy from course)
        # Note: In a real implementation, you'd look up the course's skill tags
        # For now, we'll generate some random skill tags
        num_skills = random.randint(1, 3)
        interaction_skills = random.sample(SKILL_TAGS, num_skills)
        skill_tags = "|".join(interaction_skills)
        
        interactions.append({
            'student_id': student_id,
            'course_id': course_id,
            'timestamp': timestamp,
            'event_type': event_type,
            'progress': progress,
            'quiz_score': quiz_score,
            'skill_tags': skill_tags
        })
    
    return pd.DataFrame(interactions)

def generate_sample_data(
    n_students: int = 10000,
    n_courses: int = 500,
    n_interactions: int = 200000,
    output_dir: str = "data"
) -> Dict[str, pd.DataFrame]:
    """Generate synthetic educational data and save to CSV files."""
    logger.info("Starting data generation...")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate courses data
    courses_df = generate_course_data(n_courses)
    
    # Generate interactions data
    interactions_df = generate_interaction_data(n_students, n_courses, n_interactions)
    
    # Save to CSV files
    courses_file = output_path / "courses.csv"
    interactions_file = output_path / "interactions.csv"
    
    courses_df.to_csv(courses_file, index=False)
    interactions_df.to_csv(interactions_file, index=False)
    
    logger.info(f"Data saved to:")
    logger.info(f"  - Courses: {courses_file} ({len(courses_df)} rows)")
    logger.info(f"  - Interactions: {interactions_file} ({len(interactions_df)} rows)")
    
    # Print summary statistics
    print("\n📊 Data Generation Summary:")
    print(f"   • Students: {n_students:,}")
    print(f"   • Courses: {n_courses:,}")
    print(f"   • Interactions: {n_interactions:,}")
    print(f"   • Event types: {interactions_df['event_type'].value_counts().to_dict()}")
    print(f"   • Progress range: {interactions_df['progress'].min()}-{interactions_df['progress'].max()}")
    print(f"   • Quiz scores (non-null): {interactions_df['quiz_score'].notna().sum():,}")
    print(f"   • Files saved to: {output_dir}/")
    
    return {
        "courses": courses_df,
        "interactions": interactions_df
    }

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate synthetic educational data")
    parser.add_argument("--students", type=int, default=10000, 
                       help="Number of students to generate (default: 10000)")
    parser.add_argument("--courses", type=int, default=500, 
                       help="Number of courses to generate (default: 500)")
    parser.add_argument("--interactions", type=int, default=200000, 
                       help="Number of interactions to generate (default: 200000)")
    parser.add_argument("--output-dir", default="data", 
                       help="Output directory for generated data (default: data)")
    parser.add_argument("--seed", type=int, default=42, 
                       help="Random seed for reproducibility (default: 42)")
    
    args = parser.parse_args()
    
    # Set the random seed from CLI argument
    global RANDOM_SEED
    RANDOM_SEED = args.seed
    np.random.seed(RANDOM_SEED)
    random.seed(RANDOM_SEED)
    
    logger.info(f"Using random seed: {RANDOM_SEED}")
    
    try:
        data = generate_sample_data(
            n_students=args.students,
            n_courses=args.courses,
            n_interactions=args.interactions,
            output_dir=args.output_dir
        )
        logger.info("✅ Data generation completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Error generating sample data: {e}")
        raise

if __name__ == "__main__":
    main() 