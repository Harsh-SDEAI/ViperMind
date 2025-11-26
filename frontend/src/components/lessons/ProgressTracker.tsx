import React from 'react';
import { UserProgress } from '../../services/lessons';

interface ProgressTrackerProps {
  progress?: UserProgress;
  isCompleted: boolean;
  onMarkComplete: () => void;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  progress,
  isCompleted,
  onMarkComplete
}) => {
  // Provide default values if progress is undefined
  const safeProgress = progress || {
    status: 'available',
    attempts: 0,
    time_spent: 0
  };

  // Ensure status is always a string
  const safeStatus = safeProgress.status || 'available';
  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'in_progress':
        return 'text-blue-600 bg-blue-100';
      case 'available':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-gray-400 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'in_progress':
        return '📖';
      case 'available':
        return '📚';
      default:
        return '🔒';
    }
  };

  return (
    <div className="bg-white border rounded-lg p-4 min-w-64">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-medium text-gray-900">Your Progress</h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(safeStatus)}`}>
          {getStatusIcon(safeStatus)} {safeStatus.replace('_', ' ')}
        </span>
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        {safeProgress.time_spent > 0 && (
          <div className="flex justify-between">
            <span>Time spent:</span>
            <span className="font-medium">{formatTime(safeProgress.time_spent)}</span>
          </div>
        )}
        
        {safeProgress.attempts > 0 && (
          <div className="flex justify-between">
            <span>Study sessions:</span>
            <span className="font-medium">{safeProgress.attempts}</span>
          </div>
        )}

        {safeProgress.best_score !== undefined && safeProgress.best_score > 0 && (
          <div className="flex justify-between">
            <span>Best score:</span>
            <span className="font-medium">{Math.round(safeProgress.best_score)}%</span>
          </div>
        )}

        {safeProgress.last_accessed && (
          <div className="flex justify-between">
            <span>Last accessed:</span>
            <span className="font-medium">
              {new Date(safeProgress.last_accessed).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>

      {!isCompleted && (
        <div className="mt-4 pt-3 border-t">
          <button
            onClick={onMarkComplete}
            className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors"
          >
            Mark as Complete
          </button>
        </div>
      )}

      {isCompleted && (
        <div className="mt-4 pt-3 border-t">
          <div className="flex items-center justify-center text-green-600 text-sm font-medium">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Lesson Completed!
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressTracker;