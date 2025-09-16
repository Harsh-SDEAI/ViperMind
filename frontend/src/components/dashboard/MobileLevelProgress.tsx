import React, { useState } from 'react';
import { LevelProgress } from '../../services/dashboard';

interface MobileLevelProgressProps {
  levelProgress: LevelProgress[];
}

const MobileLevelProgress: React.FC<MobileLevelProgressProps> = ({ levelProgress }) => {
  const [expandedLevel, setExpandedLevel] = useState<string | null>(null);

  const getLevelIcon = (levelCode: string) => {
    switch (levelCode) {
      case 'B': return '🐍';
      case 'I': return '⚡';
      case 'A': return '🚀';
      default: return '📚';
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 60) return 'bg-yellow-500';
    if (percentage >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreColor = (score: number | null, threshold: number) => {
    if (score === null) return 'text-gray-400';
    if (score >= threshold) return 'text-green-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-3">
      {levelProgress.map((level) => (
        <div
          key={level.level_id}
          className={`bg-white rounded-lg border ${
            level.is_unlocked ? 'border-gray-200' : 'border-gray-100 bg-gray-50'
          }`}
        >
          {/* Level Header */}
          <div 
            className="p-4 cursor-pointer"
            onClick={() => setExpandedLevel(
              expandedLevel === level.level_id ? null : level.level_id
            )}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="text-2xl">{getLevelIcon(level.level_code)}</div>
                <div className="flex-1">
                  <h3 className={`font-semibold ${
                    level.is_unlocked ? 'text-gray-900' : 'text-gray-500'
                  }`}>
                    {level.level_name}
                  </h3>
                  <div className="text-sm text-gray-600">
                    {level.completed_topics}/{level.total_topics} topics • {Math.round(level.completion_percentage)}%
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                {/* Status Badge */}
                {!level.is_unlocked ? (
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                    🔒 Locked
                  </span>
                ) : level.level_final_passed ? (
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                    ✓ Complete
                  </span>
                ) : level.can_advance ? (
                  <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    Ready
                  </span>
                ) : null}

                {/* Expand Icon */}
                <svg 
                  className={`w-4 h-4 text-gray-400 transform transition-transform ${
                    expandedLevel === level.level_id ? 'rotate-180' : ''
                  }`} 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-3">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(level.completion_percentage)}`}
                  style={{ width: `${level.completion_percentage}%` }}
                />
              </div>
            </div>
          </div>

          {/* Expanded Content */}
          {expandedLevel === level.level_id && (
            <div className="px-4 pb-4 border-t bg-gray-50">
              <div className="pt-4 space-y-3">
                {/* Sections */}
                {level.sections.map((section) => (
                  <div key={section.section_id} className="bg-white rounded-lg p-3 border">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 text-sm">{section.section_name}</h4>
                      {section.section_test_passed ? (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                          ✓ Passed
                        </span>
                      ) : section.section_test_score !== null ? (
                        <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">
                          ✗ Failed
                        </span>
                      ) : (
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                          Not Taken
                        </span>
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between text-xs text-gray-600 mb-2">
                      <span>{section.completed_topics}/{section.total_topics} topics</span>
                      {section.section_test_score !== null && (
                        <span className={getScoreColor(section.section_test_score, 75)}>
                          Test: {section.section_test_score}%
                        </span>
                      )}
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-1">
                      <div 
                        className={`h-1 rounded-full transition-all duration-300 ${getProgressColor(section.completion_percentage)}`}
                        style={{ width: `${section.completion_percentage}%` }}
                      />
                    </div>
                  </div>
                ))}

                {/* Level Final */}
                <div className="bg-blue-50 rounded-lg p-3 border border-blue-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-blue-900 text-sm">Level Final Exam</h4>
                      <div className="text-xs text-blue-700">
                        {level.level_final_score !== null ? (
                          <span className={getScoreColor(level.level_final_score, 80)}>
                            Score: {level.level_final_score}%
                          </span>
                        ) : level.can_advance ? (
                          <span>Ready to take</span>
                        ) : (
                          <span>Complete sections first</span>
                        )}
                      </div>
                    </div>
                    
                    {level.can_advance && !level.level_final_passed && (
                      <button className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700">
                        Take Exam
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default MobileLevelProgress;