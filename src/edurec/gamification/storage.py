#!/usr/bin/env python3
"""
Storage layer for gamification data.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path

from .models import UserStats

class GamificationStorage:
    """File-based storage for gamification data."""
    
    def __init__(self, data_dir: str = "data/gamification"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.data_dir / "users").mkdir(exist_ok=True)
        
    def get_user_stats(self, user_id: str) -> UserStats:
        """Get user's gamification stats."""
        user_file = self.data_dir / "users" / f"{user_id}.json"
        
        if user_file.exists():
            try:
                with open(user_file, 'r') as f:
                    data = json.load(f)
                return UserStats.from_dict(data)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading user stats for {user_id}: {e}")
                # Return fresh stats if file is corrupted
                return UserStats(user_id)
        else:
            # New user
            return UserStats(user_id)
    
    def save_user_stats(self, stats: UserStats):
        """Save user's gamification stats."""
        user_file = self.data_dir / "users" / f"{stats.user_id}.json"
        
        try:
            with open(user_file, 'w') as f:
                json.dump(stats.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving user stats for {stats.user_id}: {e}")
    
    def get_all_user_stats(self) -> List[UserStats]:
        """Get stats for all users (for leaderboards)."""
        all_stats = []
        users_dir = self.data_dir / "users"
        
        if not users_dir.exists():
            return all_stats
        
        for user_file in users_dir.glob("*.json"):
            try:
                with open(user_file, 'r') as f:
                    data = json.load(f)
                stats = UserStats.from_dict(data)
                all_stats.append(stats)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading user stats from {user_file}: {e}")
                continue
        
        return all_stats
    
    def delete_user_stats(self, user_id: str) -> bool:
        """Delete user's gamification stats."""
        user_file = self.data_dir / "users" / f"{user_id}.json"
        
        if user_file.exists():
            try:
                user_file.unlink()
                return True
            except Exception as e:
                print(f"Error deleting user stats for {user_id}: {e}")
                return False
        
        return False
    
    def get_user_count(self) -> int:
        """Get total number of users with gamification data."""
        users_dir = self.data_dir / "users"
        if not users_dir.exists():
            return 0
        return len(list(users_dir.glob("*.json")))