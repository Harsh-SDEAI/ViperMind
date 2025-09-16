import React, { useState } from 'react';
import { RemedialContent, RemedialCard } from '../../services/remedial';
import remedialService from '../../services/remedial';
import CodeBlock from '../common/CodeBlock';

interface RemedialCardsProps {
  content: RemedialContent;
  onComplete: () => void;
}

const RemedialCards: React.FC<RemedialCardsProps> = ({ content, onComplete }) => {
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showHints, setShowHints] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [cardStartTime, setCardStartTime] = useState(Date.now());

  const cards = content.cards || [];
  const currentCard = cards[currentCardIndex];

  if (!cards.length) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">No remedial cards available</p>
      </div>
    );
  }

  const handleCardComplete = async () => {
    if (!currentCard) return;

    try {
      const timeSpent = Math.floor((Date.now() - cardStartTime) / 1000);
      const result = await remedialService.completeRemedialCard(currentCard.id, timeSpent);
      
      // Move to next card or complete all
      if (currentCardIndex < cards.length - 1) {
        setCurrentCardIndex(prev => prev + 1);
        setSelectedAnswer(null);
        setShowAnswer(false);
        setShowHints(false);
        setCardStartTime(Date.now());
      } else if (result.progress.all_completed) {
        onComplete();
      }
    } catch (err) {
      console.error('Error completing card:', err);
    }
  };

  const handleAnswerSelect = (answerIndex: number) => {
    setSelectedAnswer(answerIndex);
  };

  const handleShowAnswer = () => {
    setShowAnswer(true);
  };

  const completedCards = cards.filter(card => card.is_completed).length;
  const progressPercentage = (completedCards / cards.length) * 100;

  return (
    <div className="space-y-6">
      {/* Progress Header */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">
            Card {currentCardIndex + 1} of {cards.length}
          </h3>
          <span className="text-sm text-gray-600">
            {completedCards} completed
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>

      {/* Current Card */}
      {currentCard && (
        <div className="border rounded-lg p-6">
          {/* Card Header */}
          <div className="mb-4">
            <h4 className="text-xl font-semibold text-gray-900 mb-2">
              {currentCard.topic_concept}
            </h4>
            {currentCard.is_completed && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                ✓ Completed
              </span>
            )}
          </div>

          {/* Explanation */}
          <div className="mb-6">
            <h5 className="text-lg font-medium text-gray-900 mb-3">Explanation</h5>
            <p className="text-gray-700 leading-relaxed">{currentCard.explanation}</p>
          </div>

          {/* Code Example */}
          {currentCard.code_example && (
            <div className="mb-6">
              <h5 className="text-lg font-medium text-gray-900 mb-3">Code Example</h5>
              <CodeBlock code={currentCard.code_example} language="python" />
            </div>
          )}

          {/* Practice Question */}
          {currentCard.practice_question && (
            <div className="mb-6">
              <h5 className="text-lg font-medium text-gray-900 mb-3">Practice Question</h5>
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-blue-900 font-medium mb-4">
                  {currentCard.practice_question.question}
                </p>
                
                <div className="space-y-2">
                  {currentCard.practice_question.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleAnswerSelect(index)}
                      disabled={showAnswer}
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        selectedAnswer === index
                          ? showAnswer
                            ? index === currentCard.practice_question!.correct_answer
                              ? 'bg-green-100 border-green-300 text-green-800'
                              : 'bg-red-100 border-red-300 text-red-800'
                            : 'bg-blue-100 border-blue-300 text-blue-800'
                          : showAnswer && index === currentCard.practice_question!.correct_answer
                          ? 'bg-green-100 border-green-300 text-green-800'
                          : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <span className="font-medium mr-2">{String.fromCharCode(65 + index)}.</span>
                      {option}
                    </button>
                  ))}
                </div>

                <div className="flex justify-between items-center mt-4">
                  <button
                    onClick={() => setShowHints(!showHints)}
                    className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                  >
                    {showHints ? 'Hide Hints' : 'Show Hints'}
                  </button>
                  
                  {selectedAnswer !== null && !showAnswer && (
                    <button
                      onClick={handleShowAnswer}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                    >
                      Check Answer
                    </button>
                  )}
                </div>

                {/* Answer Explanation */}
                {showAnswer && currentCard.practice_question.explanation && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <p className="text-gray-700 text-sm">
                      <strong>Explanation:</strong> {currentCard.practice_question.explanation}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Hints */}
          {showHints && currentCard.hints.length > 0 && (
            <div className="mb-6">
              <h5 className="text-lg font-medium text-gray-900 mb-3">Hints</h5>
              <div className="bg-yellow-50 rounded-lg p-4">
                <ul className="space-y-2">
                  {currentCard.hints.map((hint, index) => (
                    <li key={index} className="flex items-start">
                      <svg className="w-5 h-5 text-yellow-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      <span className="text-yellow-800">{hint}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Card Actions */}
          <div className="flex justify-between items-center pt-4 border-t">
            <div className="flex space-x-2">
              {currentCardIndex > 0 && (
                <button
                  onClick={() => setCurrentCardIndex(prev => prev - 1)}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  Previous Card
                </button>
              )}
            </div>

            <div className="flex space-x-2">
              {!currentCard.is_completed && (
                <button
                  onClick={handleCardComplete}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
                >
                  Complete Card
                </button>
              )}
              
              {currentCardIndex < cards.length - 1 && (
                <button
                  onClick={() => {
                    setCurrentCardIndex(prev => prev + 1);
                    setSelectedAnswer(null);
                    setShowAnswer(false);
                    setShowHints(false);
                    setCardStartTime(Date.now());
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Next Card
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Cards Overview */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h5 className="text-sm font-medium text-gray-700 mb-3">Cards Overview</h5>
        <div className="grid grid-cols-4 gap-2">
          {cards.map((card, index) => (
            <button
              key={card.id}
              onClick={() => setCurrentCardIndex(index)}
              className={`p-2 rounded text-xs font-medium transition-colors ${
                index === currentCardIndex
                  ? 'bg-blue-600 text-white'
                  : card.is_completed
                  ? 'bg-green-100 text-green-800'
                  : 'bg-white text-gray-600 hover:bg-gray-100'
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

export default RemedialCards;