import React, { useState } from 'react';
import { AssessmentResult } from '../../services/assessments';
import QuestionDisplay from './QuestionDisplay';

interface ScoreDisplayProps {
  result: AssessmentResult;
  assessmentType: string;
  onRetake?: () => void;
  onBackToCurriculum: () => void;
  showRetakeInfo?: boolean;
}

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({
  result,
  assessmentType,
  onRetake,
  onBackToCurriculum,
  showRetakeInfo = false
}) => {
  const [showReview, setShowReview] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreIcon = (passed: boolean) => {
    return passed ? '🎉' : '📚';
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getAssessmentTitle = () => {
    switch (assessmentType) {
      case 'quiz': return 'Quiz';
      case 'section_test': return 'Section Test';
      case 'level_final': return 'Level Final';
      default: return 'Assessment';
    }
  };

  const getPassThreshold = () => {
    switch (assessmentType) {
      case 'quiz': return 70;
      case 'section_test': return 75;
      case 'level_final': return 80;
      default: return 70;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Results Header */}
      <div className="text-center mb-8">
        <div className="text-6xl mb-4">{getScoreIcon(result.passed)}</div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {getAssessmentTitle()} Results
        </h1>
        <div className={`text-5xl font-bold mb-4 ${getScoreColor(result.score)}`}>
          {Math.round(result.score)}%
        </div>
        <div className={`text-xl font-medium mb-4 ${
          result.passed ? 'text-green-600' : 'text-red-600'
        }`}>
          {result.passed ? 'Passed!' : 'Not Passed'}
        </div>
        <div className="text-gray-600">
          You need {getPassThreshold()}% to pass this {assessmentType.replace('_', ' ')}
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white border rounded-lg p-6 text-center">
          <div className="text-2xl font-bold text-green-600 mb-2">
            {result.correct_answers}
          </div>
          <div className="text-gray-600">Correct Answers</div>
        </div>
        
        <div className="bg-white border rounded-lg p-6 text-center">
          <div className="text-2xl font-bold text-blue-600 mb-2">
            {result.total_questions}
          </div>
          <div className="text-gray-600">Total Questions</div>
        </div>
        
        <div className="bg-white border rounded-lg p-6 text-center">
          <div className="text-2xl font-bold text-purple-600 mb-2">
            {formatTime(result.time_taken)}
          </div>
          <div className="text-gray-600">Time Taken</div>
        </div>
      </div>

      {/* AI Feedback */}
      <div className="bg-blue-50 border-l-4 border-blue-400 rounded-r-lg p-6 mb-8">
        <h3 className="font-medium text-blue-900 mb-2 flex items-center">
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          AI Feedback
        </h3>
        <p className="text-blue-800 leading-relaxed">{result.feedback}</p>
      </div>

      {/* Next Steps */}
      <div className={`border-l-4 rounded-r-lg p-6 mb-8 ${
        result.passed ? 'bg-green-50 border-green-400' : 'bg-yellow-50 border-yellow-400'
      }`}>
        <h3 className={`font-medium mb-2 ${
          result.passed ? 'text-green-900' : 'text-yellow-900'
        }`}>
          Next Steps
        </h3>
        <p className={`leading-relaxed ${
          result.passed ? 'text-green-800' : 'text-yellow-800'
        }`}>
          {result.next_steps.message}
        </p>
        
        {result.next_steps.review_topics && result.next_steps.review_topics.length > 0 && (
          <div className="mt-3">
            <div className="text-sm font-medium text-yellow-900 mb-2">
              Topics to review:
            </div>
            <div className="flex flex-wrap gap-2">
              {result.next_steps.review_topics.flat().map((topic, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-yellow-200 text-yellow-800 text-xs rounded-full"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Retake Information - Removed for now as retake_info is not in the interface */}

      {/* Question Review */}
      <div className="mb-8">
        <button
          onClick={() => setShowReview(!showReview)}
          className="flex items-center justify-between w-full p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <span className="font-medium text-gray-900">Review Questions</span>
          <svg
            className={`w-5 h-5 text-gray-500 transform transition-transform ${
              showReview ? 'rotate-180' : ''
            }`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {showReview && (
          <div className="mt-4 space-y-8">
            {result.question_results.map((questionResult, index) => (
              <div key={questionResult.question_id} className="border rounded-lg p-6">
                <QuestionDisplay
                  question={{
                    id: questionResult.question_id,
                    question: questionResult.question,
                    options: questionResult.options,
                    correct_answer: questionResult.correct_answer,
                    explanation: questionResult.explanation,
                    concept_tags: questionResult.concept_tags,
                    difficulty: 'medium'
                  }}
                  questionNumber={index + 1}
                  selectedAnswer={questionResult.user_answer}
                  onAnswerSelect={() => {}} // Read-only
                  showCorrectAnswer={true}
                  showExplanation={true}
                />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4">
        {/* Remedial Content Button */}
        {!result.passed && (
          <button
            onClick={() => {
              // Navigate to remedial content or generate it
              window.location.href = `/remedial/generate?assessment_id=${result.assessment_id}`;
            }}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium"
          >
            Get Help & Review
          </button>
        )}

        {onRetake && !result.passed && (
          <button
            onClick={onRetake}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Retake {getAssessmentTitle()}
          </button>
        )}
        
        <button
          onClick={onBackToCurriculum}
          className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium"
        >
          Back to Curriculum
        </button>
        
        {result.passed && result.next_steps.unlock_next && (
          <button
            onClick={onBackToCurriculum}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
          >
            Continue Learning
          </button>
        )}
      </div>
    </div>
  );
};

export default ScoreDisplay;