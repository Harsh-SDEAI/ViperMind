import React from 'react';
import { Question } from '../../services/assessments';
import CodeBlock from '../common/CodeBlock';

interface MobileQuestionDisplayProps {
  question: Question;
  questionNumber: number;
  totalQuestions: number;
  selectedAnswer?: number;
  onAnswerSelect: (answerIndex: number) => void;
  showCorrectAnswer?: boolean;
  showExplanation?: boolean;
}

const MobileQuestionDisplay: React.FC<MobileQuestionDisplayProps> = ({
  question,
  questionNumber,
  totalQuestions,
  selectedAnswer,
  onAnswerSelect,
  showCorrectAnswer = false,
  showExplanation = false
}) => {
  const getOptionLetter = (index: number) => String.fromCharCode(65 + index);

  const getOptionStyle = (index: number) => {
    const isSelected = selectedAnswer === index;
    const isCorrect = showCorrectAnswer && index === question.correct_answer;
    const isWrong = showCorrectAnswer && isSelected && index !== question.correct_answer;

    if (isWrong) {
      return 'border-red-300 bg-red-50 text-red-800';
    }
    if (isCorrect) {
      return 'border-green-300 bg-green-50 text-green-800';
    }
    if (isSelected) {
      return 'border-blue-300 bg-blue-50 text-blue-800';
    }
    return 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 active:bg-gray-100';
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      {/* Question Header */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-blue-600">
            Question {questionNumber} of {totalQuestions}
          </span>
          {question.difficulty && (
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
              question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {question.difficulty}
            </span>
          )}
        </div>
        
        {/* Concept Tags */}
        {question.concept_tags && question.concept_tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {question.concept_tags.map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Question Text */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 leading-relaxed">
          {question.question}
        </h3>
      </div>

      {/* Code Snippet */}
      {question.code_snippet && (
        <div className="mb-6">
          <CodeBlock code={question.code_snippet} language="python" />
        </div>
      )}

      {/* Answer Options */}
      <div className="space-y-3 mb-6">
        {question.options.map((option, index) => (
          <button
            key={index}
            onClick={() => !showCorrectAnswer && onAnswerSelect(index)}
            disabled={showCorrectAnswer}
            className={`w-full p-4 rounded-lg border-2 text-left transition-all duration-200 ${getOptionStyle(index)}`}
          >
            <div className="flex items-start">
              <div className={`flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center mr-3 font-semibold text-sm ${
                selectedAnswer === index 
                  ? 'border-current bg-current text-white' 
                  : 'border-current'
              }`}>
                {getOptionLetter(index)}
              </div>
              <div className="flex-1 text-sm leading-relaxed">
                {option}
              </div>
              
              {/* Correct/Wrong Indicators */}
              {showCorrectAnswer && (
                <div className="flex-shrink-0 ml-2">
                  {index === question.correct_answer ? (
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : selectedAnswer === index ? (
                    <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  ) : null}
                </div>
              )}
            </div>
          </button>
        ))}
      </div>

      {/* Explanation */}
      {showExplanation && question.explanation && (
        <div className="bg-blue-50 border-l-4 border-blue-400 rounded-r-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Explanation</h4>
          <p className="text-blue-800 text-sm leading-relaxed">{question.explanation}</p>
        </div>
      )}

      {/* Selection Status */}
      {!showCorrectAnswer && (
        <div className="text-center">
          {selectedAnswer !== undefined ? (
            <div className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Answer selected: {getOptionLetter(selectedAnswer)}
            </div>
          ) : (
            <div className="text-sm text-gray-500">
              Tap an option to select your answer
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MobileQuestionDisplay;