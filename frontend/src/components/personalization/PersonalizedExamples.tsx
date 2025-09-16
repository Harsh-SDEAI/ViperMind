import React, { useState, useEffect } from 'react';
import personalizationService, { PersonalizedExamples as ExamplesType } from '../../services/personalization';
import CodeBlock from '../common/CodeBlock';

interface PersonalizedExamplesProps {
  topic: string;
  autoLoad?: boolean;
  className?: string;
}

const PersonalizedExamples: React.FC<PersonalizedExamplesProps> = ({
  topic,
  autoLoad = false,
  className = ''
}) => {
  const [examples, setExamples] = useState<ExamplesType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [personalized, setPersonalized] = useState(false);
  const [currentExampleIndex, setCurrentExampleIndex] = useState(0);

  useEffect(() => {
    if (autoLoad) {
      loadExamples();
    }
  }, [topic, autoLoad]);

  const loadExamples = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await personalizationService.getPersonalizedExamples(topic);
      
      if (response.success) {
        setExamples(response.examples);
        setPersonalized(response.personalized);
        setCurrentExampleIndex(0);
      } else {
        setError('Failed to load personalized examples');
      }
    } catch (err) {
      setError('Error loading examples');
      console.error('Error getting examples:', err);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-20 bg-gray-200 rounded mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <p className="text-red-600 mb-2">{error}</p>
        <button
          onClick={loadExamples}
          className="text-sm text-red-600 hover:text-red-800 underline"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!examples && !autoLoad) {
    return (
      <div className={`bg-blue-50 border border-blue-200 rounded-lg p-4 ${className}`}>
        <div className="text-center">
          <svg className="w-12 h-12 text-blue-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <h3 className="text-lg font-medium text-blue-900 mb-2">Get Personalized Examples</h3>
          <p className="text-blue-700 mb-4">
            Get code examples tailored to your interests and learning style for {topic}
          </p>
          <button
            onClick={loadExamples}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Load Examples
          </button>
        </div>
      </div>
    );
  }

  if (!examples) {
    return null;
  }

  const currentExample = examples.examples[currentExampleIndex];

  return (
    <div className={`bg-white rounded-lg border ${className}`}>
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Personalized Examples: {topic}
            </h3>
            {personalized && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 mt-1">
                ✨ Personalized for you
              </span>
            )}
          </div>
          
          {examples.examples.length > 1 && (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentExampleIndex(Math.max(0, currentExampleIndex - 1))}
                disabled={currentExampleIndex === 0}
                className="p-1 rounded text-gray-400 hover:text-gray-600 disabled:opacity-50"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              
              <span className="text-sm text-gray-600">
                {currentExampleIndex + 1} of {examples.examples.length}
              </span>
              
              <button
                onClick={() => setCurrentExampleIndex(Math.min(examples.examples.length - 1, currentExampleIndex + 1))}
                disabled={currentExampleIndex === examples.examples.length - 1}
                className="p-1 rounded text-gray-400 hover:text-gray-600 disabled:opacity-50"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Current Example */}
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-xl font-semibold text-gray-900">{currentExample.title}</h4>
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(currentExample.difficulty)}`}>
            {currentExample.difficulty}
          </span>
        </div>

        <p className="text-gray-700 mb-4">{currentExample.description}</p>

        {/* Interest Connection */}
        {currentExample.interest_connection && (
          <div className="bg-blue-50 border-l-4 border-blue-400 rounded-r-lg p-3 mb-4">
            <p className="text-blue-800 text-sm">
              <strong>Why this matters to you:</strong> {currentExample.interest_connection}
            </p>
          </div>
        )}

        {/* Code */}
        <div className="mb-4">
          <h5 className="text-sm font-medium text-gray-700 mb-2">Code Example:</h5>
          <CodeBlock code={currentExample.code} language="python" />
        </div>

        {/* Explanation */}
        <div className="mb-4">
          <h5 className="text-sm font-medium text-gray-700 mb-2">Explanation:</h5>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-gray-700 text-sm leading-relaxed">{currentExample.explanation}</p>
          </div>
        </div>

        {/* Example Navigation */}
        {examples.examples.length > 1 && (
          <div className="flex justify-center space-x-1 mb-4">
            {examples.examples.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentExampleIndex(index)}
                className={`w-3 h-3 rounded-full transition-colors ${
                  index === currentExampleIndex 
                    ? 'bg-blue-600' 
                    : 'bg-gray-300 hover:bg-gray-400'
                }`}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t bg-gray-50">
        <div className="mb-3">
          <h5 className="text-sm font-medium text-gray-700 mb-2">Learning Objectives:</h5>
          <ul className="space-y-1">
            {examples.learning_objectives.map((objective, index) => (
              <li key={index} className="flex items-start">
                <svg className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 text-sm">{objective}</span>
              </li>
            ))}
          </ul>
        </div>

        {examples.next_steps && (
          <div className="bg-blue-50 rounded-lg p-3">
            <h5 className="text-sm font-medium text-blue-900 mb-1">Next Steps:</h5>
            <p className="text-blue-800 text-sm">{examples.next_steps}</p>
          </div>
        )}

        <div className="flex justify-between items-center mt-4">
          <button
            onClick={loadExamples}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            🔄 Generate New Examples
          </button>
          
          <div className="text-xs text-gray-500">
            Personalized based on your learning style
          </div>
        </div>
      </div>
    </div>
  );
};

export default PersonalizedExamples;