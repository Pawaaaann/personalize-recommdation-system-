import React, { useState } from 'react';
import { Calendar, Clock, BookOpen, Target, CheckCircle, Play, Pause, ExternalLink, Download } from 'lucide-react';

interface LearningPathProps {
  careerPathId: string;
  assessment: any;
  onBack: () => void;
}

interface StudySession {
  day: string;
  time: string;
  duration: number;
  topic: string;
  activity: string;
  course?: string;
}

interface WeeklySchedule {
  week: number;
  focus: string;
  sessions: StudySession[];
  goals: string[];
  projects: string[];
}

const LEARNING_PATHS: Record<string, WeeklySchedule[]> = {
  'frontend-developer': [
    {
      week: 1,
      focus: 'HTML Fundamentals & Basic Structure',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'HTML Basics', activity: 'Learn HTML tags and structure', course: 'HTML, CSS, and Javascript for Web Developers' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'HTML Forms', activity: 'Practice building forms', course: 'HTML, CSS, and Javascript for Web Developers' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Build personal portfolio structure' }
      ],
      goals: ['Understand HTML document structure', 'Learn semantic HTML tags', 'Build basic webpage layout'],
      projects: ['Personal Portfolio - HTML Structure']
    },
    {
      week: 2,
      focus: 'CSS Styling & Layout',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'CSS Selectors', activity: 'Learn CSS basics and selectors', course: 'HTML, CSS, and Javascript for Web Developers' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'CSS Box Model', activity: 'Understand layout and spacing', course: 'HTML, CSS, and Javascript for Web Developers' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Style your portfolio with CSS' }
      ],
      goals: ['Master CSS selectors and properties', 'Understand box model and layout', 'Apply responsive design principles'],
      projects: ['Personal Portfolio - Styling with CSS']
    },
    {
      week: 3,
      focus: 'JavaScript Fundamentals',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'JavaScript Variables', activity: 'Learn variables, data types, and operators', course: 'HTML, CSS, and Javascript for Web Developers' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'JavaScript Functions', activity: 'Practice writing functions', course: 'HTML, CSS, and Javascript for Web Developers' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Add interactivity to portfolio' }
      ],
      goals: ['Understand JavaScript basics', 'Write simple functions', 'Manipulate DOM elements'],
      projects: ['Personal Portfolio - Interactive Elements']
    }
  ],
  'backend-developer': [
    {
      week: 1,
      focus: 'Python Programming Fundamentals',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'Python Basics', activity: 'Learn variables, data types, control structures', course: 'Python for Everybody' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Python Functions', activity: 'Practice writing functions', course: 'Python for Everybody' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Build simple Python scripts' }
      ],
      goals: ['Master Python syntax', 'Write clean, readable code', 'Handle different data types'],
      projects: ['Python Calculator', 'File Processing Script', 'Simple API']
    },
    {
      week: 2,
      focus: 'Database Design & SQL',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'SQL Fundamentals', activity: 'Learn database design and SQL queries', course: 'SQL for Data Science' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Database Relationships', activity: 'Understand foreign keys and joins', course: 'SQL for Data Science' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Design and build a database' }
      ],
      goals: ['Design database schemas', 'Write complex SQL queries', 'Understand data relationships'],
      projects: ['User Management Database', 'E-commerce Database', 'Blog Database']
    }
  ],
  'full-stack-developer': [
    {
      week: 1,
      focus: 'Full-Stack Architecture',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'System Design', activity: 'Learn full-stack architecture patterns', course: 'Full Stack Web Development' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'API Design', activity: 'Design RESTful APIs', course: 'Full Stack Web Development' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Plan full-stack application' }
      ],
      goals: ['Understand full-stack architecture', 'Design scalable systems', 'Plan API structure'],
      projects: ['Full-Stack App Architecture', 'API Design Document', 'System Requirements']
    }
  ],
  'data-analyst': [
    {
      week: 1,
      focus: 'SQL Fundamentals & Database Basics',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'SQL Basics', activity: 'Learn SELECT, FROM, WHERE clauses', course: 'SQL for Data Science' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'SQL Joins', activity: 'Practice different types of joins', course: 'SQL for Data Science' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Query sample database' }
      ],
      goals: ['Write basic SQL queries', 'Understand database relationships', 'Filter and sort data'],
      projects: ['Customer Data Analysis', 'Sales Report Queries']
    },
    {
      week: 2,
      focus: 'Excel Advanced & Data Manipulation',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'Excel Formulas', activity: 'Master VLOOKUP, INDEX, MATCH', course: 'Excel for Data Analysis' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Pivot Tables', activity: 'Create dynamic reports and charts', course: 'Excel for Data Analysis' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Build sales dashboard' }
      ],
      goals: ['Master advanced Excel functions', 'Create pivot tables and charts', 'Build interactive dashboards'],
      projects: ['Sales Performance Dashboard', 'Customer Analytics Report']
    }
  ],
  'data-scientist': [
    {
      week: 1,
      focus: 'Python Programming Fundamentals',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'Python Basics', activity: 'Variables, data types, control structures', course: 'Python for Everybody' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Functions & Modules', activity: 'Write reusable functions', course: 'Python for Everybody' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Build simple data processing script' }
      ],
      goals: ['Master Python syntax', 'Write clean, readable code', 'Handle different data types'],
      projects: ['Data Processing Script', 'Simple Calculator Application']
    },
    {
      week: 2,
      focus: 'Data Manipulation with Pandas',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'Pandas Basics', activity: 'DataFrames, Series, indexing', course: 'Python for Everybody' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Data Cleaning', activity: 'Handle missing values, duplicates', course: 'Python for Everybody' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Clean and analyze dataset' }
      ],
      goals: ['Master Pandas library', 'Clean and prepare data', 'Perform data transformations'],
      projects: ['Data Cleaning Pipeline', 'Exploratory Data Analysis']
    }
  ],
  'business-intelligence-analyst': [
    {
      week: 1,
      focus: 'Power BI Fundamentals',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'Power BI Interface', activity: 'Learn Power BI workspace and tools', course: 'Power BI for Beginners' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Data Import', activity: 'Import and transform data sources', course: 'Power BI for Beginners' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Create first Power BI report' }
      ],
      goals: ['Navigate Power BI interface', 'Import data from various sources', 'Create basic visualizations'],
      projects: ['Sales Data Report', 'Customer Dashboard', 'Performance Metrics']
    }
  ],
  'digital-marketer': [
    {
      week: 1,
      focus: 'Digital Marketing Fundamentals',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'SEO Basics', activity: 'Learn search engine optimization fundamentals', course: 'Digital Marketing Specialization' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Social Media Marketing', activity: 'Understand social media platforms and strategies', course: 'Digital Marketing Specialization' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Create digital marketing plan' }
      ],
      goals: ['Understand SEO principles', 'Learn social media strategies', 'Create marketing plans'],
      projects: ['SEO Strategy Document', 'Social Media Calendar', 'Marketing Campaign Plan']
    }
  ],
  'product-manager': [
    {
      week: 1,
      focus: 'Product Strategy Fundamentals',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'Product Vision', activity: 'Define product vision and strategy', course: 'Product Management Specialization' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'User Research', activity: 'Learn user research methodologies', course: 'Product Management Specialization' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Create product roadmap' }
      ],
      goals: ['Define product vision', 'Understand user research', 'Create product roadmaps'],
      projects: ['Product Vision Document', 'User Research Plan', 'Product Roadmap']
    }
  ],
  'ui-designer': [
    {
      week: 1,
      focus: 'Design Fundamentals',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'Design Principles', activity: 'Learn color theory, typography, and layout', course: 'UI/UX Design Specialization' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Figma Basics', activity: 'Master Figma interface and tools', course: 'UI/UX Design Specialization' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Design mobile app interface' }
      ],
      goals: ['Understand design principles', 'Master Figma tools', 'Create user interfaces'],
      projects: ['Mobile App Design', 'Website Mockup', 'Design System']
    }
  ],
  'content-creator': [
    {
      week: 1,
      focus: 'Content Creation Fundamentals',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'Content Strategy', activity: 'Learn content planning and strategy', course: 'Content Marketing Strategy' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Social Media Content', activity: 'Create engaging social media content', course: 'Content Marketing Strategy' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Create content calendar' }
      ],
      goals: ['Plan content strategy', 'Create engaging content', 'Manage social media'],
      projects: ['Content Calendar', 'Social Media Campaign', 'Content Style Guide']
    }
  ],
  'cybersecurity-analyst': [
    {
      week: 1,
      focus: 'Security Fundamentals',
      sessions: [
        { day: 'Monday', time: '19:00', duration: 60, topic: 'Network Security', activity: 'Learn network security principles', course: 'Cybersecurity Specialization' },
        { day: 'Wednesday', time: '19:00', duration: 60, topic: 'Security Tools', activity: 'Master security analysis tools', course: 'Cybersecurity Specialization' },
        { day: 'Saturday', time: '10:00', duration: 90, topic: 'Project Work', activity: 'Conduct security assessment' }
      ],
      goals: ['Understand security principles', 'Master security tools', 'Conduct security assessments'],
      projects: ['Security Assessment Report', 'Incident Response Plan', 'Security Policy Document']
    }
  ]
};

