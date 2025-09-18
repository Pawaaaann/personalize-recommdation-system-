import React, { useState, useEffect } from 'react';
import { Crown, Trophy, Medal, TrendingUp, User } from 'lucide-react';
import { gamificationService, LeaderboardEntry } from '../../services/gamification';

interface LeaderboardProps {
  currentUserId?: string;
}

export const Leaderboard: React.FC<LeaderboardProps> = ({ currentUserId }) => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [userRank, setUserRank] = useState<number>(-1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, [currentUserId]);

  const loadLeaderboard = async () => {
    try {
      const [leaderboardData, rank] = await Promise.all([
        gamificationService.getLeaderboard(50),
        currentUserId ? gamificationService.getUserRank(currentUserId) : Promise.resolve(-1)
      ]);

      setLeaderboard(leaderboardData);
      setUserRank(rank);
    } catch (error) {
      console.error('Error loading leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <Crown className="w-5 h-5 text-yellow-500" />;
      case 2:
        return <Trophy className="w-5 h-5 text-gray-400" />;
      case 3:
        return <Medal className="w-5 h-5 text-orange-500" />;
      default:
        return <div className="w-5 h-5 rounded-full bg-gray-300 flex items-center justify-center text-xs font-bold text-gray-600">{rank}</div>;
    }
  };

  const getRankBg = (rank: number, isCurrentUser: boolean) => {
    if (isCurrentUser) {
      return 'bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200';
    }
    
    switch (rank) {
      case 1:
        return 'bg-gradient-to-r from-yellow-50 to-yellow-100 border-yellow-200';
      case 2:
        return 'bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200';
      case 3:
        return 'bg-gradient-to-r from-orange-50 to-orange-100 border-orange-200';
      default:
        return 'bg-white border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          {[...Array(10)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-500" />
          Leaderboard
        </h2>
        {currentUserId && userRank > 0 && (
          <div className="text-sm text-gray-600">
            Your rank: #{userRank}
          </div>
        )}
      </div>

      {/* User's Position (if not in top 10) */}
      {currentUserId && userRank > 10 && (
        <div className={`p-4 rounded-lg border-2 mb-4 ${getRankBg(userRank, true)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center">
                {getRankIcon(userRank)}
              </div>
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-blue-600" />
                <span className="font-medium text-blue-900">You</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-blue-900">
                {leaderboard.find(entry => entry.user_id === currentUserId)?.total_xp.toLocaleString() || '0'} XP
              </div>
              <div className="text-sm text-blue-600">
                Level {leaderboard.find(entry => entry.user_id === currentUserId)?.level || 1}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Leaderboard List */}
      <div className="space-y-2">
        {leaderboard.slice(0, 20).map((entry) => {
          const isCurrentUser = entry.user_id === currentUserId;
          
          return (
            <div
              key={entry.user_id}
              className={`p-4 rounded-lg border transition-all hover:shadow-md ${getRankBg(entry.rank, isCurrentUser)}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  {/* Rank */}
                  <div className="flex items-center justify-center w-8">
                    {getRankIcon(entry.rank)}
                  </div>

                  {/* User Info */}
                  <div className="flex items-center gap-2 flex-1">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                      {isCurrentUser ? <User className="w-4 h-4" /> : entry.username.charAt(0)}
                    </div>
                    <div>
                      <div className="font-medium text-gray-900">
                        {isCurrentUser ? 'You' : entry.username}
                      </div>
                      <div className="text-sm text-gray-600">
                        Level {entry.level} • {entry.badges_count} badges
                      </div>
                    </div>
                  </div>

                  {/* Streak */}
                  {entry.current_streak > 0 && (
                    <div className="flex items-center gap-1 px-2 py-1 bg-orange-100 rounded-full">
                      <span className="text-orange-600 text-sm">🔥</span>
                      <span className="text-xs font-medium text-orange-700">{entry.current_streak}</span>
                    </div>
                  )}
                </div>

                {/* XP */}
                <div className="text-right">
                  <div className="text-lg font-bold text-gray-900">
                    {entry.total_xp.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-600">XP</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {leaderboard.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No learners on the leaderboard yet.</p>
          <p className="text-sm">Be the first to start your learning journey!</p>
        </div>
      )}
    </div>
  );
};