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
export declare const authApi: {
    login: (email: string, password: string) => Promise<LoginResponse>;
    signup: (email: string, username: string, password: string, fullName: string) => Promise<SignupResponse>;
};
export declare const videoApi: {
    getVideos: (token: string) => Promise<any>;
    createVideo: (token: string, videoData: any) => Promise<any>;
    getVideoById: (token: string, videoId: number) => Promise<any>;
    updateVideo: (token: string, videoId: number, videoData: any) => Promise<any>;
};
export declare const projectApi: {
    getProjects: (token: string) => Promise<any>;
    createProject: (token: string, projectData: any) => Promise<any>;
};
