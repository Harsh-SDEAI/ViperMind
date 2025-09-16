import React from 'react';
import { Achievements } from '../../services/dashboard';

interface AchievementsCardProps {
  achievements: Achievements;
}

const AchievementsCard: React.FC<AchievementsCardProps> = ({ achievements }) => {
  const getStreakIcon = (streak: number) => {
    if (streak >= 10) return '🔥';
    if (streak >= 5) return '⚡';
    if (streak >= 3) return '✨';
    return '🎯';
  };

  const getBadgeIcon = (badgeName: string) => {
    switch (badgeName.toLowerCase()) {
      case 'perfectionist':
        return '💎';
      case 'quick learner':
        return '🚀';
      case 'persistent':
        return '💪';
      default:
        return '🏆';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Achievements</h2>
      
      <div className="space-y-6">
        {/* Streaks */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">Learning Streaks</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg p-4 border border-orange-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600">Current Streak</div>
                  <div className="text-2xl font-bold text-orange-600">
                    {achievements.current_streak}
                  </div>
                </div>
                <div className="text-2xl">
                  {getStreakIcon(achievements.current_streak)}
                </div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {achievements.current_streak === 0 ? 'Start your streak!' : 
                 achievements.current_streak === 1 ? 'Keep it going!' :
                 'On fire! 🔥'}
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600">Best Streak</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {achievements.longest_streak}
                  </div>
                </div>
                <div className="text-2xl">👑</div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Personal record
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">Performance Stats</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600">Perfect Scores</div>
                  <div className="text-2xl font-bold text-green-600">
                    {achievements.perfect_scores}
                  </div>
                </div>
                <div className="text-2xl">💯</div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                100% assessments
              </div>
            </div>

            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-gray-600">First Try Passes</div>
                  <div className="text-2xl font-bold text-yellow-600">
                    {achievements.first_try_passes}
                  </div>
                </div>
                <div className="text-2xl">⚡</div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Passed on first attempt
              </div>
            </div>
          </div>
        </div>

        {/* Badges */}
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">Badges Earned</h3>
          {achievements.badges_earned.length === 0 ? (
            <div className="text-center py-6 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
              <div className="text-3xl mb-2">🏆</div>
              <p className="text-sm text-gray-500">No badges earned yet</p>
              <p className="text-xs text-gray-400 mt-1">Keep learning to unlock achievements!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {achievements.badges_earned.map((badge, index) => (
                <div
                  key={index}
                  className="flex items-center space-x-3 p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200"
                >
                  <div className="text-2xl">
                    {getBadgeIcon(badge.name)}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{badge.name}</h4>
                    <p className="text-sm text-gray-600">{badge.description}</p>
                  </div>
                  <div className="text-xs text-purple-600 font-medium">
                    EARNED
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Motivational Message */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">🌟</div>
            <div>
              <h4 className="font-medium text-blue-900">Keep Learning!</h4>
              <p className="text-sm text-blue-700">
                {achievements.current_streak > 0 
                  ? `You're on a ${achievements.current_streak}-assessment streak! Keep it up!`
                  : achievements.perfect_scores > 0
                  ? `You've achieved ${achievements.perfect_scores} perfect scores. Excellent work!`
                  : "Every assessment brings you closer to mastery. You've got this!"
                }
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AchievementsCard;