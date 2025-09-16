import React, { useState, useEffect } from 'react';
import assessmentService from '../../services/assessments';

interface RetakeInfo {
  target_id: string;
  assessment_type: string;
  attempts_used: number;
  max_attempts: number;
  remaining_attempts: number;
  can_attempt: boolean;
  can_retake: boolean;
  best_score: number | null;
  best_passed: boolean;
  retake_requirements?: {
    review_required: boolean;
    message: string;
  };
  assessment_history: Array<{
    id: string;
    attempt_number: number;
    score: number;
    passed: boolean;
    submitted_at: string;
  }>;
}

interface RetakeManagerProps {
  targetId: string;
  assessmentType: 'quiz' | 'section_test' | 'level_final';
  onRetakeStart: () => void;
  onNewAttempt: () => void;
  className?: string;
}

export const RetakeManager: React.FC<RetakeManagerProps> = ({
  targetId,
  assessmentType,
  onRetakeStart,
  onNewAttempt,
  className = ''
}) => {
  const [retakeInfo, setRetakeInfo] = useState<RetakeInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRetakeInfo();
  }, [targetId, assessmentType]);

  const fetchRetakeInfo = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await assessmentService.getRemainingAttempts(targetId, assessmentType);
      setRetakeInfo(response);
    } catch (err) {
      setError('Failed to load retake information');
      console.error('Error fetching retake info:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetake = () => {
    if (retakeInfo?.can_retake) {
      onRetakeStart();
    }
  };

  const handleNewAttempt = () => {
    if (retakeInfo?.can_attempt) {
      onNewAttempt();
    }
  };

  const formatScore = (score: number | null): string => {
    return score !== null ? `${Math.round(score)}%` : 'N/A';
  };

  const getPassThreshold = (type: string): number => {
    switch (type) {
      case 'quiz': return 70;
      case 'section_test': return 75;
      case 'level_final': return 80;
      default: return 70;
    }
  };

  const getAttemptLimitText = (type: string): string => {
    switch (type) {
      case 'quiz': return 'Unlimited attempts';
      case 'section_test': return '2 attempts (1 retake)';
      case 'level_final': return '2 attempts (1 retake)';
      default: return '1 attempt';
    }
  };

  if (loading) {
    return (
      <div className={`bg-gray-50 rounded-lg p-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error || !retakeInfo) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <p className="text-red-600 text-sm">{error || 'Unable to load retake information'}</p>
      </div>
    );
  }

  const passThreshold = getPassThreshold(assessmentType);
  const hasAttempts = retakeInfo.assessment_history.length > 0;

  return (
    <div className={`bg-white border rounded-lg p-4 ${className}`}>
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Assessment Attempts
          </h3>
          <span className="text-sm text-gray-500">
            {getAttemptLimitText(assessmentType)}
          </span>
        </div>

        {/* Best Score Display */}
        {hasAttempts && (
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Best Score:</span>
              <div className="flex items-center space-x-2">
                <span className={`text-lg font-bold ${
                  retakeInfo.best_passed ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formatScore(retakeInfo.best_score)}
                </span>
                {retakeInfo.best_passed ? (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Passed
                  </span>
                ) : (
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Failed (Need {passThreshold}%)
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Attempt Status */}
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">
            Attempts used: {retakeInfo.attempts_used} / {retakeInfo.max_attempts === 999 ? '∞' : retakeInfo.max_attempts}
          </span>
          <span className={`font-medium ${
            retakeInfo.remaining_attempts > 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            {retakeInfo.remaining_attempts > 0 
              ? `${retakeInfo.remaining_attempts === 999 ? '∞' : retakeInfo.remaining_attempts} remaining`
              : 'No attempts remaining'
            }
          </span>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2">
          {!hasAttempts && retakeInfo.can_attempt && (
            <button
              onClick={handleNewAttempt}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Assessment
            </button>
          )}

          {hasAttempts && retakeInfo.best_passed && (
            <div className="text-center py-2">
              <span className="text-green-600 font-medium">✓ Assessment Completed Successfully</span>
            </div>
          )}

          {hasAttempts && !retakeInfo.best_passed && retakeInfo.can_retake && (
            <>
              {retakeInfo.retake_requirements?.review_required && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <p className="text-yellow-800 text-sm">
                    {retakeInfo.retake_requirements.message}
                  </p>
                </div>
              )}
              <button
                onClick={handleRetake}
                className="w-full bg-orange-600 text-white py-2 px-4 rounded-lg hover:bg-orange-700 transition-colors"
              >
                Retake Assessment
              </button>
            </>
          )}

          {hasAttempts && !retakeInfo.best_passed && !retakeInfo.can_retake && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 text-sm text-center">
                No more attempts available. Contact support if you need assistance.
              </p>
            </div>
          )}
        </div>

        {/* Attempt History */}
        {hasAttempts && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Attempt History</h4>
            <div className="space-y-2">
              {retakeInfo.assessment_history.map((attempt, index) => (
                <div
                  key={attempt.id}
                  className="flex items-center justify-between text-sm bg-gray-50 rounded p-2"
                >
                  <span className="text-gray-600">
                    Attempt {attempt.attempt_number}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className={`font-medium ${
                      attempt.passed ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatScore(attempt.score)}
                    </span>
                    <span className="text-gray-500 text-xs">
                      {new Date(attempt.submitted_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RetakeManager;