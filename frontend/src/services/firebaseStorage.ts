import { doc, setDoc, getDoc, collection, getDocs } from 'firebase/firestore';
import { db } from '../firebase/config';

export interface UserAssessmentData {
  userId: string;
  interests: string[];
  skillLevel: string;
  careerGoals: string[];
  completedAt: Date;
  recommendations?: any[];
}

export interface UserStats {
  user_id: string;
  level: number;
  xp: number;
  total_courses_completed: number;
  streak_days: number;
  badges: string[];
  last_activity?: Date;
}

export class FirebaseStorageService {
  
  /**
   * Save user assessment data to Firestore
   */
  async saveUserAssessment(userId: string, assessmentData: UserAssessmentData): Promise<void> {
    try {
      const docRef = doc(db, 'user_assessments', userId);
      await setDoc(docRef, {
        ...assessmentData,
        completedAt: assessmentData.completedAt.toISOString(),
        lastUpdated: new Date().toISOString()
      });
      console.log('User assessment saved to Firebase:', userId);
    } catch (error) {
      console.error('Error saving user assessment to Firebase:', error);
      throw error;
    }
  }

  /**
   * Get user assessment data from Firestore
   */
  async getUserAssessment(userId: string): Promise<UserAssessmentData | null> {
    try {
      const docRef = doc(db, 'user_assessments', userId);
      const docSnap = await getDoc(docRef);
      
      if (docSnap.exists()) {
        const data = docSnap.data();
        return {
          ...data,
          completedAt: new Date(data.completedAt)
        } as UserAssessmentData;
      }
      return null;
    } catch (error) {
      console.error('Error getting user assessment from Firebase:', error);
      return null;
    }
  }

  /**
   * Save user gamification stats to Firestore
   */
  async saveUserStats(userId: string, stats: UserStats): Promise<void> {
    try {
      const docRef = doc(db, 'user_stats', userId);
      await setDoc(docRef, {
        ...stats,
        last_activity: stats.last_activity ? stats.last_activity.toISOString() : new Date().toISOString(),
        lastUpdated: new Date().toISOString()
      });
      console.log('User stats saved to Firebase:', userId);
    } catch (error) {
      console.error('Error saving user stats to Firebase:', error);
      throw error;
    }
  }

  /**
   * Get user gamification stats from Firestore
   */
  async getUserStats(userId: string): Promise<UserStats | null> {
    try {
      const docRef = doc(db, 'user_stats', userId);
      const docSnap = await getDoc(docRef);
      
      if (docSnap.exists()) {
        const data = docSnap.data();
        return {
          ...data,
          last_activity: data.last_activity ? new Date(data.last_activity) : undefined
        } as UserStats;
      }
      return null;
    } catch (error) {
      console.error('Error getting user stats from Firebase:', error);
      return null;
    }
  }

  /**
   * Get all user stats for leaderboards
   */
  async getAllUserStats(): Promise<UserStats[]> {
    try {
      const querySnapshot = await getDocs(collection(db, 'user_stats'));
      const allStats: UserStats[] = [];
      
      querySnapshot.forEach((doc) => {
        const data = doc.data();
        allStats.push({
          ...data,
          last_activity: data.last_activity ? new Date(data.last_activity) : undefined
        } as UserStats);
      });
      
      return allStats;
    } catch (error) {
      console.error('Error getting all user stats from Firebase:', error);
      return [];
    }
  }

  /**
   * Check if user has data in Firebase
   */
  async hasUserData(userId: string): Promise<{ hasAssessment: boolean; hasStats: boolean }> {
    try {
      const [assessmentDoc, statsDoc] = await Promise.all([
        getDoc(doc(db, 'user_assessments', userId)),
        getDoc(doc(db, 'user_stats', userId))
      ]);
      
      return {
        hasAssessment: assessmentDoc.exists(),
        hasStats: statsDoc.exists()
      };
    } catch (error) {
      console.error('Error checking user data in Firebase:', error);
      return { hasAssessment: false, hasStats: false };
    }
  }

  /**
   * Migrate user data from local storage to Firebase
   */
  async migrateUserToFirebase(userId: string, localAssessmentData?: UserAssessmentData, localStatsData?: UserStats): Promise<void> {
    try {
      const promises = [];
      
      if (localAssessmentData) {
        promises.push(this.saveUserAssessment(userId, localAssessmentData));
      }
      
      if (localStatsData) {
        promises.push(this.saveUserStats(userId, localStatsData));
      }
      
      await Promise.all(promises);
      console.log('User data migrated to Firebase successfully:', userId);
    } catch (error) {
      console.error('Error migrating user data to Firebase:', error);
      throw error;
    }
  }
}

export const firebaseStorageService = new FirebaseStorageService();