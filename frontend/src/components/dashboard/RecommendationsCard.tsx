import React from 'react';
import { Recommendation } from '../../services/dashboard';

interface RecommendationsCardProps {
  recommendations: Recommendation[];
}

const RecommendationsCard: React.FC<RecommendationsCardProps> = ({ recommendations }) => {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'border-red-200 bg-red-50';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50';
      case 'low':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return (
          <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case 'medium':
        return (
          <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'low':
        return (
          <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getActionButton = (recommendation: Recommendation) => {
    const buttonConfig = {
      'view_remedial_content': {
        text: 'View Remedial Content',
        className: 'bg-purple-600 hover:bg-purple-700 text-white'
      },
      'view_failed_assessments': {
        text: 'View Failed Assessments',
        className: 'bg-orange-600 hover:bg-orange-700 text-white'
      },
      'start_topic': {
        text: 'Start Topic',
        className: 'bg-green-600 hover:bg-green-700 text-white'
      },
      'continue_learning': {
        text: 'Continue Learning',
        className: 'bg-blue-600 hover:bg-blue-700 text-white'
      }
    };

    const config = buttonConfig[recommendation.action as keyof typeof buttonConfig] || {
      text: 'Take Action',
      className: 'bg-gray-600 hover:bg-gray-700 text-white'
    };

    return (
      <button 
        className={`mt-3 px-4 py-2 rounded text-sm font-medium transition-colors ${config.className}`}
        onClick={() => {
          // Handle different actions
          switch (recommendation.action) {
            case 'view_remedial_content':
              window.location.href = '/remedial';
              break;
            case 'view_failed_assessments':
              window.location.href = '/assessments/failed';
              break;
            case 'start_topic':
              if (recommendation.topic_id) {
                window.location.href = `/topics/${recommendation.topic_id}`;
              }
              break;
            case 'continue_learning':
              window.location.href = '/curriculum';
              break;
            default:
              console.log('Action not implemented:', recommendation.action);
          }
        }}
      >
        {config.text}
      </button>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Recommendations</h2>
        <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      </div>
      
      {recommendations.length === 0 ? (
        <div className="text-center py-8">
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
          <p className="text-gray-500">Great job!</p>
          <p className="text-sm text-gray-400 mt-1">No recommendations at the moment. Keep up the good work!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {recommendations.map((recommendation, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getPriorityColor(recommendation.priority)}`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getPriorityIcon(recommendation.priority)}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <h3 className="font-medium text-gray-900">{recommendation.title}</h3>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      recommendation.priority === 'high' ? 'bg-red-100 text-red-800' :
                      recommendation.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {recommendation.priority.toUpperCase()}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-700 mb-2">{recommendation.message}</p>
                  
                  {getActionButton(recommendation)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecommendationsCard;