import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Login } from './components/Login';
import { Dashboard } from './components/Dashboard';
import { InterestAssessment } from './components/InterestAssessment';
import { CareerRecommendations } from './components/CareerRecommendations';
import { InterestBasedRecommendations } from './components/InterestBasedRecommendations';
import { LearningPath } from './components/LearningPath';
import { UserAssessment } from './components/InterestAssessment';

type AppView = 'login' | 'assessment' | 'careers' | 'course-recommendations' | 'learning-path' | 'dashboard';

function AppContent() {
  const { currentUser, loading } = useAuth();
  const [currentView, setCurrentView] = useState<AppView>('login');
  const [userAssessment, setUserAssessment] = useState<UserAssessment | null>(null);
  const [selectedCareerPath, setSelectedCareerPath] = useState<string>('');

  useEffect(() => {
    if (currentUser && !loading) {
      // Check if user has existing assessment
      const assessmentKey = `assessment_${currentUser.uid}`;
      const savedAssessment = localStorage.getItem(assessmentKey);
      
      if (savedAssessment) {
        try {
          const assessment = JSON.parse(savedAssessment);
          setUserAssessment(assessment);
          setCurrentView('dashboard'); // Existing user: go to dashboard
        } catch (error) {
          console.error('Failed to parse saved assessment:', error);
          setCurrentView('assessment'); // Fallback to assessment if data is corrupted
        }
      } else {
        // For existing users without saved assessment data, check if they're returning users
        // If user has displayName or email, they might be existing users - send to dashboard
        const hasCompletedAssessmentBefore = localStorage.getItem(`user_has_assessment_${currentUser.uid}`);
        
        if (hasCompletedAssessmentBefore) {
          // User has completed assessment before but localStorage was cleared
          // Take them to dashboard with a notice that they can retake assessment
          setCurrentView('dashboard');
        } else {
          // Truly new user: go to assessment
          setCurrentView('assessment');
        }
      }
    } else if (!currentUser && !loading) {
      setCurrentView('login'); // Not logged in: show login
    }
  }, [currentUser, loading]);



  const handleAssessmentComplete = (assessment: UserAssessment) => {
    setUserAssessment(assessment);
    // Save assessment for the current user
    if (currentUser) {
      localStorage.setItem(`assessment_${currentUser.uid}`, JSON.stringify(assessment));
      // Set flag to remember this user has completed an assessment
      localStorage.setItem(`user_has_assessment_${currentUser.uid}`, 'true');
    }
    setCurrentView('dashboard'); // After assessment, go to dashboard
  };

  const handleViewLearningPath = (careerPath: string) => {
    setSelectedCareerPath(careerPath);
    setCurrentView('learning-path');
  };

  const handleViewCourseRecommendations = () => {
    setCurrentView('course-recommendations');
  };

  const handleBackToCareers = () => {
    setCurrentView('careers');
  };

  const handleLogout = () => {
    setUserAssessment(null);
    setCurrentView('login');
    // Keep assessment data in localStorage for future logins
  };

  const handleRetakeAssessment = () => {
    setUserAssessment(null);
    setCurrentView('assessment');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'login':
        return <Login />;
      case 'assessment':
        return <InterestAssessment onComplete={handleAssessmentComplete} />;
      case 'careers':
        return (
          <div>
            <div className="bg-white shadow-sm border-b">
              <div className="max-w-6xl mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">Career Guidance System</h1>
                    <p className="text-gray-600">Welcome back, {currentUser?.displayName || currentUser?.email}</p>
                    {userAssessment && (
                      <p className="text-sm text-gray-500 mt-1">
                        Based on your interests in {userAssessment.selectedDomain} and {userAssessment.selectedSubdomain}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={handleRetakeAssessment}
                      className="btn-secondary"
                    >
                      Retake Assessment
                    </button>
                    <button
                      onClick={handleLogout}
                      className="btn-secondary"
                    >
                      Logout
                    </button>
                  </div>
                </div>
                
                {/* Navigation Tabs */}
                <div className="flex gap-4 mt-6">
                  <button
                    onClick={() => setCurrentView('careers')}
                    className="bg-primary-600 text-white px-4 py-2 rounded-lg font-medium"
                  >
                    Career Paths
                  </button>
                  <button
                    onClick={handleViewCourseRecommendations}
                    className="bg-gray-100 text-gray-700 hover:bg-gray-200 px-4 py-2 rounded-lg font-medium transition-colors"
                  >
                    Course Recommendations
                  </button>
                </div>
              </div>
            </div>
            {userAssessment && (
              <CareerRecommendations 
                assessment={userAssessment} 
                onViewLearningPath={handleViewLearningPath} 
              />
            )}
          </div>
        );
      case 'course-recommendations':
        return (
          <div>
            <div className="bg-white shadow-sm border-b">
              <div className="max-w-6xl mx-auto px-4 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">Course Recommendations</h1>
                    <p className="text-gray-600">Personalized courses based on your interests</p>
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={handleBackToCareers}
                      className="btn-secondary"
                    >
                      Back to Career Paths
                    </button>
                    <button
                      onClick={handleLogout}
                      className="btn-secondary"
                    >
                      Logout
                    </button>
                  </div>
                </div>
                

              </div>
            </div>
            {userAssessment && (
              <InterestBasedRecommendations assessment={userAssessment} />
            )}
          </div>
        );
      case 'learning-path':
        return (
          <LearningPath
            careerPathId={selectedCareerPath}
            assessment={userAssessment}
            onBack={handleBackToCareers}
          />
        );
      case 'dashboard':
        return <Dashboard studentId={currentUser?.uid || ''} onLogout={handleLogout} assessment={userAssessment} />;
      default:
        return <Login />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50">
      {renderCurrentView()}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
