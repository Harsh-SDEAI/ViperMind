// Common types for the application
export interface User {
  id: string;
  email: string;
  username: string;
  current_level: 'beginner' | 'intermediate' | 'advanced';
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

// Authentication types
export interface LoginCredentials {
  email_or_username: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  password: string;
  current_level?: 'beginner' | 'intermediate' | 'advanced';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}