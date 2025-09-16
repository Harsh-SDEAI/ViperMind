import React from 'react';
import { Question } from '../../services/assessments';
import CodeBlock from '../common/CodeBlock';

interface QuestionDisplayProps {
  question: Question;
  questionNumber: number;
  selectedAnswer?: number;
  onAnswerSelect: (answerIndex: number) => void;
  showCorrectAnswer?: boolean;
  showExplanation?: boolean;
}

const QuestionDisplay: React.FC<QuestionDisplayProps> = ({
  question,
  questionNumber,
  selectedAnswer,
  onAnswerSelect,
  showCorrectAnswer = false,
  showExplanation = false
}) => {
  const getOptionStyle = (index: number) => {
    let baseStyle = "w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ";
    
    if (showCorrectAnswer) {
      if (index === question.correct_answer) {
        baseStyle += "border-green-500 bg-green-50 text-green-800 ";
      } else if (index === selectedAnswer && index !== question.correct_answer) {
        baseStyle += "border-red-500 bg-red-50 text-red-800 ";
      } else {
        baseStyle += "border-gray-200 bg-gray-50 text-gray-600 ";
      }
    } else {
      if (selectedAnswer === index) {
        baseStyle += "border-blue-500 bg-blue-50 text-blue-800 ";
      } else {
        baseStyle += "border-gray-200 hover:border-gray-300 hover:bg-gray-50 ";
      }
    }
    
    return baseStyle;
  };

  const getOptionIcon = (index: number) => {
    if (showCorrectAnswer) {
      if (index === question.correct_answer) {
        return '✓';
      } else if (index === selectedAnswer && index !== question.correct_answer) {
        return '✗';
      }
    }
    return String.fromCharCode(65 + index); // A, B, C, D
  };

  const getOptionIconStyle = (index: number) => {
    let baseStyle = "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mr-3 ";
    
    if (showCorrectAnswer) {
      if (index === question.correct_answer) {
        baseStyle += "bg-green-500 text-white ";
      } else if (index === selectedAnswer && index !== question.correct_answer) {
        baseStyle += "bg-red-500 text-white ";
      } else {
        baseStyle += "bg-gray-300 text-gray-600 ";
      }
    } else {
      if (selectedAnswer === index) {
        baseStyle += "bg-blue-500 text-white ";
      } else {
        baseStyle += "bg-gray-200 text-gray-600 ";
      }
    }
    
    return baseStyle;
  };

  return (
    <div className="space-y-6">
      {/* Question Header */}
      <div className="flex items-start space-x-4">
        <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
          {questionNumber}
        </div>
        <div className="flex-1">
          <h2 className="text-lg font-medium text-gray-900 leading-relaxed">
            {question.question}
          </h2>
          
          {/* Concept Tags */}
          {question.concept_tags.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {question.concept_tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Code Snippet */}
      {question.code_snippet && (
        <div className="ml-12">
          <CodeBlock code={question.code_snippet} language="python" />
        </div>
      )}

      {/* Answer Options */}
      <div className="ml-12 space-y-3">
        {question.options.map((option, index) => (
          <button
            key={index}
            onClick={() => !showCorrectAnswer && onAnswerSelect(index)}
            disabled={showCorrectAnswer}
            className={getOptionStyle(index)}
          >
            <div className="flex items-center">
              <div className={getOptionIconStyle(index)}>
                {getOptionIcon(index)}
              </div>
              <span className="flex-1">{option}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Explanation */}
      {showExplanation && question.explanation && (
        <div className="ml-12 mt-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded-r-lg">
          <h4 className="font-medium text-yellow-900 mb-2">Explanation:</h4>
          <p className="text-yellow-800 leading-relaxed">{question.explanation}</p>
        </div>
      )}

      {/* Difficulty Indicator */}
      <div className="ml-12 flex items-center space-x-4 text-sm text-gray-500">
        <span>Difficulty: 
          <span className={`ml-1 font-medium ${
            question.difficulty === 'easy' ? 'text-green-600' :
            question.difficulty === 'hard' ? 'text-red-600' :
            'text-yellow-600'
          }`}>
            {question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
          </span>
        </span>
      </div>
    </div>
  );
};

export default QuestionDisplay;