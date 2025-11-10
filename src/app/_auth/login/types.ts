// Type definitions for the Login feature

export interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export interface LoginResponse {
  user: {
    id: string;
    email: string;
    name: string;
    avatar?: string;
  };
  session: {
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  };
}

export interface LoginError {
  error: {
    code: string;
    message: string;
    details?: Record<string, string>;
  };
}

export interface SocialProvider {
  id: 'google' | 'facebook' | 'twitter';
  name: string;
  icon: string;
  color: string;
}
