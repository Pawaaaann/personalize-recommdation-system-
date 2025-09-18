import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { gamificationService, UserStats } from '../../services/gamification';
import { UserStatsCard } from './UserStatsCard';
import { BadgeShowcase } from './BadgeShowcase';
import { Leaderboard } from './Leaderboard';
import { LeaderboardDrivenSuggestions } from './LeaderboardDrivenSuggestions';
import { GamificationNotifications, NotificationData } from './GamificationNotifications';

export const GamificationDashboard: React.FC = () => {
  const { currentUser } = useAuth();
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState<NotificationData[]>([]);

  useEffect(() => {
    if (currentUser) {
      loadUserStats();
    }
  }, [currentUser]);

  const loadUserStats = async () => {
    if (!currentUser) return;
    
    try {
      const stats = await gamificationService.getUserStats(currentUser.uid);
      setUserStats(stats);
    } catch (error) {
      console.error('Error loading user stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewNotifications = (newNotifications: NotificationData[]) => {
    setNotifications(prev => [...prev, ...newNotifications]);
    // Clear notifications after adding them
    setTimeout(() => {
      setNotifications([]);
    }, 100);
  };

  const dismissNotification = (index: number) => {
    setNotifications(prev => prev.filter((_, i) => i !== index));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="h-64 bg-gray-200 rounded-xl"></div>
              <div className="h-64 bg-gray-200 rounded-xl"></div>
            </div>
            <div className="h-96 bg-gray-200 rounded-xl"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!currentUser || !userStats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Authentication Required</h2>
          <p className="text-gray-600">Please log in to view your gamification progress.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Learning Journey</h1>
          <p className="text-gray-600">Track your progress, earn badges, and compete with other learners!</p>
        </div>

        {/* Stats and Leaderboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <UserStatsCard stats={userStats} />
          <Leaderboard currentUserId={currentUser.uid} />
        </div>

        {/* Leaderboard-Driven Suggestions */}
        <div className="mb-8">
          <LeaderboardDrivenSuggestions currentUserId={currentUser.uid} userStats={userStats} />
        </div>

        {/* Badge Showcase */}
        <BadgeShowcase 
          userId={currentUser.uid} 
          earnedBadgeIds={userStats.earned_badges} 
        />
      </div>

      {/* Notifications */}
      <GamificationNotifications 
        notifications={notifications}
        onDismiss={dismissNotification}
      />
    </div>
  );
};