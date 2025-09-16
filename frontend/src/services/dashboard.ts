import api from './api';

export interface UserInfo {
  id: string;
  username: string;
  current_level: string;
  member_since: string;
}

export interface OverallStats {
  topics_completed: number;
  total_topics: number;
  completion_percentage: number;
  assessments_taken: number;
  assessments_passed: number;
  pass_rate: number;
  average_scores: {
    quiz: number;
    section_test: number;
    level_final: number;
  };
  total_study_time_minutes: number;
  remedial_stats: {
    assigned: number;
    completed: number;
    completion_rate: number;
  };
}

export interface SectionProgress {
  section_id: string;
  section_name: string;
  section_code: string;
  total_topics: number;
  completed_topics: number;
  completion_percentage: number;
  section_test_score: number | null;
  section_test_passed: boolean;
}

export interface LevelProgress {
  level_id: string;
  level_name: string;
  level_code: string;
  total_topics: number;
  completed_topics: number;
  completion_percentage: number;
  level_final_score: number | null;
  level_final_passed: boolean;
  is_unlocked: boolean;
  can_advance: boolean;
  sections: SectionProgress[];
}

export interface Activity {
  type: string;
  timestamp: string;
  description: string;
  score?: number;
  passed?: boolean;
  assessment_type?: string;
  topic_name?: string;
}

export interface PerformanceTrend {
  direction: 'improving' | 'declining' | 'stable';
  magnitude: number;
  current_average: number;
  previous_average: number;
  total_assessments: number;
}

export interface LearningInsight {
  type: string;
  title: string;
  message: string;
  action?: string;
  concepts?: string[];
  pattern?: string;
  performance?: string;
}

export interface Recommendation {
  type: string;
  priority: 'high' | 'medium' | 'low';
  title: string;
  message: string;
  action: string;
  topic_id?: string;
}

export interface Badge {
  name: string;
  description: string;
}

export interface Achievements {
  current_streak: number;
  longest_streak: number;
  perfect_scores: number;
  first_try_passes: number;
  badges_earned: Badge[];
}

export interface DashboardData {
  user_info: UserInfo;
  overall_stats: OverallStats;
  level_progress: LevelProgress[];
  recent_activity: Activity[];
  performance_trends: { [key: string]: PerformanceTrend };
  learning_insights: LearningInsight[];
  recommendations: Recommendation[];
  achievements: Achievements;
}

class DashboardService {
  async getDashboardData(): Promise<DashboardData> {
    const response = await api.get('/dashboard/');
    return response.data;
  }

  async getUserStats(): Promise<{
    overall_stats: OverallStats;
    achievements: Achievements;
    performance_trends: { [key: string]: PerformanceTrend };
  }> {
    const response = await api.get('/dashboard/stats');
    return response.data;
  }

  async getLearningInsights(): Promise<{
    learning_insights: LearningInsight[];
    recommendations: Recommendation[];
  }> {
    const response = await api.get('/dashboard/insights');
    return response.data;
  }

  async getRecentActivity(days: number = 7): Promise<{
    recent_activity: Activity[];
    days: number;
  }> {
    const response = await api.get(`/dashboard/activity?days=${days}`);
    return response.data;
  }
}

export default new DashboardService();