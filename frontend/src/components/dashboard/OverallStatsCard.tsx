import React from 'react';
import { OverallStats } from '../../services/dashboard';

interface OverallStatsCardProps {
  stats: OverallStats;
}

const OverallStatsCard: React.FC<OverallStatsCardProps> = ({ stats }) => {
  const formatTime = (minutes: number): string => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Learning Overview</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {/* Topics Progress */}
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-3">
            <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-gray-200"
                stroke="currentColor"
                strokeWidth="3"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-blue-600"
                stroke="currentColor"
                strokeWidth="3"
                strokeDasharray={`${stats.completion_percentage}, 100`}
                strokeLinecap="round"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-sm font-semibold text-gray-900">
                {Math.round(stats.completion_percentage)}%
              </span>
            </div>
          </div>
          <div className="text-sm text-gray-600">Topics Completed</div>
          <div className="text-lg font-semibold text-gray-900">
            {stats.topics_completed}/{stats.total_topics}
          </div>
        </div>

        {/* Assessment Pass Rate */}
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-3">
            <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-gray-200"
                stroke="currentColor"
                strokeWidth="3"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className={stats.pass_rate >= 80 ? 'text-green-600' : stats.pass_rate >= 60 ? 'text-yellow-600' : 'text-red-600'}
                stroke="currentColor"
                strokeWidth="3"
                strokeDasharray={`${stats.pass_rate}, 100`}
                strokeLinecap="round"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-sm font-semibold text-gray-900">
                {Math.round(stats.pass_rate)}%
              </span>
            </div>
          </div>
          <div className="text-sm text-gray-600">Pass Rate</div>
          <div className="text-lg font-semibold text-gray-900">
            {stats.assessments_passed}/{stats.assessments_taken}
          </div>
        </div>

        {/* Study Time */}
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-3 bg-purple-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="text-sm text-gray-600">Study Time</div>
          <div className="text-lg font-semibold text-gray-900">
            {formatTime(stats.total_study_time_minutes)}
          </div>
        </div>

        {/* Remedial Progress */}
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-3 bg-orange-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <div className="text-sm text-gray-600">Remedial Help</div>
          <div className="text-lg font-semibold text-gray-900">
            {stats.remedial_stats.completed}/{stats.remedial_stats.assigned}
          </div>
        </div>
      </div>

      {/* Average Scores */}
      <div className="mt-8 pt-6 border-t">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Average Scores</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-1">Quizzes</div>
            <div className={`text-2xl font-bold ${getScoreColor(stats.average_scores.quiz)}`}>
              {stats.average_scores.quiz}%
            </div>
            <div className="text-xs text-gray-500">Need 70%</div>
          </div>
          
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-1">Section Tests</div>
            <div className={`text-2xl font-bold ${getScoreColor(stats.average_scores.section_test)}`}>
              {stats.average_scores.section_test}%
            </div>
            <div className="text-xs text-gray-500">Need 75%</div>
          </div>
          
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-1">Level Finals</div>
            <div className={`text-2xl font-bold ${getScoreColor(stats.average_scores.level_final)}`}>
              {stats.average_scores.level_final}%
            </div>
            <div className="text-xs text-gray-500">Need 80%</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OverallStatsCard;