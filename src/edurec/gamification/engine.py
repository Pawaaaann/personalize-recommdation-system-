#!/usr/bin/env python3
"""
Gamification engine for tracking achievements, awarding badges, and managing user progress.
"""

import json
import os
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .models import UserStats, LeaderboardEntry
from .badge_definitions import BADGES, get_badge
from .storage import GamificationStorage

class GamificationEngine:
    """Main engine for handling all gamification logic."""
    
    def __init__(self, storage: Optional[GamificationStorage] = None):
        self.storage = storage or GamificationStorage()
        
    def get_user_stats(self, user_id: str) -> UserStats:
        """Get user's gamification stats."""
        return self.storage.get_user_stats(user_id)
    
    def process_user_activity(self, user_id: str, activity_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user activity and update gamification stats.
        
        Args:
            user_id: ID of the user
            activity_type: Type of activity (view, like, complete, enroll, etc.)
            metadata: Additional metadata about the activity
            
        Returns:
            Dictionary with updates made (badges earned, XP gained, etc.)
        """
        stats = self.get_user_stats(user_id)
        updates = {
            'xp_gained': 0,
            'badges_earned': [],
            'level_up': False,
            'streak_updated': False
        }
        
        # Update activity streak
        today = date.today()
        streak_continued = stats.update_streak(today)
        if streak_continued:
            updates['streak_updated'] = True
        
        # Process different activity types
        xp_earned = 0
        
        if activity_type == 'view':
            xp_earned = 10
            
        elif activity_type == 'like':
            xp_earned = 15
            stats.courses_liked += 1
            
        elif activity_type == 'enroll':
            xp_earned = 30
            
        elif activity_type == 'complete':
            xp_earned = 100
            stats.courses_completed += 1
            
            # Add domain to explored domains
            if metadata and 'domain' in metadata:
                stats.domains_explored.add(metadata['domain'].lower())
                
        elif activity_type == 'assessment':
            xp_earned = 50
            
        elif activity_type == 'career_path_selection':
            xp_earned = 25
            
        elif activity_type == 'study_session':
            # Award XP based on study time (1 XP per minute)
            minutes = metadata.get('minutes', 0) if metadata else 0
            xp_earned = minutes
            stats.total_study_minutes += minutes
        
        # Add XP and check for level up
        if xp_earned > 0:
            level_up = stats.add_xp(xp_earned)
            updates['xp_gained'] = xp_earned
            updates['level_up'] = level_up
            
            if level_up:
                # Bonus XP for leveling up
                stats.add_xp(50)
                updates['xp_gained'] += 50
        
        # Check for new badges
        new_badges = self._check_badge_eligibility(stats)
        for badge_id in new_badges:
            if stats.award_badge(badge_id):
                badge = get_badge(badge_id)
                if badge:
                    stats.add_xp(badge.points)
                    updates['badges_earned'].append(badge_id)
                    updates['xp_gained'] += badge.points
        
        # Save updated stats
        self.storage.save_user_stats(stats)
        
        return updates
    
    def _check_badge_eligibility(self, stats: UserStats) -> List[str]:
        """Check which badges the user is now eligible for."""
        eligible_badges = []
        
        for badge_id, badge in BADGES.items():
            if stats.has_badge(badge_id):
                continue  # Already earned
                
            if self._meets_requirements(stats, badge.requirements):
                eligible_badges.append(badge_id)
        
        return eligible_badges
    
    def _meets_requirements(self, stats: UserStats, requirements: Dict[str, Any]) -> bool:
        """Check if user meets badge requirements."""
        for req_key, req_value in requirements.items():
            
            if req_key == 'current_streak':
                if stats.current_streak < req_value:
                    return False
                    
            elif req_key == 'longest_streak':
                if stats.longest_streak < req_value:
                    return False
                    
            elif req_key == 'courses_completed':
                if stats.courses_completed < req_value:
                    return False
                    
            elif req_key == 'courses_liked':
                if stats.courses_liked < req_value:
                    return False
                    
            elif req_key == 'total_xp':
                if stats.total_xp < req_value:
                    return False
                    
            elif req_key == 'domains_explored_count':
                if len(stats.domains_explored) < req_value:
                    return False
                    
            elif req_key == 'domain_courses':
                # Check courses completed in specific domains
                for domain, required_count in req_value.items():
                    # This would need to be tracked separately
                    # For now, assume we have this data
                    pass
                    
            elif req_key == 'weekend_days':
                weekend_days = sum(1 for d in stats.activity_days if d.weekday() >= 5)
                if weekend_days < req_value:
                    return False
        
        return True
    
    def get_leaderboard(self, limit: int = 50) -> List[LeaderboardEntry]:
        """Get the global leaderboard."""
        all_stats = self.storage.get_all_user_stats()
        
        # Sort by total XP descending
        sorted_users = sorted(all_stats, key=lambda s: s.total_xp, reverse=True)
        
        leaderboard = []
        for i, stats in enumerate(sorted_users[:limit]):
            entry = LeaderboardEntry(
                user_id=stats.user_id,
                username=f"User{stats.user_id[-4:]}",  # Anonymous display name
                total_xp=stats.total_xp,
                level=stats.level,
                current_streak=stats.current_streak,
                badges_count=len(stats.earned_badges),
                rank=i + 1
            )
            leaderboard.append(entry)
        
        return leaderboard
    
    def get_user_rank(self, user_id: str) -> int:
        """Get user's rank on the leaderboard."""
        leaderboard = self.get_leaderboard(1000)  # Get top 1000
        for entry in leaderboard:
            if entry.user_id == user_id:
                return entry.rank
        return -1  # Not in top 1000
    
    def get_badge_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's progress towards earning badges."""
        stats = self.get_user_stats(user_id)
        progress = {}
        
        for badge_id, badge in BADGES.items():
            if stats.has_badge(badge_id):
                progress[badge_id] = {
                    'earned': True,
                    'progress': 1.0,
                    'badge': badge
                }
            else:
                # Calculate progress towards this badge
                badge_progress = self._calculate_badge_progress(stats, badge.requirements)
                progress[badge_id] = {
                    'earned': False,
                    'progress': badge_progress,
                    'badge': badge
                }
        
        return progress
    
    def _calculate_badge_progress(self, stats: UserStats, requirements: Dict[str, Any]) -> float:
        """Calculate progress (0.0 to 1.0) towards badge requirements."""
        if not requirements:
            return 0.0
        
        progress_values = []
        
        for req_key, req_value in requirements.items():
            current_value = 0
            
            if req_key == 'current_streak':
                current_value = stats.current_streak
            elif req_key == 'longest_streak':
                current_value = stats.longest_streak
            elif req_key == 'courses_completed':
                current_value = stats.courses_completed
            elif req_key == 'courses_liked':
                current_value = stats.courses_liked
            elif req_key == 'total_xp':
                current_value = stats.total_xp
            elif req_key == 'domains_explored_count':
                current_value = len(stats.domains_explored)
            elif req_key == 'weekend_days':
                current_value = sum(1 for d in stats.activity_days if d.weekday() >= 5)
            
            # Calculate progress for this requirement
            if isinstance(req_value, (int, float)):
                progress = min(current_value / req_value, 1.0)
                progress_values.append(progress)
        
        # Return average progress across all requirements
        return sum(progress_values) / len(progress_values) if progress_values else 0.0