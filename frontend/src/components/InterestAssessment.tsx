import React, { useState } from 'react';
import { BookOpen, Target, TrendingUp, Clock, CheckCircle } from 'lucide-react';

interface Domain {
  id: string;
  name: string;
  description: string;
  icon: string;
  subdomains: Subdomain[];
}

interface Subdomain {
  id: string;
  name: string;
  description: string;
  careerPaths: CareerPath[];
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
}

interface InterestAssessmentProps {
  onComplete: (assessment: UserAssessment) => void;
}

export interface UserAssessment {
  selectedDomain: string;
  selectedSubdomain: string;
  interests: string[];
  experienceLevel: 'beginner' | 'intermediate' | 'advanced';
  timeCommitment: 'part-time' | 'full-time' | 'flexible';
  learningGoals: string[];
}

const DOMAINS: Domain[] = [
  {
    id: 'technology',
    name: 'Technology & Software',
    description: 'Software development, IT, cybersecurity, and emerging tech',
    icon: '💻',
    subdomains: [
      {
        id: 'web-development',
        name: 'Web Development',
        description: 'Frontend, backend, and full-stack development',
        careerPaths: [
          {
            id: 'frontend-developer',
            name: 'Frontend Developer',
            description: 'Build user interfaces and interactive web experiences',
            difficulty: 'beginner',
            estimatedTime: '6-12 months',
            skills: ['HTML', 'CSS', 'JavaScript', 'React', 'UI/UX'],
            salaryRange: '$60K - $120K',
            growthPotential: 'high'
          },
          {
            id: 'backend-developer',
            name: 'Backend Developer',
            description: 'Develop server-side logic and APIs',
            difficulty: 'intermediate',
            estimatedTime: '8-18 months',
            skills: ['Python', 'Node.js', 'Databases', 'APIs', 'Cloud'],
            salaryRange: '$70K - $140K',
            growthPotential: 'high'
          },
          {
            id: 'full-stack-developer',
            name: 'Full-Stack Developer',
            description: 'Handle both frontend and backend development',
            difficulty: 'advanced',
            estimatedTime: '12-24 months',
            skills: ['Full-stack technologies', 'System Design', 'DevOps'],
            salaryRange: '$80K - $150K',
            growthPotential: 'high'
          }
        ]
      },
      {
        id: 'data-science',
        name: 'Data Science & AI',
        description: 'Machine learning, data analysis, and artificial intelligence',
        careerPaths: [
          {
            id: 'data-analyst',
            name: 'Data Analyst',
            description: 'Analyze data to help businesses make decisions',
            difficulty: 'beginner',
            estimatedTime: '4-8 months',
            skills: ['SQL', 'Python', 'Excel', 'Statistics', 'Visualization'],
            salaryRange: '$50K - $90K',
            growthPotential: 'high'
          },
          {
            id: 'data-scientist',
            name: 'Data Scientist',
            description: 'Build predictive models and advanced analytics',
            difficulty: 'advanced',
            estimatedTime: '12-24 months',
            skills: ['Machine Learning', 'Python', 'Statistics', 'Big Data'],
            salaryRange: '$80K - $150K',
            growthPotential: 'high'
          },
          {
            id: 'business-intelligence-analyst',
            name: 'Business Intelligence Analyst',
            description: 'Transform data into actionable business insights',
            difficulty: 'intermediate',
            estimatedTime: '6-12 months',
            skills: ['SQL', 'Power BI', 'Tableau', 'Business Analysis'],
            salaryRange: '$60K - $100K',
            growthPotential: 'high'
          }
        ]
      },
      {
        id: 'cybersecurity',
        name: 'Cybersecurity',
        description: 'Protect systems and networks from cyber threats',
        careerPaths: [
          {
            id: 'cybersecurity-analyst',
            name: 'Cybersecurity Analyst',
            description: 'Protect systems and networks from cyber threats',
            difficulty: 'intermediate',
            estimatedTime: '8-18 months',
            skills: ['Network Security', 'Ethical Hacking', 'Incident Response'],
            salaryRange: '$70K - $120K',
            growthPotential: 'very high'
          }
        ]
      }
    ]
  },
  {
    id: 'business',
    name: 'Business & Management',
    description: 'Entrepreneurship, marketing, finance, and operations',
    icon: '💼',
    subdomains: [
      {
        id: 'digital-marketing',
        name: 'Digital Marketing',
        description: 'Online marketing, SEO, social media, and analytics',
        careerPaths: [
          {
            id: 'digital-marketer',
            name: 'Digital Marketer',
            description: 'Create and manage online marketing campaigns',
            difficulty: 'beginner',
            estimatedTime: '3-6 months',
            skills: ['SEO', 'Social Media', 'Google Ads', 'Analytics'],
            salaryRange: '$40K - $80K',
            growthPotential: 'high'
          }
        ]
      },
      {
        id: 'product-management',
        name: 'Product Management',
        description: 'Lead product strategy and development',
        careerPaths: [
          {
            id: 'product-manager',
            name: 'Product Manager',
            description: 'Lead product strategy and development',
            difficulty: 'intermediate',
            estimatedTime: '8-18 months',
            skills: ['Product Strategy', 'User Research', 'Agile', 'Data Analysis'],
            salaryRange: '$70K - $130K',
            growthPotential: 'high'
          }
        ]
      }
    ]
  },
  {
    id: 'creative',
    name: 'Creative & Design',
    description: 'Graphic design, UX/UI, content creation, and multimedia',
    icon: '🎨',
    subdomains: [
      {
        id: 'ui-ux-design',
        name: 'UI/UX Design',
        description: 'Design user interfaces and user experiences',
        careerPaths: [
          {
            id: 'ui-designer',
            name: 'UI Designer',
            description: 'Create beautiful and functional user interfaces',
            difficulty: 'beginner',
            estimatedTime: '6-12 months',
            skills: ['Figma', 'Adobe Creative Suite', 'Design Principles'],
            salaryRange: '$50K - $100K',
            growthPotential: 'high'
          }
        ]
      },
      {
        id: 'content-creation',
        name: 'Content Creation',
        description: 'Create engaging digital content for various platforms',
        careerPaths: [
          {
            id: 'content-creator',
            name: 'Content Creator',
            description: 'Create engaging digital content for various platforms',
            difficulty: 'beginner',
            estimatedTime: '3-6 months',
            skills: ['Content Writing', 'Social Media', 'Video Editing', 'Photography'],
            salaryRange: '$35K - $70K',
            growthPotential: 'medium'
          }
        ]
      }
    ]
  }
];

