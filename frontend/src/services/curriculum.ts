import api from './api';

export interface Topic {
  id: string;
  name: string;
  order: number;
  is_unlocked?: boolean;
  is_completed?: boolean;
  progress_percentage?: number;
}

export interface Section {
  id: string;
  name: string;
  code: string;
  description?: string;
  order: number;
  topics: Topic[];
  is_unlocked?: boolean;
  completion_percentage?: number;
}

export interface Level {
  id: string;
  name: string;
  code: string;
  description?: string;
  order: number;
  sections: Section[];
  is_unlocked?: boolean;
  completion_percentage?: number;
}

export interface CurriculumStructure {
  levels: Level[];
}

export interface CurriculumWithProgress {
  levels: Level[];
}

class CurriculumService {
  async getCurriculumStructure(): Promise<CurriculumStructure> {
    const response = await api.get('/curriculum/structure');
    return response.data;
  }

  async getCurriculumWithProgress(): Promise<CurriculumWithProgress> {
    const response = await api.get('/curriculum/progress');
    return response.data;
  }

  async getLevelDetails(levelId: string): Promise<Level> {
    const response = await api.get(`/curriculum/levels/${levelId}`);
    return response.data;
  }

  async getSectionDetails(sectionId: string): Promise<Section> {
    const response = await api.get(`/curriculum/sections/${sectionId}`);
    return response.data;
  }

  async getTopicDetails(topicId: string): Promise<Topic> {
    const response = await api.get(`/curriculum/topics/${topicId}`);
    return response.data;
  }
}

export default new CurriculumService();