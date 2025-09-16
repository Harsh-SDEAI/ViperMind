import React from 'react';
import { LearningInsight } from '../../services/dashboard';

interface LearningInsightsCardProps {
  insights: LearningInsight[];
}

const LearningInsightsCard: React.FC<LearningInsightsCardProps> = ({ insights }) => {
  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'weak_areas':
        return (
          <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case 'study_pattern':
        return (
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        );
      case 'assessment_performance':
        return (
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'weak_areas':
        return 'border-yellow-200 bg-yellow-50';
      case 'study_pattern':
        return 'border-blue-200 bg-blue-50';
      case 'assessment_performance':
        return 'border-green-200 bg-green-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getActionButton = (insight: LearningInsight) => {
    if (!insight.action) return null;

    const buttonText = {
      'review_concepts': 'Review Concepts',
      'continue_practice': 'Continue Practice',
      'maintain_pace': 'Keep It Up'
    }[insight.action] || 'Take Action';

    return (
      <button className="mt-3 px-3 py-1 bg-white border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50 transition-colors">
        {buttonText}
      </button>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Learning Insights</h2>
        <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      
      {insights.length === 0 ? (
        <div className="text-center py-8">
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <p className="text-gray-500">No insights available yet</p>
          <p className="text-sm text-gray-400 mt-1">Complete more assessments to get personalized insights!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {insights.map((insight, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getInsightColor(insight.type)}`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getInsightIcon(insight.type)}
                </div>
                
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900 mb-1">{insight.title}</h3>
                  <p className="text-sm text-gray-700 mb-2">{insight.message}</p>
                  
                  {/* Weak Concepts */}
                  {insight.concepts && insight.concepts.length > 0 && (
                    <div className="mb-3">
                      <div className="text-xs text-gray-600 mb-1">Focus on:</div>
                      <div className="flex flex-wrap gap-1">
                        {insight.concepts.slice(0, 3).map((concept, conceptIndex) => (
                          <span
                            key={conceptIndex}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-white text-gray-700 border"
                          >
                            {concept}
                          </span>
                        ))}
                        {insight.concepts.length > 3 && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-white text-gray-500 border">
                            +{insight.concepts.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {getActionButton(insight)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LearningInsightsCard;