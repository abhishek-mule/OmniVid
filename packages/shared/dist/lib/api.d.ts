import { AxiosInstance } from 'axios';
declare const apiClient: AxiosInstance;
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
export declare const videoApi: {
    /**
     * Create a new video generation request
     */
    createVideo(data: VideoCreateRequest): Promise<VideoResponse>;
    /**
     * Get video status and details
     */
    getVideo(videoId: string): Promise<VideoResponse>;
    /**
     * List all videos with pagination
     */
    listVideos(params?: {
        page?: number;
        page_size?: number;
        status?: string;
    }): Promise<VideoListResponse>;
    /**
     * Download video file
     */
    getDownloadUrl(videoId: string): string;
    /**
     * Delete a video
     */
    deleteVideo(videoId: string): Promise<{
        message: string;
        video_id: string;
    }>;
    /**
     * Cancel video generation
     */
    cancelVideo(videoId: string): Promise<{
        message: string;
        video_id: string;
    }>;
};
export declare const healthApi: {
    check(): Promise<{
        status: string;
        database: string;
        redis: string;
        celery: string;
    }>;
};
export type TemplateItem = {
    id: string;
    name: string;
    description: string;
    thumbnail: string;
    category: string;
};
export declare const simpleApi: {
    listTemplates(): Promise<TemplateItem[]>;
    createVideo(payload: {
        prompt: string;
        settings?: any;
    }): Promise<{
        video_id: string;
    }>;
    getWebSocketUrl(videoId: string): string;
    getDownloadUrl(videoId: string): string;
};
export default apiClient;
