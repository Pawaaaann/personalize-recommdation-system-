// Gamification API service
import { api } from './api';

export interface UserStats {
  user_id: string;
  total_xp: number;
  level: number;
  current_streak: number;
  longest_streak: number;
  earned_badges: string[];
  courses_completed: number;
  courses_liked: number;
  domains_explored: string[];
}

export interface Badge {
  id: string;
  name: string;
  description: string;
  type: string;
  rarity: string;
  icon: string;
  points: number;
  color: string;
}

export interface LeaderboardEntry {
  user_id: string;
  username: string;
  total_xp: number;
  level: number;
  current_streak: number;
  badges_count: number;
  rank: number;
}

export interface ActivityUpdate {
  xp_gained: number;
  badges_earned: string[];
  level_up: boolean;
  streak_updated: boolean;
  current_stats: UserStats;
}

class GamificationService {
  private baseUrl = '/api/gamification';

  async getUserStats(userId: string): Promise<UserStats> {
    try {
      const response = await fetch(`${this.baseUrl}/stats/${userId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch user stats: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching user stats:', error);
      // Return default stats if API fails
      return {
        user_id: userId,
        total_xp: 0,
        level: 1,
        current_streak: 0,
        longest_streak: 0,
        earned_badges: [],
        courses_completed: 0,
        courses_liked: 0,
        domains_explored: []
      };
    }
  }

  async getAllBadges(): Promise<Badge[]> {
    try {
      const response = await fetch(`${this.baseUrl}/badges`);
      if (!response.ok) {
        throw new Error(`Failed to fetch badges: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching badges:', error);
      return [];
    }
  }

  async getBadgeProgress(userId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/badges/progress/${userId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch badge progress: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching badge progress:', error);
      return { badge_progress: {} };
    }
  }

  async getLeaderboard(limit: number = 50): Promise<LeaderboardEntry[]> {
    try {
      const response = await fetch(`${this.baseUrl}/leaderboard?limit=${limit}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch leaderboard: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      return [];
    }
  }

  async getUserRank(userId: string): Promise<number> {
    try {
      const response = await fetch(`${this.baseUrl}/rank/${userId}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch user rank: ${response.statusText}`);
      }
      const data = await response.json();
      return data.rank;
    } catch (error) {
      console.error('Error fetching user rank:', error);
      return -1;
    }
  }

  // Helper method to calculate XP needed for next level
  calculateXpForNextLevel(currentLevel: number): number {
    // Level formula: level = floor(sqrt(XP / 100)) + 1
    // So XP needed = (level)^2 * 100
    return (currentLevel) * (currentLevel) * 100;
  }

  // Helper method to get level progress percentage
  getLevelProgress(totalXp: number, currentLevel: number): number {
    const currentLevelXp = (currentLevel - 1) * (currentLevel - 1) * 100;
    const nextLevelXp = currentLevel * currentLevel * 100;
    const progressXp = totalXp - currentLevelXp;
    const neededXp = nextLevelXp - currentLevelXp;
    return Math.min((progressXp / neededXp) * 100, 100);
  }
}

export const gamificationService = new GamificationService();