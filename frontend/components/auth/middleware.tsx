import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSupabaseAuth } from './AuthProvider';
import type { User } from '@supabase/supabase-js';

interface AuthGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function AuthGuard({ children, fallback }: AuthGuardProps) {
  const { user, loading } = useSupabaseAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      // Redirect to login if not authenticated
      const currentPath = window.location.pathname;
      router.push(`/auth/login?next=${encodeURIComponent(currentPath)}`);
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return fallback || <div>Redirecting to login...</div>;
  }

  return <>{children}</>;
}
