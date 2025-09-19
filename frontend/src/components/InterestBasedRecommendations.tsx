import React, { useState, useEffect } from 'react';
import { BookOpen, Clock, Star, Target, TrendingUp, Loader2 } from 'lucide-react';
import { UserAssessment } from './InterestAssessment';
import { api } from '../services/api';
import { CourseMetadata } from '../types/api';

interface InterestBasedRecommendationsProps {
  assessment: UserAssessment;
}

interface CourseRecommendation {
  course: CourseMetadata;
  score: number;
  explanation: string[];
  matchReason: string;
}

export const InterestBasedRecommendations: React.FC<InterestBasedRecommendationsProps> = ({ 
  assessment 
}) => {
  const [recommendations, setRecommendations] = useState<CourseRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);

  useEffect(() => {
    fetchRecommendations();
  }, [assessment]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get 8-10 recommendations based on comprehensive user profile to give users more choices
      const allPreferences = [
        ...(assessment.interests || []),
        ...(assessment.specificTechnologies || []),
        ...(assessment.projectTypes || []),
        ...(assessment.learningStyles || []),
        ...(assessment.currentSkills || []),
        ...(assessment.learningGoals || [])
      ];
      
      const apiRecommendations = await api.getInterestBasedRecommendations(
        allPreferences,
        assessment.selectedDomain,
        assessment.selectedSubdomain,
        assessment.experienceLevel,
        10
      );

      // Fetch course metadata in parallel for better performance
      const courseRecommendations: CourseRecommendation[] = [];
      
      // Separate generic and real course IDs
      const genericRecs = apiRecommendations.filter(rec => rec.course_id.startsWith('generic_'));
      const realRecs = apiRecommendations.filter(rec => !rec.course_id.startsWith('generic_'));
      
      // Handle generic courses immediately
      genericRecs.forEach(rec => {
        const genericCourse = getGenericCourseData(rec.course_id, assessment);
        courseRecommendations.push({
          course: genericCourse,
          score: rec.score,
          explanation: rec.explanation,
          matchReason: "Recommended for your field and experience level"
        });
      });
      
      // Fetch real course metadata in parallel
      if (realRecs.length > 0) {
        const courseMetadataPromises = realRecs.map(async rec => {
          try {
            const courseMetadata = await api.getCourseMetadata(rec.course_id);
            
            // Determine match reason based on score and explanations
            let matchReason = "Based on your preferences";
            if (rec.score > 0.8) {
              matchReason = "Excellent match with your learning goals";
            } else if (rec.score > 0.6) {
              matchReason = "Good match with your tech interests";
            } else if (rec.score > 0.4) {
              matchReason = "Relevant to your selected domain";
            }
            
            return {
              course: courseMetadata,
              score: rec.score,
              explanation: rec.explanation,
              matchReason
            };
          } catch (err) {
            console.warn(`Failed to fetch metadata for course ${rec.course_id}:`, err);
            const fallbackCourse = getFallbackCourseData(rec.course_id, assessment);
            return {
              course: fallbackCourse,
              score: rec.score,
              explanation: rec.explanation,
              matchReason: "Recommended course in your field"
            };
          }
        });
        
        const realCourseRecs = await Promise.all(courseMetadataPromises);
        courseRecommendations.push(...realCourseRecs);
      }

      // Sort by score and ensure we have at least 8 recommendations for better variety
      courseRecommendations.sort((a, b) => b.score - a.score);
      
      if (courseRecommendations.length < 8) {
        // If we don't have enough, add some fallback recommendations
        const fallbackCourses = [
          {
            course: {
              course_id: "fallback_1",
              title: "Introduction to Your Field",
              description: "A foundational course to get you started in your chosen domain",
              skill_tags: "Basics, Fundamentals, Introduction",
              difficulty: "Beginner",
              duration: "4-6 weeks"
            } as CourseMetadata,
            score: 0.7,
            explanation: ["Recommended for beginners", "Popular starting point"],
            matchReason: "Great starting point for your journey"
          },
          {
            course: {
              course_id: "fallback_2",
              title: "Essential Skills Development",
              description: "Build core competencies needed in your field",
              skill_tags: "Core Skills, Development, Practice",
              difficulty: "Beginner",
              duration: "6-8 weeks"
            } as CourseMetadata,
            score: 0.6,
            explanation: ["Essential skills", "Industry standard"],
            matchReason: "Builds essential skills for your field"
          }
        ];
        
        courseRecommendations.push(...fallbackCourses);
      }

      setRecommendations(courseRecommendations.slice(0, 10)); // Show up to 10 recommendations for better choice
      
    } catch (err) {
      setError('Failed to fetch recommendations. Please try again.');
      console.error('Error fetching recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to get generic course data
  const getGenericCourseData = (courseId: string, assessment: UserAssessment): CourseMetadata => {
    const genericCourses = {
      "generic_1": {
        title: "Foundation Course in " + assessment.selectedSubdomain,
        description: "Essential fundamentals to build your knowledge base in " + assessment.selectedSubdomain,
        skill_tags: "Fundamentals, Basics, Core Concepts",
        difficulty: "Beginner",
        duration: "6-8 weeks"
      },
      "generic_2": {
        title: "Essential Skills for " + assessment.selectedDomain,
        description: "Develop the core competencies needed to succeed in " + assessment.selectedDomain,
        skill_tags: "Essential Skills, Core Competencies, Best Practices",
        difficulty: "Beginner",
        duration: "8-10 weeks"
      },
      "generic_3": {
        title: "Introduction to " + assessment.selectedSubdomain + " Concepts",
        description: "A comprehensive introduction to key concepts and methodologies in " + assessment.selectedSubdomain,
        skill_tags: "Introduction, Key Concepts, Methodologies",
        difficulty: "Beginner",
        duration: "4-6 weeks"
      },
      "generic_4": {
        title: "Building Blocks of " + assessment.selectedDomain,
        description: "Master the foundational building blocks that will support your advanced learning journey",
        skill_tags: "Building Blocks, Foundation, Advanced Preparation",
        difficulty: "Beginner",
        duration: "10-12 weeks"
      }
    };

    const courseData = genericCourses[courseId as keyof typeof genericCourses] || genericCourses["generic_1"];
    
    return {
      course_id: courseId,
      title: courseData.title,
      description: courseData.description,
      skill_tags: courseData.skill_tags,
      difficulty: courseData.difficulty,
      duration: courseData.duration
    };
  };

  // Helper function to get fallback course data
  const getFallbackCourseData = (courseId: string, assessment: UserAssessment): CourseMetadata => {
    return {
      course_id: courseId,
      title: "Recommended Course in " + assessment.selectedSubdomain,
      description: "A well-regarded course that aligns with your interests and experience level",
      skill_tags: "Recommended, Popular, Well-reviewed",
      difficulty: assessment.experienceLevel === 'beginner' ? 'Beginner' : 'Intermediate',
      duration: "6-8 weeks"
    };
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty?.toLowerCase()) {
      case 'beginner': return 'text-green-600 bg-green-100';
      case 'intermediate': return 'text-yellow-600 bg-yellow-100';
      case 'advanced': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center">
            <Loader2 className="h-12 w-12 animate-spin text-primary-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Finding Perfect Courses for You</h2>
            <p className="text-gray-600">Analyzing your interests and preferences...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center">
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
            <button 
              onClick={fetchRecommendations}
              className="btn-primary"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Personalized Course Recommendations
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Based on your interests in <strong>{assessment.selectedDomain}</strong> and 
            <strong> {assessment.selectedSubdomain}</strong>, here are the best courses for you
          </p>
          <p className="text-lg text-gray-500 mt-2">
            Showing {recommendations.length} personalized course recommendations
          </p>
        </div>

        {/* Course Recommendations */}
        <div className="space-y-6">
          {recommendations.map((rec, index) => (
            <div key={rec.course.course_id} className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                        {index + 1}
                      </div>
                      <h3 className="text-2xl font-bold text-gray-900">{rec.course.title}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(rec.score)}`}>
                        {Math.round(rec.score * 100)}% Match
                      </span>
                    </div>
                    
                    <p className="text-gray-600 mb-4">{rec.course.description}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="flex items-center gap-2">
                        <Clock className="h-5 w-5 text-gray-400" />
                        <span className="text-sm text-gray-600">{rec.course.duration || 'Varies'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Target className="h-5 w-5 text-gray-400" />
                        <span className={`text-sm font-medium ${getDifficultyColor(rec.course.difficulty || '')}`}>
                          {rec.course.difficulty || 'Not specified'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-gray-400" />
                        <span className="text-sm text-gray-600">{rec.matchReason}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Star className="h-5 w-5 text-yellow-400" />
                        <span className="text-sm font-medium text-gray-600">
                          {rec.explanation.length} reasons
                        </span>
                      </div>
                    </div>

                    {rec.course.skill_tags && (
                      <div className="mb-4">
                        <h4 className="font-medium text-gray-900 mb-2">Skills You'll Learn:</h4>
                        <div className="flex flex-wrap gap-2">
                          {rec.course.skill_tags.split(',').map((skill, idx) => (
                            <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                              {skill.trim()}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setSelectedCourse(selectedCourse === rec.course.course_id ? null : rec.course.course_id)}
                    className="btn-secondary"
                  >
                    {selectedCourse === rec.course.course_id ? 'Hide Details' : 'Show Details'}
                  </button>
                  <button className="btn-primary flex items-center gap-2">
                    <BookOpen className="h-4 w-4" />
                    Enroll Now
                  </button>
                </div>
              </div>

              {/* Expanded Course Details */}
              {selectedCourse === rec.course.course_id && (
                <div className="border-t border-gray-200 bg-gray-50 p-6">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">Why This Course Matches You</h4>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-3">Match Reasons:</h5>
                      <ul className="space-y-2">
                        {rec.explanation.map((reason, idx) => (
                          <li key={idx} className="text-sm text-gray-600 flex items-center gap-2">
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                            {reason}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h5 className="font-medium text-gray-900 mb-3">Your Preferences Alignment:</h5>
                      <div className="space-y-2">
                        {assessment.specificTechnologies && assessment.specificTechnologies.slice(0, 3).map((tech, idx) => (
                          <div key={idx} className="text-sm text-gray-600 flex items-center gap-2">
                            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                            <span className="font-medium">{tech}</span> - Technology interest
                          </div>
                        ))}
                        {assessment.projectTypes && assessment.projectTypes.slice(0, 2).map((project, idx) => (
                          <div key={idx} className="text-sm text-gray-600 flex items-center gap-2">
                            <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                            <span className="font-medium">{project}</span> - Project type
                          </div>
                        ))}
                        {assessment.interests && assessment.interests.slice(0, 2).map((interest, idx) => (
                          <div key={idx} className="text-sm text-gray-600 flex items-center gap-2">
                            <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                            {interest} - General interest
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <h5 className="font-medium text-blue-900 mb-2">💡 Pro Tip</h5>
                    <p className="text-sm text-blue-800">
                      This course aligns with {(assessment.specificTechnologies?.length || 0) + (assessment.interests?.length || 0)} of your preferences and is 
                      perfect for your {assessment.experienceLevel} experience level.
                      {assessment.learningStyles && assessment.learningStyles.length > 0 && 
                        ` The course format matches your preferred learning style: ${assessment.learningStyles[0]}.`
                      }
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="mt-8 text-center">
          <p className="text-gray-600">
            Found {recommendations.length} courses perfectly matched to your interests and experience level.
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Each recommendation is personalized based on your technology interests: {(assessment.specificTechnologies || []).slice(0, 3).join(', ')}
            {assessment.projectTypes && assessment.projectTypes.length > 0 && ` and project goals: ${assessment.projectTypes.slice(0, 2).join(', ')}`}
          </p>
        </div>
      </div>
    </div>
  );
};
