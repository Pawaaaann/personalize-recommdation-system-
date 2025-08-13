import React, { useState, useEffect } from 'react';
import { LogOut, RefreshCw, User, BookOpen } from 'lucide-react';
import { RecommendationResponse, CourseMetadata } from '../types/api';
import { api } from '../services/api';
import { CourseCard } from './CourseCard';
import { LoadingSkeleton } from './LoadingSkeleton';

interface DashboardProps {
  studentId: string;
  onLogout: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ studentId, onLogout }) => {
  const [recommendations, setRecommendations] = useState<RecommendationResponse[]>([]);
  const [courseMetadata, setCourseMetadata] = useState<Record<string, CourseMetadata>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchRecommendations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const recs = await api.getRecommendations(studentId, 10);
      setRecommendations(recs);
      
      // Fetch course metadata for each recommendation
      const metadata: Record<string, CourseMetadata> = {};
      await Promise.all(
        recs.map(async (rec) => {
          try {
            const courseData = await api.getCourseMetadata(rec.course_id);
            metadata[rec.course_id] = courseData;
          } catch (error) {
            console.warn(`Failed to fetch metadata for course ${rec.course_id}:`, error);
          }
        })
      );
      
      setCourseMetadata(metadata);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      setError('Failed to load recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchRecommendations();
    setIsRefreshing(false);
  };

  const handleFeedback = (courseId: string, feedback: 'like' | 'dislike') => {
    console.log(`User ${studentId} ${feedback}d course ${courseId}`);
    // In a real app, you might want to update the UI or refetch recommendations
  };

  useEffect(() => {
    fetchRecommendations();
  }, [studentId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <div className="h-8 bg-gray-200 rounded w-48 mb-4 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-32 animate-pulse"></div>
          </div>
          <LoadingSkeleton count={5} />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="space-x-4">
            <button onClick={handleRefresh} className="btn-primary">
              Try Again
            </button>
            <button onClick={onLogout} className="btn-secondary">
              Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <BookOpen className="h-5 w-5 text-white" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">EduRec Dashboard</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <User className="h-4 w-4" />
                <span>{studentId}</span>
              </div>
              
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="btn-secondary flex items-center gap-2"
                aria-label="Refresh recommendations"
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                <span className="hidden sm:inline">Refresh</span>
              </button>
              
              <button
                onClick={onLogout}
                className="btn-secondary flex items-center gap-2"
                aria-label="Logout"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {studentId}!
          </h2>
          <p className="text-gray-600">
            Here are your personalized course recommendations based on your learning preferences.
          </p>
        </div>

        {/* Recommendations Count */}
        <div className="mb-6">
          <p className="text-sm text-gray-500">
            Showing {recommendations.length} recommended courses
          </p>
        </div>

        {/* Recommendations Grid */}
        {recommendations.length > 0 ? (
          <div className="space-y-6">
            {recommendations.map((recommendation) => (
              <CourseCard
                key={recommendation.course_id}
                recommendation={recommendation}
                courseMetadata={courseMetadata[recommendation.course_id]}
                studentId={studentId}
                onFeedback={handleFeedback}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">📚</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations found</h3>
            <p className="text-gray-600 mb-6">
              We couldn't find any courses that match your profile right now.
            </p>
            <button onClick={handleRefresh} className="btn-primary">
              Try Again
            </button>
          </div>
        )}
      </main>
    </div>
  );
};
