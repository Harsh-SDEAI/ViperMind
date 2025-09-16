import React, { useEffect } from 'react';

interface MobileTimerProps {
  timeRemaining: number;
  onTimeUp: () => void;
  onTimeUpdate: (time: number) => void;
}

const MobileTimer: React.FC<MobileTimerProps> = ({
  timeRemaining,
  onTimeUp,
  onTimeUpdate
}) => {
  useEffect(() => {
    if (timeRemaining <= 0) {
      onTimeUp();
      return;
    }

    const timer = setInterval(() => {
      const newTime = timeRemaining - 1;
      onTimeUpdate(newTime);
      
      if (newTime <= 0) {
        onTimeUp();
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [timeRemaining, onTimeUp, onTimeUpdate]);

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getTimerColor = (seconds: number): string => {
    if (seconds <= 60) return 'text-red-600'; // Last minute
    if (seconds <= 300) return 'text-yellow-600'; // Last 5 minutes
    return 'text-gray-700';
  };

  const getTimerIcon = (seconds: number): string => {
    if (seconds <= 60) return '⏰';
    if (seconds <= 300) return '⏱️';
    return '🕐';
  };

  return (
    <div className={`flex items-center text-sm font-medium ${getTimerColor(timeRemaining)}`}>
      <span className="mr-1">{getTimerIcon(timeRemaining)}</span>
      <span>{formatTime(timeRemaining)}</span>
    </div>
  );
};

export default MobileTimer;