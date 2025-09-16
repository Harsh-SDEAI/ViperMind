import React, { useState } from 'react';
import { ViperMindError } from '../../utils/errorHandling';

interface ErrorDisplayProps {
  error: ViperMindError | string;
  onRetry?: () => void;
  onDismiss?: () => void;
  showDetails?: boolean;
  className?: string;
}

const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  onRetry,
  onDismiss,
  showDetails = false,
  className = ''
}) => {
  const [showFullDetails, setShowFullDetails] = useState(false);

  const viperError = typeof error === 'string' 
    ? new ViperMindError({
        type: 'internal_error',
        code: 'GENERIC_ERROR',
        message: error
      })
    : error;

  const getErrorIcon = (type: string) => {
    switch (type) {
      case 'network_error': return '📡';
      case 'ai_service_error': return '🤖';
      case 'database_error': return '💾';
      case 'validation_error': return '⚠️';
      case 'authentication_error': return '🔐';
      case 'authorization_error': return '🚫';
      case 'not_found_error': return '🔍';
      case 'rate_limit_error': return '⏱️';
      case 'timeout_error': return '⏰';
      default: return '❌';
    }
  };

  const getErrorColor = (type: string) => {
    switch (type) {
      case 'validation_error':
      case 'authentication_error':
      case 'authorization_error':
        return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      case 'network_error':
      case 'timeout_error':
        return 'border-blue-200 bg-blue-50 text-blue-800';
      case 'ai_service_error':
        return 'border-purple-200 bg-purple-50 text-purple-800';
      case 'rate_limit_error':
        return 'border-orange-200 bg-orange-50 text-orange-800';
      default:
        return 'border-red-200 bg-red-50 text-red-800';
    }
  };

  return (
    <div className={`rounded-lg border p-4 ${getErrorColor(viperError.type)} ${className}`}>
      <div className="flex items-start space-x-3">
        {/* Error Icon */}
        <div className="flex-shrink-0 text-2xl">
          {getErrorIcon(viperError.type)}
        </div>

        <div className="flex-1 min-w-0">
          {/* Error Message */}
          <h3 className="font-medium mb-1">
            {viperError.userMessage}
          </h3>

          {/* Error Details */}
          {showDetails && viperError.message !== viperError.userMessage && (
            <p className="text-sm opacity-75 mb-2">
              {viperError.message}
            </p>
          )}

          {/* Request ID */}
          {viperError.requestId && (
            <p className="text-xs opacity-60 mb-2 font-mono">
              Request ID: {viperError.requestId}
            </p>
          )}

          {/* Recovery Suggestions */}
          {viperError.recoverySuggestions.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium mb-1">What you can do:</p>
              <ul className="text-sm space-y-1">
                {viperError.recoverySuggestions.slice(0, 3).map((suggestion, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Fallback Available */}
          {viperError.fallbackAvailable && (
            <div className="mb-3 p-2 bg-white bg-opacity-50 rounded text-sm">
              <span className="font-medium">Good news:</span> We have backup content available while we fix this issue.
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-2">
            {onRetry && viperError.isRetryable() && (
              <button
                onClick={onRetry}
                className="px-3 py-1 bg-white bg-opacity-80 hover:bg-opacity-100 rounded text-sm font-medium transition-colors"
              >
                {viperError.retryAfter ? `Retry in ${viperError.retryAfter}s` : 'Try Again'}
              </button>
            )}

            {viperError.fallbackAvailable && (
              <button
                onClick={() => {
                  // Trigger fallback content loading
                  if (onRetry) onRetry();
                }}
                className="px-3 py-1 bg-white bg-opacity-80 hover:bg-opacity-100 rounded text-sm font-medium transition-colors"
              >
                Use Backup Content
              </button>
            )}

            {onDismiss && (
              <button
                onClick={onDismiss}
                className="px-3 py-1 bg-white bg-opacity-80 hover:bg-opacity-100 rounded text-sm font-medium transition-colors"
              >
                Dismiss
              </button>
            )}

            {showDetails && (
              <button
                onClick={() => setShowFullDetails(!showFullDetails)}
                className="px-3 py-1 bg-white bg-opacity-80 hover:bg-opacity-100 rounded text-sm font-medium transition-colors"
              >
                {showFullDetails ? 'Hide Details' : 'Show Details'}
              </button>
            )}
          </div>

          {/* Full Error Details */}
          {showFullDetails && (
            <div className="mt-3 p-3 bg-white bg-opacity-50 rounded">
              <div className="text-xs space-y-2">
                <div>
                  <strong>Error Type:</strong> {viperError.type}
                </div>
                <div>
                  <strong>Error Code:</strong> {viperError.code}
                </div>
                {viperError.requestId && (
                  <div>
                    <strong>Request ID:</strong> {viperError.requestId}
                  </div>
                )}
                <div>
                  <strong>Timestamp:</strong> {new Date().toLocaleString()}
                </div>
                {viperError.message !== viperError.userMessage && (
                  <div>
                    <strong>Technical Details:</strong> {viperError.message}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorDisplay;