import React, { useState } from 'react';
import { Level } from '../../services/curriculum';
import SectionCard from './SectionCard';
import ProgressBar from '../common/ProgressBar';

interface LevelCardProps {
  level: Level;
}

const LevelCard: React.FC<LevelCardProps> = ({ level }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getLevelIcon = (code: string) => {
    switch (code) {
      case 'B':
        return '🌱';
      case 'I':
        return '🌿';
      case 'A':
        return '🌳';
      default:
        return '📚';
    }
  };

  const getLevelColor = (code: string) => {
    switch (code) {
      case 'B':
        return 'green';
      case 'I':
        return 'blue';
      case 'A':
        return 'purple';
      default:
        return 'gray';
    }
  };

  const color = getLevelColor(level.code);
  const isUnlocked = level.is_unlocked ?? false;
  const completionPercentage = level.completion_percentage ?? 0;

  return (
    <div className={`border rounded-lg shadow-sm ${
      isUnlocked ? 'border-gray-200' : 'border-gray-100 opacity-60'
    }`}>
      <div
        className={`p-6 cursor-pointer ${
          isUnlocked ? 'hover:bg-gray-50' : 'bg-gray-50'
        }`}
        onClick={() => isUnlocked && setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="text-3xl">{getLevelIcon(level.code)}</div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className={`text-xl font-semibold ${
                  isUnlocked ? 'text-gray-900' : 'text-gray-500'
                }`}>
                  {level.name}
                </h3>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  color === 'green' ? 'bg-green-100 text-green-800' :
                  color === 'blue' ? 'bg-blue-100 text-blue-800' :
                  color === 'purple' ? 'bg-purple-100 text-purple-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  Level {level.code}
                </span>
                {!isUnlocked && (
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-600">
                    🔒 Locked
                  </span>
                )}
              </div>
              <p className={`text-sm mt-1 ${
                isUnlocked ? 'text-gray-600' : 'text-gray-400'
              }`}>
                {level.description}
              </p>
              {isUnlocked && (
                <div className="mt-3">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-600">Progress</span>
                    <span className="font-medium">{Math.round(completionPercentage)}%</span>
                  </div>
                  <ProgressBar 
                    percentage={completionPercentage} 
                    color={color}
                    height="h-2"
                  />
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">
              {level.sections.length} sections
            </span>
            {isUnlocked && (
              <svg
                className={`w-5 h-5 text-gray-400 transform transition-transform ${
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
        <div className="border-t border-gray-200 p-6 bg-gray-50">
          <div className="space-y-4">
            {level.sections.map((section) => (
              <SectionCard key={section.id} section={section} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LevelCard;