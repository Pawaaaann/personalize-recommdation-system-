import React, { useState } from 'react';
import { Clock, TrendingUp, DollarSign, BookOpen, Star, ExternalLink } from 'lucide-react';
import { UserAssessment } from './InterestAssessment';

interface CareerRecommendationsProps {
  assessment: UserAssessment | null;
  onViewLearningPath: (careerPath: string) => void;
}

interface CareerPath {
  id: string;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  skills: string[];
  salaryRange: string;
  growthPotential: 'high' | 'medium' | 'low' | 'very high';
  matchScore: number; // baseline score
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

// Map subdomain ids -> career paths
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
              level: 'Intermediate',
              price: '$49/month'
            }
          ],
          projects: ['E-commerce Platform', 'Social Media App', 'Project Management Tool']
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
      skills: ['SQL', 'Python', 'Excel', 'Statistics', 'Visualization', 'Data Analysis'],
      salaryRange: '$50K - $90K',
      growthPotential: 'high',
      matchScore: 84,
      learningPath: [
        {
          phase: 'Foundation (Months 1-2)',
          duration: '2 months',
          topics: ['SQL Fundamentals', 'Excel Advanced', 'Basic Statistics'],
          courses: [
            {
              title: 'SQL for Data Science',
              platform: 'coursera',
              url: 'https://www.coursera.org/learn/sql-for-data-science',
              rating: 4.6,
              duration: '20 hours',
              level: 'Beginner',
              price: 'Free'
            }
          ],
          projects: ['Sales Data Analysis', 'Customer Segmentation', 'Performance Dashboard']
        }
      ]
    },
    {
      id: 'data-scientist',
      name: 'Data Scientist',
      description: 'Build predictive models and advanced analytics',
      difficulty: 'advanced',
      estimatedTime: '12-24 months',
      skills: ['Machine Learning', 'Python', 'Statistics', 'Big Data', 'Deep Learning'],
      salaryRange: '$80K - $150K',
      growthPotential: 'high',
      matchScore: 82,
      learningPath: [
        {
          phase: 'Foundation (Months 1-6)',
          duration: '6 months',
          topics: ['Python Programming', 'Statistics & Mathematics', 'Data Manipulation', 'Data Visualization'],
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
          projects: ['Data Analysis Portfolio', 'Statistical Analysis Report', 'Interactive Dashboards']
        }
      ]
    },
    {
      id: 'business-intelligence-analyst',
      name: 'Business Intelligence Analyst',
      description: 'Transform data into actionable business insights',
      difficulty: 'intermediate',
      estimatedTime: '6-12 months',
      skills: ['SQL', 'Power BI', 'Tableau', 'Business Analysis', 'Data Modeling', 'Analytics'],
      salaryRange: '$60K - $100K',
      growthPotential: 'high',
      matchScore: 80,
      learningPath: [
        {
          phase: 'BI Tools & Analysis (Months 1-6)',
          duration: '6 months',
          topics: ['Power BI', 'Tableau', 'Data Modeling', 'Business Analysis'],
          courses: [
            {
              title: 'Power BI for Beginners',
              platform: 'udemy',
              url: 'https://www.udemy.com/course/power-bi-complete-introduction/',
              rating: 4.7,
              duration: '15 hours',
              level: 'Beginner',
              price: '$19.99'
            }
          ],
          projects: ['Sales Dashboard', 'Customer Analytics Report', 'KPI Tracking System']
        }
      ]
    }
  ],
  // Business subdomains
  'digital-marketing': [
    {
      id: 'digital-marketer',
      name: 'Digital Marketer',
      description: 'Create and manage online marketing campaigns',
      difficulty: 'beginner',
      estimatedTime: '3-6 months',
      skills: ['SEO', 'Social Media', 'Google Ads', 'Analytics', 'Content Marketing'],
      salaryRange: '$40K - $80K',
      growthPotential: 'high',
      matchScore: 78,
      learningPath: [
        {
          phase: 'Digital Marketing Fundamentals (Months 1-3)',
          duration: '3 months',
          topics: ['SEO Basics', 'Social Media Marketing', 'Google Ads', 'Analytics'],
          courses: [
            {
              title: 'Digital Marketing Specialization',
              platform: 'coursera',
              url: 'https://www.coursera.org/specializations/digital-marketing',
              rating: 4.7,
              duration: '60 hours',
              level: 'Beginner',
              price: 'Free'
            }
          ],
          projects: ['SEO Campaign', 'Social Media Strategy', 'Google Ads Campaign']
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
      estimatedTime: '8-18 months',
      skills: ['Product Strategy', 'User Research', 'Agile', 'Data Analysis', 'Leadership'],
      salaryRange: '$70K - $130K',
      growthPotential: 'high',
      matchScore: 75,
      learningPath: [
        {
          phase: 'Product Management Fundamentals (Months 1-8)',
          duration: '8 months',
          topics: ['Product Strategy', 'User Research', 'Agile Methodology', 'Data Analysis'],
          courses: [
            {
              title: 'Product Management Specialization',
              platform: 'coursera',
              url: 'https://www.coursera.org/specializations/product-management',
              rating: 4.6,
              duration: '80 hours',
              level: 'Intermediate',
              price: '$49/month'
            }
          ],
          projects: ['Product Roadmap', 'User Research Report', 'MVP Development Plan']
        }
      ]
    }
  ],
  // Creative subdomains
  'ui-ux-design': [
    {
      id: 'ui-designer',
      name: 'UI Designer',
      description: 'Create beautiful and functional user interfaces',
      difficulty: 'beginner',
      estimatedTime: '6-12 months',
      skills: ['Figma', 'Adobe Creative Suite', 'Design Principles', 'Prototyping', 'User Research'],
      salaryRange: '$50K - $100K',
      growthPotential: 'high',
      matchScore: 72,
      learningPath: [
        {
          phase: 'Design Fundamentals (Months 1-6)',
          duration: '6 months',
          topics: ['Design Principles', 'Figma', 'Prototyping', 'User Research'],
          courses: [
            {
              title: 'UI/UX Design Specialization',
              platform: 'coursera',
              url: 'https://www.coursera.org/specializations/ui-ux-design',
              rating: 4.5,
              duration: '70 hours',
              level: 'Beginner',
              price: '$49/month'
            }
          ],
          projects: ['Mobile App Design', 'Website Redesign', 'Design System']
        }
      ]
    }
  ],
  'content-creation': [
    {
      id: 'content-creator',
      name: 'Content Creator',
      description: 'Create engaging digital content for various platforms',
      difficulty: 'beginner',
      estimatedTime: '3-6 months',
      skills: ['Content Writing', 'Social Media', 'Video Editing', 'Photography', 'Storytelling'],
      salaryRange: '$35K - $70K',
      growthPotential: 'medium',
      matchScore: 68,
      learningPath: [
        {
          phase: 'Content Creation Fundamentals (Months 1-3)',
          duration: '3 months',
          topics: ['Content Writing', 'Social Media Strategy', 'Basic Video Editing', 'Photography'],
          courses: [
            {
              title: 'Content Marketing Strategy',
              platform: 'udemy',
              url: 'https://www.udemy.com/course/content-marketing-masterclass/',
              rating: 4.6,
              duration: '12 hours',
              level: 'Beginner',
              price: '$19.99'
            }
          ],
          projects: ['Content Calendar', 'Social Media Campaign', 'Video Content Series']
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
      skills: ['Network Security', 'Ethical Hacking', 'Incident Response', 'Security Tools', 'Compliance'],
      salaryRange: '$70K - $120K',
      growthPotential: 'very high',
      matchScore: 70,
      learningPath: [
        {
          phase: 'Security Fundamentals (Months 1-8)',
          duration: '8 months',
          topics: ['Network Security', 'Ethical Hacking', 'Security Tools', 'Incident Response'],
          courses: [
            {
              title: 'Cybersecurity Specialization',
              platform: 'coursera',
              url: 'https://www.coursera.org/specializations/cybersecurity',
              rating: 4.7,
              duration: '90 hours',
              level: 'Intermediate',
              price: '$49/month'
            }
          ],
          projects: ['Security Assessment Report', 'Incident Response Plan', 'Security Policy Document']
        }
      ]
    }
  ]
};

export const CareerRecommendations: React.FC<CareerRecommendationsProps> = ({ 
  assessment, 
  onViewLearningPath 
}) => {
  const [selectedCareerPath, setSelectedCareerPath] = useState<string>('');

  // Strictly use the selected subdomain's career paths
  // Add fallback for cases where selectedSubdomain might be undefined or empty
  const selectedSubdomain = assessment?.selectedSubdomain || '';
  let availableCareerPaths = CAREER_PATHS[selectedSubdomain] || [];
  
  // If no career paths found for the selected subdomain, show paths from all domains
  if (availableCareerPaths.length === 0) {
    availableCareerPaths = Object.values(CAREER_PATHS).flat();
  }

  // Dynamic scoring: boost by interests overlap and experience fit
  const normalizedInterests = (assessment?.interests || []).map(i => i.toLowerCase());
  const experienceWeight = (difficulty: CareerPath['difficulty']) => {
    const userLevel = assessment?.experienceLevel || 'beginner';
    if (userLevel === 'beginner') {
      return difficulty === 'beginner' ? 10 : difficulty === 'intermediate' ? 0 : -10;
    }
    if (userLevel === 'intermediate') {
      return difficulty === 'beginner' ? 5 : difficulty === 'intermediate' ? 10 : 0;
    }
    // advanced
    return difficulty === 'advanced' ? 10 : 0;
  };

  const computeSortScore = (path: CareerPath): number => {
    const skills = path.skills.map(s => s.toLowerCase());
    const interestMatches = normalizedInterests.reduce((acc, interest) => {
      const matched = skills.some(skill => skill.includes(interest) || interest.includes(skill));
      return acc + (matched ? 1 : 0);
    }, 0);
    const interestBonus = Math.min(interestMatches * 5, 20); // up to +20
    const levelBonus = experienceWeight(path.difficulty);
    return path.matchScore + interestBonus + levelBonus;
  };

  const filteredCareerPaths = availableCareerPaths
    .filter(path => {
      const userLevel = assessment?.experienceLevel || 'beginner';
      if (userLevel === 'beginner') return path.difficulty !== 'advanced';
      if (userLevel === 'intermediate') return path.difficulty !== 'advanced' || true;
      return true;
    })
    .sort((a, b) => computeSortScore(b) - computeSortScore(a))
    .slice(0, 10);

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-600 bg-green-100';
      case 'intermediate': return 'text-yellow-600 bg-yellow-100';
      case 'advanced': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getGrowthColor = (growth: string) => {
    switch (growth) {
      case 'very high': return 'text-purple-600 bg-purple-100';
      case 'high': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Your Career Path Recommendations
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {assessment?.selectedDomain && assessment?.selectedSubdomain ? (
              <>Based on your interests in <strong>{assessment.selectedDomain}</strong> and 
              <strong> {assessment.selectedSubdomain}</strong>, here are the best career paths for you</>
            ) : (
              <>Explore these career paths across all domains to find what interests you most</>
            )}
          </p>
          <p className="text-lg text-gray-500 mt-2">
            Showing {filteredCareerPaths.length} {assessment?.selectedDomain ? 'personalized ' : ''}recommendations
          </p>
        </div>

        {/* Career Paths */}
        <div className="space-y-6">
          {filteredCareerPaths.map((careerPath) => (
            <div key={careerPath.id} className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-2xl font-bold text-gray-900">{careerPath.name}</h3>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColor(careerPath.difficulty)}`}>
                        {careerPath.difficulty}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-4">{careerPath.description}</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="flex items-center gap-2">
                        <Clock className="h-5 w-5 text-gray-400" />
                        <span className="text-sm text-gray-600">{careerPath.estimatedTime}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <DollarSign className="h-5 w-5 text-gray-400" />
                        <span className="text-sm text-gray-600">{careerPath.salaryRange}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-gray-400" />
                        <span className={`text-sm font-medium ${getGrowthColor(careerPath.growthPotential)}`}>{careerPath.growthPotential} growth</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Star className="h-5 w-5 text-yellow-400" />
                        <span className={`text-sm font-medium ${getMatchScoreColor(careerPath.matchScore)}`}>
                          {careerPath.matchScore}% base match
                        </span>
                      </div>
                    </div>

                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2">Key Skills You'll Learn:</h4>
                      <div className="flex flex-wrap gap-2">
                        {careerPath.skills.map((skill) => (
                          <span key={skill} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => onViewLearningPath(careerPath.id)}
                    className="btn-primary flex items-center gap-2"
                  >
                    <BookOpen className="h-4 w-4" />
                    View Learning Path
                  </button>
                  <button
                    onClick={() => setSelectedCareerPath(selectedCareerPath === careerPath.id ? '' : careerPath.id)}
                    className="btn-secondary"
                  >
                    {selectedCareerPath === careerPath.id ? 'Hide Details' : 'Show Details'}
                  </button>
                </div>
              </div>

              {/* Expanded Learning Path Details */}
              {selectedCareerPath === careerPath.id && (
                <div className="border-t border-gray-200 bg-gray-50 p-6">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">Learning Roadmap</h4>
                  <div className="space-y-6">
                    {careerPath.learningPath.map((phase, index) => (
                      <div key={index} className="bg-white rounded-lg p-4 border border-gray-200">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                            {index + 1}
                          </div>
                          <div>
                            <h5 className="font-semibold text-gray-900">{phase.phase}</h5>
                            <p className="text-sm text-gray-600">{phase.duration}</p>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <h6 className="font-medium text-gray-900 mb-2">Topics Covered:</h6>
                            <ul className="space-y-1">
                              {phase.topics.map((topic, idx) => (
                                <li key={idx} className="text-sm text-gray-600 flex items-center gap-2">
                                  <div className="w-2 h-2 bg-primary-400 rounded-full"></div>
                                  {topic}
                                </li>
                              ))}
                            </ul>
                          </div>
                          
                          <div>
                            <h6 className="font-medium text-gray-900 mb-2">Recommended Courses:</h6>
                            <div className="space-y-2">
                              {phase.courses.map((course, idx) => (
                                <div key={idx} className="text-sm">
                                  <a 
                                    href={course.url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="text-primary-600 hover:text-primary-800 flex items-center gap-1"
                                  >
                                    {course.title}
                                    <ExternalLink className="h-3 w-3" />
                                  </a>
                                  <div className="text-gray-500 text-xs">
                                    {course.platform} • {course.duration} • {course.price}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                          
                          <div>
                            <h6 className="font-medium text-gray-900 mb-2">Projects to Build:</h6>
                            <ul className="space-y-1">
                              {phase.projects.map((project, idx) => (
                                <li key={idx} className="text-sm text-gray-600 flex items-center gap-2">
                                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
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
              )}
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="mt-8 text-center">
          <p className="text-gray-600">
            Found {filteredCareerPaths.length} career paths matching your interests and experience level.
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Click "View Learning Path" to see detailed study schedules and course recommendations.
          </p>
        </div>
      </div>
    </div>
  );
};
