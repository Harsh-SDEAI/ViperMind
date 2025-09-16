import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useResponsive } from '../../hooks/useResponsive';
import assessmentService, { Assessment, AssessmentResult, AnswerSubmission } from '../../services/assessments';
import MobileQuestionDisplay from './MobileQuestionDisplay';
import MobileTimer from './MobileTimer';
import MobileProgressIndicator from './MobileProgressIndicator';
import ScoreDisplay from './ScoreDisplay';

interface MobileAssessmentInterfaceProps {
  assessmentType: 'quiz' | 'section_test' | 'level_final';
}

const MobileAssessmentInterface: React.FC<MobileAssessmentInterfaceProps> = ({ assessmentType }) => {
  const { targetId } = useParams<{ targetId: string }>();
  const navigate = useNavigate();
  const { isMobile, orientation } = useResponsive();
  
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<{ [questionId: string]: number }>({});
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startTime] = useState(Date.now());
  const [showQuestionOverview, setShowQuestionOverview] = useState(false);

  useEffect(() => {
    if (targetId) {
      generateAssessment();
    }
  }, [targetId, assessmentType]);

  const generateAssessment = async () => {
    try {
      setLoading(true);
      const assessmentData = await assessmentService.generateAssessment({
        target_id: targetId!,
        assessment_type: assessmentType,
        difficulty: 'medium',
        question_count: getDefaultQuestionCount()
      });
      
      setAssessment(assessmentData);
      setTimeRemaining(assessmentData.time_limit * 60);
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

  const handleQuestionJump = (index: number) => {
    setCurrentQuestionIndex(index);
    setShowQuestionOverview(false);
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

  const getAssessmentTitle = () => {
    switch (assessmentType) {
      case 'quiz': return 'Quiz';
      case 'section_test': return 'Section Test';
      case 'level_final': return 'Level Final';
      default: return 'Assessment';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading assessment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg p-6 max-w-sm w-full text-center shadow-lg">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-y-2">
            <button
              onClick={generateAssessment}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Try Again
            </button>
            <button
              onClick={handleBackToCurriculum}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
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
      <div className="min-h-screen bg-gray-50">
        <ScoreDisplay
          result={result}
          assessmentType={assessmentType}
          onBackToCurriculum={handleBackToCurriculum}
        />
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const currentQuestion = assessment.questions[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === assessment.questions.length - 1;
  const allQuestionsAnswered = assessment.questions.every(q => answers[q.id] !== undefined);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Mobile Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between mb-2">
          <button
            onClick={handleBackToCurriculum}
            className="flex items-center text-gray-600 hover:text-gray-900"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="text-sm">Back</span>
          </button>
          
          <h1 className="text-lg font-semibold text-gray-900">{getAssessmentTitle()}</h1>
          
          <MobileTimer
            timeRemaining={timeRemaining}
            onTimeUp={handleTimeUp}
            onTimeUpdate={setTimeRemaining}
          />
        </div>

        <MobileProgressIndicator
          currentQuestion={currentQuestionIndex + 1}
          totalQuestions={assessment.questions.length}
          answeredQuestions={Object.keys(answers).length}
        />
      </div>

      {/* Question Content */}
      <div className="flex-1 p-4">
        <MobileQuestionDisplay
          question={currentQuestion}
          questionNumber={currentQuestionIndex + 1}
          totalQuestions={assessment.questions.length}
          selectedAnswer={answers[currentQuestion.id]}
          onAnswerSelect={(answerIndex) => handleAnswerSelect(currentQuestion.id, answerIndex)}
        />
      </div>

      {/* Mobile Navigation */}
      <div className="bg-white border-t border-gray-200 p-4 sticky bottom-0">
        <div className="flex items-center justify-between mb-3">
          <button
            onClick={handlePreviousQuestion}
            disabled={currentQuestionIndex === 0}
            className={`flex items-center px-4 py-2 rounded-lg font-medium ${
              currentQuestionIndex === 0
                ? 'bg-gray-100 text-gray-400'
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Previous
          </button>

          <button
            onClick={() => setShowQuestionOverview(!showQuestionOverview)}
            className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg font-medium"
          >
            {currentQuestionIndex + 1} of {assessment.questions.length}
          </button>

          {isLastQuestion ? (
            <button
              onClick={handleSubmitAssessment}
              disabled={!allQuestionsAnswered || isSubmitting}
              className={`flex items-center px-4 py-2 rounded-lg font-medium ${
                !allQuestionsAnswered || isSubmitting
                  ? 'bg-gray-100 text-gray-400'
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {isSubmitting ? 'Submitting...' : 'Submit'}
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </button>
          ) : (
            <button
              onClick={handleNextQuestion}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
            >
              Next
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>

        {/* Question Overview */}
        {showQuestionOverview && (
          <div className="border-t pt-3">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Questions</h3>
            <div className="grid grid-cols-5 gap-2">
              {assessment.questions.map((_, index) => (
                <button
                  key={index}
                  onClick={() => handleQuestionJump(index)}
                  className={`h-10 rounded text-sm font-medium transition-colors ${
                    index === currentQuestionIndex
                      ? 'bg-blue-600 text-white'
                      : answers[assessment.questions[index].id] !== undefined
                      ? 'bg-green-100 text-green-800 border border-green-300'
                      : 'bg-gray-100 text-gray-600 border border-gray-300'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MobileAssessmentInterface;