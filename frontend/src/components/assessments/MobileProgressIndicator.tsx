import React from 'react';

interface MobileProgressIndicatorProps {
  currentQuestion: number;
  totalQuestions: number;
  answeredQuestions: number;
}

const MobileProgressIndicator: React.FC<MobileProgressIndicatorProps> = ({
  currentQuestion,
  totalQuestions,
  answeredQuestions
}) => {
  const progressPercentage = (currentQuestion / totalQuestions) * 100;
  const completionPercentage = (answeredQuestions / totalQuestions) * 100;

  return (
    <div className="space-y-2">
      {/* Progress Bar */}
      <div className="relative">
        <div className="w-full bg-gray-200 rounded-full h-2">
          {/* Completion Progress (answered questions) */}
          <div 
            className="bg-green-400 h-2 rounded-full transition-all duration-300"
            style={{ width: `${completionPercentage}%` }}
          />
          {/* Current Position Indicator */}
          <div 
            className="absolute top-0 h-2 w-1 bg-blue-600 rounded-full transition-all duration-300"
            style={{ left: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="flex items-center justify-between text-xs text-gray-600">
        <span>Question {currentQuestion} of {totalQuestions}</span>
        <span>{answeredQuestions} answered</span>
      </div>
    </div>
  );
};

export default MobileProgressIndicator;