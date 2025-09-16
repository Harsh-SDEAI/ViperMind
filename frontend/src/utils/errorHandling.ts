/**
 * Frontend error handling utilities for ViperMind
 */

export interface ApiError {
  type: string;
  code: string;
  message: string;
  details?: string;
  request_id?: string;
  timestamp?: string;
  recovery_suggestions?: string[];
  fallback_available?: boolean;
  retry_after?: number;
}

export interface ErrorResponse {
  success: false;
  error: ApiError;
}

export class ViperMindError extends Error {
  public readonly type: string;
  public readonly code: string;
  public readonly userMessage: string;
  public readonly recoverySuggestions: string[];
  public readonly fallbackAvailable: boolean;
  public readonly retryAfter?: number;
  public readonly requestId?: string;

  constructor(apiError: ApiError) {
    super(apiError.details || apiError.message);
    this.name = 'ViperMindError';
    this.type = apiError.type;
    this.code = apiError.code;
    this.userMessage = apiError.message;
    this.recoverySuggestions = apiError.recovery_suggestions || [];
    this.fallbackAvailable = apiError.fallback_available || false;
    this.retryAfter = apiError.retry_after;
    this.requestId = apiError.request_id;
  }

  isRetryable(): boolean {
    const retryableTypes = [
      'ai_service_error',
      'external_api_error',
      'network_error',
      'timeout_error',
      'rate_limit_error'
    ];
    return retryableTypes.includes(this.type);
  }

  shouldShowFallback(): boolean {
    return this.fallbackAvailable;
  }

  getRetryDelay(): number {
    return this.retryAfter ? this.retryAfter * 1000 : 1000; // Convert to milliseconds
  }
}

export class ErrorHandler {
  private static instance: ErrorHandler;
  private errorLog: ViperMindError[] = [];
  private maxLogSize = 100;

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  handleError(error: any): ViperMindError {
    let viperError: ViperMindError;

    if (error.response?.data?.error) {
      // API error response
      viperError = new ViperMindError(error.response.data.error);
    } else if (error.name === 'ViperMindError') {
      // Already a ViperMind error
      viperError = error;
    } else if (error.code === 'NETWORK_ERROR' || !navigator.onLine) {
      // Network error
      viperError = new ViperMindError({
        type: 'network_error',
        code: 'NETWORK_UNAVAILABLE',
        message: 'Network connection is unavailable. Please check your internet connection.',
        recovery_suggestions: [
          'Check your internet connection',
          'Try again in a moment',
          'Contact support if the issue persists'
        ]
      });
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      // Timeout error
      viperError = new ViperMindError({
        type: 'timeout_error',
        code: 'REQUEST_TIMEOUT',
        message: 'Request timed out. Please try again.',
        recovery_suggestions: [
          'Try again with a simpler request',
          'Check your network connection',
          'Contact support if the issue persists'
        ]
      });
    } else {
      // Generic error
      viperError = new ViperMindError({
        type: 'internal_error',
        code: 'UNKNOWN_ERROR',
        message: 'An unexpected error occurred. Please try again.',
        details: error.message || String(error),
        recovery_suggestions: [
          'Try refreshing the page',
          'Try again in a moment',
          'Contact support if the issue persists'
        ]
      });
    }

    this.logError(viperError);
    return viperError;
  }

  private logError(error: ViperMindError): void {
    // Add to error log
    this.errorLog.unshift(error);
    
    // Maintain log size
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog = this.errorLog.slice(0, this.maxLogSize);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ViperMind Error:', {
        type: error.type,
        code: error.code,
        message: error.userMessage,
        details: error.message,
        requestId: error.requestId,
        recoverySuggestions: error.recoverySuggestions
      });
    }

    // Send to error tracking service (if configured)
    this.reportError(error);
  }

  private reportError(error: ViperMindError): void {
    // In a real application, you would send this to an error tracking service
    // like Sentry, LogRocket, or a custom analytics endpoint
    
    // For now, we'll just store it locally
    try {
      const errorReport = {
        timestamp: new Date().toISOString(),
        type: error.type,
        code: error.code,
        message: error.userMessage,
        details: error.message,
        requestId: error.requestId,
        userAgent: navigator.userAgent,
        url: window.location.href
      };

      // Store in localStorage for debugging
      const existingReports = JSON.parse(localStorage.getItem('vipermind_errors') || '[]');
      existingReports.unshift(errorReport);
      
      // Keep only last 50 errors
      const recentReports = existingReports.slice(0, 50);
      localStorage.setItem('vipermind_errors', JSON.stringify(recentReports));
    } catch (e) {
      // Ignore localStorage errors
    }
  }

  getRecentErrors(): ViperMindError[] {
    return [...this.errorLog];
  }

  clearErrorLog(): void {
    this.errorLog = [];
  }
}

