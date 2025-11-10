'use client';

import { Suspense } from 'react';
import { AuthForm } from './auth-form';
import { useSearchParams } from 'next/navigation';

export function AuthFormWrapper() {
  const searchParams = useSearchParams();
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <AuthForm type="login" searchParams={searchParams} />
    </Suspense>
  );
}