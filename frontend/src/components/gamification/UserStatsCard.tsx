import React from 'react';
import { Trophy, Zap, Flame, Star, TrendingUp } from 'lucide-react';
import type { UserStats } from '../../services/gamification';
import { gamificationService } from '../../services/gamification';

interface UserStatsCardProps {
  stats: UserStats;
}

export const UserStatsCard: React.FC<UserStatsCardProps> = ({ stats }) => {
  const levelProgress = gamificationService.getLevelProgress(stats.total_xp, stats.level);
  const nextLevelXp = gamificationService.calculateXpForNextLevel(stats.level);
  const currentLevelXp = stats.level > 1 ? gamificationService.calculateXpForNextLevel(stats.level - 1) : 0;
  const xpNeeded = nextLevelXp - stats.total_xp;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Your Progress</h2>
        <div className="flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-purple-100 to-pink-100 rounded-full">
          <Star className="w-4 h-4 text-purple-600" />
          <span className="text-sm font-medium text-purple-700">Level {stats.level}</span>
        </div>
      </div>

      {/* XP Progress Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Experience Points</span>
          <span className="text-sm text-gray-500">{stats.total_xp.toLocaleString()} XP</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 mb-1">
          <div
            className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500"
            style={{ width: `${levelProgress}%` }}
          />
        </div>
        <p className="text-xs text-gray-500">
          {xpNeeded.toLocaleString()} XP needed for Level {stats.level + 1}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Current Streak */}
        <div className="text-center p-4 bg-orange-50 rounded-lg border border-orange-100">
          <div className="flex items-center justify-center mb-2">
            <Flame className="w-5 h-5 text-orange-500" />
          </div>
          <div className="text-2xl font-bold text-orange-700 mb-1">
            {stats.current_streak}
          </div>
          <div className="text-xs text-orange-600 font-medium">
            Day Streak
          </div>
        </div>

        {/* Courses Completed */}
        <div className="text-center p-4 bg-green-50 rounded-lg border border-green-100">
          <div className="flex items-center justify-center mb-2">
            <Trophy className="w-5 h-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold text-green-700 mb-1">
            {stats.courses_completed}
          </div>
          <div className="text-xs text-green-600 font-medium">
            Completed
          </div>
        </div>

        {/* Badges Earned */}
        <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-100">
          <div className="flex items-center justify-center mb-2">
            <Zap className="w-5 h-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-blue-700 mb-1">
            {stats.earned_badges.length}
          </div>
          <div className="text-xs text-blue-600 font-medium">
            Badges
          </div>
        </div>

        {/* Domains Explored */}
        <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-100">
          <div className="flex items-center justify-center mb-2">
            <TrendingUp className="w-5 h-5 text-purple-500" />
          </div>
          <div className="text-2xl font-bold text-purple-700 mb-1">
            {stats.domains_explored.length}
          </div>
          <div className="text-xs text-purple-600 font-medium">
            Domains
          </div>
        </div>
      </div>

      {/* Achievement Highlights */}
      {stats.longest_streak > 0 && (
        <div className="mt-4 p-3 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
          <div className="flex items-center gap-2">
            <Flame className="w-4 h-4 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-800">
              Personal Best: {stats.longest_streak} day learning streak!
            </span>
          </div>
        </div>
      )}
    </div>
  );
};