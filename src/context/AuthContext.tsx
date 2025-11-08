"use client";
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

type AuthContextValue = {
  authenticated: boolean;
  loading: boolean;
  error?: string;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | undefined>(undefined);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(undefined);
    try {
      const res = await fetch('/api/auth/session', { cache: 'no-store' });
      const json = await res.json();
      setAuthenticated(!!json?.authenticated);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Session check failed');
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      setAuthenticated(false);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const value: AuthContextValue = { authenticated, loading, error, refresh, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}