export interface RecommendationResponse {
  course_id: string;
  score: number;
  explanation: string[];
}

export interface CourseMetadata {
  course_id: string;
  title: string;
  description?: string;
  skill_tags?: string;
  difficulty?: string;
  duration?: string;
}

export interface InteractionEvent {
  student_id: string;
  course_id: string;
  event_type: 'like' | 'dislike' | 'view' | 'enroll' | 'complete' | 'rate';
  timestamp?: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  models_loaded: boolean;
}
