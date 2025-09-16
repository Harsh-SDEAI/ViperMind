import React from 'react';

interface ProgressBarProps {
  percentage: number;
  color?: 'blue' | 'green' | 'purple' | 'gray';
  height?: string;
  showLabel?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ 
  percentage, 
  color = 'blue', 
  height = 'h-2',
  showLabel = false 
}) => {
  const colorClasses = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    purple: 'bg-purple-600',
    gray: 'bg-gray-600'
  };

  const backgroundClasses = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    purple: 'bg-purple-100',
    gray: 'bg-gray-100'
  };

  const clampedPercentage = Math.min(Math.max(percentage, 0), 100);

  return (
    <div className="w-full">
      <div className={`${backgroundClasses[color]} rounded-full ${height} overflow-hidden`}>
        <div
          className={`${colorClasses[color]} ${height} rounded-full transition-all duration-300 ease-out`}
          style={{ width: `${clampedPercentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="text-xs text-gray-600 mt-1 text-right">
          {Math.round(clampedPercentage)}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;