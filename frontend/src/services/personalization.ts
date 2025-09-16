import api from './api';

export interface UserProfile {
  user_id: string;
  primary_learning_style: string;
  content_preference: string;
  learning_pace: string;
  interests: string[];
  difficulty_preference: string;
  engagement_style: string;
  learning_style_confidence: number;
  adaptation_strategies: any;
  last_analysis_date?: string;
}

export interface LearningStyleUpdate {
  interests: string[];
  preferred_examples: string;
  learning_pace_preference: string;
}

export interface HintRequest {
  question_id: string;
  topic: string;
  difficulty?: string;
  attempts?: number;
  context?: any;
}

export interface PersonalizedHint {
  hint_text: string;
  hint_type: string;
  code_snippet?: string;
  visual_aid?: string;
  follow_up_questions: string[];
  encouragement: string;
  difficulty_level: string;
}

export interface PersonalizedExample {
  title: string;
  description: string;
  code: string;
  explanation: string;
  interest_connection: string;
  difficulty: string;
}

export interface PersonalizedExamples {
  examples: PersonalizedExample[];
  learning_objectives: string[];
  next_steps: string;
}

export interface AdaptiveContent {
  introduction: string;
  core_concepts: Array<{
    concept: string;
    explanation: string;
    example: string;
  }>;
  practice_exercises: Array<{
    exercise: string;
    code_template: string;
    solution_hint: string;
  }>;
  assessment_questions: Array<{
    question: string;
    options: string[];
    correct_answer: number;
    explanation: string;
  }>;
  personalization_notes: string;
}

class PersonalizationService {
  async getUserProfile(): Promise<UserProfile> {
    const response = await api.get('/personalization/profile');
    return response.data;
  }

  async analyzeLearningStyle(): Promise<any> {
    const response = await api.post('/personalization/analyze-learning-style');
    return response.data;
  }

  async updateLearningPreferences(preferences: LearningStyleUpdate): Promise<any> {
    const response = await api.post('/personalization/update-preferences', preferences);
    return response.data;
  }

  async getPersonalizedHint(request: HintRequest): Promise<{
    success: boolean;
    hint: PersonalizedHint;
    personalized: boolean;
    message?: string;
  }> {
    const response = await api.post('/personalization/hint', request);
    return response.data;
  }

  async getPersonalizedExamples(topic: string, contentType: string = 'lesson', currentLevel: string = 'beginner'): Promise<{
    success: boolean;
    examples: PersonalizedExamples;
    personalized: boolean;
  }> {
    const response = await api.post('/personalization/examples', {
      topic,
      content_type: contentType,
      current_level: currentLevel
    });
    return response.data;
  }

  async optimizeDifficulty(topicId: string): Promise<any> {
    const response = await api.post('/personalization/optimize-difficulty', null, {
      params: { topic_id: topicId }
    });
    return response.data;
  }

  async getAdaptiveContent(topic: string): Promise<{
    success: boolean;
    content: AdaptiveContent;
    personalized: boolean;
    source: string;
  }> {
    const response = await api.get(`/personalization/adaptive-content/${topic}`);
    return response.data;
  }

  async getEffectivenessStats(): Promise<{
    total_personalized_content: number;
    avg_content_effectiveness: number;
    personalized_interactions: number;
    avg_interaction_effectiveness: number;
    content_breakdown: { [key: string]: number };
  }> {
    const response = await api.get('/personalization/effectiveness-stats');
    return response.data;
  }
}

export default new PersonalizationService();