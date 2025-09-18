#!/usr/bin/env python3
"""
Gamification data models and classes.
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from enum import Enum
import json

class BadgeType(Enum):
    """Types of badges that can be earned."""
    STREAK = "streak"
    COMPLETION = "completion" 
    EXPLORATION = "exploration"
    CONSISTENCY = "consistency"
    MILESTONE = "milestone"
    SPECIALIZATION = "specialization"

class BadgeRarity(Enum):
    """Badge rarity levels."""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class Badge:
    """Represents a badge that can be earned by users."""
    id: str
    name: str
    description: str
    type: BadgeType
    rarity: BadgeRarity
    icon: str  # Icon name or emoji
    requirements: Dict[str, Any]  # Requirements to earn this badge
    points: int  # XP points awarded for earning this badge
    color: str  # CSS color class
    
class UserStats:
    """Tracks user gamification statistics."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.total_xp = 0
        self.level = 1
        self.current_streak = 0
        self.longest_streak = 0
        self.last_activity_date: Optional[date] = None
        self.earned_badges: List[str] = []  # List of badge IDs
        self.courses_completed = 0
        self.courses_liked = 0
        self.domains_explored = set()
        self.activity_days = set()  # Track unique days of activity
        self.total_study_minutes = 0
        
    def add_xp(self, points: int) -> bool:
        """Add XP points and check if user leveled up."""
        old_level = self.level
        self.total_xp += points
        self.level = self._calculate_level()
        return self.level > old_level
    
    def _calculate_level(self) -> int:
        """Calculate user level based on total XP."""
        # Level formula: level = floor(sqrt(XP / 100)) + 1
        import math
        return int(math.sqrt(self.total_xp / 100)) + 1
    
    def update_streak(self, activity_date: date) -> bool:
        """Update user's learning streak. Returns True if streak continues."""
        if self.last_activity_date is None:
            # First activity
            self.current_streak = 1
            self.last_activity_date = activity_date
            self.activity_days.add(activity_date)
            return True
        
        days_diff = (activity_date - self.last_activity_date).days
        
        if days_diff == 1:
            # Consecutive day - streak continues
            self.current_streak += 1
            self.longest_streak = max(self.longest_streak, self.current_streak)
            self.last_activity_date = activity_date
            self.activity_days.add(activity_date)
            return True
        elif days_diff == 0:
            # Same day - just add to activity days
            self.activity_days.add(activity_date)
            return True
        else:
            # Streak broken
            self.current_streak = 1
            self.last_activity_date = activity_date
            self.activity_days.add(activity_date)
            return False
    
    def has_badge(self, badge_id: str) -> bool:
        """Check if user has earned a specific badge."""
        return badge_id in self.earned_badges
    
    def award_badge(self, badge_id: str) -> bool:
        """Award a badge to the user. Returns True if newly earned."""
        if not self.has_badge(badge_id):
            self.earned_badges.append(badge_id)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'user_id': self.user_id,
            'total_xp': self.total_xp,
            'level': self.level,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'earned_badges': self.earned_badges,
            'courses_completed': self.courses_completed,
            'courses_liked': self.courses_liked,
            'domains_explored': list(self.domains_explored),
            'activity_days': [d.isoformat() for d in self.activity_days],
            'total_study_minutes': self.total_study_minutes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserStats':
        """Create UserStats from dictionary."""
        stats = cls(data['user_id'])
        stats.total_xp = data.get('total_xp', 0)
        stats.level = data.get('level', 1)
        stats.current_streak = data.get('current_streak', 0)
        stats.longest_streak = data.get('longest_streak', 0)
        
        if data.get('last_activity_date'):
            from datetime import date
            stats.last_activity_date = date.fromisoformat(data['last_activity_date'])
        
        stats.earned_badges = data.get('earned_badges', [])
        stats.courses_completed = data.get('courses_completed', 0)
        stats.courses_liked = data.get('courses_liked', 0)
        stats.domains_explored = set(data.get('domains_explored', []))
        
        if data.get('activity_days'):
            from datetime import date
            stats.activity_days = {date.fromisoformat(d) for d in data['activity_days']}
        
        stats.total_study_minutes = data.get('total_study_minutes', 0)
        return stats

@dataclass
class LeaderboardEntry:
    """Represents a user's position on the leaderboard."""
    user_id: str
    username: str  # Display name
    total_xp: int
    level: int
    current_streak: int
    badges_count: int
    rank: int