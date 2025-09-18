import React, { useState, useEffect } from 'react';
import { Zap, Trophy, TrendingUp, Star, X } from 'lucide-react';

export interface NotificationData {
  type: 'xp' | 'level_up' | 'badge' | 'streak';
  message: string;
  details?: string;
  icon?: string;
  points?: number;
}

interface GamificationNotificationsProps {
  notifications: NotificationData[];
  onDismiss: (index: number) => void;
}

export const GamificationNotifications: React.FC<GamificationNotificationsProps> = ({
  notifications,
  onDismiss
}) => {
  const [visibleNotifications, setVisibleNotifications] = useState<(NotificationData & { id: number })[]>([]);

  useEffect(() => {
    // Add new notifications with unique IDs
    const newNotifications = notifications.map((notif, index) => ({
      ...notif,
      id: Date.now() + index
    }));
    
    setVisibleNotifications(prev => [...prev, ...newNotifications]);

    // Auto-dismiss notifications after 5 seconds
    newNotifications.forEach((notif, index) => {
      setTimeout(() => {
        setVisibleNotifications(prev => prev.filter(n => n.id !== notif.id));
      }, 5000 + (index * 500)); // Stagger dismissal
    });
  }, [notifications]);

  const getNotificationStyle = (type: string) => {
    switch (type) {
      case 'xp':
        return 'bg-gradient-to-r from-blue-500 to-purple-500 text-white';
      case 'level_up':
        return 'bg-gradient-to-r from-yellow-400 to-orange-500 text-white';
      case 'badge':
        return 'bg-gradient-to-r from-green-500 to-teal-500 text-white';
      case 'streak':
        return 'bg-gradient-to-r from-orange-500 to-red-500 text-white';
      default:
        return 'bg-gradient-to-r from-gray-500 to-gray-600 text-white';
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'xp':
        return <Zap className="w-5 h-5" />;
      case 'level_up':
        return <Star className="w-5 h-5" />;
      case 'badge':
        return <Trophy className="w-5 h-5" />;
      case 'streak':
        return <TrendingUp className="w-5 h-5" />;
      default:
        return <Zap className="w-5 h-5" />;
    }
  };

  const handleDismiss = (id: number) => {
    setVisibleNotifications(prev => prev.filter(n => n.id !== id));
  };

  if (visibleNotifications.length === 0) return null;

  return (
    <div className="fixed top-20 right-4 z-50 space-y-2 max-w-sm">
      {visibleNotifications.map((notification, index) => (
        <div
          key={notification.id}
          className={`${getNotificationStyle(notification.type)} p-4 rounded-lg shadow-lg transform transition-all duration-300`}
          style={{
            transform: 'translateX(0)',
            opacity: 1,
            animationDelay: `${index * 100}ms`
          }}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3 flex-1">
              <div className="flex-shrink-0 mt-0.5">
                {notification.icon ? (
                  <span className="text-xl">{notification.icon}</span>
                ) : (
                  getIcon(notification.type)
                )}
              </div>
              <div className="flex-1">
                <div className="font-semibold text-sm mb-1">
                  {notification.message}
                </div>
                {notification.details && (
                  <div className="text-xs opacity-90">
                    {notification.details}
                  </div>
                )}
                {notification.points && (
                  <div className="text-xs opacity-90 mt-1">
                    +{notification.points} XP
                  </div>
                )}
              </div>
            </div>
            <button
              onClick={() => handleDismiss(notification.id)}
              className="flex-shrink-0 ml-2 opacity-70 hover:opacity-100 transition-opacity"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};