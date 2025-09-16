import api from './api';

export interface CodeExample {
  title: string;
  code: string;
  explanation: string;
  output?: string;
}

export interface LessonContent {
  why_it_matters: string;
  key_ideas: string[];
  examples: CodeExample[];
  pitfalls: string[];
  recap: string;
}

export interface UserProgress {
  status: string;
  best_score?: number;
  attempts: number;
  time_spent: number;
  last_accessed?: string;
}

export interface LessonResponse {
  topic_id: string;
  topic_name: string;
  lesson_content: LessonContent;
  is_generated: boolean;
  user_progress: UserProgress;
}

export interface NextTopic {
  id: string;
  name: string;
  order: number;
}

export interface NavigationResponse {
  next_topic?: NextTopic;
  previous_topic?: NextTopic;
  same_section?: boolean;
  message?: string;
  next_section?: {
    id: string;
    name: string;
    code: string;
  };
  previous_section?: {
    id: string;
    name: string;
    code: string;
  };
}

export interface ProgressUpdate {
  topic_id: string;
  completed?: boolean;
  time_spent?: number;
}

class LessonService {
  async getLessonContent(topicId: string): Promise<LessonResponse> {
    const response = await api.get(`/lessons/topic/${topicId}`);
    return response.data;
  }

  async updateProgress(progressUpdate: ProgressUpdate): Promise<any> {
    const response = await api.post('/lessons/progress/update', progressUpdate);
    return response.data;
  }

  async getNextTopic(topicId: string): Promise<NavigationResponse> {
    const response = await api.get(`/lessons/topic/${topicId}/next`);
    return response.data;
  }

  async getPreviousTopic(topicId: string): Promise<NavigationResponse> {
    const response = await api.get(`/lessons/topic/${topicId}/previous`);
    return response.data;
  }
}

export default new LessonService();