const COURSE_RECOMMENDATIONS = {
  'frontend-developer': [
    {
      title: 'HTML, CSS, and Javascript for Web Developers',
      platform: 'Coursera',
      instructor: 'Yaakov Chaikin',
      rating: 4.7,
      students: '2.3M+',
      duration: '40 hours',
      price: 'Free (audit)',
      url: 'https://www.coursera.org/learn/html-css-javascript-for-web-developers',
      description: 'Learn the fundamental tools that every web page coder needs to know. Start from the ground up by learning how to implement modern web pages with HTML and CSS.',
      topics: ['HTML5', 'CSS3', 'JavaScript', 'Responsive Design'],
      certificate: true
    },
    {
      title: 'Responsive Web Design',
      platform: 'freeCodeCamp',
      instructor: 'freeCodeCamp Team',
      rating: 4.8,
      students: '500K+',
      duration: '300 hours',
      price: 'Free',
      url: 'https://www.freecodecamp.org/learn/responsive-web-design/',
      description: 'Learn the languages that developers use to build webpages: HTML (Hypertext Markup Language) for content, and CSS (Cascading Style Sheets) for design.',
      topics: ['HTML', 'CSS', 'Responsive Design', 'Accessibility'],
      certificate: true
    },
    {
      title: 'Modern JavaScript (ES6+)',
      platform: 'Udemy',
      instructor: 'Jonas Schmedtmann',
      rating: 4.8,
      students: '150K+',
      duration: '20 hours',
      price: '$19.99',
      url: 'https://www.udemy.com/course/javascript-beginners-complete-tutorial/',
      description: 'Learn modern JavaScript from the very beginning, step-by-step. Ditch the old tutorials and start with ES6+ syntax.',
      topics: ['ES6+ Features', 'Async JavaScript', 'Modules', 'Modern Syntax'],
      certificate: true
    }
  ],
  'backend-developer': [
    {
      title: 'Python for Everybody',
      platform: 'Coursera',
      instructor: 'Charles Severance',
      rating: 4.8,
      students: '2.5M+',
      duration: '80 hours',
      price: 'Free (audit)',
      url: 'https://www.coursera.org/specializations/python',
      description: 'Learn Python programming from the ground up. Perfect for beginners with no programming experience.',
      topics: ['Python', 'Programming', 'Data Structures', 'Web Scraping'],
      certificate: true
    },
    {
      title: 'SQL for Data Science',
      platform: 'Coursera',
      instructor: 'Sadie St. Lawrence',
      rating: 4.6,
      students: '500K+',
      duration: '20 hours',
      price: 'Free (audit)',
      url: 'https://www.coursera.org/learn/sql-for-data-science',
      description: 'Learn SQL fundamentals for data science applications. Master querying databases and extracting insights from data.',
      topics: ['SQL', 'Database Design', 'Data Querying', 'Data Analysis'],
      certificate: true
    }
  ],
  'full-stack-developer': [
    {
      title: 'Full Stack Web Development',
      platform: 'Coursera',
      instructor: 'Jogesh K. Muppala',
      rating: 4.6,
      students: '800K+',
      duration: '120 hours',
      price: '$49/month',
      url: 'https://www.coursera.org/specializations/full-stack-web-development',
      description: 'Learn to build complete web applications from frontend to backend. Master both client and server-side development.',
      topics: ['Frontend Development', 'Backend Development', 'Database Design', 'Deployment'],
      certificate: true
    }
  ],
  'data-analyst': [
    {
      title: 'SQL for Data Science',
      platform: 'Coursera',
      instructor: 'Sadie St. Lawrence',
      rating: 4.6,
      students: '500K+',
      duration: '20 hours',
      price: 'Free (audit)',
      url: 'https://www.coursera.org/learn/sql-for-data-science',
      description: 'Learn SQL fundamentals for data science applications. Master querying databases and extracting insights from data.',
      topics: ['SQL', 'Database Design', 'Data Querying', 'Data Analysis'],
      certificate: true
    },
    {
      title: 'Excel Skills for Business',
      platform: 'Coursera',
      instructor: 'Nicholas Waple',
      rating: 4.8,
      students: '1.2M+',
      duration: '60 hours',
      price: 'Free (audit)',
      url: 'https://www.coursera.org/specializations/excel-business',
      description: 'Master Excel for business applications. Learn advanced formulas, pivot tables, and data visualization.',
      topics: ['Excel', 'Business Analytics', 'Data Visualization', 'Advanced Formulas'],
      certificate: true
    },
    {
      title: 'Data Analysis with Python',
      platform: 'freeCodeCamp',
      instructor: 'freeCodeCamp Team',
      rating: 4.7,
      students: '300K+',
      duration: '200 hours',
      price: 'Free',
      url: 'https://www.freecodecamp.org/learn/data-analysis-with-python/',
      description: 'Learn data analysis using Python libraries like Pandas, NumPy, and Matplotlib.',
      topics: ['Python', 'Pandas', 'Data Analysis', 'Data Visualization'],
      certificate: true
    }
  ],
  'data-scientist': [
    {
      title: 'Python for Everybody',
      platform: 'Coursera',
      instructor: 'Charles Severance',
      rating: 4.8,
      students: '2.5M+',
      duration: '80 hours',
      price: 'Free (audit)',
      url: 'https://www.coursera.org/specializations/python',
      description: 'Learn Python programming from the ground up. Perfect for beginners with no programming experience.',
      topics: ['Python', 'Programming', 'Data Structures', 'Web Scraping'],
      certificate: true
    },
    {
      title: 'Statistics with Python',
      platform: 'Coursera',
      instructor: 'Brenda Gunderson',
      rating: 4.7,
      students: '800K+',
      duration: '60 hours',
      price: 'Free (audit)',
      url: 'https://www.coursera.org/specializations/statistics-with-python',
      description: 'Learn statistical concepts and apply them using Python. Essential for data science and machine learning.',
      topics: ['Statistics', 'Python', 'Data Analysis', 'Hypothesis Testing'],
      certificate: true
    },
    {
      title: 'Machine Learning Specialization',
      platform: 'Coursera',
      instructor: 'Andrew Ng',
      rating: 4.9,
      students: '4.8M+',
      duration: '100 hours',
      price: '$49/month',
      url: 'https://www.coursera.org/specializations/machine-learning-introduction',
      description: 'Master machine learning algorithms and techniques. Learn from the founder of Coursera and Stanford professor.',
      topics: ['Machine Learning', 'Supervised Learning', 'Unsupervised Learning', 'Neural Networks'],
      certificate: true
    },
    {
      title: 'Deep Learning Specialization',
      platform: 'Coursera',
      instructor: 'Andrew Ng',
      rating: 4.8,
      students: '1.2M+',
      duration: '120 hours',
      price: '$49/month',
      url: 'https://www.coursera.org/specializations/deep-learning',
      description: 'Master deep learning and neural networks. Build and train neural networks for various applications.',
      topics: ['Deep Learning', 'Neural Networks', 'Computer Vision', 'Natural Language Processing'],
      certificate: true
    }
  ],
  'business-intelligence-analyst': [
    {
      title: 'Power BI for Beginners',
      platform: 'Udemy',
      instructor: 'Maven Analytics',
      rating: 4.7,
      students: '200K+',
      duration: '15 hours',
      price: '$19.99',
      url: 'https://www.udemy.com/course/power-bi-complete-introduction/',
      description: 'Learn Power BI from scratch. Master data visualization and business intelligence reporting.',
      topics: ['Power BI', 'Data Visualization', 'Business Intelligence', 'Reporting'],
      certificate: true
    },
    {
      title: 'Tableau for Beginners',
      platform: 'Udemy',
      instructor: 'Lukas Vyhnalek',
      rating: 4.6,
      students: '150K+',
      duration: '12 hours',
      price: '$19.99',
      url: 'https://www.udemy.com/course/tableau10/',
      description: 'Master Tableau for data visualization and business intelligence. Create stunning dashboards and reports.',
      topics: ['Tableau', 'Data Visualization', 'Business Intelligence', 'Dashboard Design'],
      certificate: true
    }
  ],
  'digital-marketer': [
    {
      title: 'Digital Marketing Specialization',
      platform: 'Coursera',
      instructor: 'Aric Rindfleisch',
      rating: 4.7,
      students: '1.5M+',
      duration: '60 hours',
      price: 'Free (audit)',
      url: 'https://www.coursera.org/specializations/digital-marketing',
      description: 'Master digital marketing strategies and tools. Learn SEO, social media, content marketing, and analytics.',
      topics: ['Digital Marketing', 'SEO', 'Social Media', 'Content Marketing', 'Analytics'],
      certificate: true
    }
  ],
  'product-manager': [
    {
      title: 'Product Management Specialization',
      platform: 'Coursera',
      instructor: 'Dan Olsen',
      rating: 4.6,
      students: '600K+',
      duration: '80 hours',
      price: '$49/month',
      url: 'https://www.coursera.org/specializations/product-management',
      description: 'Learn product management fundamentals. Master product strategy, user research, and agile methodologies.',
      topics: ['Product Strategy', 'User Research', 'Agile', 'Data Analysis', 'Leadership'],
      certificate: true
    }
  ],
  'ui-designer': [
    {
      title: 'UI/UX Design Specialization',
      platform: 'Coursera',
      instructor: 'Michael Worthington',
      rating: 4.5,
      students: '400K+',
      duration: '70 hours',
      price: '$49/month',
      url: 'https://www.coursera.org/specializations/ui-ux-design',
      description: 'Master UI/UX design principles and tools. Learn to create beautiful and functional user interfaces.',
      topics: ['UI Design', 'UX Design', 'Design Principles', 'Prototyping', 'User Research'],
      certificate: true
    }
  ],
  'content-creator': [
    {
      title: 'Content Marketing Strategy',
      platform: 'Udemy',
      instructor: 'Brad Merrill',
      rating: 4.6,
      students: '100K+',
      duration: '12 hours',
      price: '$19.99',
      url: 'https://www.udemy.com/course/content-marketing-masterclass/',
      description: 'Master content marketing strategies. Learn to create engaging content that drives results.',
      topics: ['Content Marketing', 'Content Strategy', 'Social Media', 'Content Creation'],
      certificate: true
    }
  ],
  'cybersecurity-analyst': [
    {
      title: 'Cybersecurity Specialization',
      platform: 'Coursera',
      instructor: 'Dr. Edward G. Amoroso',
      rating: 4.7,
      students: '300K+',
      duration: '90 hours',
      price: '$49/month',
      url: 'https://www.coursera.org/specializations/cybersecurity',
      description: 'Master cybersecurity fundamentals. Learn network security, ethical hacking, and incident response.',
      topics: ['Cybersecurity', 'Network Security', 'Ethical Hacking', 'Incident Response', 'Security Tools'],
      certificate: true
    }
  ]
};

