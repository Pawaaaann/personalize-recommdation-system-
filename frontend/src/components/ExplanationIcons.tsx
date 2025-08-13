import React from 'react';
import { Brain, Users, TrendingUp, Target, Star } from 'lucide-react';

interface ExplanationIconsProps {
  explanations: string[];
  className?: string;
}

export const ExplanationIcons: React.FC<ExplanationIconsProps> = ({ explanations, className = '' }) => {
  const getIcon = (explanation: string) => {
    const lowerExplanation = explanation.toLowerCase();
    
    if (lowerExplanation.includes('skill_match') || lowerExplanation.includes('skill')) {
      return <Brain className="w-4 h-4" />;
    }
    if (lowerExplanation.includes('similar_users') || lowerExplanation.includes('users')) {
      return <Users className="w-4 h-4" />;
    }
    if (lowerExplanation.includes('popular') || lowerExplanation.includes('trending')) {
      return <TrendingUp className="w-4 h-4" />;
    }
    if (lowerExplanation.includes('target') || lowerExplanation.includes('goal')) {
      return <Target className="w-4 h-4" />;
    }
    return <Star className="w-4 h-4" />;
  };

  const getColor = (explanation: string) => {
    const lowerExplanation = explanation.toLowerCase();
    
    if (lowerExplanation.includes('skill_match') || lowerExplanation.includes('skill')) {
      return 'text-blue-600 bg-blue-100';
    }
    if (lowerExplanation.includes('similar_users') || lowerExplanation.includes('users')) {
      return 'text-green-600 bg-green-100';
    }
    if (lowerExplanation.includes('popular') || lowerExplanation.includes('trending')) {
      return 'text-orange-600 bg-orange-100';
    }
    if (lowerExplanation.includes('target') || lowerExplanation.includes('goal')) {
      return 'text-purple-600 bg-purple-100';
    }
    return 'text-gray-600 bg-gray-100';
  };

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {explanations.map((explanation, index) => (
        <div
          key={index}
          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getColor(explanation)}`}
          title={explanation}
        >
          {getIcon(explanation)}
          <span className="hidden sm:inline">{explanation.replace('_', ' ')}</span>
        </div>
      ))}
    </div>
  );
};
