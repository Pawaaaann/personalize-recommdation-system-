# EduRec Frontend

A modern, responsive React application for the educational recommendation system, built with Vite and Tailwind CSS.

## Features

- **Mobile-first responsive design** with Tailwind CSS
- **Student login** with simple student ID input
- **Personalized dashboard** showing course recommendations
- **Interactive course cards** with thumbs up/down feedback
- **Explanation icons** for recommendation reasoning
- **Loading skeletons** and error handling
- **Accessibility features** including ARIA labels and keyboard navigation

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for utility-first styling
- **Lucide React** for beautiful icons
- **Modern ES6+** features

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running on port 8000 (see backend setup)

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser to `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
src/
├── components/          # React components
│   ├── CourseCard.tsx  # Course recommendation card
│   ├── Dashboard.tsx   # Main dashboard view
│   ├── ExplanationIcons.tsx # Recommendation reasoning icons
│   ├── LoadingSkeleton.tsx  # Loading state skeleton
│   └── Login.tsx       # Student login form
├── services/            # API service functions
│   └── api.ts          # HTTP client for backend API
├── types/               # TypeScript type definitions
│   └── api.ts          # API response/request types
├── App.tsx              # Main application component
├── main.tsx             # Application entry point
└── index.css            # Global styles with Tailwind
```

## API Integration

The frontend communicates with the backend API through the following endpoints:

- `GET /api/health` - Health check
- `GET /api/recommend/{student_id}?k=10` - Get recommendations
- `GET /api/course/{course_id}` - Get course metadata
- `POST /api/interactions` - Record user feedback

## Usage

1. **Login**: Enter your student ID (e.g., "user_001", "user_002")
2. **View Recommendations**: Browse personalized course suggestions
3. **Provide Feedback**: Use thumbs up/down buttons on each course card
4. **Refresh**: Click the refresh button to get new recommendations
5. **Logout**: Return to the login screen

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint (if configured)

### Adding New Components

1. Create your component in `src/components/`
2. Export it from the components index (if desired)
3. Import and use it in your desired location

### Styling

- Use Tailwind CSS utility classes for styling
- Custom components are defined in `src/index.css`
- Follow the existing design patterns for consistency

## Browser Support

- Modern browsers with ES6+ support
- Mobile-first responsive design
- Progressive enhancement for older browsers

## Contributing

1. Follow the existing code style and patterns
2. Ensure all components are accessible
3. Test on both desktop and mobile devices
4. Update types when modifying API contracts

## Troubleshooting

### Common Issues

1. **API Connection Failed**: Ensure the backend is running on port 8000
2. **Build Errors**: Check TypeScript types and dependencies
3. **Styling Issues**: Verify Tailwind CSS is properly configured

### Debug Mode

Enable browser developer tools to see:
- API request/response logs
- Component state changes
- Error messages and stack traces
