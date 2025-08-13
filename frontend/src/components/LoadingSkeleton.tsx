import React from 'react';

interface LoadingSkeletonProps {
  count?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ count = 3 }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="card animate-pulse">
          <div className="flex items-start space-x-4">
            {/* Course image placeholder */}
            <div className="w-16 h-16 bg-gray-200 rounded-lg flex-shrink-0"></div>
            
            <div className="flex-1 space-y-3">
              {/* Title placeholder */}
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              
              {/* Description placeholder */}
              <div className="space-y-2">
                <div className="h-3 bg-gray-200 rounded w-full"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
              </div>
              
              {/* Tags and progress placeholder */}
              <div className="flex items-center space-x-2">
                <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                <div className="h-6 bg-gray-200 rounded-full w-20"></div>
              </div>
              
              {/* Action buttons placeholder */}
              <div className="flex items-center space-x-2 pt-2">
                <div className="h-8 bg-gray-200 rounded w-20"></div>
                <div className="h-8 bg-gray-200 rounded w-20"></div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
