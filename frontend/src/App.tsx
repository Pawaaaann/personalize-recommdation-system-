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
      // Check for saved assessment data first
      const assessmentKey = `assessment_${currentUser.uid}`;
      const savedAssessment = localStorage.getItem(assessmentKey);
      
      if (savedAssessment) {
        try {
          const assessment = JSON.parse(savedAssessment);
          setUserAssessment(assessment);
          setCurrentView('careers'); // Existing user with data: go to career recommendations
        } catch (error) {
          console.error('Failed to parse saved assessment:', error);
          // Clear corrupted data
          localStorage.removeItem(assessmentKey);
          setUserAssessment(null);
          setCurrentView('assessment'); // Corrupted data: retake assessment
        }
      } else {
        // Check if this is likely an existing user (has profile info from Google/other providers)
        const isLikelyExistingUser = currentUser.displayName || 
                                   (currentUser.email && !currentUser.email.includes('test')) ||
                                   currentUser.photoURL;
        
        if (isLikelyExistingUser) {
          // Existing user without saved assessment data - go to careers with empty assessment
          setUserAssessment(null);
          setCurrentView('careers');
        } else {
          // Truly new user: go to assessment
          setUserAssessment(null);
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
            <CareerRecommendations 
              assessment={userAssessment} 
              onViewLearningPath={handleViewLearningPath} 
            />
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
            {userAssessment ? (
              <InterestBasedRecommendations assessment={userAssessment} />
            ) : (
              <div className="max-w-6xl mx-auto px-4 py-8">
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 mb-6">
                  <h3 className="text-lg font-semibold text-amber-900 mb-2">⚠️ Assessment Data Not Found</h3>
                  <p className="text-amber-800 mb-4">
                    We couldn't find your previous assessment results. This might happen if you've cleared your browser data or are using a different device.
                    <br /><br />
                    <strong>To restore your personalized course recommendations:</strong>
                  </p>
                  <button
                    onClick={handleRetakeAssessment}
                    className="bg-amber-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-amber-700 transition-colors"
                  >
                    Retake Assessment (5 minutes)
                  </button>
                </div>
                
                {/* Show sample courses */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h4 className="font-semibold text-gray-900 mb-2">HTML, CSS & JavaScript</h4>
                    <p className="text-gray-600 text-sm mb-3">Foundation courses for web development</p>
                    <div className="text-sm text-gray-500">Various platforms available</div>
                  </div>
                  <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h4 className="font-semibold text-gray-900 mb-2">Python Programming</h4>
                    <p className="text-gray-600 text-sm mb-3">Learn programming fundamentals and data science</p>
                    <div className="text-sm text-gray-500">Various platforms available</div>
                  </div>
                  <div className="bg-white rounded-lg shadow-sm border p-6">
                    <h4 className="font-semibold text-gray-900 mb-2">React Development</h4>
                    <p className="text-gray-600 text-sm mb-3">Build modern frontend applications</p>
                    <div className="text-sm text-gray-500">Various platforms available</div>
                  </div>
                </div>
              </div>
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
        return <Dashboard 
          studentId={currentUser?.uid || ''} 
          onLogout={handleLogout} 
          assessment={userAssessment} 
          onTakeAssessment={handleRetakeAssessment}
        />;
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
