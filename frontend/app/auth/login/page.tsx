'use client';

import { AuthForm } from '@/components/auth/auth-form';

export default function LoginPage() {
  return (
    <div className="container relative mx-auto flex h-screen max-w-lg flex-col items-center justify-center">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6">
        <div className="flex flex-col space-y-2 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">
            Welcome back
          </h1>
          <p className="text-sm text-muted-foreground">
            Enter your credentials to access your account
          </p>
        </div>
        <AuthForm type="login" />
      </div>
    </div>
  );
}
