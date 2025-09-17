import React, { useEffect, useRef } from 'react';

interface TimerProps {
  timeRemaining: number; // in seconds
  onTimeUp: () => void;
  onTimeUpdate: React.Dispatch<React.SetStateAction<number>>;
}

const Timer: React.FC<TimerProps> = ({ timeRemaining, onTimeUp, onTimeUpdate }) => {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (timeRemaining > 0) {
      intervalRef.current = setInterval(() => {
        onTimeUpdate(prev => {
          const newTime = prev - 1;
          if (newTime <= 0) {
            onTimeUp();
            return 0;
          }
          return newTime;
        });
      }, 1000);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [timeRemaining, onTimeUp, onTimeUpdate]);

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getTimerColor = () => {
    const totalMinutes = Math.floor(timeRemaining / 60);
    if (totalMinutes <= 2) return 'text-red-600 bg-red-50 border-red-200';
    if (totalMinutes <= 5) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-green-600 bg-green-50 border-green-200';
  };



  return (
    <div className="flex items-center space-x-3">
      <div className={`px-4 py-2 rounded-lg border-2 font-mono text-lg font-bold ${getTimerColor()}`}>
        <div className="flex items-center space-x-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{formatTime(timeRemaining)}</span>
        </div>
      </div>
      
      {timeRemaining <= 300 && ( // Show warning when 5 minutes or less
        <div className="text-sm text-red-600 font-medium">
          {timeRemaining <= 60 ? 'Time almost up!' : 'Running low on time!'}
        </div>
      )}
    </div>
  );
};

export default Timer;