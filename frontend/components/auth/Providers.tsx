// Auth provider wrapper for Next.js
"use client";

import { AuthProvider } from '@omnivid/shared/contexts';

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}