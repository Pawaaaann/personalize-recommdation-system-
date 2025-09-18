import { firebaseStorageService, UserAssessmentData, UserStats } from './firebaseStorage';

export interface HybridStorageConfig {
  apiBaseUrl: string;
  enableAutoMigration: boolean;
}

export class HybridStorageService {
  private config: HybridStorageConfig;

  constructor(config: HybridStorageConfig) {
    this.config = config;
  }

  /**
   * Get user assessment data with hybrid approach:
   * 1. Check Firebase first
   * 2. If not found, check backend file storage
   * 3. If found in backend, optionally migrate to Firebase
   */
  async getUserAssessment(userId: string): Promise<UserAssessmentData | null> {
    try {
      // First, try Firebase
      console.log('Checking Firebase for user assessment:', userId);
      const firebaseData = await firebaseStorageService.getUserAssessment(userId);
      
      if (firebaseData) {
        console.log('Found user assessment in Firebase:', userId);
        return firebaseData;
      }

      // If not in Firebase, try backend API
      console.log('Checking backend for user assessment:', userId);
      const backendData = await this.getAssessmentFromBackend(userId);
      
      if (backendData && this.config.enableAutoMigration) {
        console.log('Found assessment in backend, migrating to Firebase:', userId);
        // Migrate to Firebase for future faster access
        try {
          await firebaseStorageService.saveUserAssessment(userId, backendData);
        } catch (migrationError) {
          console.warn('Failed to migrate assessment to Firebase:', migrationError);
        }
      }

      return backendData;
    } catch (error) {
      console.error('Error getting user assessment:', error);
      return null;
    }
  }

  /**
   * Save user assessment data to Firebase (primary) and optionally to backend
   */
  async saveUserAssessment(userId: string, assessmentData: UserAssessmentData): Promise<void> {
    try {
      // Save to Firebase first (primary storage)
      await firebaseStorageService.saveUserAssessment(userId, assessmentData);
      
      // Also save to backend for redundancy during transition period
      try {
        await this.saveAssessmentToBackend(userId, assessmentData);
      } catch (backendError) {
        console.warn('Failed to save assessment to backend:', backendError);
        // Don't fail the entire operation if Firebase succeeded
      }
    } catch (error) {
      console.error('Error saving user assessment:', error);
      throw error;
    }
  }

  /**
   * Get user stats with hybrid approach
   */
  async getUserStats(userId: string): Promise<UserStats | null> {
    try {
      // First, try Firebase
      console.log('Checking Firebase for user stats:', userId);
      const firebaseData = await firebaseStorageService.getUserStats(userId);
      
      if (firebaseData) {
        console.log('Found user stats in Firebase:', userId);
        return firebaseData;
      }

      // If not in Firebase, try backend API
      console.log('Checking backend for user stats:', userId);
      const backendData = await this.getStatsFromBackend(userId);
      
      if (backendData && this.config.enableAutoMigration) {
        console.log('Found stats in backend, migrating to Firebase:', userId);
        try {
          await firebaseStorageService.saveUserStats(userId, backendData);
        } catch (migrationError) {
          console.warn('Failed to migrate stats to Firebase:', migrationError);
        }
      }

      return backendData;
    } catch (error) {
      console.error('Error getting user stats:', error);
      return null;
    }
  }

  /**
   * Save user stats to Firebase (primary)
   */
  async saveUserStats(userId: string, stats: UserStats): Promise<void> {
    try {
      await firebaseStorageService.saveUserStats(userId, stats);
    } catch (error) {
      console.error('Error saving user stats:', error);
      throw error;
    }
  }

  /**
   * Get all user stats for leaderboards
   */
  async getAllUserStats(): Promise<UserStats[]> {
    try {
      // Get from Firebase first
      const firebaseStats = await firebaseStorageService.getAllUserStats();
      
      // If Firebase has data or auto-migration is disabled, return Firebase data
      if (firebaseStats.length > 0 || !this.config.enableAutoMigration) {
        return firebaseStats;
      }

      // If Firebase is empty and auto-migration is enabled, get from backend
      const backendStats = await this.getAllStatsFromBackend();
      
      // Migrate backend data to Firebase for future use
      if (backendStats.length > 0) {
        console.log('Migrating all user stats to Firebase');
        const migrationPromises = backendStats.map(stats => 
          firebaseStorageService.saveUserStats(stats.user_id, stats).catch(err => 
            console.warn(`Failed to migrate stats for user ${stats.user_id}:`, err)
          )
        );
        await Promise.allSettled(migrationPromises);
      }

      return backendStats;
    } catch (error) {
      console.error('Error getting all user stats:', error);
      return [];
    }
  }

