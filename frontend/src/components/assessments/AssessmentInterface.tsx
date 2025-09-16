import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useResponsive } from '../../hooks/useResponsive';
import assessmentService, { Assessment, AssessmentResult, AnswerSubmission } from '../../services/assessments';
import QuestionDisplay from './QuestionDisplay';
import Timer from './Timer';
import ProgressIndicator from './ProgressIndicator';
import ScoreDisplay from './ScoreDisplay';
import LoadingSpinner from '../common/LoadingSpinner';
import MobileAssessmentInterface from './MobileAssessmentInterface';

interface AssessmentInterfaceProps {
  assessmentType: 'quiz' | 'section_test' | 'level_final';
  isRetake?: boolean;
  onBack?: () => void;
}

const AssessmentInterface: React.FC<AssessmentInterfaceProps> = ({ 
  assessmentType, 
  isRetake = false, 
  onBack 
}) => {
  const { targetId } = useParams<{ targetId: string }>();
  const navigate = useNavigate();
  const { isMobile } = useResponsive();
  
  // All hooks must be called before any conditional returns
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<{ [questionId: string]: number }>({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (targetId) {
      generateAssessment();
    }
  }, [targetId, assessmentType]);

  // Use mobile interface for mobile devices
  if (isMobile) {
    return <MobileAssessmentInterface assessmentType={assessmentType} />;
  }

  const generateAssessment = async () => {
    try {
      setLoading(true);
      
      // Use retake endpoint if this is a retake
      const assessmentData = isRetake 
        ? await assessmentService.initiateRetake({
            target_id: targetId!,
            assessment_type: assessmentType,
            difficulty: 'medium',
            question_count: getDefaultQuestionCount()
          })
        : await assessmentService.generateAssessment({
            target_id: targetId!,
            assessment_type: assessmentType,
            difficulty: 'medium',
            question_count: getDefaultQuestionCount()
          });
      
      setAssessment(assessmentData);
      setTimeRemaining(assessmentData.time_limit * 60); // Convert minutes to seconds
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate assessment');
    } finally {
      setLoading(false);
    }
  };

  const getDefaultQuestionCount = () => {
    switch (assessmentType) {
      case 'quiz': return 4;
      case 'section_test': return 15;
      case 'level_final': return 20;
      default: return 4;
    }
  };

  const handleAnswerSelect = (questionId: string, answerIndex: number) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }));
  };

  const handleNextQuestion = () => {
    if (assessment && currentQuestionIndex < assessment.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmitAssessment = async () => {
    if (!assessment) return;

    setIsSubmitting(true);
    try {
      const submissionAnswers: AnswerSubmission[] = assessment.questions.map(question => ({
        question_id: question.id,
        selected_answer: answers[question.id] ?? -1
      }));

      const timeTaken = Math.floor((Date.now() - startTime) / 1000);

      const result = await assessmentService.submitAssessment({
        assessment_id: assessment.assessment_id,
        answers: submissionAnswers,
        time_taken: timeTaken
      });

      setResult(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit assessment');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTimeUp = () => {
    if (!result) {
      handleSubmitAssessment();
    }
  };

  const handleBackToCurriculum = () => {
    navigate('/curriculum');
  };

  const handleRetakeAssessment = () => {
    setAssessment(null);
    setCurrentQuestionIndex(0);
    setAnswers({});
    setResult(null);
    setError(null);
    generateAssessment();
  };

  const getAssessmentTitle = () => {
    switch (assessmentType) {
      case 'quiz': return 'Topic Quiz';
      case 'section_test': return 'Section Test';
      case 'level_final': return 'Level Final Exam';
      default: return 'Assessment';
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="text-red-600 text-lg font-medium mb-2">Error</div>
          <div className="text-gray-600 mb-4">{error}</div>
          <div className="space-x-4">
            <button
              onClick={generateAssessment}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Try Again
            </button>
            <button
              onClick={handleBackToCurriculum}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              Back to Curriculum
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (result) {
    return (
      <ScoreDisplay
        result={result}
        assessmentType={assessmentType}
        onRetake={assessmentType === 'quiz' ? handleRetakeAssessment : undefined}
        onBackToCurriculum={handleBackToCurriculum}
      />
    );
  }

  if (!assessment) {
    return <LoadingSpinner />;
  }

  const currentQuestion = assessment.questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === assessment.questions.length - 1;
  const allQuestionsAnswered = assessment.questions.every(q => answers[q.id] !== undefined);

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-4">
            {onBack && (
              <button
                onClick={onBack}
                className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back
              </button>
            )}
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {getAssessmentTitle()} {isRetake && '(Retake)'}
              </h1>
              <p className="text-gray-600">{assessment.target_name}</p>
            </div>
          </div>
          
          <Timer
            timeRemaining={timeRemaining}
            onTimeUp={handleTimeUp}
            onTimeUpdate={setTimeRemaining}
          />
        </div>

        <div className="bg-blue-50 rounded-lg p-4 mb-4">
          <p className="text-blue-800 text-sm">{assessment.instructions}</p>
        </div>

        <ProgressIndicator
          currentQuestion={currentQuestionIndex + 1}
          totalQuestions={assessment.questions.length}
          answeredQuestions={Object.keys(answers).length}
        />
      </div>

      {/* Question */}
      <div className="mb-8">
        <QuestionDisplay
          question={currentQuestion}
          questionNumber={currentQuestionIndex + 1}
          selectedAnswer={answers[currentQuestion.id]}
          onAnswerSelect={(answerIndex) => handleAnswerSelect(currentQuestion.id, answerIndex)}
        />
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <button
          onClick={handlePreviousQuestion}
          disabled={currentQuestionIndex === 0}
          className={`px-4 py-2 rounded-md font-medium ${
            currentQuestionIndex === 0
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-gray-600 text-white hover:bg-gray-700'
          }`}
        >
          Previous
        </button>

        <div className="flex space-x-4">
          {isLastQuestion ? (
            <button
              onClick={handleSubmitAssessment}
              disabled={!allQuestionsAnswered || isSubmitting}
              className={`px-6 py-2 rounded-md font-medium ${
                !allQuestionsAnswered || isSubmitting
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Assessment'}
            </button>
          ) : (
            <button
              onClick={handleNextQuestion}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
            >
              Next
            </button>
          )}
        </div>
      </div>

      {/* Question Overview */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium text-gray-900 mb-3">Question Overview</h3>
        <div className="grid grid-cols-10 gap-2">
          {assessment.questions.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentQuestionIndex(index)}
              className={`w-8 h-8 rounded text-sm font-medium ${
                index === currentQuestionIndex
                  ? 'bg-blue-600 text-white'
                  : answers[assessment.questions[index].id] !== undefined
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-200 text-gray-600'
              }`}
            >
              {index + 1}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AssessmentInterface;