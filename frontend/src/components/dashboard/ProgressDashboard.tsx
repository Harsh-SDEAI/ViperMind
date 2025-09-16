import React, { useState, useEffect } from 'react';
import { useResponsive } from '../../hooks/useResponsive';
import dashboardService, { DashboardData } from '../../services/dashboard';
import OverallStatsCard from './OverallStatsCard';
import LevelProgressCard from './LevelProgressCard';
import RecentActivityCard from './RecentActivityCard';
import PerformanceTrendsCard from './PerformanceTrendsCard';
import LearningInsightsCard from './LearningInsightsCard';
import RecommendationsCard from './RecommendationsCard';
import AchievementsCard from './AchievementsCard';
import MobileDashboard from './MobileDashboard';

const ProgressDashboard: React.FC = () => {
  const { isMobile } = useResponsive();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Use mobile dashboard for mobile devices
  if (isMobile) {
    return <MobileDashboard />;
  }

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

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="bg-white rounded-lg p-6 h-32">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-6 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-medium text-red-900 mb-2">Unable to Load Dashboard</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={fetchDashboardData}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {dashboardData.user_info.username}!
            </h1>
            <p className="text-gray-600 mt-1">
              Here's your learning progress and insights
            </p>
          </div>
          
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
              refreshing 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <svg 
              className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>

        {/* Overall Stats */}
        <div className="mb-8">
          <OverallStatsCard stats={dashboardData.overall_stats} />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Left Column - Level Progress */}
          <div className="lg:col-span-2">
            <LevelProgressCard levelProgress={dashboardData.level_progress} />
          </div>

          {/* Right Column - Insights and Recommendations */}
          <div className="space-y-6">
            <LearningInsightsCard insights={dashboardData.learning_insights} />
            <RecommendationsCard recommendations={dashboardData.recommendations} />
          </div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Activity */}
          <div>
            <RecentActivityCard activities={dashboardData.recent_activity} />
          </div>

          {/* Performance Trends */}
          <div>
            <PerformanceTrendsCard trends={dashboardData.performance_trends} />
          </div>

          {/* Achievements */}
          <div>
            <AchievementsCard achievements={dashboardData.achievements} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressDashboard;