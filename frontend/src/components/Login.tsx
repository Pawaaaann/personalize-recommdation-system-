import React, { useState } from 'react';
import { BookOpen, ArrowRight } from 'lucide-react';

interface LoginProps {
  onLogin: (studentId: string) => void;
  isLoading?: boolean;
}

export const Login: React.FC<LoginProps> = ({ onLogin, isLoading = false }) => {
  const [studentId, setStudentId] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!studentId.trim()) {
      setError('Please enter your student ID');
      return;
    }
    
    if (studentId.trim().length < 3) {
      setError('Student ID must be at least 3 characters');
      return;
    }
    
    onLogin(studentId.trim());
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-50 px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-primary-600 rounded-full flex items-center justify-center mb-4">
            <BookOpen className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to EduRec
          </h2>
          <p className="text-gray-600">
            Get personalized course recommendations based on your interests and learning history
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="studentId" className="block text-sm font-medium text-gray-700 mb-2">
                Student ID
              </label>
              <input
                id="studentId"
                type="text"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                placeholder="Enter your student ID"
                className="input-field"
                disabled={isLoading}
                aria-describedby={error ? "studentId-error" : undefined}
              />
              {error && (
                <p id="studentId-error" className="mt-2 text-sm text-red-600">
                  {error}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading || !studentId.trim()}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Loading...
                </>
              ) : (
                <>
                  Get Recommendations
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          {/* Demo Info */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Demo:</strong> Try entering "user_001" or "user_002" to see sample recommendations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
