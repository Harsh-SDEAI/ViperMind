import React, { useState } from 'react';
import { LevelProgress } from '../../services/dashboard';

interface LevelProgressCardProps {
  levelProgress: LevelProgress[];
}

const LevelProgressCard: React.FC<LevelProgressCardProps> = ({ levelProgress }) => {
  const [expandedLevel, setExpandedLevel] = useState<string | null>(null);

  const toggleLevelExpansion = (levelId: string) => {
    setExpandedLevel(expandedLevel === levelId ? null : levelId);
  };

  const getLevelIcon = (levelCode: string) => {
    switch (levelCode) {
      case 'B': return '🐍'; // Beginner
      case 'I': return '⚡'; // Intermediate
      case 'A': return '🚀'; // Advanced
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
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Level Progress</h2>
      
      <div className="space-y-4">
        {levelProgress.map((level) => (
          <div
            key={level.level_id}
            className={`border rounded-lg transition-all duration-200 ${
              level.is_unlocked ? 'border-gray-200' : 'border-gray-100 bg-gray-50'
            }`}
          >
            {/* Level Header */}
            <div 
              className="p-4 cursor-pointer"
              onClick={() => toggleLevelExpansion(level.level_id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">{getLevelIcon(level.level_code)}</div>
                  <div>
                    <h3 className={`font-semibold ${
                      level.is_unlocked ? 'text-gray-900' : 'text-gray-500'
                    }`}>
                      {level.level_name}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>{level.completed_topics}/{level.total_topics} topics</span>
                      <span>{Math.round(level.completion_percentage)}% complete</span>
                      {level.level_final_score !== null && (
                        <span className={getScoreColor(level.level_final_score, 80)}>
                          Final: {level.level_final_score}%
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  {/* Progress Bar */}
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(level.completion_percentage)}`}
                      style={{ width: `${level.completion_percentage}%` }}
                    ></div>
                  </div>

                  {/* Status Badges */}
                  <div className="flex space-x-1">
                    {!level.is_unlocked && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        🔒 Locked
                      </span>
                    )}
                    {level.level_final_passed && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        ✓ Completed
                      </span>
                    )}
                    {level.can_advance && !level.level_final_passed && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Ready for Final
                      </span>
                    )}
                  </div>

                  {/* Expand Icon */}
                  <svg 
                    className={`w-5 h-5 text-gray-400 transform transition-transform ${
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
            </div>

            {/* Level Details */}
            {expandedLevel === level.level_id && (
              <div className="px-4 pb-4 border-t bg-gray-50">
                <div className="pt-4">
                  <h4 className="font-medium text-gray-900 mb-3">Sections</h4>
                  <div className="space-y-3">
                    {level.sections.map((section) => (
                      <div key={section.section_id} className="bg-white rounded-lg p-3 border">
                        <div className="flex items-center justify-between">
                          <div>
                            <h5 className="font-medium text-gray-900">{section.section_name}</h5>
                            <div className="flex items-center space-x-3 text-sm text-gray-600 mt-1">
                              <span>{section.completed_topics}/{section.total_topics} topics</span>
                              <span>{Math.round(section.completion_percentage)}% complete</span>
                              {section.section_test_score !== null && (
                                <span className={getScoreColor(section.section_test_score, 75)}>
                                  Test: {section.section_test_score}%
                                </span>
                              )}
                            </div>
                          </div>

                          <div className="flex items-center space-x-2">
                            {/* Section Progress Bar */}
                            <div className="w-16 bg-gray-200 rounded-full h-1.5">
                              <div 
                                className={`h-1.5 rounded-full transition-all duration-300 ${getProgressColor(section.completion_percentage)}`}
                                style={{ width: `${section.completion_percentage}%` }}
                              ></div>
                            </div>

                            {/* Section Status */}
                            {section.section_test_passed ? (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                ✓ Passed
                              </span>
                            ) : section.section_test_score !== null ? (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                ✗ Failed
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                                Not Taken
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Level Actions */}
                  <div className="mt-4 pt-3 border-t flex justify-between items-center">
                    <div className="text-sm text-gray-600">
                      {level.level_final_score !== null ? (
                        <span>Level Final: <span className={getScoreColor(level.level_final_score, 80)}>{level.level_final_score}%</span></span>
                      ) : level.can_advance ? (
                        <span className="text-blue-600">Ready to take Level Final</span>
                      ) : (
                        <span>Complete sections to unlock Level Final</span>
                      )}
                    </div>

                    {level.can_advance && !level.level_final_passed && (
                      <button className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors">
                        Take Level Final
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LevelProgressCard;