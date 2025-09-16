import React from 'react';
import { NavigationResponse } from '../../services/lessons';

interface LessonNavigationProps {
  navigation: {
    next?: NavigationResponse;
    previous?: NavigationResponse;
  };
  onNavigate: (topicId: string) => void;
  isCompleted: boolean;
}

const LessonNavigation: React.FC<LessonNavigationProps> = ({
  navigation,
  onNavigate,
  isCompleted
}) => {
  const { previous, next } = navigation;

  return (
    <div className="flex items-center justify-between">
      {/* Previous Topic */}
      <div className="flex-1">
        {previous?.previous_topic ? (
          <button
            onClick={() => onNavigate(previous.previous_topic!.id)}
            className="flex items-center text-blue-600 hover:text-blue-800 group"
          >
            <svg 
              className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <div className="text-left">
              <div className="text-sm text-gray-500">Previous</div>
              <div className="font-medium">{previous.previous_topic.name}</div>
              {!previous.same_section && previous.previous_section && (
                <div className="text-xs text-gray-400">
                  {previous.previous_section.name}
                </div>
              )}
            </div>
          </button>
        ) : (
          <div className="text-gray-400 text-sm">
            {previous?.message || 'No previous topic'}
          </div>
        )}
      </div>

      {/* Completion Status */}
      <div className="flex-shrink-0 mx-8">
        {isCompleted ? (
          <div className="flex items-center text-green-600 bg-green-50 px-4 py-2 rounded-full">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            <span className="font-medium">Completed</span>
          </div>
        ) : (
          <div className="flex items-center text-blue-600 bg-blue-50 px-4 py-2 rounded-full">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <span className="font-medium">In Progress</span>
          </div>
        )}
      </div>

      {/* Next Topic */}
      <div className="flex-1 flex justify-end">
        {next?.next_topic ? (
          <button
            onClick={() => onNavigate(next.next_topic!.id)}
            className={`flex items-center group ${
              isCompleted 
                ? 'text-blue-600 hover:text-blue-800' 
                : 'text-gray-400 cursor-not-allowed'
            }`}
            disabled={!isCompleted}
          >
            <div className="text-right">
              <div className="text-sm text-gray-500">
                {isCompleted ? 'Next' : 'Complete lesson to continue'}
              </div>
              <div className="font-medium">{next.next_topic.name}</div>
              {!next.same_section && next.next_section && (
                <div className="text-xs text-gray-400">
                  {next.next_section.name}
                </div>
              )}
            </div>
            <svg 
              className={`w-5 h-5 ml-2 transition-transform ${
                isCompleted ? 'group-hover:translate-x-1' : ''
              }`}
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        ) : (
          <div className="text-gray-400 text-sm text-right">
            {next?.message || 'No next topic'}
          </div>
        )}
      </div>
    </div>
  );
};

export default LessonNavigation;