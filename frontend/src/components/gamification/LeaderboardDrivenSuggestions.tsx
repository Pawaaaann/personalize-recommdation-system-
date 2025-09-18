import React, { useState, useEffect } from 'react';
import { Trophy, TrendingUp, Target, Zap } from 'lucide-react';
import { gamificationService, LeaderboardEntry, UserStats } from '../../services/gamification';

interface LeaderboardDrivenSuggestionsProps {
  currentUserId: string;
  userStats: UserStats;
}

interface XpBooster {
  action: string;
  xp: number;
  description: string;
  icon: React.ReactNode;
}

export const LeaderboardDrivenSuggestions: React.FC<LeaderboardDrivenSuggestionsProps> = ({
  currentUserId,
  userStats
}) => {
  const [nextRankInfo, setNextRankInfo] = useState<{
    nextRank: number;
    xpNeeded: number;
    nextRankUser?: LeaderboardEntry;
  } | null>(null);
  const [xpBoosters] = useState<XpBooster[]>([
    {
      action: 'Complete a Course',
      xp: 100,
      description: 'Finish any course to earn maximum XP',
      icon: <Trophy className="w-4 h-4" />
    },
    {
      action: 'Enroll in a Course',
      xp: 30,
      description: 'Start a new learning journey',
      icon: <Target className="w-4 h-4" />
    },
    {
      action: 'Like 5 Courses',
      xp: 75,
      description: 'Rate courses to help others (15 XP each)',
      icon: <TrendingUp className="w-4 h-4" />
    },
    {
      action: 'Maintain Streak',
      xp: 10,
      description: 'Keep learning daily for streak bonus',
      icon: <Zap className="w-4 h-4" />
    }
  ]);

  useEffect(() => {
    loadLeaderboardInfo();
  }, [currentUserId, userStats]);

  const loadLeaderboardInfo = async () => {
    try {
      const [leaderboard, userRank] = await Promise.all([
        gamificationService.getLeaderboard(100),
        gamificationService.getUserRank(currentUserId)
      ]);

      if (userRank > 1) {
        // Find the user one rank above
        const nextRankUser = leaderboard.find(entry => entry.rank === userRank - 1);
        if (nextRankUser) {
          const xpNeeded = nextRankUser.total_xp - userStats.total_xp;
          setNextRankInfo({
            nextRank: userRank - 1,
            xpNeeded: Math.max(xpNeeded, 0),
            nextRankUser
          });
        }
      }
    } catch (error) {
      console.error('Error loading leaderboard info:', error);
    }
  };

  const getActionsNeeded = (targetXp: number, actionXp: number): number => {
    return Math.ceil(targetXp / actionXp);
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="w-5 h-5 text-indigo-500" />
        <h2 className="text-xl font-semibold text-gray-900">Beat the Next Rank</h2>
      </div>

      {nextRankInfo && nextRankInfo.xpNeeded > 0 ? (
        <div className="space-y-6">
          {/* Next Rank Target */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 border border-indigo-200">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-lg font-bold text-indigo-900">
                  Rank #{nextRankInfo.nextRank}
                </div>
                <div className="text-sm text-indigo-600">
                  {nextRankInfo.nextRankUser?.username || 'Next Rank'}
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-indigo-700">
                  {nextRankInfo.xpNeeded.toLocaleString()}
                </div>
                <div className="text-sm text-indigo-600">XP needed</div>
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="w-full bg-indigo-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                style={{ 
                  width: `${Math.min(
                    (userStats.total_xp / (nextRankInfo.nextRankUser?.total_xp || userStats.total_xp + nextRankInfo.xpNeeded)) * 100, 
                    100
                  )}%` 
                }}
              />
            </div>
          </div>

          {/* XP Boosters */}
          <div>
            <h3 className="font-semibold text-gray-900 mb-4">Fastest Ways to Rank Up</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {xpBoosters.map((booster, index) => {
                const actionsNeeded = getActionsNeeded(nextRankInfo.xpNeeded, booster.xp);
                
                return (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white">
                      {booster.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 text-sm">
                        {booster.action}
                      </div>
                      <div className="text-xs text-gray-600">
                        {booster.description}
                      </div>
                      <div className="text-xs text-blue-600 font-medium mt-1">
                        {actionsNeeded}x needed for next rank (+{booster.xp} XP each)
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-6">
          <Trophy className="w-12 h-12 mx-auto text-yellow-500 mb-4" />
          <div className="text-lg font-semibold text-gray-900 mb-2">
            You're at the Top!
          </div>
          <div className="text-gray-600 text-sm">
            Keep learning to maintain your position on the leaderboard.
          </div>
        </div>
      )}
    </div>
  );
};