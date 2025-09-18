import React, { useState } from 'react';
import { LogOut, User, BookOpen, Mail, Target, Clock, TrendingUp, DollarSign, Star, ExternalLink } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { UserAssessment } from './InterestAssessment';

interface CareerPath {
  id: string;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  skills: string[];
  salaryRange: string;
  growthPotential: 'high' | 'medium' | 'low' | 'very high';
  matchScore: number;
  learningPath: LearningPhase[];
}

interface LearningPhase {
  phase: string;
  duration: string;
  topics: string[];
  courses: Course[];
  projects: string[];
}

interface Course {
  title: string;
  platform: 'coursera' | 'udemy' | 'edx' | 'freecodecamp';
  url: string;
  rating: number;
  duration: string;
  level: string;
  price: string;
}

// Career paths data
const CAREER_PATHS: Record<string, CareerPath[]> = {
  'web-development': [
    {
      id: 'frontend-developer',
      name: 'Frontend Developer',
      description: 'Build user interfaces and interactive web experiences',
      difficulty: 'beginner',
      estimatedTime: '6-12 months',
      skills: ['HTML', 'CSS', 'JavaScript', 'React', 'UI/UX'],
      salaryRange: '$60K - $120K',
      growthPotential: 'high',
      matchScore: 85,
      learningPath: [
        {
          phase: 'Foundation (Months 1-3)',
          duration: '3 months',
          topics: ['HTML Fundamentals', 'CSS Styling', 'JavaScript Basics', 'Responsive Design'],
          courses: [
            {
              title: 'HTML, CSS, and Javascript for Web Developers',
              platform: 'coursera',
              url: 'https://www.coursera.org/learn/html-css-javascript-for-web-developers',
              rating: 4.7,
              duration: '40 hours',
              level: 'Beginner',
              price: 'Free'
            }
          ],
          projects: ['Personal Portfolio Website', 'Restaurant Landing Page', 'Weather App UI']
        },
        {
          phase: 'Intermediate (Months 4-6)',
          duration: '3 months',
          topics: ['React Framework', 'State Management', 'API Integration', 'Testing'],
          courses: [
            {
              title: 'React - The Complete Guide',
              platform: 'udemy',
              url: 'https://www.udemy.com/course/react-the-complete-guide-incl-redux/',
              rating: 4.6,
              duration: '48 hours',
              level: 'Intermediate',
              price: '$84.99'
            }
          ],
          projects: ['Todo App with React', 'E-commerce Product Catalog', 'Social Media Dashboard']
        }
      ]
    },
    {
      id: 'backend-developer',
      name: 'Backend Developer',
      description: 'Develop server-side logic and APIs',
      difficulty: 'intermediate',
      estimatedTime: '8-18 months',
      skills: ['Python', 'Node.js', 'Databases', 'APIs', 'Cloud'],
      salaryRange: '$70K - $140K',
      growthPotential: 'high',
      matchScore: 80,
      learningPath: [
        {
          phase: 'Foundation (Months 1-6)',
          duration: '6 months',
          topics: ['Python/Node.js', 'Database Design', 'API Development', 'Authentication'],
          courses: [
            {
              title: 'Python for Everybody',
              platform: 'coursera',
              url: 'https://www.coursera.org/specializations/python',
              rating: 4.8,
              duration: '80 hours',
              level: 'Beginner',
              price: 'Free'
            }
          ],
          projects: ['REST API', 'User Authentication System', 'Database Management App']
        }
      ]
    },
    {
      id: 'full-stack-developer',
      name: 'Full-Stack Developer',
      description: 'Handle both frontend and backend development',
      difficulty: 'advanced',
      estimatedTime: '12-24 months',
      skills: ['Full-stack technologies', 'System Design', 'DevOps'],
      salaryRange: '$80K - $150K',
      growthPotential: 'high',
      matchScore: 78,
      learningPath: [
        {
          phase: 'Full-Stack Integration (Months 1-12)',
          duration: '12 months',
          topics: ['Frontend + Backend', 'Database Design', 'API Integration', 'Deployment'],
          courses: [
            {
              title: 'Full Stack Web Development',
              platform: 'coursera',
              url: 'https://www.coursera.org/specializations/full-stack-web-development',
              rating: 4.6,
              duration: '120 hours',
              level: 'Advanced',
              price: 'Free'
            }
          ],
          projects: ['Complete E-commerce Platform', 'Social Media App', 'Real-time Chat Application']
        }
      ]
    }
  ],
  'data-science': [
    {
      id: 'data-analyst',
      name: 'Data Analyst',
      description: 'Analyze data to help businesses make decisions',
      difficulty: 'beginner',
      estimatedTime: '4-8 months',
      skills: ['SQL', 'Python', 'Excel', 'Statistics', 'Visualization'],
      salaryRange: '$50K - $90K',
      growthPotential: 'high',
      matchScore: 85,
      learningPath: [
        {
          phase: 'Foundation (Months 1-4)',
          duration: '4 months',
          topics: ['SQL Fundamentals', 'Excel/Google Sheets', 'Python Basics', 'Statistics'],
          courses: [
            {
              title: 'Google Data Analytics Professional Certificate',
              platform: 'coursera',
              url: 'https://www.coursera.org/professional-certificates/google-data-analytics',
              rating: 4.6,
              duration: '180 hours',
              level: 'Beginner',
              price: 'Free'
            }
          ],
          projects: ['Sales Data Analysis', 'Customer Behavior Analysis', 'Financial Dashboard']
        }
      ]
    },
    {
      id: 'data-scientist',
      name: 'Data Scientist',
      description: 'Build predictive models and advanced analytics',
      difficulty: 'advanced',
      estimatedTime: '12-24 months',
      skills: ['Machine Learning', 'Python', 'Statistics', 'Big Data'],
      salaryRange: '$80K - $150K',
      growthPotential: 'high',
      matchScore: 80,
      learningPath: [
        {
          phase: 'Machine Learning (Months 1-12)',
          duration: '12 months',
          topics: ['Machine Learning', 'Deep Learning', 'Python/R', 'Big Data Tools'],
          courses: [
            {
              title: 'Machine Learning Specialization',
              platform: 'coursera',
              url: 'https://www.coursera.org/specializations/machine-learning-introduction',
              rating: 4.9,
              duration: '120 hours',
              level: 'Advanced',
              price: 'Free'
            }
          ],
          projects: ['Predictive Model', 'Recommendation System', 'Computer Vision App']
        }
      ]
    }
  ],
  'cybersecurity': [
    {
      id: 'cybersecurity-analyst',
      name: 'Cybersecurity Analyst',
      description: 'Protect systems and networks from cyber threats',
      difficulty: 'intermediate',
      estimatedTime: '8-18 months',
      skills: ['Network Security', 'Ethical Hacking', 'Incident Response'],
      salaryRange: '$70K - $120K',
      growthPotential: 'very high',
      matchScore: 85,
      learningPath: [
        {
          phase: 'Security Fundamentals (Months 1-8)',
          duration: '8 months',
          topics: ['Network Security', 'Ethical Hacking', 'Security Tools', 'Compliance'],
          courses: [
            {
              title: 'Google Cybersecurity Professional Certificate',
              platform: 'coursera',
              url: 'https://www.coursera.org/professional-certificates/google-cybersecurity',
              rating: 4.7,
              duration: '180 hours',
              level: 'Intermediate',
              price: 'Free'
            }
          ],
          projects: ['Security Assessment', 'Incident Response Plan', 'Penetration Testing']
        }
      ]
    }
  ],
  'digital-marketing': [
    {
      id: 'digital-marketer',
      name: 'Digital Marketer',
      description: 'Create and manage online marketing campaigns',
      difficulty: 'beginner',
      estimatedTime: '3-6 months',
      skills: ['SEO', 'Social Media', 'Google Ads', 'Analytics'],
      salaryRange: '$40K - $80K',
      growthPotential: 'high',
      matchScore: 85,
      learningPath: [
        {
          phase: 'Digital Marketing Basics (Months 1-3)',
          duration: '3 months',
          topics: ['SEO', 'Social Media Marketing', 'Google Ads', 'Analytics'],
          courses: [
            {
              title: 'Google Digital Marketing & E-commerce Certificate',
              platform: 'coursera',
              url: 'https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce',
              rating: 4.7,
              duration: '120 hours',
              level: 'Beginner',
              price: 'Free'
            }
          ],
          projects: ['SEO Campaign', 'Social Media Strategy', 'PPC Campaign']
        }
      ]
    }
  ],
  'product-management': [
    {
      id: 'product-manager',
      name: 'Product Manager',
      description: 'Lead product strategy and development',
      difficulty: 'intermediate',
      estimatedTime: '6-12 months',
      skills: ['Product Strategy', 'User Research', 'Analytics', 'Leadership'],
      salaryRange: '$80K - $140K',
      growthPotential: 'high',
      matchScore: 85,
      learningPath: [
        {
          phase: 'Product Management Fundamentals (Months 1-6)',
          duration: '6 months',
          topics: ['Product Strategy', 'User Research', 'Product Analytics', 'Agile Methodology'],
          courses: [
            {
              title: 'Product Management Fundamentals',
              platform: 'udemy',
              url: 'https://www.udemy.com/course/product-management-fundamentals/',
              rating: 4.5,
              duration: '40 hours',
              level: 'Intermediate',
              price: '$79.99'
            }
          ],
          projects: ['Product Roadmap', 'User Research Study', 'Product Launch Plan']
        }
      ]
    }
  ]
};

