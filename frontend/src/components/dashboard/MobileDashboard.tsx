import React, { useState, useEffect } from 'react';
import dashboardService, { DashboardData } from '../../services/dashboard';
import MobileStatsCard from './MobileStatsCard';
import MobileLevelProgress from './MobileLevelProgress';
import MobileRecentActivity from './MobileRecentActivity';
import MobileRecommendations from './MobileRecommendations';

const MobileDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'progress' | 'activity'>('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardService.getDashboardData();
      setDashboardData(data);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          <div className="grid grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
          <div className="h-40 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg p-6 max-w-sm w-full text-center shadow-lg">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Unable to Load Dashboard</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'progress', label: 'Progress', icon: '📈' },
    { id: 'activity', label: 'Activity', icon: '📝' }
  ] as const;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4">
        <h1 className="text-xl font-bold text-gray-900">
          Welcome back, {dashboardData.user_info.username}! 👋
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          Here's your learning progress
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200 px-4">
        <div className="flex space-x-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center px-3 py-3 text-sm font-medium rounded-t-lg transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-4 space-y-4">
        {activeTab === 'overview' && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              <MobileStatsCard
                title="Topics"
                value={`${dashboardData.overall_stats.topics_completed}/${dashboardData.overall_stats.total_topics}`}
                percentage={dashboardData.overall_stats.completion_percentage}
                icon="📚"
                color="blue"
              />
              <MobileStatsCard
                title="Pass Rate"
                value={`${Math.round(dashboardData.overall_stats.pass_rate)}%`}
                percentage={dashboardData.overall_stats.pass_rate}
                icon="✅"
                color="green"
              />
              <MobileStatsCard
                title="Study Time"
                value={`${Math.floor(dashboardData.overall_stats.total_study_time_minutes / 60)}h`}
                subtitle={`${dashboardData.overall_stats.total_study_time_minutes % 60}m`}
                icon="⏱️"
                color="purple"
              />
              <MobileStatsCard
                title="Streak"
                value={`${dashboardData.achievements.current_streak}`}
                subtitle="assessments"
                icon="🔥"
                color="orange"
              />
            </div>

            {/* Recommendations */}
            <MobileRecommendations recommendations={dashboardData.recommendations} />

            {/* Quick Actions */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                <button className="flex items-center justify-center p-3 bg-blue-50 text-blue-700 rounded-lg border border-blue-200">
                  <span className="mr-2">📖</span>
                  <span className="text-sm font-medium">Continue Learning</span>
                </button>
                <button className="flex items-center justify-center p-3 bg-green-50 text-green-700 rounded-lg border border-green-200">
                  <span className="mr-2">📝</span>
                  <span className="text-sm font-medium">Take Quiz</span>
                </button>
              </div>
            </div>
          </>
        )}

        {activeTab === 'progress' && (
          <MobileLevelProgress levelProgress={dashboardData.level_progress} />
        )}

        {activeTab === 'activity' && (
          <MobileRecentActivity activities={dashboardData.recent_activity} />
        )}
      </div>
    </div>
  );
};

export default MobileDashboard;