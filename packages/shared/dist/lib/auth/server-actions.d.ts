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
export declare function getCurrentUser(): Promise<({
    accounts: {
        id: string;
        userId: string;
        type: string;
        provider: string;
        providerAccountId: string;
        refresh_token: string | null;
        access_token: string | null;
        expires_at: number | null;
        token_type: string | null;
        scope: string | null;
        id_token: string | null;
        session_state: string | null;
    }[];
} & {
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
}) | null>;
export declare function requireAuth(): Promise<{
    accounts: {
        id: string;
        userId: string;
        type: string;
        provider: string;
        providerAccountId: string;
        refresh_token: string | null;
        access_token: string | null;
        expires_at: number | null;
        token_type: string | null;
        scope: string | null;
        id_token: string | null;
        session_state: string | null;
    }[];
} & {
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
}>;
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
