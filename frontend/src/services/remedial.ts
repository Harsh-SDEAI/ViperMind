import api from './api';

export interface RemedialCard {
  id: string;
  topic_concept: string;
  explanation: string;
  code_example?: string;
  practice_question?: {
    question: string;
    options: string[];
    correct_answer: number;
    explanation: string;
  };
  hints: string[];
  is_completed: boolean;
  attempts: number;
  time_spent: number;
}

export interface RemedialContent {
  id: string;
  assessment_id: string;
  target_id: string;
  type: 'mini_explainer' | 'remedial_card' | 'review_week';
  title: string;
  content: string;
  ai_generated_content?: any;
  weak_concepts: string[];
  status: 'assigned' | 'in_progress' | 'completed' | 'skipped';
  completion_percentage: number;
  time_spent: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  cards?: RemedialCard[];
}

export interface RemedialProgress {
  total_assigned: number;
  completed: number;
  in_progress: number;
  completion_percentage: number;
  time_spent_total: number;
  weak_concepts: string[];
  concept_frequency: { [key: string]: number };
}

class RemedialService {
  async generateRemedialContent(assessmentId: string): Promise<any> {
    const response = await api.post('/remedial/generate', null, {
      params: { assessment_id: assessmentId }
    });
    return response.data;
  }

  async getUserRemedialContent(userId: string): Promise<{ remedial_content: RemedialContent[] }> {
    const response = await api.get(`/remedial/user/${userId}`);
    return response.data;
  }

  async getRemedialContent(remedialId: string): Promise<RemedialContent> {
    const response = await api.get(`/remedial/${remedialId}`);
    return response.data;
  }

  async completeRemedialContent(remedialId: string, timeSpent: number = 0): Promise<any> {
    const response = await api.post(`/remedial/${remedialId}/complete`, { time_spent: timeSpent });
    return response.data;
  }

  async completeRemedialCard(cardId: string, timeSpent: number = 0): Promise<any> {
    const response = await api.post(`/remedial/cards/${cardId}/complete`, { time_spent: timeSpent });
    return response.data;
  }

  async getRemedialProgress(userId: string): Promise<RemedialProgress> {
    const response = await api.get(`/remedial/progress/${userId}`);
    return response.data;
  }
}

export default new RemedialService();