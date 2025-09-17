import api from './api';

export interface Question {
  id: string;
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  code_snippet?: string;
  concept_tags: string[];
  difficulty: string;
}

export interface Assessment {
  assessment_id: string;
  target_id: string;
  target_name: string;
  assessment_type: string;
  questions: Question[];
  time_limit: number; // in minutes
  attempt_number: number;
  max_attempts: number;
  instructions: string;
}

export interface AnswerSubmission {
  question_id: string;
  selected_answer: number;
}

export interface AssessmentSubmission {
  assessment_id: string;
  answers: AnswerSubmission[];
  time_taken: number; // in seconds
}

export interface QuestionResult {
  question_id: string;
  question: string;
  options: string[];
  user_answer: number;
  correct_answer: number;
  is_correct: boolean;
  explanation: string;
  concept_tags: string[];
}

export interface AssessmentResult {
  assessment_id: string;
  score: number;
  passed: boolean;
  total_questions: number;
  correct_answers: number;
  time_taken: number;
  feedback: string;
  question_results: QuestionResult[];
  next_steps: {
    message: string;
    action: string;
    unlock_next: boolean;
    review_topics?: string[][];
  };
}

export interface AssessmentHistory {
  id: string;
  type: string;
  target_id: string;
  score?: number;
  passed?: boolean;
  attempt_number: number;
  time_taken?: number;
  created_at: string;
  submitted_at?: string;
}

export interface AttemptsInfo {
  target_id: string;
  assessment_type: string;
  attempts_used: number;
  max_attempts: number;
  remaining_attempts: number;
  can_attempt: boolean;
  can_retake: boolean;
  best_score: number | null;
  best_passed: boolean;
  retake_requirements?: {
    review_required: boolean;
    message: string;
  };
  assessment_history: Array<{
    id: string;
    attempt_number: number;
    score: number;
    passed: boolean;
    submitted_at: string;
  }>;
}

export interface AssessmentRequest {
  target_id: string;
  assessment_type: 'quiz' | 'section_test' | 'level_final';
  difficulty?: string;
  question_count?: number;
}

class AssessmentService {
  async generateAssessment(request: AssessmentRequest): Promise<Assessment> {
    const response = await api.post('/assessments/generate', request);
    return response.data;
  }

  async submitAssessment(submission: AssessmentSubmission): Promise<AssessmentResult> {
    const response = await api.post('/assessments/submit', submission);
    return response.data;
  }

  async getAssessmentHistory(assessmentType?: string, targetId?: string): Promise<AssessmentHistory[]> {
    const params = new URLSearchParams();
    if (assessmentType) params.append('assessment_type', assessmentType);
    if (targetId) params.append('target_id', targetId);
    
    const response = await api.get(`/assessments/history?${params.toString()}`);
    return response.data.assessments;
  }

  async getRemainingAttempts(targetId: string, assessmentType: string): Promise<AttemptsInfo> {
    const response = await api.get(`/assessments/attempts/${targetId}?assessment_type=${assessmentType}`);
    return response.data;
  }

  async initiateRetake(request: AssessmentRequest): Promise<Assessment> {
    const response = await api.post('/assessments/retake', request);
    return response.data;
  }

  async getBestScores(userId: string) {
    const response = await api.get(`/assessments/best-scores/${userId}`);
    return response.data;
  }
}

const assessmentService = new AssessmentService();
export default assessmentService;