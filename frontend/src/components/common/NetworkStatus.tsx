import React, { useState, useEffect } from 'react';
import { networkMonitor } from '../../utils/errorHandling';

interface NetworkStatusProps {
  className?: string;
  showDetails?: boolean;
}

const NetworkStatus: React.FC<NetworkStatusProps> = ({ 
  className = '',
  showDetails = false 
}) => {
  const [isOnline, setIsOnline] = useState(networkMonitor.getStatus());
  const [showOfflineMessage, setShowOfflineMessage] = useState(false);

  useEffect(() => {
    const unsubscribe = networkMonitor.onStatusChange((online) => {
      setIsOnline(online);
      
      if (!online) {
        setShowOfflineMessage(true);
      } else {
        // Hide offline message after a delay when back online
        setTimeout(() => setShowOfflineMessage(false), 3000);
      }
    });

    return unsubscribe;
  }, []);

  if (isOnline && !showOfflineMessage) {
    return null; // Don't show anything when online
  }

  return (
    <div className={`fixed top-4 right-4 z-50 ${className}`}>
      <div className={`
        rounded-lg shadow-lg p-3 transition-all duration-300
        ${isOnline 
          ? 'bg-green-100 border border-green-200 text-green-800' 
          : 'bg-red-100 border border-red-200 text-red-800'
        }
      `}>
        <div className="flex items-center space-x-2">
          {/* Status Icon */}
          <div className="flex-shrink-0">
            {isOnline ? (
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            ) : (
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            )}
          </div>

          {/* Status Message */}
          <div className="flex-1">
            <p className="text-sm font-medium">
              {isOnline ? 'Back Online' : 'No Internet Connection'}
            </p>
            
            {showDetails && (
              <p className="text-xs opacity-75 mt-1">
                {isOnline 
                  ? 'Your connection has been restored'
                  : 'Some features may not work properly'
                }
              </p>
            )}
          </div>

          {/* Dismiss Button */}
          {isOnline && (
            <button
              onClick={() => setShowOfflineMessage(false)}
              className="flex-shrink-0 text-green-600 hover:text-green-800 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Offline Actions */}
        {!isOnline && (
          <div className="mt-2 pt-2 border-t border-red-200">
            <div className="flex space-x-2">
              <button
                onClick={() => window.location.reload()}
                className="px-2 py-1 bg-red-200 hover:bg-red-300 rounded text-xs font-medium transition-colors"
              >
                Retry
              </button>
              <button
                onClick={() => setShowOfflineMessage(false)}
                className="px-2 py-1 bg-red-200 hover:bg-red-300 rounded text-xs font-medium transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NetworkStatus;