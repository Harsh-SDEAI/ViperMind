import React from 'react';

interface MobileStatsCardProps {
  title: string;
  value: string;
  subtitle?: string;
  percentage?: number;
  icon: string;
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red';
}

const MobileStatsCard: React.FC<MobileStatsCardProps> = ({
  title,
  value,
  subtitle,
  percentage,
  icon,
  color
}) => {
  const getColorClasses = (color: string) => {
    switch (color) {
      case 'blue':
        return 'bg-blue-50 border-blue-200 text-blue-700';
      case 'green':
        return 'bg-green-50 border-green-200 text-green-700';
      case 'purple':
        return 'bg-purple-50 border-purple-200 text-purple-700';
      case 'orange':
        return 'bg-orange-50 border-orange-200 text-orange-700';
      case 'red':
        return 'bg-red-50 border-red-200 text-red-700';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-700';
    }
  };

  const getProgressColor = (color: string) => {
    switch (color) {
      case 'blue': return 'bg-blue-500';
      case 'green': return 'bg-green-500';
      case 'purple': return 'bg-purple-500';
      case 'orange': return 'bg-orange-500';
      case 'red': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className={`rounded-lg border p-4 ${getColorClasses(color)}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <div className="text-right">
          <div className="text-lg font-bold">{value}</div>
          {subtitle && (
            <div className="text-xs opacity-75">{subtitle}</div>
          )}
        </div>
      </div>
      
      <div className="text-sm font-medium mb-1">{title}</div>
      
      {percentage !== undefined && (
        <div className="w-full bg-white bg-opacity-50 rounded-full h-1.5">
          <div 
            className={`h-1.5 rounded-full transition-all duration-300 ${getProgressColor(color)}`}
            style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
          />
        </div>
      )}
    </div>
  );
};

export default MobileStatsCard;