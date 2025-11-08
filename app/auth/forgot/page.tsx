"use client";
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Link from 'next/link';
import { Icons } from '@/components/icons';
import { buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const schema = z.object({
  email: z.string().email({ message: 'Please enter a valid email address' }),
});

type FormData = z.infer<typeof schema>;

export default function ForgotPage() {
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/auth/request-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.message || 'Something went wrong');
      alert('If an account exists, a reset link has been sent.');
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container flex h-screen w-screen flex-col items-center justify-center">
      <Link
        href="/"
        className={cn(
          buttonVariants({ variant: 'ghost' }),
          'absolute left-4 top-4 md:left-8 md:top-8'
        )}
      >
        <Icons.chevronLeft className="mr-2 h-4 w-4" />
        Back
      </Link>
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
        <div className="flex flex-col space-y-2 text-center">
          <Icons.logo className="mx-auto h-6 w-6" />
          <h1 className="text-2xl font-semibold tracking-tight">Forgot password</h1>
          <p className="text-sm text-muted-foreground">Enter your email to receive a reset link</p>
        </div>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="grid gap-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" disabled={isLoading} {...register('email')} />
            {errors?.email && <p className="px-1 text-xs text-red-600">{errors.email.message}</p>}
            <Button type="submit" disabled={isLoading} className="mt-4">{isLoading ? 'Sending…' : 'Send reset link'}</Button>
          </div>
        </form>
        <p className="px-8 text-center text-sm text-muted-foreground">
          Remembered? <Link href="/auth/login" className="hover:text-brand underline underline-offset-4">Log in</Link>
        </p>
      </div>
    </div>
  );
}