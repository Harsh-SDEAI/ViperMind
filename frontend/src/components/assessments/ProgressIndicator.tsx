import React from 'react';

interface ProgressIndicatorProps {
  currentQuestion: number;
  totalQuestions: number;
  answeredQuestions: number;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  currentQuestion,
  totalQuestions,
  answeredQuestions
}) => {
  const progressPercentage = (currentQuestion / totalQuestions) * 100;
  const completionPercentage = (answeredQuestions / totalQuestions) * 100;

  return (
    <div className="space-y-3">
      {/* Progress Bar */}
      <div className="relative">
        <div className="w-full bg-gray-200 rounded-full h-3">
          {/* Completion Progress (answered questions) */}
          <div
            className="bg-green-400 h-3 rounded-full transition-all duration-300"
            style={{ width: `${completionPercentage}%` }}
          />
          {/* Current Position Indicator */}
          <div
            className="absolute top-0 h-3 w-1 bg-blue-600 rounded-full transition-all duration-300"
            style={{ left: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Progress Text */}
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center space-x-4">
          <span className="text-gray-600">
            Question {currentQuestion} of {totalQuestions}
          </span>
          <span className="text-green-600 font-medium">
            {answeredQuestions} answered
          </span>
          {answeredQuestions < totalQuestions && (
            <span className="text-yellow-600">
              {totalQuestions - answeredQuestions} remaining
            </span>
          )}
        </div>
        
        <div className="text-gray-500">
          {Math.round(completionPercentage)}% complete
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center space-x-6 text-xs text-gray-500">
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-400 rounded-full"></div>
          <span>Answered</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-gray-200 rounded-full"></div>
          <span>Not answered</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-1 h-3 bg-blue-600 rounded-full"></div>
          <span>Current position</span>
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;