export class RetryManager {
  private retryAttempts = new Map<string, number>();
  private maxRetries = 3;

  async withRetry<T>(
    operation: () => Promise<T>,
    operationId: string,
    maxRetries: number = this.maxRetries
  ): Promise<T> {
    const currentAttempts = this.retryAttempts.get(operationId) || 0;

    try {
      const result = await operation();
      // Reset retry count on success
      this.retryAttempts.delete(operationId);
      return result;
    } catch (error) {
      const viperError = ErrorHandler.getInstance().handleError(error);

      if (viperError.isRetryable() && currentAttempts < maxRetries) {
        // Increment retry count
        this.retryAttempts.set(operationId, currentAttempts + 1);
        
        // Wait before retrying
        const delay = viperError.getRetryDelay() * Math.pow(2, currentAttempts); // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, delay));
        
        // Retry the operation
        return this.withRetry(operation, operationId, maxRetries);
      } else {
        // Max retries reached or not retryable
        this.retryAttempts.delete(operationId);
        throw viperError;
      }
    }
  }

  clearRetryCount(operationId: string): void {
    this.retryAttempts.delete(operationId);
  }
}

export class FallbackManager {
  private fallbackContent = new Map<string, any>();

  constructor() {
    this.initializeFallbackContent();
  }

  private initializeFallbackContent(): void {
    // Pre-load fallback content
    this.fallbackContent.set('lesson_content', {
      title: 'Python Basics',
      content: 'Python is a powerful, easy-to-learn programming language that is widely used for web development, data analysis, artificial intelligence, and more.',
      examples: [
        'print("Hello, World!")',
        'x = 5\nprint(x)',
        'name = "Alice"\nprint(f"Hello, {name}!")'
      ],
      keyPoints: [
        'Python uses indentation to define code blocks',
        'Variables don\'t need to be declared with a specific type',
        'Python is case-sensitive'
      ]
    });

    this.fallbackContent.set('assessment_questions', [
      {
        id: 'fallback_1',
        question: 'What is Python?',
        options: [
          'A programming language',
          'A type of snake',
          'A web browser',
          'An operating system'
        ],
        correct_answer: 0,
        explanation: 'Python is a high-level programming language known for its simplicity and readability.'
      }
    ]);

    this.fallbackContent.set('hint', {
      hint_text: 'Think about the core concept being tested. Break down the problem into smaller steps.',
      encouragement: 'You\'re on the right track! Keep thinking through it step by step.',
      hint_type: 'general'
    });
  }

  getFallbackContent(contentType: string, context?: any): any {
    const content = this.fallbackContent.get(contentType);
    
    if (!content) {
      return {
        message: 'Fallback content not available for this type.',
        available: false
      };
    }

    return {
      ...content,
      fallback: true,
      message: 'Using offline content due to service unavailability.'
    };
  }

  hasFallback(contentType: string): boolean {
    return this.fallbackContent.has(contentType);
  }
}

// Global instances
export const errorHandler = ErrorHandler.getInstance();
export const retryManager = new RetryManager();
export const fallbackManager = new FallbackManager();

// Utility functions
export const handleApiError = (error: any): ViperMindError => {
  return errorHandler.handleError(error);
};

export const withRetry = <T>(
  operation: () => Promise<T>,
  operationId: string,
  maxRetries?: number
): Promise<T> => {
  return retryManager.withRetry(operation, operationId, maxRetries);
};

export const getFallbackContent = (contentType: string, context?: any): any => {
  return fallbackManager.getFallbackContent(contentType, context);
};

// Network status monitoring
export class NetworkMonitor {
  private static instance: NetworkMonitor;
  private isOnline = navigator.onLine;
  private listeners: ((online: boolean) => void)[] = [];

  static getInstance(): NetworkMonitor {
    if (!NetworkMonitor.instance) {
      NetworkMonitor.instance = new NetworkMonitor();
    }
    return NetworkMonitor.instance;
  }

  constructor() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.notifyListeners(true);
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.notifyListeners(false);
    });
  }

  getStatus(): boolean {
    return this.isOnline;
  }

  onStatusChange(callback: (online: boolean) => void): () => void {
    this.listeners.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  private notifyListeners(online: boolean): void {
    this.listeners.forEach(callback => callback(online));
  }
}

export const networkMonitor = NetworkMonitor.getInstance();