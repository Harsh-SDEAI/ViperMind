import React from 'react';
import { RemedialContent } from '../../services/remedial';
import CodeBlock from '../common/CodeBlock';

interface MiniExplainerProps {
  content: RemedialContent;
  onComplete: () => void;
}

const MiniExplainer: React.FC<MiniExplainerProps> = ({ content, onComplete }) => {
  const aiContent = content.ai_generated_content;

  if (!aiContent) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">No content available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Main Explanation */}
      <div className="prose max-w-none">
        <p className="text-gray-700 leading-relaxed">{aiContent.explanation}</p>
      </div>

      {/* Code Example */}
      {aiContent.code_example && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Code Example</h3>
          <CodeBlock code={aiContent.code_example} language="python" />
        </div>
      )}

      {/* Key Points */}
      {aiContent.key_points && aiContent.key_points.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Key Points</h3>
          <ul className="space-y-2">
            {aiContent.key_points.map((point: string, index: number) => (
              <li key={index} className="flex items-start">
                <svg className="w-5 h-5 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-gray-700">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tips */}
      {aiContent.tips && aiContent.tips.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Tips for Success</h3>
          <div className="bg-blue-50 rounded-lg p-4">
            <ul className="space-y-2">
              {aiContent.tips.map((tip: string, index: number) => (
                <li key={index} className="flex items-start">
                  <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span className="text-blue-800">{tip}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Encouragement */}
      {aiContent.encouragement && (
        <div className="bg-green-50 border-l-4 border-green-400 rounded-r-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <p className="text-green-800 font-medium">{aiContent.encouragement}</p>
          </div>
        </div>
      )}

      {/* Action Button */}
      <div className="flex justify-center pt-4">
        <button
          onClick={onComplete}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          I've Reviewed This Content
        </button>
      </div>
    </div>
  );
};

export default MiniExplainer;