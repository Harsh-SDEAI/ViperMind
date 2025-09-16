import React, { useState } from 'react';
import { Section } from '../../services/curriculum';
import TopicList from './TopicList';
import ProgressBar from '../common/ProgressBar';

interface SectionCardProps {
  section: Section;
}

const SectionCard: React.FC<SectionCardProps> = ({ section }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const isUnlocked = section.is_unlocked ?? false;
  const completionPercentage = section.completion_percentage ?? 0;

  return (
    <div className={`border rounded-md ${
      isUnlocked ? 'border-gray-200 bg-white' : 'border-gray-100 bg-gray-50 opacity-70'
    }`}>
      <div
        className={`p-4 cursor-pointer ${
          isUnlocked ? 'hover:bg-gray-50' : ''
        }`}
        onClick={() => isUnlocked && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <h4 className={`font-medium ${
                isUnlocked ? 'text-gray-900' : 'text-gray-500'
              }`}>
                {section.name}
              </h4>
              <span className={`px-2 py-1 text-xs font-medium rounded ${
                isUnlocked ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-600'
              }`}>
                {section.code}
              </span>
              {!isUnlocked && (
                <span className="text-xs text-gray-400">🔒</span>
              )}
            </div>
            <p className={`text-sm ${
              isUnlocked ? 'text-gray-600' : 'text-gray-400'
            }`}>
              {section.description}
            </p>
            {isUnlocked && (
              <div className="mt-2">
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="text-gray-500">
                    {section.topics.filter(t => t.is_completed).length} of {section.topics.length} topics completed
                  </span>
                  <span className="font-medium">{Math.round(completionPercentage)}%</span>
                </div>
                <ProgressBar 
                  percentage={completionPercentage} 
                  color="blue"
                  height="h-1.5"
                />
              </div>
            )}
          </div>
          <div className="flex items-center space-x-2 ml-4">
            <span className="text-xs text-gray-500">
              {section.topics.length} topics
            </span>
            {isUnlocked && (
              <svg
                className={`w-4 h-4 text-gray-400 transform transition-transform ${
                  isExpanded ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            )}
          </div>
        </div>
      </div>

      {isExpanded && isUnlocked && (
        <div className="border-t border-gray-100 p-4 bg-gray-50">
          <TopicList topics={section.topics} />
        </div>
      )}
    </div>
  );
};

export default SectionCard;