  /**
   * Check if user has any data in the system
   */
  async hasUserData(userId: string): Promise<{ hasAssessment: boolean; hasStats: boolean }> {
    try {
      const firebaseCheck = await firebaseStorageService.hasUserData(userId);
      
      if (firebaseCheck.hasAssessment && firebaseCheck.hasStats) {
        return firebaseCheck;
      }

      // Check backend for missing data
      const backendAssessment = !firebaseCheck.hasAssessment ? await this.getAssessmentFromBackend(userId) : null;
      const backendStats = !firebaseCheck.hasStats ? await this.getStatsFromBackend(userId) : null;

      return {
        hasAssessment: firebaseCheck.hasAssessment || !!backendAssessment,
        hasStats: firebaseCheck.hasStats || !!backendStats
      };
    } catch (error) {
      console.error('Error checking user data:', error);
      return { hasAssessment: false, hasStats: false };
    }
  }

  // Backend API methods
  private async getAssessmentFromBackend(userId: string): Promise<UserAssessmentData | null> {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/api/users/${userId}/assessment`);
      if (response.ok) {
        const data = await response.json();
        // Normalize backend response to canonical format
        return {
          userId,
          interests: data.interests || [],
          skillLevel: data.skill_level || data.skillLevel || 'beginner',
          careerGoals: data.career_goals || data.careerGoals || [],
          domain: data.domain,
          subdomain: data.subdomain,
          experienceLevel: data.experience_level || data.experienceLevel,
          completedAt: new Date(data.completed_at || data.completedAt || Date.now()),
          recommendations: data.recommendations
        };
      }
      return null;
    } catch (error) {
      console.error('Error fetching assessment from backend:', error);
      return null;
    }
  }

  private async saveAssessmentToBackend(userId: string, assessmentData: UserAssessmentData): Promise<void> {
    try {
      await fetch(`${this.config.apiBaseUrl}/api/users/${userId}/assessment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assessmentData)
      });
    } catch (error) {
      console.error('Error saving assessment to backend:', error);
      throw error;
    }
  }

  private async getStatsFromBackend(userId: string): Promise<UserStats | null> {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/api/gamification/stats/${userId}`);
      if (response.ok) {
        const data = await response.json();
        // Normalize backend response to canonical format
        return {
          user_id: userId,
          level: data.level || 1,
          xp: data.total_xp || data.xp || 0,
          total_courses_completed: data.courses_completed || data.total_courses_completed || 0,
          streak_days: data.current_streak || data.streak_days || 0,
          badges: data.earned_badges || data.badges || [],
          last_activity: data.last_activity ? new Date(data.last_activity) : undefined
        };
      }
      return null;
    } catch (error) {
      console.error('Error fetching stats from backend:', error);
      return null;
    }
  }

  private async getAllStatsFromBackend(): Promise<UserStats[]> {
    try {
      const response = await fetch(`${this.config.apiBaseUrl}/api/gamification/leaderboard`);
      if (response.ok) {
        const data = await response.json();
        return data.map((item: any) => ({
          user_id: item.user_id,
          level: item.level || 1,
          xp: item.xp || 0,
          total_courses_completed: item.total_courses_completed || 0,
          streak_days: item.streak_days || 0,
          badges: item.badges || [],
          last_activity: item.last_activity ? new Date(item.last_activity) : undefined
        }));
      }
      return [];
    } catch (error) {
      console.error('Error fetching all stats from backend:', error);
      return [];
    }
  }
}

// Default hybrid storage instance
export const hybridStorage = new HybridStorageService({
  apiBaseUrl: window.location.origin, // Use the same origin for both dev and prod
  enableAutoMigration: true
});