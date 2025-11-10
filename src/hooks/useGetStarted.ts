"use client";
import { useRouter } from 'next/navigation';

export function useGetStarted() {
  const router = useRouter();

  const start = async (next: string = '/app/editor') => {
    try {
      const res = await fetch('/api/auth/session', { cache: 'no-store' });
      const json = await res.json();
      if (json?.authenticated) {
        router.push('/app/editor');
      } else {
        router.push(`/auth/login?next=${encodeURIComponent(next)}`);
      }
    } catch {
      router.push(`/auth/login?next=${encodeURIComponent(next)}`);
    }
  };

  return { start };
}