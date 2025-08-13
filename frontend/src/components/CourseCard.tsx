import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, BookOpen, Clock, Target } from 'lucide-react';
import { RecommendationResponse, CourseMetadata, InteractionEvent } from '../types/api';
import { ExplanationIcons } from './ExplanationIcons';
import { api } from '../services/api';

interface CourseCardProps {
  recommendation: RecommendationResponse;
  courseMetadata?: CourseMetadata;
  studentId: string;
  onFeedback?: (courseId: string, feedback: 'like' | 'dislike') => void;
}

export const CourseCard: React.FC<CourseCardProps> = ({ 
  recommendation, 
  courseMetadata, 
  studentId, 
  onFeedback 
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [userFeedback, setUserFeedback] = useState<'like' | 'dislike' | null>(null);

  const handleFeedback = async (feedback: 'like' | 'dislike') => {
    if (isSubmitting || userFeedback === feedback) return;
    
    setIsSubmitting(true);
    try {
      const interaction: InteractionEvent = {
        student_id: studentId,
        course_id: recommendation.course_id,
        event_type: feedback,
        timestamp: new Date().toISOString()
      };
      
      await api.recordInteraction(interaction);
      setUserFeedback(feedback);
      onFeedback?.(recommendation.course_id, feedback);
    } catch (error) {
      console.error('Failed to record feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getProgressBadge = () => {
    if (recommendation.score >= 0.8) {
      return { text: 'High Match', color: 'bg-success-500 text-white' };
    } else if (recommendation.score >= 0.6) {
      return { text: 'Good Match', color: 'bg-warning-500 text-white' };
    } else {
      return { text: 'Fair Match', color: 'bg-gray-500 text-white' };
    }
  };

  const progressBadge = getProgressBadge();

  return (
    <div className="card group hover:shadow-lg transition-all duration-200">
      <div className="flex items-start space-x-4">
        {/* Course Image Placeholder */}
        <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <BookOpen className="w-8 h-8 text-white" />
        </div>
        
        <div className="flex-1 min-w-0">
          {/* Course Title and Score */}
          <div className="flex items-start justify-between mb-2">
            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
              {courseMetadata?.title || `Course ${recommendation.course_id}`}
            </h3>
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${progressBadge.color}`}>
              {progressBadge.text}
            </div>
          </div>
          
          {/* Course Description */}
          {courseMetadata?.description && (
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">
              {courseMetadata.description}
            </p>
          )}
          
          {/* Course Metadata */}
          <div className="flex flex-wrap items-center gap-3 mb-3 text-xs text-gray-500">
            {courseMetadata?.difficulty && (
              <div className="flex items-center gap-1">
                <Target className="w-3 h-3" />
                <span className="capitalize">{courseMetadata.difficulty}</span>
              </div>
            )}
            {courseMetadata?.duration && (
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <span>{courseMetadata.duration}</span>
              </div>
            )}
            {courseMetadata?.skill_tags && (
              <div className="flex items-center gap-1">
                <span className="bg-gray-100 px-2 py-1 rounded">
                  {courseMetadata.skill_tags.split(',')[0]}
                </span>
              </div>
            )}
          </div>
          
          {/* Explanation Icons */}
          <ExplanationIcons explanations={recommendation.explanation} className="mb-4" />
          
          {/* Feedback Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleFeedback('like')}
              disabled={isSubmitting}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                userFeedback === 'like'
                  ? 'bg-success-100 text-success-700 border border-success-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-success-50 hover:text-success-600 hover:border-success-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              aria-label="Like this course"
            >
              <ThumbsUp className="w-4 h-4" />
              <span className="hidden sm:inline">Like</span>
            </button>
            
            <button
              onClick={() => handleFeedback('dislike')}
              disabled={isSubmitting}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                userFeedback === 'dislike'
                  ? 'bg-red-100 text-red-700 border border-red-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-red-50 hover:text-red-600 hover:border-red-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
              aria-label="Dislike this course"
            >
              <ThumbsDown className="w-4 h-4" />
              <span className="hidden sm:inline">Dislike</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
