import React, { useState, useEffect } from 'react';
import curriculumService, { Level } from '../../services/curriculum';
import LevelCard from './LevelCard';
import LoadingSpinner from '../common/LoadingSpinner';

const CurriculumOverview: React.FC = () => {
  const [levels, setLevels] = useState<Level[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCurriculum();
  }, []);

  const loadCurriculum = async () => {
    try {
      setLoading(true);
      const curriculum = await curriculumService.getCurriculumWithProgress();
      setLevels(curriculum.levels);
    } catch (err) {
      setError('Failed to load curriculum');
      console.error('Error loading curriculum:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="text-red-600 text-lg font-medium mb-2">Error</div>
          <div className="text-gray-600">{error}</div>
          <button
            onClick={loadCurriculum}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Python Learning Path
        </h1>
        <p className="text-gray-600">
          Master Python programming through our structured curriculum designed for progressive learning.
        </p>
      </div>

      <div className="space-y-6">
        {levels.map((level) => (
          <LevelCard key={level.id} level={level} />
        ))}
      </div>

      <div className="mt-12 bg-blue-50 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-blue-900 mb-3">
          How It Works
        </h2>
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
              1
            </div>
            <div>
              <div className="font-medium text-blue-900">Learn</div>
              <div className="text-blue-700">Study topics with AI-powered lessons</div>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
              2
            </div>
            <div>
              <div className="font-medium text-blue-900">Practice</div>
              <div className="text-blue-700">Take quizzes and assessments</div>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
              3
            </div>
            <div>
              <div className="font-medium text-blue-900">Progress</div>
              <div className="text-blue-700">Unlock new levels and advance</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurriculumOverview;