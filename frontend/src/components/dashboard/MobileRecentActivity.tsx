import React from 'react';
import { Activity } from '../../services/dashboard';

interface MobileRecentActivityProps {
  activities: Activity[];
}

const MobileRecentActivity: React.FC<MobileRecentActivityProps> = ({ activities }) => {
  const getActivityIcon = (type: string, passed?: boolean) => {
    if (type === 'assessment') {
      return passed ? '✅' : '❌';
    }
    if (type === 'topic_completion') {
      return '🎯';
    }
    return '📝';
  };

  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
  };

  if (activities.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
        <div className="text-4xl mb-3">📝</div>
        <h3 className="font-medium text-gray-900 mb-2">No Recent Activity</h3>
        <p className="text-sm text-gray-600">Start learning to see your progress here!</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-gray-900">Recent Activity</h3>
      </div>
      
      <div className="divide-y divide-gray-100">
        {activities.slice(0, 8).map((activity, index) => (
          <div key={index} className="p-4 flex items-start space-x-3">
            <div className="flex-shrink-0 text-lg">
              {getActivityIcon(activity.type, activity.passed)}
            </div>
            
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-900 leading-relaxed">
                {activity.description}
              </p>
              
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-xs text-gray-500">
                  {formatTimeAgo(activity.timestamp)}
                </span>
                
                {activity.type === 'assessment' && activity.score !== undefined && (
                  <>
                    <span className="text-xs text-gray-400">•</span>
                    <span className={`text-xs font-medium ${
                      activity.passed ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {activity.score}%
                    </span>
                  </>
                )}
                
                {activity.assessment_type && (
                  <>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-500 capitalize">
                      {activity.assessment_type.replace('_', ' ')}
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Status Badge */}
            {activity.type === 'assessment' && (
              <div className="flex-shrink-0">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                  activity.passed 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {activity.passed ? 'Passed' : 'Failed'}
                </span>
              </div>
            )}
          </div>
        ))}
        
        {activities.length > 8 && (
          <div className="p-4 text-center">
            <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
              View All Activity
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MobileRecentActivity;