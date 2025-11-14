import type { User } from '@supabase/supabase-js';
type AuthContextType = {
    user: User | null;
    loading: boolean;
    signIn: (email: string, password: string) => Promise<{
        data: any;
        error: any;
    }>;
    signUp: (email: string, password: string, fullName: string) => Promise<{
        data: any;
        error: any;
    }>;
    signOut: () => Promise<void>;
    signInWithGoogle: () => Promise<{
        data: any;
        error: any;
    }>;
    signInWithGithub: () => Promise<{
        data: any;
        error: any;
    }>;
};
import type { ReactNode } from 'react';
export declare const AuthProvider: ({ children }: {
    children: ReactNode;
}) => import("react").JSX.Element;
export declare const useAuth: () => AuthContextType;
export {};
