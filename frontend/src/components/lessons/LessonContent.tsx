import React from 'react';
import { LessonContent as LessonContentType } from '../../services/lessons';
import CodeBlock from '../common/CodeBlock';

interface LessonContentProps {
  content: LessonContentType;
}

const LessonContent: React.FC<LessonContentProps> = ({ content }) => {
  return (
    <div className="space-y-8">
      {/* Why It Matters */}
      <section className="bg-blue-50 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-blue-900 mb-3 flex items-center">
          <span className="text-2xl mr-2">💡</span>
          Why This Matters
        </h2>
        <p className="text-blue-800 leading-relaxed">
          {content.why_it_matters}
        </p>
      </section>

      {/* Key Ideas */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <span className="text-2xl mr-2">🎯</span>
          Key Concepts
        </h2>
        <div className="grid gap-3">
          {content.key_ideas.map((idea, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                {index + 1}
              </div>
              <p className="text-gray-700">{idea}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Examples */}
      <section>
        <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <span className="text-2xl mr-2">💻</span>
          Code Examples
        </h2>
        <div className="space-y-6">
          {content.examples.map((example, index) => (
            <div key={index} className="border rounded-lg overflow-hidden">
              <div className="bg-gray-100 px-4 py-3 border-b">
                <h3 className="font-medium text-gray-900">{example.title}</h3>
              </div>
              <div className="p-4">
                <div className="mb-4">
                  <CodeBlock code={example.code} language="python" />
                </div>
                <div className="mb-3">
                  <p className="text-gray-700 leading-relaxed">{example.explanation}</p>
                </div>
                {example.output && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-600 mb-2">Output:</h4>
                    <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm whitespace-pre-wrap">
                      {example.output}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Common Pitfalls */}
      {content.pitfalls && content.pitfalls.length > 0 && (
        <section className="bg-yellow-50 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-yellow-900 mb-4 flex items-center">
            <span className="text-2xl mr-2">⚠️</span>
            Common Pitfalls
          </h2>
          <div className="space-y-3">
            {content.pitfalls.map((pitfall, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-yellow-600 rounded-full flex-shrink-0 mt-2"></div>
                <p className="text-yellow-800">{pitfall}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Recap */}
      <section className="bg-green-50 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-green-900 mb-3 flex items-center">
          <span className="text-2xl mr-2">📝</span>
          Key Takeaways
        </h2>
        <p className="text-green-800 leading-relaxed">
          {content.recap}
        </p>
      </section>
    </div>
  );
};

export default LessonContent;