interface DashboardProps {
  studentId: string;
  onLogout: () => void;
  assessment: UserAssessment | null;
  onTakeAssessment: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ studentId, onLogout, assessment, onTakeAssessment }) => {
  const [selectedCareerPath, setSelectedCareerPath] = useState<CareerPath | null>(null);
  const { currentUser } = useAuth();

  // Get career paths based on assessment
  const getRecommendedCareerPaths = (): CareerPath[] => {
    if (!assessment) return [];
    
    const pathsForSubdomain = CAREER_PATHS[assessment.selectedSubdomain] || [];
    
    // Calculate match scores based on assessment
    return pathsForSubdomain.map(path => {
      let score = path.matchScore;
      
      // Adjust score based on experience level
      if (assessment.experienceLevel === 'beginner' && path.difficulty === 'beginner') {
        score += 10;
      } else if (assessment.experienceLevel === 'intermediate' && path.difficulty === 'intermediate') {
        score += 10;
      } else if (assessment.experienceLevel === 'advanced' && path.difficulty === 'advanced') {
        score += 10;
      }
      
      // Adjust score based on time commitment
      if (assessment.timeCommitment === 'full-time') {
        score += 5;
      }
      
      return { ...path, matchScore: Math.min(score, 100) };
    }).sort((a, b) => b.matchScore - a.matchScore);
  };

  const recommendedPaths = getRecommendedCareerPaths();

  if (!assessment) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="text-gray-400 text-6xl mb-4">📋</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome Back!</h2>
          <p className="text-gray-600 mb-6">
            Complete your career assessment to see personalized recommendations and get started.
          </p>
          <div className="flex gap-4 justify-center">
            <button onClick={onTakeAssessment} className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors">
              Take Assessment
            </button>
            <button onClick={onLogout} className="btn-secondary">
              Logout
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Get display name from Firebase user or fallback to studentId
  const displayName = currentUser?.displayName || currentUser?.email?.split('@')[0] || studentId;
  const userEmail = currentUser?.email;

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
              {/* User Info */}
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <User className="h-4 w-4" />
                  <span className="font-medium">{displayName}</span>
                </div>
                {userEmail && (
                  <div className="flex items-center space-x-1 text-gray-500">
                    <Mail className="h-3 w-3" />
                    <span className="hidden sm:inline">{userEmail}</span>
                  </div>
                )}
              </div>
              
              <button
                onClick={() => setSelectedCareerPath(null)}
                className="btn-secondary flex items-center gap-2"
                aria-label="View all paths"
              >
                <Target className="h-4 w-4" />
                <span className="hidden sm:inline">All Paths</span>
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
        {/* Assessment Summary */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {displayName}!
          </h2>
          <p className="text-gray-600">
            Your personalized career roadmap based on your assessment
          </p>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center gap-2 text-blue-800 font-medium">
              <Target className="h-5 w-5" />
              Your Profile: {assessment.selectedDomain} - {assessment.selectedSubdomain}
            </div>
            <p className="text-blue-600 text-sm mt-1">
              Experience: {assessment.experienceLevel} | Time Commitment: {assessment.timeCommitment}
            </p>
          </div>
        </div>

        {selectedCareerPath ? (
          /* Detailed Career Path View */
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <button
                onClick={() => setSelectedCareerPath(null)}
                className="text-primary-600 hover:text-primary-800 font-medium"
              >
                ← Back to All Career Paths
              </button>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">{selectedCareerPath.name}</h3>
                  <p className="text-gray-600 mt-1">{selectedCareerPath.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-green-600">{selectedCareerPath.matchScore}%</div>
                  <div className="text-sm text-gray-500">Match Score</div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <Clock className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                  <div className="text-sm font-medium text-gray-900">{selectedCareerPath.estimatedTime}</div>
                  <div className="text-xs text-gray-500">Duration</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <DollarSign className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                  <div className="text-sm font-medium text-gray-900">{selectedCareerPath.salaryRange}</div>
                  <div className="text-xs text-gray-500">Salary Range</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <TrendingUp className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                  <div className="text-sm font-medium text-gray-900 capitalize">{selectedCareerPath.growthPotential}</div>
                  <div className="text-xs text-gray-500">Growth</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <Target className="h-6 w-6 text-gray-600 mx-auto mb-2" />
                  <div className="text-sm font-medium text-gray-900 capitalize">{selectedCareerPath.difficulty}</div>
                  <div className="text-xs text-gray-500">Level</div>
                </div>
              </div>
              
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-3">Required Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedCareerPath.skills.map((skill, index) => (
                    <span key={index} className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Learning Roadmap</h4>
                <div className="space-y-6">
                  {selectedCareerPath.learningPath.map((phase, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h5 className="text-lg font-medium text-gray-900">{phase.phase}</h5>
                        <span className="text-sm text-gray-500">{phase.duration}</span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <h6 className="font-medium text-gray-700 mb-2">Topics</h6>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {phase.topics.map((topic, topicIndex) => (
                              <li key={topicIndex} className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 bg-primary-500 rounded-full" />
                                {topic}
                              </li>
                            ))}
                          </ul>
                        </div>
                        
                        <div>
                          <h6 className="font-medium text-gray-700 mb-2">Courses</h6>
                          <div className="space-y-2">
                            {phase.courses.map((course, courseIndex) => (
                              <div key={courseIndex} className="border border-gray-200 rounded p-3 text-sm">
                                <div className="font-medium text-gray-900">{course.title}</div>
                                <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                                  <span className="capitalize">{course.platform}</span>
                                  <span className="flex items-center gap-1">
                                    <Star className="h-3 w-3 text-yellow-400 fill-current" />
                                    {course.rating}
                                  </span>
                                  <span>{course.duration}</span>
                                  <span className="font-medium text-green-600">{course.price}</span>
                                </div>
                                <a 
                                  href={course.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 mt-2 text-primary-600 hover:text-primary-800 text-xs"
                                >
                                  View Course <ExternalLink className="h-3 w-3" />
                                </a>
                              </div>
                            ))}
                          </div>
                        </div>
                        
                        <div>
                          <h6 className="font-medium text-gray-700 mb-2">Projects</h6>
                          <ul className="text-sm text-gray-600 space-y-1">
                            {phase.projects.map((project, projectIndex) => (
                              <li key={projectIndex} className="flex items-center gap-2">
                                <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                                {project}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Career Paths Overview */
          <div>
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Recommended Career Paths</h3>
              <p className="text-gray-600">
                Based on your interest in {assessment.selectedDomain} and {assessment.selectedSubdomain}
              </p>
            </div>
            
            {recommendedPaths.length > 0 ? (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {recommendedPaths.map((path) => (
                  <div key={path.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h4 className="text-xl font-semibold text-gray-900">{path.name}</h4>
                        <p className="text-gray-600 mt-1">{path.description}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-green-600">{path.matchScore}%</div>
                        <div className="text-xs text-gray-500">Match</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Clock className="h-4 w-4" />
                        <span>{path.estimatedTime}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <DollarSign className="h-4 w-4" />
                        <span>{path.salaryRange}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <TrendingUp className="h-4 w-4" />
                        <span className="capitalize">{path.growthPotential} Growth</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <Target className="h-4 w-4" />
                        <span className="capitalize">{path.difficulty} Level</span>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <div className="text-sm font-medium text-gray-700 mb-2">Key Skills:</div>
                      <div className="flex flex-wrap gap-1">
                        {path.skills.slice(0, 4).map((skill, index) => (
                          <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                            {skill}
                          </span>
                        ))}
                        {path.skills.length > 4 && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-500 rounded text-xs">
                            +{path.skills.length - 4} more
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <button
                      onClick={() => setSelectedCareerPath(path)}
                      className="w-full btn-primary"
                    >
                      View Learning Roadmap
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">🎯</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No career paths found</h3>
                <p className="text-gray-600">
                  We couldn't find career paths for your selected interests. Please retake the assessment.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};
