import React from 'react';
import { Recommendation } from '../../services/dashboard';

interface MobileRecommendationsProps {
  recommendations: Recommendation[];
}

const MobileRecommendations: React.FC<MobileRecommendationsProps> = ({ recommendations }) => {
  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return '🔴';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '💡';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-200 bg-red-50';
      case 'medium': return 'border-yellow-200 bg-yellow-50';
      case 'low': return 'border-blue-200 bg-blue-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  const handleAction = (recommendation: Recommendation) => {
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
  };

  if (recommendations.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4 text-center">
        <div className="text-3xl mb-2">🎉</div>
        <h3 className="font-medium text-gray-900 mb-1">Great job!</h3>
        <p className="text-sm text-gray-600">No recommendations at the moment. Keep up the good work!</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-gray-900">Recommendations</h3>
      </div>
      
      <div className="p-4 space-y-3">
        {recommendations.slice(0, 3).map((recommendation, index) => (
          <div
            key={index}
            className={`rounded-lg border p-3 ${getPriorityColor(recommendation.priority)}`}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 text-lg">
                {getPriorityIcon(recommendation.priority)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <h4 className="font-medium text-gray-900 text-sm">{recommendation.title}</h4>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    recommendation.priority === 'high' ? 'bg-red-100 text-red-800' :
                    recommendation.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {recommendation.priority.toUpperCase()}
                  </span>
                </div>
                
                <p className="text-sm text-gray-700 mb-3 leading-relaxed">
                  {recommendation.message}
                </p>
                
                <button
                  onClick={() => handleAction(recommendation)}
                  className={`w-full px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    recommendation.priority === 'high' ? 'bg-red-600 hover:bg-red-700 text-white' :
                    recommendation.priority === 'medium' ? 'bg-yellow-600 hover:bg-yellow-700 text-white' :
                    'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {recommendation.action === 'view_remedial_content' ? 'View Help Content' :
                   recommendation.action === 'view_failed_assessments' ? 'Review Assessments' :
                   recommendation.action === 'start_topic' ? 'Start Topic' :
                   recommendation.action === 'continue_learning' ? 'Continue Learning' :
                   'Take Action'}
                </button>
              </div>
            </div>
          </div>
        ))}
        
        {recommendations.length > 3 && (
          <div className="text-center pt-2">
            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              View All Recommendations
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MobileRecommendations;