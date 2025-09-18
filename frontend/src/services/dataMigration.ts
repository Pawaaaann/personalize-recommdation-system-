import { firebaseStorageService, UserAssessmentData, UserStats } from './firebaseStorage';

export interface MigrationResult {
  userId: string;
  success: boolean;
  error?: string;
  migratedData: {
    assessment: boolean;
    stats: boolean;
  };
}

export interface MigrationSummary {
  totalUsers: number;
  successfulMigrations: number;
  failedMigrations: number;
  results: MigrationResult[];
  startTime: Date;
  endTime: Date;
  duration: number;
}

export class DataMigrationService {
  
  /**
   * Migrate a single user's data from backend to Firebase
   */
  async migrateUser(userId: string, forceOverwrite: boolean = false): Promise<MigrationResult> {
    const result: MigrationResult = {
      userId,
      success: false,
      migratedData: {
        assessment: false,
        stats: false
      }
    };

    try {
      console.log(`Starting migration for user: ${userId}`);

      // Check if user already has data in Firebase (unless force overwrite)
      if (!forceOverwrite) {
        const existingData = await firebaseStorageService.hasUserData(userId);
        if (existingData.hasAssessment && existingData.hasStats) {
          console.log(`User ${userId} already has complete data in Firebase, skipping`);
          result.success = true;
          result.migratedData = { assessment: true, stats: true };
          return result;
        }
      }

      // Migrate assessment data
      try {
        const assessmentData = await this.getAssessmentFromBackend(userId);
        if (assessmentData) {
          await firebaseStorageService.saveUserAssessment(userId, assessmentData);
          result.migratedData.assessment = true;
          console.log(`✅ Migrated assessment data for user: ${userId}`);
        }
      } catch (error) {
        console.warn(`Failed to migrate assessment for user ${userId}:`, error);
      }

      // Migrate stats data
      try {
        const statsData = await this.getStatsFromBackend(userId);
        if (statsData) {
          await firebaseStorageService.saveUserStats(userId, statsData);
          result.migratedData.stats = true;
          console.log(`✅ Migrated stats data for user: ${userId}`);
        }
      } catch (error) {
        console.warn(`Failed to migrate stats for user ${userId}:`, error);
      }

      result.success = result.migratedData.assessment || result.migratedData.stats;
      
      if (result.success) {
        console.log(`✅ Migration completed successfully for user: ${userId}`);
      } else {
        console.log(`⚠️ No data found to migrate for user: ${userId}`);
      }

    } catch (error) {
      result.error = error instanceof Error ? error.message : String(error);
      console.error(`❌ Migration failed for user ${userId}:`, error);
    }

    return result;
  }

  /**
   * Migrate all users from backend to Firebase
   */
  async migrateAllUsers(forceOverwrite: boolean = false): Promise<MigrationSummary> {
    const startTime = new Date();
    console.log('🚀 Starting bulk migration of all users...');

    const summary: MigrationSummary = {
      totalUsers: 0,
      successfulMigrations: 0,
      failedMigrations: 0,
      results: [],
      startTime,
      endTime: new Date(),
      duration: 0
    };

    try {
      // Get all user IDs from backend
      const userIds = await this.getAllUserIdsFromBackend();
      summary.totalUsers = userIds.length;

      console.log(`Found ${userIds.length} users to migrate`);

      // Migrate users in batches to avoid overwhelming Firebase
      const batchSize = 10;
      for (let i = 0; i < userIds.length; i += batchSize) {
        const batch = userIds.slice(i, i + batchSize);
        console.log(`Migrating batch ${Math.floor(i / batchSize) + 1}/${Math.ceil(userIds.length / batchSize)}`);

        const batchPromises = batch.map(userId => this.migrateUser(userId, forceOverwrite));
        const batchResults = await Promise.allSettled(batchPromises);

        batchResults.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            summary.results.push(result.value);
            if (result.value.success) {
              summary.successfulMigrations++;
            } else {
              summary.failedMigrations++;
            }
          } else {
            summary.results.push({
              userId: batch[index],
              success: false,
              error: result.reason?.message || 'Unknown error',
              migratedData: { assessment: false, stats: false }
            });
            summary.failedMigrations++;
          }
        });

        // Small delay between batches to be respectful to Firebase
        if (i + batchSize < userIds.length) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }

    } catch (error) {
      console.error('Error during bulk migration:', error);
    }

    summary.endTime = new Date();
    summary.duration = summary.endTime.getTime() - summary.startTime.getTime();

    console.log('📊 Migration Summary:');
    console.log(`Total users: ${summary.totalUsers}`);
    console.log(`Successful migrations: ${summary.successfulMigrations}`);
    console.log(`Failed migrations: ${summary.failedMigrations}`);
    console.log(`Duration: ${summary.duration / 1000}s`);

    return summary;
  }

  /**
   * Verify migration by checking data consistency
   */
  async verifyMigration(userId: string): Promise<{
    consistent: boolean;
    issues: string[];
  }> {
    const issues: string[] = [];

    try {
      // Check if data exists in both Firebase and backend
      const firebaseData = await firebaseStorageService.hasUserData(userId);
      const backendAssessment = await this.getAssessmentFromBackend(userId);
      const backendStats = await this.getStatsFromBackend(userId);

      if (backendAssessment && !firebaseData.hasAssessment) {
        issues.push('Assessment data exists in backend but missing in Firebase');
      }

      if (backendStats && !firebaseData.hasStats) {
        issues.push('Stats data exists in backend but missing in Firebase');
      }

      // TODO: Add deeper data consistency checks if needed
      
    } catch (error) {
      issues.push(`Error during verification: ${error}`);
    }

    return {
      consistent: issues.length === 0,
      issues
    };
  }

  // Private helper methods
  private async getAssessmentFromBackend(userId: string): Promise<UserAssessmentData | null> {
    try {
      const apiBaseUrl = window.location.origin;
      
      const response = await fetch(`${apiBaseUrl}/api/users/${userId}/assessment`);
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

  private async getStatsFromBackend(userId: string): Promise<UserStats | null> {
    try {
      const apiBaseUrl = window.location.origin;
      
      const response = await fetch(`${apiBaseUrl}/api/gamification/stats/${userId}`);
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

  private async getAllUserIdsFromBackend(): Promise<string[]> {
    try {
      const apiBaseUrl = window.location.origin;

      // Try to get user IDs from gamification stats endpoint
      const response = await fetch(`${apiBaseUrl}/api/gamification/all-users`);
      if (response.ok) {
        const data = await response.json();
        return data.map((user: any) => user.user_id || user.id).filter(Boolean);
      }

      // Fallback: try to get from leaderboard endpoint
      const leaderboardResponse = await fetch(`${apiBaseUrl}/api/gamification/leaderboard`);
      if (leaderboardResponse.ok) {
        const leaderboardData = await leaderboardResponse.json();
        return leaderboardData.map((user: any) => user.user_id || user.id).filter(Boolean);
      }

      console.warn('No user list endpoint available, returning empty list');
      return [];
    } catch (error) {
      console.error('Error fetching user IDs from backend:', error);
      return [];
    }
  }
}

export const dataMigrationService = new DataMigrationService();