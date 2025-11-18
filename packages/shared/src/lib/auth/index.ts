const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    username: string;
    full_name: string;
  };
}

export interface SignupResponse {
  id: number;
  email: string;
  username: string;
  full_name: string;
  message: string;
}

export interface ApiError {
  detail: string;
}

// Auth API calls
export const authApi = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username: email, password }),
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail);
    }

    return response.json();
  },

  signup: async (email: string, username: string, password: string, fullName: string): Promise<SignupResponse> => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        username,
        password,
        full_name: fullName,
      }),
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({ detail: 'Signup failed' }));
      throw new Error(error.detail);
    }

    return response.json();
  },
};

// Video API calls
export const videoApi = {
  getVideos: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/videos`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch videos');
    }

    return response.json();
  },

  createVideo: async (token: string, videoData: any) => {
    const response = await fetch(`${API_BASE_URL}/api/videos`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(videoData),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to create video: ${error}`);
    }

    return response.json();
  },

  getVideoById: async (token: string, videoId: number) => {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch video');
    }

    return response.json();
  },

  updateVideo: async (token: string, videoId: number, videoData: any) => {
    const response = await fetch(`${API_BASE_URL}/api/videos/${videoId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(videoData),
    });

    if (!response.ok) {
      throw new Error('Failed to update video');
    }

    return response.json();
  },
};

// Projects API calls
export const projectApi = {
  getProjects: async (token: string) => {
    const response = await fetch(`${API_BASE_URL}/api/projects`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch projects');
    }

    return response.json();
  },

  createProject: async (token: string, projectData: any) => {
    const response = await fetch(`${API_BASE_URL}/api/projects`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(projectData),
    });

    if (!response.ok) {
      throw new Error('Failed to create project');
    }

    return response.json();
  },
};
