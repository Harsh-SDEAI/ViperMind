import React, { useState, useEffect } from 'react';
import remedialService, { RemedialContent as RemedialContentType } from '../../services/remedial';
import MiniExplainer from './MiniExplainer';
import RemedialCards from './RemedialCards';
import ReviewSchedule from './ReviewSchedule';

interface RemedialContentProps {
  remedialId: string;
  onComplete?: () => void;
  className?: string;
}

const RemedialContent: React.FC<RemedialContentProps> = ({
  remedialId,
  onComplete,
  className = ''
}) => {
  const [content, setContent] = useState<RemedialContentType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    fetchRemedialContent();
  }, [remedialId]);

  const fetchRemedialContent = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await remedialService.getRemedialContent(remedialId);
      setContent(data);
    } catch (err) {
      setError('Failed to load remedial content');
      console.error('Error fetching remedial content:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!content) return;

    try {
      const timeSpent = Math.floor((Date.now() - startTime) / 1000);
      await remedialService.completeRemedialContent(content.id, timeSpent);
      
      if (onComplete) {
        onComplete();
      }
    } catch (err) {
      console.error('Error completing remedial content:', err);
    }
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-4/6"></div>
        </div>
      </div>
    );
  }

  if (error || !content) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-6 ${className}`}>
        <div className="flex items-center">
          <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-red-600">{error || 'Unable to load remedial content'}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border ${className}`}>
      {/* Header */}
      <div className="border-b p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{content.title}</h2>
            <div className="flex items-center mt-2 space-x-4 text-sm text-gray-600">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                content.status === 'completed' ? 'bg-green-100 text-green-800' :
                content.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {content.status.replace('_', ' ').toUpperCase()}
              </span>
              <span>{Math.round(content.completion_percentage)}% Complete</span>
              <span>{Math.floor(content.time_spent / 60)} min spent</span>
            </div>
          </div>
          
          {content.status !== 'completed' && (
            <button
              onClick={handleComplete}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Mark Complete
            </button>
          )}
        </div>

        {/* Weak Concepts */}
        {content.weak_concepts.length > 0 && (
          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Focus Areas:</h3>
            <div className="flex flex-wrap gap-2">
              {content.weak_concepts.map((concept, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"
                >
                  {concept}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-6">
        {content.type === 'mini_explainer' && (
          <MiniExplainer content={content} onComplete={handleComplete} />
        )}
        
        {content.type === 'remedial_card' && (
          <RemedialCards content={content} onComplete={handleComplete} />
        )}
        
        {content.type === 'review_week' && (
          <ReviewSchedule content={content} onComplete={handleComplete} />
        )}
      </div>
    </div>
  );
};

export default RemedialContent;