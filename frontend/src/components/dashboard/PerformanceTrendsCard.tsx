import React from 'react';
import { PerformanceTrend } from '../../services/dashboard';

interface PerformanceTrendsCardProps {
  trends: { [key: string]: PerformanceTrend };
}

const PerformanceTrendsCard: React.FC<PerformanceTrendsCardProps> = ({ trends }) => {
  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'improving':
        return (
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        );
      case 'declining':
        return (
          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
          </svg>
        );
      case 'stable':
        return (
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
          </svg>
        );
      default:
        return (
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        );
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'improving':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'declining':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'stable':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const formatAssessmentType = (type: string) => {
    return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getTrendMessage = (trend: PerformanceTrend, type: string) => {
    const typeFormatted = formatAssessmentType(type);
    
    switch (trend.direction) {
      case 'improving':
        return `Your ${typeFormatted.toLowerCase()} scores are improving! Up ${trend.magnitude.toFixed(1)}% from ${trend.previous_average}% to ${trend.current_average}%.`;
      case 'declining':
        return `Your ${typeFormatted.toLowerCase()} scores have declined by ${trend.magnitude.toFixed(1)}% from ${trend.previous_average}% to ${trend.current_average}%. Consider reviewing the material.`;
      case 'stable':
        return `Your ${typeFormatted.toLowerCase()} scores are stable at around ${trend.current_average}%. Consistent performance!`;
      default:
        return `${typeFormatted} performance data available.`;
    }
  };

  const trendEntries = Object.entries(trends);

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Performance Trends</h2>
      
      {trendEntries.length === 0 ? (
        <div className="text-center py-8">
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-gray-500">No trend data available</p>
          <p className="text-sm text-gray-400 mt-1">Complete more assessments to see your performance trends!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {trendEntries.map(([type, trend]) => (
            <div
              key={type}
              className={`p-4 rounded-lg border ${getTrendColor(trend.direction)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {getTrendIcon(trend.direction)}
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-900 mb-1">
                      {formatAssessmentType(type)}
                    </h3>
                    <p className="text-sm text-gray-700 mb-2">
                      {getTrendMessage(trend, type)}
                    </p>
                    <div className="text-xs text-gray-600">
                      Based on {trend.total_assessments} recent assessments
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-lg font-semibold text-gray-900">
                    {trend.current_average}%
                  </div>
                  <div className={`text-sm font-medium ${
                    trend.direction === 'improving' ? 'text-green-600' :
                    trend.direction === 'declining' ? 'text-red-600' :
                    'text-blue-600'
                  }`}>
                    {trend.direction === 'improving' && '+'}
                    {trend.direction === 'declining' && '-'}
                    {trend.direction !== 'stable' && `${trend.magnitude.toFixed(1)}%`}
                    {trend.direction === 'stable' && 'Stable'}
                  </div>
                </div>
              </div>

              {/* Mini Progress Bars */}
              <div className="mt-3 flex items-center space-x-2">
                <span className="text-xs text-gray-500 w-12">Before:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                  <div 
                    className="bg-gray-400 h-1.5 rounded-full"
                    style={{ width: `${trend.previous_average}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-600 w-8">{trend.previous_average}%</span>
              </div>
              
              <div className="mt-1 flex items-center space-x-2">
                <span className="text-xs text-gray-500 w-12">Now:</span>
                <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                  <div 
                    className={`h-1.5 rounded-full ${
                      trend.direction === 'improving' ? 'bg-green-500' :
                      trend.direction === 'declining' ? 'bg-red-500' :
                      'bg-blue-500'
                    }`}
                    style={{ width: `${trend.current_average}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-600 w-8">{trend.current_average}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PerformanceTrendsCard;