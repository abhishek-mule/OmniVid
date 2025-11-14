import React from 'react';
type AuthContextValue = {
    authenticated: boolean;
    loading: boolean;
    error?: string;
    refresh: () => Promise<void>;
    logout: () => Promise<void>;
};
export declare function AuthProvider({ children }: {
    children: React.ReactNode;
}): React.JSX.Element;
export declare function useAuth(): AuthContextValue;
export {};
