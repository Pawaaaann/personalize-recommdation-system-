import React, { useState, useEffect } from 'react';
import { Award, Lock, CheckCircle } from 'lucide-react';
import { gamificationService, Badge } from '../../services/gamification';

interface BadgeShowcaseProps {
  userId: string;
  earnedBadgeIds: string[];
}

interface BadgeWithProgress extends Badge {
  earned: boolean;
  progress: number;
}

export const BadgeShowcase: React.FC<BadgeShowcaseProps> = ({ userId, earnedBadgeIds }) => {
  const [badges, setBadges] = useState<BadgeWithProgress[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBadges();
  }, [userId, earnedBadgeIds]);

  const loadBadges = async () => {
    try {
      const [allBadges, badgeProgress] = await Promise.all([
        gamificationService.getAllBadges(),
        gamificationService.getBadgeProgress(userId)
      ]);

      const badgesWithProgress: BadgeWithProgress[] = allBadges.map(badge => ({
        ...badge,
        earned: earnedBadgeIds.includes(badge.id),
        progress: badgeProgress.badge_progress[badge.id]?.progress || 0
      }));

      setBadges(badgesWithProgress);
    } catch (error) {
      console.error('Error loading badges:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { id: 'all', name: 'All Badges', count: badges.length },
    { id: 'earned', name: 'Earned', count: badges.filter(b => b.earned).length },
    { id: 'streak', name: 'Streaks', count: badges.filter(b => b.type === 'streak').length },
    { id: 'completion', name: 'Completion', count: badges.filter(b => b.type === 'completion').length },
    { id: 'exploration', name: 'Exploration', count: badges.filter(b => b.type === 'exploration').length },
  ];

  const filteredBadges = badges.filter(badge => {
    if (selectedCategory === 'all') return true;
    if (selectedCategory === 'earned') return badge.earned;
    return badge.type === selectedCategory;
  });

  const getRarityGradient = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'from-gray-400 to-gray-600';
      case 'rare': return 'from-blue-400 to-blue-600';
      case 'epic': return 'from-purple-400 to-purple-600';
      case 'legendary': return 'from-yellow-400 to-yellow-600';
      default: return 'from-gray-400 to-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
          <Award className="w-5 h-5 text-yellow-500" />
          Badge Collection
        </h2>
        <div className="text-sm text-gray-600">
          {earnedBadgeIds.length} of {badges.length} earned
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 mb-6">
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
              selectedCategory === category.id
                ? 'bg-primary-100 text-primary-700 border-primary-200'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border-gray-200'
            } border`}
          >
            {category.name} ({category.count})
          </button>
        ))}
      </div>

      {/* Badge Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {filteredBadges.map(badge => (
          <div
            key={badge.id}
            className={`relative p-4 rounded-lg border-2 transition-all hover:scale-105 ${
              badge.earned
                ? 'bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-300 shadow-md'
                : 'bg-gray-50 border-gray-200'
            }`}
          >
            {/* Badge Icon */}
            <div className="text-center mb-3">
              <div className={`w-12 h-12 mx-auto rounded-full bg-gradient-to-br ${getRarityGradient(badge.rarity)} flex items-center justify-center text-white text-xl font-bold shadow-lg`}>
                {badge.icon}
              </div>
            </div>

            {/* Badge Info */}
            <div className="text-center">
              <h3 className={`font-semibold text-sm mb-1 ${
                badge.earned ? 'text-gray-900' : 'text-gray-500'
              }`}>
                {badge.name}
              </h3>
              <p className={`text-xs mb-2 ${
                badge.earned ? 'text-gray-600' : 'text-gray-400'
              }`}>
                {badge.description}
              </p>
              
              {/* XP Points */}
              <div className={`text-xs font-medium ${
                badge.earned ? 'text-yellow-600' : 'text-gray-400'
              }`}>
                +{badge.points} XP
              </div>
            </div>

            {/* Status Indicator */}
            <div className="absolute top-2 right-2">
              {badge.earned ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : (
                <Lock className="w-4 h-4 text-gray-400" />
              )}
            </div>

            {/* Progress Bar for Unearned Badges */}
            {!badge.earned && badge.progress > 0 && (
              <div className="mt-2">
                <div className="w-full bg-gray-200 rounded-full h-1">
                  <div
                    className="bg-gradient-to-r from-blue-400 to-purple-500 h-1 rounded-full transition-all duration-500"
                    style={{ width: `${badge.progress * 100}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500 text-center mt-1">
                  {Math.round(badge.progress * 100)}% complete
                </div>
              </div>
            )}

            {/* Rarity Indicator */}
            <div className={`absolute bottom-2 left-2 px-2 py-1 rounded text-xs font-medium text-white bg-gradient-to-r ${getRarityGradient(badge.rarity)}`}>
              {badge.rarity.charAt(0).toUpperCase() + badge.rarity.slice(1)}
            </div>
          </div>
        ))}
      </div>

      {filteredBadges.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Award className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No badges found in this category.</p>
          <p className="text-sm">Keep learning to earn your first badge!</p>
        </div>
      )}
    </div>
  );
};