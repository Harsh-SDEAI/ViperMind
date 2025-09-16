import React from 'react';
import { Topic } from '../../services/curriculum';
import { useNavigate } from 'react-router-dom';

interface TopicListProps {
  topics: Topic[];
}

const TopicList: React.FC<TopicListProps> = ({ topics }) => {
  const navigate = useNavigate();

  const handleTopicClick = (topic: Topic) => {
    if (topic.is_unlocked) {
      navigate(`/learn/topic/${topic.id}`);
    }
  };

  const handleQuizClick = (topic: Topic, event: React.MouseEvent) => {
    event.stopPropagation();
    if (topic.is_unlocked) {
      navigate(`/quiz/${topic.id}`);
    }
  };

  const getTopicIcon = (topic: Topic) => {
    if (topic.is_completed) {
      return '✅';
    } else if (topic.is_unlocked) {
      return '📖';
    } else {
      return '🔒';
    }
  };

  const getTopicStatus = (topic: Topic) => {
    if (topic.is_completed) {
      return 'Completed';
    } else if (topic.is_unlocked) {
      return 'Available';
    } else {
      return 'Locked';
    }
  };

  const getTopicStatusColor = (topic: Topic) => {
    if (topic.is_completed) {
      return 'text-green-600';
    } else if (topic.is_unlocked) {
      return 'text-blue-600';
    } else {
      return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-2">
      {topics.map((topic) => (
        <div
          key={topic.id}
          className={`flex items-center justify-between p-3 rounded-md border ${
            topic.is_unlocked
              ? 'border-gray-200 bg-white hover:bg-gray-50 cursor-pointer'
              : 'border-gray-100 bg-gray-50 opacity-60'
          }`}
          onClick={() => handleTopicClick(topic)}
        >
          <div className="flex items-center space-x-3">
            <span className="text-lg">{getTopicIcon(topic)}</span>
            <div>
              <div className={`font-medium text-sm ${
                topic.is_unlocked ? 'text-gray-900' : 'text-gray-500'
              }`}>
                {topic.name}
              </div>
              <div className={`text-xs ${getTopicStatusColor(topic)}`}>
                {getTopicStatus(topic)}
                {topic.is_unlocked && topic.progress_percentage !== undefined && topic.progress_percentage > 0 && (
                  <span className="ml-2">
                    • {Math.round(topic.progress_percentage)}% progress
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {topic.is_unlocked && (
              <button
                onClick={(e) => handleQuizClick(topic, e)}
                className="px-3 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full hover:bg-blue-200 transition-colors"
              >
                Quiz
              </button>
            )}
            {topic.is_completed && (
              <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded-full">
                Complete
              </span>
            )}
            {topic.is_unlocked && !topic.is_completed && (
              <svg
                className="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default TopicList;