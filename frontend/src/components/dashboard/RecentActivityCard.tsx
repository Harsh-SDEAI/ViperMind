import React from 'react';
import { Activity } from '../../services/dashboard';

interface RecentActivityCardProps {
  activities: Activity[];
}

const RecentActivityCard: React.FC<RecentActivityCardProps> = ({ activities }) => {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'assessment':
        return (
          <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        );
      case 'topic_completion':
        return (
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      default:
        return (
          <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getActivityColor = (activity: Activity) => {
    if (activity.type === 'assessment') {
      if (activity.passed) return 'border-green-200 bg-green-50';
      return 'border-red-200 bg-red-50';
    }
    if (activity.type === 'topic_completion') {
      return 'border-blue-200 bg-blue-50';
    }
    return 'border-gray-200 bg-gray-50';
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

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Recent Activity</h2>
      
      {activities.length === 0 ? (
        <div className="text-center py-8">
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-gray-500">No recent activity</p>
          <p className="text-sm text-gray-400 mt-1">Start learning to see your progress here!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {activities.slice(0, 10).map((activity, index) => (
            <div
              key={index}
              className={`flex items-start space-x-3 p-3 rounded-lg border ${getActivityColor(activity)}`}
            >
              <div className="flex-shrink-0 mt-0.5">
                {getActivityIcon(activity.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900">{activity.description}</p>
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

              {/* Status Indicator */}
              {activity.type === 'assessment' && (
                <div className="flex-shrink-0">
                  {activity.passed ? (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Passed
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                      Failed
                    </span>
                  )}
                </div>
              )}
              
              {activity.type === 'topic_completion' && (
                <div className="flex-shrink-0">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    Completed
                  </span>
                </div>
              )}
            </div>
          ))}
          
          {activities.length > 10 && (
            <div className="text-center pt-3">
              <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                View All Activity
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RecentActivityCard;