import React, { useState } from 'react';
import { RemedialContent } from '../../services/remedial';

interface ReviewScheduleProps {
  content: RemedialContent;
  onComplete: () => void;
}

const ReviewSchedule: React.FC<ReviewScheduleProps> = ({ content, onComplete }) => {
  const [completedDays, setCompletedDays] = useState<Set<number>>(new Set());
  const [expandedDay, setExpandedDay] = useState<number | null>(null);

  const schedule = content.ai_generated_content;

  if (!schedule || !schedule.daily_schedule) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">No review schedule available</p>
      </div>
    );
  }

  const handleDayComplete = (day: number) => {
    const newCompleted = new Set(completedDays);
    if (completedDays.has(day)) {
      newCompleted.delete(day);
    } else {
      newCompleted.add(day);
    }
    setCompletedDays(newCompleted);

    // If all days are completed, mark the entire review as complete
    if (newCompleted.size === schedule.daily_schedule.length) {
      onComplete();
    }
  };

  const toggleDayExpansion = (day: number) => {
    setExpandedDay(expandedDay === day ? null : day);
  };

  const completionPercentage = (completedDays.size / schedule.daily_schedule.length) * 100;

  return (
    <div className="space-y-6">
      {/* Schedule Overview */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-blue-900 mb-2">{schedule.title}</h3>
        <p className="text-blue-800 mb-4">{schedule.overview}</p>
        
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-blue-700 mb-1">
            <span>Progress</span>
            <span>{completedDays.size} of {schedule.daily_schedule.length} days completed</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${completionPercentage}%` }}
            ></div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-blue-700 font-medium">Duration:</span>
            <span className="ml-2 text-blue-800">7 days</span>
          </div>
          <div>
            <span className="text-blue-700 font-medium">Daily Time:</span>
            <span className="ml-2 text-blue-800">2-3 hours</span>
          </div>
        </div>
      </div>

      {/* Daily Schedule */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-900">Daily Schedule</h4>
        
        {schedule.daily_schedule.map((daySchedule: any, index: number) => (
          <div
            key={daySchedule.day}
            className={`border rounded-lg transition-all duration-200 ${
              completedDays.has(daySchedule.day) 
                ? 'bg-green-50 border-green-200' 
                : 'bg-white border-gray-200'
            }`}
          >
            {/* Day Header */}
            <div 
              className="p-4 cursor-pointer"
              onClick={() => toggleDayExpansion(daySchedule.day)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDayComplete(daySchedule.day);
                    }}
                    className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors ${
                      completedDays.has(daySchedule.day)
                        ? 'bg-green-600 border-green-600 text-white'
                        : 'border-gray-300 hover:border-green-400'
                    }`}
                  >
                    {completedDays.has(daySchedule.day) && (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </button>
                  
                  <div>
                    <h5 className={`font-semibold ${
                      completedDays.has(daySchedule.day) ? 'text-green-800' : 'text-gray-900'
                    }`}>
                      Day {daySchedule.day}: {daySchedule.title}
                    </h5>
                    <p className={`text-sm ${
                      completedDays.has(daySchedule.day) ? 'text-green-700' : 'text-gray-600'
                    }`}>
                      {daySchedule.goal}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    completedDays.has(daySchedule.day)
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {daySchedule.estimated_time}
                  </span>
                  
                  <svg 
                    className={`w-5 h-5 text-gray-400 transform transition-transform ${
                      expandedDay === daySchedule.day ? 'rotate-180' : ''
                    }`} 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Day Details */}
            {expandedDay === daySchedule.day && (
              <div className="px-4 pb-4 border-t">
                <div className="pt-4 space-y-4">
                  {/* Topics */}
                  <div>
                    <h6 className="font-medium text-gray-900 mb-2">Topics to Review:</h6>
                    <div className="flex flex-wrap gap-2">
                      {daySchedule.topics.map((topic: string, topicIndex: number) => (
                        <span
                          key={topicIndex}
                          className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Activities */}
                  <div>
                    <h6 className="font-medium text-gray-900 mb-2">Activities:</h6>
                    <ul className="space-y-1">
                      {daySchedule.activities.map((activity: string, activityIndex: number) => (
                        <li key={activityIndex} className="flex items-start">
                          <svg className="w-4 h-4 text-blue-500 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="text-gray-700 text-sm">{activity}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Resources */}
      {schedule.resources && schedule.resources.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h5 className="font-medium text-gray-900 mb-3">Recommended Resources</h5>
          <ul className="space-y-2">
            {schedule.resources.map((resource: string, index: number) => (
              <li key={index} className="flex items-start">
                <svg className="w-4 h-4 text-gray-500 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                <span className="text-gray-700 text-sm">{resource}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Milestones */}
      {schedule.milestones && schedule.milestones.length > 0 && (
        <div className="bg-yellow-50 rounded-lg p-4">
          <h5 className="font-medium text-yellow-900 mb-3">Milestones to Track</h5>
          <ul className="space-y-2">
            {schedule.milestones.map((milestone: string, index: number) => (
              <li key={index} className="flex items-start">
                <svg className="w-4 h-4 text-yellow-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
                <span className="text-yellow-800 text-sm">{milestone}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Retake Preparation */}
      {schedule.retake_preparation && (
        <div className="bg-green-50 border-l-4 border-green-400 rounded-r-lg p-4">
          <h5 className="font-medium text-green-900 mb-2">Retake Preparation</h5>
          <p className="text-green-800 text-sm">{schedule.retake_preparation}</p>
        </div>
      )}

      {/* Complete Button */}
      {completedDays.size === schedule.daily_schedule.length && (
        <div className="text-center pt-4">
          <button
            onClick={onComplete}
            className="px-8 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium text-lg"
          >
            Complete Review Schedule
          </button>
        </div>
      )}
    </div>
  );
};

export default ReviewSchedule;