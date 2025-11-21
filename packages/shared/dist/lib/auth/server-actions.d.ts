export declare function login(formData: FormData): Promise<{
    error: string;
    success?: undefined;
} | {
    success: boolean;
    error?: undefined;
}>;
export declare function register(formData: FormData): Promise<{
    error: string;
    success?: undefined;
} | {
    success: boolean;
    error?: undefined;
}>;
export declare function logout(): Promise<void>;
export declare function requestPasswordReset(formData: FormData): Promise<{
    success: boolean;
    error?: undefined;
} | {
    error: string;
    success?: undefined;
}>;
export declare function resetPassword(formData: FormData): Promise<{
    error: string;
    success?: undefined;
} | {
    success: boolean;
    error?: undefined;
}>;
export declare function getCurrentUser(): Promise<any>;
export declare function requireAuth(): Promise<any>;
export declare function handleOAuthCallback(provider: string, profile: {
    id: string;
    email: string;
    name?: string;
    image?: string;
}, accessToken?: string, refreshToken?: string): Promise<{
    success: boolean;
    error?: undefined;
} | {
    error: string;
    success?: undefined;
}>;
