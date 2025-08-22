# 🚀 EduRec - AI-Powered Career Guidance & Learning Recommendation System

A comprehensive platform that helps users discover their career path, get personalized learning recommendations, and follow structured study schedules with course suggestions from top platforms like Coursera, Udemy, and more.

## ✨ **Features**

### 🔐 **Authentication System**
- **Firebase Authentication** with Google Sign-in
- **Email/Password** registration and login
- **Persistent login** state across sessions
- **Secure user management**

### 🎯 **Interest Assessment**
- **6-step guided assessment** process
- **Domain selection** (Technology, Business, Creative)
- **Subdomain specialization** (Web Development, Data Science, etc.)
- **Interest mapping** and skill identification
- **Experience level** assessment
- **Time commitment** evaluation
- **Learning goals** definition

### 🛤️ **Career Path Recommendations**
- **AI-powered career matching** based on assessment
- **Detailed career path** information
- **Salary ranges** and growth potential
- **Required skills** breakdown
- **Match score** calculation
- **Experience level** filtering

### 📚 **Learning Roadmaps**
- **Structured learning phases** from beginner to pro
- **Weekly study schedules** tailored to time commitment
- **Daily study sessions** with specific topics
- **Project-based learning** assignments
- **Progress tracking** and milestones

### 🎓 **Course Recommendations**
- **Curated course lists** from top platforms
- **Coursera, Udemy, edX, freeCodeCamp** integration
- **Course ratings** and student counts
- **Price information** and certificate availability
- **Direct links** to course platforms
- **Topic coverage** mapping

### 📅 **Study Schedule Generator**
- **Personalized weekly schedules** based on time commitment
- **Flexible study times** (part-time, full-time, flexible)
- **Goal setting** and achievement tracking
- **Project milestones** and deadlines
- **Progress visualization**

## 🏗️ **System Architecture**

```
User Flow:
Login → Interest Assessment → Career Recommendations → Learning Path → Study Schedule
   ↓
Dashboard (Traditional Course Recommendations)
```

### **Component Structure**
- `App.tsx` - Main application router and state management
- `Login.tsx` - Authentication interface
- `InterestAssessment.tsx` - 6-step assessment wizard
- `CareerRecommendations.tsx` - Career path suggestions
- `LearningPath.tsx` - Detailed learning roadmap
- `Dashboard.tsx` - Traditional course recommendations
- `AuthContext.tsx` - Firebase authentication context

## 🚀 **Getting Started**

### **Prerequisites**
- Node.js 16+ and npm
- Firebase project with Authentication enabled
- Google OAuth configured

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure Firebase**
   - Update `src/firebase/config.ts` with your Firebase credentials
   - Enable Google Authentication in Firebase Console
   - Set up authorized domains

4. **Start development server**
   ```bash
   npm run dev
   ```

## 🔧 **Configuration**

### **Firebase Setup**
1. Create a Firebase project
2. Enable Authentication (Email/Password + Google)
3. Get your configuration from Project Settings
4. Update `src/firebase/config.ts`

### **Customizing Career Paths**
Edit the `DOMAINS` array in `InterestAssessment.tsx` to add:
- New domains and subdomains
- Career path definitions
- Skill requirements
- Salary information

### **Adding Course Recommendations**
Update the `COURSE_RECOMMENDATIONS` object in `LearningPath.tsx` with:
- New course platforms
- Course details and URLs
- Pricing information
- Topic coverage

## 📊 **Data Models**

### **User Assessment**
```typescript
interface UserAssessment {
  selectedDomain: string;
  selectedSubdomain: string;
  interests: string[];
  experienceLevel: 'beginner' | 'intermediate' | 'advanced';
  timeCommitment: 'part-time' | 'full-time' | 'flexible';
  learningGoals: string[];
}
```

### **Career Path**
```typescript
interface CareerPath {
  id: string;
  name: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedTime: string;
  skills: string[];
  salaryRange: string;
  growthPotential: 'high' | 'medium' | 'low';
  matchScore: number;
  learningPath: LearningPhase[];
}
```

### **Learning Phase**
```typescript
interface LearningPhase {
  phase: string;
  duration: string;
  topics: string[];
  courses: Course[];
  projects: string[];
}
```

## 🎨 **UI/UX Features**

- **Responsive design** for all devices
- **Progressive disclosure** of information
- **Interactive elements** with hover states
- **Progress indicators** and step navigation
- **Color-coded** difficulty and growth indicators
- **Modern card-based** layout
- **Smooth transitions** and animations

## 🔒 **Security Features**

- **Firebase Authentication** with secure token management
- **Protected routes** and component access
- **User data isolation** and privacy
- **Secure API** communication
- **Input validation** and sanitization

## 📱 **Responsive Design**

- **Mobile-first** approach
- **Tablet optimization** for learning interfaces
- **Desktop enhancement** with advanced features
- **Touch-friendly** interactions
- **Accessible** design patterns

## 🚀 **Deployment**

### **Build for Production**
```bash
npm run build
```

### **Environment Variables**
Create `.env` file for production:
```env
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-domain
VITE_FIREBASE_PROJECT_ID=your-project-id
```

### **Deploy to Platforms**
- **Vercel** - Zero-config deployment
- **Netlify** - Git-based deployment
- **Firebase Hosting** - Integrated with Firebase
- **AWS S3 + CloudFront** - Scalable hosting

## 🔮 **Future Enhancements**

- **AI-powered skill gap analysis**
- **Machine learning** for better recommendations
- **Social learning** features and study groups
- **Gamification** elements and achievements
- **Integration** with learning management systems
- **Mobile app** development
- **Advanced analytics** and insights
- **Multi-language** support

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

- **Documentation**: Check this README and component files
- **Issues**: Create GitHub issues for bugs or feature requests
- **Firebase**: Refer to Firebase documentation for authentication issues
- **Community**: Join our community discussions

## 🙏 **Acknowledgments**

- **Firebase** for authentication and hosting
- **Tailwind CSS** for styling
- **React** for the UI framework
- **Coursera, Udemy, edX** for course content
- **Open source community** for inspiration and tools

---

**Built with ❤️ for learners worldwide**
