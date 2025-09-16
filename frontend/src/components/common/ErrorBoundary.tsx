import React, { Component, ErrorInfo, ReactNode } from 'react';
import { errorHandler } from '../../utils/errorHandling';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorId?: string;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to our error handling system
    const viperError = errorHandler.handleError(error);
    
    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    console.error('ErrorBoundary caught an error:', {
      error: viperError,
      errorInfo,
      componentStack: errorInfo.componentStack
    });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorId: undefined });
  };

  handleReportError = () => {
    if (this.state.error && this.state.errorId) {
      // In a real app, this would send error report to support
      const errorReport = {
        errorId: this.state.errorId,
        message: this.state.error.message,
        stack: this.state.error.stack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href
      };

      console.log('Error report generated:', errorReport);
      
      // Show success message
      alert('Error report sent. Our team will investigate this issue.');
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
            {/* Error Icon */}
            <div className="text-6xl mb-4">😵</div>
            
            {/* Error Title */}
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Oops! Something went wrong
            </h1>
            
            {/* Error Message */}
            <p className="text-gray-600 mb-6">
              We encountered an unexpected error. Don't worry, your progress is safe!
            </p>

            {/* Error ID */}
            {this.state.errorId && (
              <div className="bg-gray-50 rounded-lg p-3 mb-6">
                <p className="text-xs text-gray-500 mb-1">Error ID:</p>
                <p className="text-sm font-mono text-gray-700">{this.state.errorId}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={this.handleRetry}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Try Again
              </button>
              
              <button
                onClick={() => window.location.href = '/dashboard'}
                className="w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
              >
                Go to Dashboard
              </button>
              
              <button
                onClick={this.handleReportError}
                className="w-full px-4 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
              >
                Report This Error
              </button>
            </div>

            {/* Help Text */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                If this problem continues, please contact our support team with the error ID above.
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;