'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Icons } from '@/components/icons';
import { cn } from '@/lib/utils';
import { toast } from '@/hooks/use-toast';
import Link from 'next/link';
// import { useAuth } from '@omnivid/shared/context';

const userAuthSchema = z.object({
  email: z.string().email({ message: 'Please enter a valid email address' }),
  password: z
    .string()
    .min(8, { message: 'Password must be at least 8 characters' })
    .max(100, { message: 'Password must not exceed 100 characters' }),
  name: z.string().optional(),
});

type FormData = z.infer<typeof userAuthSchema>;

interface AuthFormProps extends React.HTMLAttributes<HTMLDivElement> {
  type: 'login' | 'register';
  searchParams?: ReturnType<typeof useSearchParams>;
}

export function AuthForm({ className, type, searchParams, ...props }: AuthFormProps) {
  const router = useRouter();
  // const { refresh } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [isGitHubLoading, setIsGitHubLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(userAuthSchema),
  });

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);

    try {
      const url = type === 'login' ? '/api/auth/login' : '/api/auth/register';
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.message || 'Something went wrong');
      }

      toast({
        title: type === 'login' ? 'Welcome back!' : 'Account created!',
        description: `You have successfully ${type === 'login' ? 'signed in' : 'signed up'}.`,
      });

      const nextParam = searchParams?.get('next') || '/app/editor';
      // try { await refresh(); } catch {}
      router.push(nextParam);
      router.refresh();
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Something went wrong',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOAuthLogin = async (provider: 'github' | 'google') => {
    if (provider === 'github') {
      setIsGitHubLoading(true);
    } else {
      setIsGoogleLoading(true);
    }

    try {
      const nextParam = searchParams?.get('next');
      const target = nextParam
        ? `/api/auth/${provider}?next=${encodeURIComponent(nextParam)}`
        : `/api/auth/${provider}`;
      window.location.href = target;
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to sign in with ' + provider,
        variant: 'destructive',
      });
    } finally {
      if (provider === 'github') {
        setIsGitHubLoading(false);
      } else {
        setIsGoogleLoading(false);
      }
    }
  };

  return (
    <div className={cn('grid gap-6', className)} {...props}>
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="grid gap-4">
          {type === 'register' && (
            <div className="grid gap-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                placeholder="John Doe"
                type="text"
                autoCapitalize="words"
                autoComplete="name"
                autoCorrect="off"
                disabled={isLoading}
                {...register('name')}
              />
              {errors?.name && (
                <p className="px-1 text-xs text-red-600">
                  {errors.name.message}
                </p>
              )}
            </div>
          )}
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              placeholder="name@example.com"
              type="email"
              autoCapitalize="none"
              autoComplete="email"
              autoCorrect="off"
              disabled={isLoading}
              {...register('email')}
            />
            {errors?.email && (
              <p className="px-1 text-xs text-red-600">
                {errors.email.message}
              </p>
            )}
          </div>
          <div className="grid gap-2">
            <div className="flex items-center">
              <Label htmlFor="password">Password</Label>
              {type === 'login' && (
                <Link
                  href="/auth/forgot"
                  className="ml-auto inline-block text-sm underline"
                >
                  Forgot password?
                </Link>
              )}
            </div>
            <Input
              id="password"
              placeholder={type === 'login' ? '••••••••' : 'At least 8 characters'}
              type="password"
              autoComplete={type === 'login' ? 'current-password' : 'new-password'}
              disabled={isLoading}
              {...register('password')}
            />
            {errors?.password && (
              <p className="px-1 text-xs text-red-600">
                {errors.password.message}
              </p>
            )}
          </div>
          <motion.button
            type="submit"
            className={cn(
              'inline-flex w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
              'disabled:pointer-events-none disabled:opacity-50',
              'h-10',
              'relative overflow-hidden',
              'group',
            )}
            disabled={isLoading}
            whileTap={{ scale: 0.98 }}
          >
            <span className="relative z-10 flex items-center">
              {isLoading && (
                <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
              )}
              {type === 'login' ? 'Sign in' : 'Create account'}
            </span>
            <motion.span
              className="absolute inset-0 bg-white/20"
              initial={{ width: 0 }}
              whileHover={{ width: '100%' }}
              transition={{ duration: 0.3 }}
            />
          </motion.button>
        </div>
      </form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <Button
          variant="outline"
          type="button"
          disabled={isLoading || isGitHubLoading}
          onClick={() => handleOAuthLogin('github')}
          className="flex items-center justify-center gap-2"
        >
          {isGitHubLoading ? (
            <Icons.spinner className="h-4 w-4 animate-spin" />
          ) : (
            <Icons.github className="h-4 w-4" />
          )}
          GitHub
        </Button>
        <Button
          variant="outline"
          type="button"
          disabled={isLoading || isGoogleLoading}
          onClick={() => handleOAuthLogin('google')}
          className="flex items-center justify-center gap-2"
        >
          {isGoogleLoading ? (
            <Icons.spinner className="h-4 w-4 animate-spin" />
          ) : (
            <Icons.google className="h-4 w-4" />
          )}
          Google
        </Button>
      </div>

      <p className="px-8 text-center text-sm text-muted-foreground">
        {type === 'login' ? (
          <>
            Don&apos;t have an account?{' '}
            <Link
              href="/auth/signup"
              className="hover:text-primary underline underline-offset-4"
            >
              Sign up
            </Link>
          </>
        ) : (
          <>
            Already have an account?{' '}
            <Link
              href="/auth/login"
              className="hover:text-primary underline underline-offset-4"
            >
              Sign in
            </Link>
          </>
        )}
      </p>
    </div>
  );
}