import React, { useState } from 'react';
import personalizationService, { HintRequest, PersonalizedHint as HintType } from '../../services/personalization';
import CodeBlock from '../common/CodeBlock';

interface PersonalizedHintProps {
  questionId: string;
  topic: string;
  difficulty?: string;
  attempts?: number;
  onHintReceived?: (hint: HintType) => void;
  className?: string;
}

const PersonalizedHint: React.FC<PersonalizedHintProps> = ({
  questionId,
  topic,
  difficulty = 'medium',
  attempts = 0,
  onHintReceived,
  className = ''
}) => {
  const [hint, setHint] = useState<HintType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);

  const requestHint = async () => {
    try {
      setLoading(true);
      setError(null);

      const hintRequest: HintRequest = {
        question_id: questionId,
        topic,
        difficulty,
        attempts
      };

      const response = await personalizationService.getPersonalizedHint(hintRequest);
      
      if (response.success) {
        setHint(response.hint);
        setShowHint(true);
        if (onHintReceived) {
          onHintReceived(response.hint);
        }
      } else {
        setError('Failed to get personalized hint');
      }
    } catch (err) {
      setError('Error requesting hint');
      console.error('Error getting hint:', err);
    } finally {
      setLoading(false);
    }
  };

  const getHintIcon = (hintType: string) => {
    switch (hintType) {
      case 'conceptual':
        return '💡';
      case 'example':
        return '📝';
      case 'step_by_step':
        return '🔢';
      case 'analogy':
        return '🔗';
      default:
        return '💭';
    }
  };

  return (
    <div className={`${className}`}>
      {!showHint ? (
        <button
          onClick={requestHint}
          disabled={loading}
          className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
            loading 
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
          }`}
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          {loading ? 'Getting hint...' : 'Get Personalized Hint'}
        </button>
      ) : hint ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="text-2xl">{getHintIcon(hint.hint_type)}</div>
            <div className="flex-1">
              <h4 className="font-medium text-yellow-900 mb-2">
                Personalized Hint
                <span className="ml-2 text-xs bg-yellow-200 text-yellow-800 px-2 py-1 rounded-full">
                  {hint.hint_type.replace('_', ' ').toUpperCase()}
                </span>
              </h4>
              
              <p className="text-yellow-800 mb-3">{hint.hint_text}</p>

              {/* Code Snippet */}
              {hint.code_snippet && (
                <div className="mb-3">
                  <h5 className="text-sm font-medium text-yellow-900 mb-2">Code Example:</h5>
                  <CodeBlock code={hint.code_snippet} language="python" />
                </div>
              )}

              {/* Visual Aid */}
              {hint.visual_aid && (
                <div className="mb-3">
                  <h5 className="text-sm font-medium text-yellow-900 mb-2">Visual Guide:</h5>
                  <div className="bg-white p-3 rounded border text-sm font-mono text-gray-700">
                    {hint.visual_aid}
                  </div>
                </div>
              )}

              {/* Follow-up Questions */}
              {hint.follow_up_questions && hint.follow_up_questions.length > 0 && (
                <div className="mb-3">
                  <h5 className="text-sm font-medium text-yellow-900 mb-2">Think About:</h5>
                  <ul className="space-y-1">
                    {hint.follow_up_questions.map((question, index) => (
                      <li key={index} className="flex items-start">
                        <span className="text-yellow-600 mr-2">•</span>
                        <span className="text-yellow-800 text-sm">{question}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Encouragement */}
              {hint.encouragement && (
                <div className="bg-yellow-100 rounded p-3 border-l-4 border-yellow-400">
                  <p className="text-yellow-800 text-sm font-medium">{hint.encouragement}</p>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-between items-center mt-4 pt-3 border-t border-yellow-200">
                <span className="text-xs text-yellow-700">
                  Difficulty: {hint.difficulty_level}
                </span>
                <div className="space-x-2">
                  <button
                    onClick={() => setShowHint(false)}
                    className="text-xs text-yellow-600 hover:text-yellow-800"
                  >
                    Hide Hint
                  </button>
                  <button
                    onClick={requestHint}
                    className="text-xs text-yellow-600 hover:text-yellow-800"
                  >
                    Get Another Hint
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-red-600 text-sm">{error}</p>
          <button
            onClick={requestHint}
            className="mt-2 text-xs text-red-600 hover:text-red-800 underline"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};

export default PersonalizedHint;