export const LearningPath: React.FC<LearningPathProps> = ({ careerPathId, assessment, onBack }) => {
  const [currentWeek, setCurrentWeek] = useState(1);
  const [showSchedule, setShowSchedule] = useState(true);
  const [showCourses, setShowCourses] = useState(true);

  const weeklySchedule = LEARNING_PATHS[careerPathId as keyof typeof LEARNING_PATHS] || [];
  const courseRecommendations = COURSE_RECOMMENDATIONS[careerPathId as keyof typeof COURSE_RECOMMENDATIONS] || [];

  const getCurrentWeekSchedule = () => {
    return weeklySchedule.find(week => week.week === currentWeek);
  };

  const generateStudySchedule = () => {
    const schedule = getCurrentWeekSchedule();
    if (!schedule) return null;

    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-gray-900">Week {currentWeek} Study Schedule</h3>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentWeek(Math.max(1, currentWeek - 1))}
              disabled={currentWeek === 1}
              className="btn-secondary disabled:opacity-50"
            >
              Previous Week
            </button>
            <button
              onClick={() => setCurrentWeek(Math.min(weeklySchedule.length, currentWeek + 1))}
              disabled={currentWeek === weeklySchedule.length}
              className="btn-secondary disabled:opacity-50"
            >
              Next Week
            </button>
          </div>
        </div>

        <div className="mb-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-2">Focus: {schedule.focus}</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <h5 className="font-medium text-blue-900 mb-2">Weekly Goals</h5>
              <ul className="space-y-1">
                {schedule.goals.map((goal, idx) => (
                  <li key={idx} className="text-sm text-blue-800 flex items-center gap-2">
                    <Target className="h-3 w-3" />
                    {goal}
                  </li>
                ))}
              </ul>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <h5 className="font-medium text-green-900 mb-2">Projects</h5>
              <ul className="space-y-1">
                {schedule.projects.map((project, idx) => (
                  <li key={idx} className="text-sm text-green-800 flex items-center gap-2">
                    <CheckCircle className="h-3 w-3" />
                    {project}
                  </li>
                ))}
              </ul>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <h5 className="font-medium text-purple-900 mb-2">Time Commitment</h5>
              <div className="text-sm text-purple-800">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="h-4 w-4" />
                  {schedule.sessions.reduce((total, session) => total + session.duration, 0)} min/week
                </div>
                <div className="text-xs">
                  {assessment.timeCommitment === 'part-time' ? 'Perfect for part-time learners' : 'Great for full-time learners'}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h5 className="text-lg font-semibold text-gray-900">Daily Study Sessions</h5>
          {schedule.sessions.map((session, idx) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 font-semibold">{session.day.slice(0, 3)}</span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">{session.topic}</div>
                    <div className="text-sm text-gray-600">{session.activity}</div>
                    {session.course && (
                      <div className="text-xs text-primary-600 mt-1">
                        📚 {session.course}
                      </div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium text-gray-900">{session.time}</div>
                  <div className="text-sm text-gray-600">{session.duration} min</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const generateCourseRecommendations = () => {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Recommended Courses</h3>
        <div className="space-y-6">
          {courseRecommendations.map((course: any, idx: number) => (
            <div key={idx} className="border border-gray-200 rounded-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-900 mb-2">{course.title}</h4>
                  <p className="text-gray-600 mb-3">{course.description}</p>
                  
                  <div className="flex items-center gap-4 mb-3">
                    <div className="flex items-center gap-1">
                      <span className="text-yellow-500">★</span>
                      <span className="text-sm font-medium">{course.rating}</span>
                    </div>
                    <div className="text-sm text-gray-600">{course.students} students</div>
                    <div className="text-sm text-gray-600">{course.duration}</div>
                    <div className="text-sm font-medium text-green-600">{course.price}</div>
                  </div>

                  <div className="mb-3">
                    <h5 className="font-medium text-gray-900 mb-2">Topics Covered:</h5>
                    <div className="flex flex-wrap gap-2">
                      {course.topics.map((topic: string, topicIdx: number) => (
                        <span key={topicIdx} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>Instructor: {course.instructor}</span>
                    <span>•</span>
                    <span>Platform: {course.platform}</span>
                    {course.certificate && (
                      <>
                        <span>•</span>
                        <span className="text-green-600">Certificate Available</span>
                      </>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex gap-3">
                <a
                  href={course.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary flex items-center gap-2"
                >
                  <ExternalLink className="h-4 w-4" />
                  View Course
                </a>
                <button className="btn-secondary flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Save for Later
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <button
              onClick={onBack}
              className="btn-secondary mb-4"
            >
              ← Back to Career Paths
            </button>
            <h1 className="text-4xl font-bold text-gray-900">Your Learning Path</h1>
            <p className="text-xl text-gray-600 mt-2">
              Personalized study schedule and course recommendations for your career goals
            </p>
          </div>
        </div>

        {/* Toggle Buttons */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setShowSchedule(!showSchedule)}
            className={`px-4 py-2 rounded-lg font-medium ${
              showSchedule 
                ? 'bg-primary-600 text-white' 
                : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            <Calendar className="h-4 w-4 inline mr-2" />
            Study Schedule
          </button>
          <button
            onClick={() => setShowCourses(!showCourses)}
            className={`px-4 py-2 rounded-lg font-medium ${
              showCourses 
                ? 'bg-primary-600 text-white' 
                : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            <BookOpen className="h-4 w-4 inline mr-2" />
            Course Recommendations
          </button>
        </div>

        {/* Content */}
        <div className="space-y-6">
          {showSchedule && generateStudySchedule()}
          {showCourses && generateCourseRecommendations()}
        </div>

        {/* Progress Tracking */}
        <div className="bg-white rounded-xl shadow-lg p-6 mt-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Track Your Progress</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl mb-2">📚</div>
              <div className="text-sm text-gray-600">Weeks Completed</div>
              <div className="font-semibold text-green-600">{currentWeek - 1}</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl mb-2">⏰</div>
              <div className="text-sm text-gray-600">Hours Studied</div>
              <div className="font-semibold text-blue-600">
                {weeklySchedule.slice(0, currentWeek - 1).reduce((total, week) => 
                  total + week.sessions.reduce((sum, session) => sum + session.duration, 0), 0
                ) / 60}
              </div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl mb-2">🎯</div>
              <div className="text-sm text-gray-600">Goals Achieved</div>
              <div className="font-semibold text-purple-600">
                {weeklySchedule.slice(0, currentWeek - 1).reduce((total, week) => total + week.goals.length, 0)}
              </div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl mb-2">🚀</div>
              <div className="text-sm text-gray-600">Projects Built</div>
              <div className="font-semibold text-orange-600">
                {weeklySchedule.slice(0, currentWeek - 1).reduce((total, week) => total + week.projects.length, 0)}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
