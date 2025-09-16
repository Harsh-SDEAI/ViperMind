import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import AssessmentInterface from './AssessmentInterface';
import RetakeManager from './RetakeManager';

interface AssessmentLauncherProps {
  assessmentType: 'quiz' | 'section_test' | 'level_final';
}

const AssessmentLauncher: React.FC<AssessmentLauncherProps> = ({ assessmentType }) => {
  const { targetId } = useParams<{ targetId: string }>();
  const [showAssessment, setShowAssessment] = useState(false);
  const [isRetake, setIsRetake] = useState(false);

  if (!targetId) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="text-red-600 text-lg font-medium mb-2">Error</div>
          <div className="text-gray-600">Invalid assessment target</div>
        </div>
      </div>
    );
  }

  const handleStartAssessment = () => {
    setIsRetake(false);
    setShowAssessment(true);
  };

  const handleStartRetake = () => {
    setIsRetake(true);
    setShowAssessment(true);
  };

  const handleBackToManager = () => {
    setShowAssessment(false);
    setIsRetake(false);
  };

  if (showAssessment) {
    return (
      <div>
        <AssessmentInterface 
          assessmentType={assessmentType}
          isRetake={isRetake}
          onBack={handleBackToManager}
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          {assessmentType === 'quiz' && 'Topic Quiz'}
          {assessmentType === 'section_test' && 'Section Test'}
          {assessmentType === 'level_final' && 'Level Final Exam'}
        </h1>
        <p className="text-gray-600">
          Review your attempt history and start your assessment
        </p>
      </div>

      <RetakeManager
        targetId={targetId}
        assessmentType={assessmentType}
        onRetakeStart={handleStartRetake}
        onNewAttempt={handleStartAssessment}
        className="mb-6"
      />

      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Assessment Guidelines</h3>
        <div className="space-y-3 text-sm text-gray-700">
          {assessmentType === 'quiz' && (
            <>
              <p>• This quiz contains 4 multiple-choice questions</p>
              <p>• You need 70% or higher to pass</p>
              <p>• You have unlimited attempts to improve your score</p>
              <p>• Time limit: 15 minutes</p>
            </>
          )}
          {assessmentType === 'section_test' && (
            <>
              <p>• This test contains 15 multiple-choice questions</p>
              <p>• You need 75% or higher to pass</p>
              <p>• You have 2 attempts total (1 retake if you fail)</p>
              <p>• Time limit: 30 minutes</p>
            </>
          )}
          {assessmentType === 'level_final' && (
            <>
              <p>• This final exam contains 20 multiple-choice questions</p>
              <p>• You need 80% or higher to pass</p>
              <p>• You have 2 attempts total (1 retake if you fail)</p>
              <p>• Time limit: 60 minutes</p>
              <p>• Review is required before retaking</p>
            </>
          )}
          <p>• Your best score will be kept for progress tracking</p>
          <p>• Make sure you have a stable internet connection</p>
        </div>
      </div>
    </div>
  );
};

export default AssessmentLauncher;