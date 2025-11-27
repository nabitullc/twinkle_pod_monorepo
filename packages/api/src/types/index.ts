export interface User {
  user_id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface ChildProfile {
  child_id: string;
  user_id: string;
  name: string;
  age: number;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Story {
  story_id: string;
  title: string;
  age_range: string;
  categories: string[];
  tags: string[];
  s3_key: string;
  thumbnail_url: string;
  duration_minutes: number;
  moral?: string;
  published: boolean;
  created_at: string;
}

export interface Progress {
  pk: string; // user_id#child_id#story_id
  user_id: string;
  child_id: string;
  story_id: string;
  paragraph_index: number;
  percentage: number;
  last_read: string;
  completed: boolean;
  completed_at?: string;
}

export interface InteractionEvent {
  event_id: string;
  user_id: string;
  child_id: string;
  story_id: string;
  event_type: 'view' | 'favorite' | 'unfavorite' | 'complete';
  timestamp: string;
  session_id?: string;
  device_type?: string;
  source?: string;
}
