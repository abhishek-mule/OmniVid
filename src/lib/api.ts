import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1_PREFIX = '/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}${API_V1_PREFIX}`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Types
export interface VideoCreateRequest {
  prompt: string;
  resolution: '720p' | '1080p' | '2k' | '4k';
  fps: 24 | 30 | 60;
  duration: number;
  quality: 'fast' | 'balanced' | 'best';
  render_engine?: 'remotion' | 'ffmpeg' | 'manim' | 'blender';
}

export interface VideoResponse {
  id: string;
  user_id?: string;
  prompt: string;
  resolution: string;
  fps: number;
  duration: number;
  quality: string;
  render_engine?: string;
  status: 'pending' | 'parsing' | 'rendering' | 'encoding' | 'finalizing' | 'success' | 'failed';
  progress: number;
  current_stage?: string;
  celery_task_id?: string;
  output_url?: string;
  file_size?: number;
  thumbnail_url?: string;
  error_message?: string;
  created_at?: string;
  updated_at?: string;
  started_at?: string;
  completed_at?: string;
}

export interface VideoListResponse {
  videos: VideoResponse[];
  total: number;
  page: number;
  page_size: number;
}

// API Methods
export const videoApi = {
  /**
   * Create a new video generation request
   */
  async createVideo(data: VideoCreateRequest): Promise<VideoResponse> {
    const response = await apiClient.post<VideoResponse>('/videos/', data);
    return response.data;
  },

  /**
   * Get video status and details
   */
  async getVideo(videoId: string): Promise<VideoResponse> {
    const response = await apiClient.get<VideoResponse>(`/videos/${videoId}`);
    return response.data;
  },

  /**
   * List all videos with pagination
   */
  async listVideos(params?: {
    page?: number;
    page_size?: number;
    status?: string;
  }): Promise<VideoListResponse> {
    const response = await apiClient.get<VideoListResponse>('/videos/', { params });
    return response.data;
  },

  /**
   * Download video file
   */
  getDownloadUrl(videoId: string): string {
    return `${API_BASE_URL}${API_V1_PREFIX}/videos/${videoId}/download`;
  },

  /**
   * Delete a video
   */
  async deleteVideo(videoId: string): Promise<{ message: string; video_id: string }> {
    const response = await apiClient.delete(`/videos/${videoId}`);
    return response.data;
  },

  /**
   * Cancel video generation
   */
  async cancelVideo(videoId: string): Promise<{ message: string; video_id: string }> {
    const response = await apiClient.post(`/videos/${videoId}/cancel`);
    return response.data;
  },
};

// Health check
export const healthApi = {
  async check(): Promise<{ status: string; database: string; redis: string; celery: string }> {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },
};

export type TemplateItem = {
  id: string;
  name: string;
  description: string;
  thumbnail: string;
  category: string;
};

function httpToWs(url: string) {
  if (url.startsWith('https://')) return url.replace('https://', 'wss://');
  if (url.startsWith('http://')) return url.replace('http://', 'ws://');
  return url;
}

export const simpleApi = {
  async listTemplates(): Promise<TemplateItem[]> {
    // Placeholder: return empty list if backend templates endpoint is not available
    try {
      const res = await axios.get(`${API_BASE_URL}/templates`);
      return Array.isArray(res.data) ? res.data as TemplateItem[] : [];
    } catch {
      return [];
    }
  },
  async createVideo(payload: { prompt: string; settings?: any }): Promise<{ video_id: string }> {
    const data: VideoCreateRequest = {
      prompt: payload.prompt,
      resolution: (payload?.settings?.resolution as any) || '1080p',
      fps: (payload?.settings?.fps as any) || 30,
      duration: (payload?.settings?.duration as any) || 15,
      quality: (payload?.settings?.quality as any) || 'balanced',
      render_engine: (payload?.settings?.render_engine as any) || 'remotion',
    };
    const resp = await videoApi.createVideo(data);
    return { video_id: resp.id };
  },
  getWebSocketUrl(videoId: string): string {
    const base = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
    return `${httpToWs(base)}/ws/videos/${videoId}`;
  },
  getDownloadUrl(videoId: string): string {
    return videoApi.getDownloadUrl(videoId);
  },
};

export default apiClient;