export const InterestAssessment: React.FC<InterestAssessmentProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedDomain, setSelectedDomain] = useState<string>('');
  const [selectedSubdomain, setSelectedSubdomain] = useState<string>('');
  const [interests, setInterests] = useState<string[]>([]);
  const [experienceLevel, setExperienceLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('beginner');
  const [timeCommitment, setTimeCommitment] = useState<'part-time' | 'full-time' | 'flexible'>('part-time');
  const [learningGoals, setLearningGoals] = useState<string[]>([]);

  const availableInterests = [
    'Problem Solving', 'Creativity', 'Analytics', 'Communication', 'Leadership',
    'Technical Skills', 'Business Strategy', 'User Experience', 'Data Analysis',
    'Project Management', 'Innovation', 'Teamwork', 'Research', 'Writing'
  ];

  const learningGoalOptions = [
    'Get a new job in the field',
    'Advance in current career',
    'Start a business',
    'Learn for personal interest',
    'Earn certifications',
    'Build a portfolio'
  ];

  const handleInterestToggle = (interest: string) => {
    setInterests(prev => 
      prev.includes(interest) 
        ? prev.filter(i => i !== interest)
        : [...prev, interest]
    );
  };

  const handleLearningGoalToggle = (goal: string) => {
    setLearningGoals(prev => 
      prev.includes(goal) 
        ? prev.filter(g => g !== goal)
        : [...prev, goal]
    );
  };

  const handleNext = () => {
    if (currentStep < 6) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    const assessment: UserAssessment = {
      selectedDomain,
      selectedSubdomain,
      interests,
      experienceLevel,
      timeCommitment,
      learningGoals
    };
    onComplete(assessment);
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1: return selectedDomain !== '';
      case 2: return selectedSubdomain !== '';
      case 3: return interests.length >= 3;
      case 4: return experienceLevel !== '';
      case 5: return timeCommitment !== '';
      case 6: return learningGoals.length >= 1;
      default: return false;
    }
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Choose Your Domain</h2>
        <p className="text-gray-600">Select the broad field that interests you most</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {DOMAINS.map((domain) => (
          <div
            key={domain.id}
            onClick={() => setSelectedDomain(domain.id)}
            className={`p-6 border-2 rounded-xl cursor-pointer transition-all ${
              selectedDomain === domain.id
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-4xl mb-4">{domain.icon}</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">{domain.name}</h3>
            <p className="text-gray-600 text-sm">{domain.description}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const renderStep2 = () => {
    const domain = DOMAINS.find(d => d.id === selectedDomain);
    if (!domain) return null;

    return (
      <div className="space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Choose Your Subdomain</h2>
          <p className="text-gray-600">Select a specific area within {domain.name}</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {domain.subdomains.map((subdomain) => (
            <div
              key={subdomain.id}
              onClick={() => setSelectedSubdomain(subdomain.id)}
              className={`p-6 border-2 rounded-xl cursor-pointer transition-all ${
                selectedSubdomain === subdomain.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{subdomain.name}</h3>
              <p className="text-gray-600 text-sm mb-4">{subdomain.description}</p>
              
              <div className="space-y-2">
                <h4 className="font-medium text-gray-900">Career Paths:</h4>
                {subdomain.careerPaths.map((path) => (
                  <div key={path.id} className="text-sm text-gray-600">
                    • {path.name} ({path.difficulty})
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">Select Your Interests</h2>
        <p className="text-gray-600">Choose at least 3 areas that excite you (select {interests.length}/3)</p>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {availableInterests.map((interest) => (
          <button
            key={interest}
            onClick={() => handleInterestToggle(interest)}
            className={`p-3 rounded-lg border-2 transition-all ${
              interests.includes(interest)
                ? 'border-primary-500 bg-primary-100 text-primary-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            {interest}
          </button>
        ))}
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">What's Your Experience Level?</h2>
        <p className="text-gray-600">This helps us tailor your learning path</p>
      </div>
      
      <div className="space-y-4">
        {[
          { value: 'beginner', label: 'Beginner', desc: 'New to the field, starting from scratch' },
          { value: 'intermediate', label: 'Intermediate', desc: 'Some experience, looking to improve' },
          { value: 'advanced', label: 'Advanced', desc: 'Experienced, looking to master advanced concepts' }
        ].map((level) => (
          <div
            key={level.value}
            onClick={() => setExperienceLevel(level.value as any)}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              experienceLevel === level.value
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <h3 className="text-lg font-semibold text-gray-900">{level.label}</h3>
            <p className="text-gray-600 text-sm">{level.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );

  const renderStep5 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">How Much Time Can You Commit?</h2>
        <p className="text-gray-600">This affects your learning schedule and timeline</p>
      </div>
      
      <div className="space-y-4">
        {[
          { value: 'part-time', label: 'Part-Time', desc: '5-10 hours per week', icon: '⏰' },
          { value: 'full-time', label: 'Full-Time', desc: '20+ hours per week', icon: '🚀' },
          { value: 'flexible', label: 'Flexible', desc: 'Varies week to week', icon: '🔄' }
        ].map((option) => (
          <div
            key={option.value}
            onClick={() => setTimeCommitment(option.value as any)}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              timeCommitment === option.value
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{option.icon}</span>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{option.label}</h3>
                <p className="text-gray-600 text-sm">{option.desc}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderStep6 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">What Are Your Learning Goals?</h2>
        <p className="text-gray-600">Select at least one goal that motivates you</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {learningGoalOptions.map((goal) => (
          <button
            key={goal}
            onClick={() => handleLearningGoalToggle(goal)}
            className={`p-4 rounded-lg border-2 transition-all text-left ${
              learningGoals.includes(goal)
                ? 'border-primary-500 bg-primary-100 text-primary-700'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            {goal}
          </button>
        ))}
      </div>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      case 4: return renderStep4();
      case 5: return renderStep5();
      case 6: return renderStep6();
      default: return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Step {currentStep} of 6</span>
            <span className="text-sm text-gray-500">{Math.round((currentStep / 6) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / 6) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          {renderCurrentStep()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-8">
          <button
            onClick={handleBack}
            disabled={currentStep === 1}
            className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Back
          </button>
          
          {currentStep < 6 ? (
            <button
              onClick={handleNext}
              disabled={!canProceed()}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleComplete}
              disabled={!canProceed()}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Complete Assessment
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
