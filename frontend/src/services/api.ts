import { RecommendationResponse, CourseMetadata, InteractionEvent, HealthResponse } from '../types/api';

const API_BASE_URL = '/api';

export const api = {
  // Health check
  async getHealth(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return response.json();
  },

  // Get recommendations for a student
  async getRecommendations(studentId: string, k: number = 10): Promise<RecommendationResponse[]> {
    const response = await fetch(`${API_BASE_URL}/recommend/${studentId}?k=${k}`);
    if (!response.ok) {
      throw new Error('Failed to fetch recommendations');
    }
    return response.json();
  },

  // Get course metadata
  async getCourseMetadata(courseId: string): Promise<CourseMetadata> {
    const response = await fetch(`${API_BASE_URL}/course/${courseId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch course metadata');
    }
    return response.json();
  },

  // Record interaction
  async recordInteraction(interaction: InteractionEvent): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/interactions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(interaction),
    });
    
    if (!response.ok) {
      throw new Error('Failed to record interaction');
    }
  },

  // Get interactions queue (for debugging)
  async getInteractionsQueue(): Promise<{ interactions: any[]; count: number }> {
    const response = await fetch(`${API_BASE_URL}/interactions/queue`);
    if (!response.ok) {
      throw new Error('Failed to fetch interactions queue');
    }
    return response.json();
  }
};
