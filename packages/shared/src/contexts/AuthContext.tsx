'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, type LoginResponse } from '../lib/auth';

type User = {
  id: number;
  email: string;
  username: string;
  full_name: string;
};

type AuthContextType = {
  user: User | null;
  token: string | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ data: LoginResponse | null; error: string | null }>;
  signUp: (email: string, password: string, fullName: string) => Promise<{ data: any; error: any }>;
  signOut: () => Promise<void>;
  signInWithGoogle: () => Promise<{ data: any; error: any }>;
  signInWithGithub: () => Promise<{ data: any; error: any }>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

import type { ReactNode } from 'react';

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check for stored token on initial load
    const storedToken = localStorage.getItem('auth_token');
    if (storedToken) {
      setToken(storedToken);
      // TODO: Validate token with backend
    }
    setLoading(false);
  }, []);

  // Sign in with email and password
  const signIn = async (email: string, password: string) => {
    try {
      const data = await authApi.login(email, password);
      setUser(data.user);
      setToken(data.access_token);
      localStorage.setItem('auth_token', data.access_token);
      router.push('/dashboard');
      return { data, error: null };
    } catch (error) {
      return { data: null, error: error instanceof Error ? error.message : 'Login failed' };
    }
  };

  // Sign up with email and password
  const signUp = async (email: string, password: string, fullName: string) => {
    try {
      const username = email.split('@')[0]; // Simple username from email
      const data = await authApi.signup(email, username, password, fullName);
      router.push('/auth/login?message=Account created successfully');
      return { data, error: null };
    } catch (error) {
      return { data: null, error: error instanceof Error ? error.message : 'Signup failed' };
    }
  };

  // Sign out
  const signOut = async () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    router.push('/auth/login');
  };

  // Sign in with Google (placeholder)
  const signInWithGoogle = async () => {
    return { data: null, error: 'Google OAuth not implemented' };
  };

  // Sign in with GitHub (placeholder)
  const signInWithGithub = async () => {
    return { data: null, error: 'GitHub OAuth not implemented' };
  };

  const value = {
    user,
    token,
    loading,
    signIn,
    signUp,
    signOut,
    signInWithGoogle,
    signInWithGithub,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading ? children : (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading OmniVid...</p>
          </div>
        </div>
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
