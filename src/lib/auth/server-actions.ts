'use server';


import { redirect } from 'next/navigation';
import { compare, hash } from 'bcryptjs';
import { z } from 'zod';
import { getSession, createSession, deleteSession } from './utils';
import * as db from './db';
import { sendPasswordResetEmail } from '../email';

// Login action
export async function login(formData: FormData) {
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  try {
    // Validate input
    const { success } = z.object({
      email: z.string().email(),
      password: z.string().min(6),
    }).safeParse({ email, password });

    if (!success) {
      return { error: 'Invalid input' };
    }

    // Find user
    const user = await db.getUserByEmail(email);
    if (!user || !user.password) {
      return { error: 'Invalid credentials' };
    }

    // Verify password
    const isValid = await compare(password, user.password);
    if (!isValid) {
      return { error: 'Invalid credentials' };
    }

    // Create session
    await createSession(user.id);

    return { success: true };
  } catch (error) {
    console.error('Login error:', error);
    return { error: 'An error occurred during login' };
  }
}

// Register action
export async function register(formData: FormData) {
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;
  const password = formData.get('password') as string;

  try {
    // Validate input
    const { success } = z.object({
      name: z.string().min(2),
      email: z.string().email(),
      password: z.string().min(6),
    }).safeParse({ name, email, password });

    if (!success) {
      return { error: 'Invalid input' };
    }

    // Check if user already exists
    const existingUser = await db.getUserByEmail(email);
    if (existingUser) {
      return { error: 'User already exists' };
    }

    // Hash password
    const hashedPassword = await hash(password, 12);

    // Create user
    const user = await db.createUser({
      name,
      email,
      password: hashedPassword,
    });

    // Create session
    await createSession(user.id);

    return { success: true };
  } catch (error) {
    console.error('Registration error:', error);
    return { error: 'An error occurred during registration' };
  }
}

// Logout action
export async function logout() {
  deleteSession();
  redirect('/auth/login');
}

// Request password reset
export async function requestPasswordReset(formData: FormData) {
  const email = formData.get('email') as string;

  try {
    const user = await db.getUserByEmail(email);
    if (!user) {
      // Don't reveal if the user exists or not
      return { success: true };
    }

    // Create reset token for user
    const created = await db.createPasswordResetToken(user.id);
    const token = created.token;

    // Send email with reset link
    const resetUrl = `${process.env.NEXT_PUBLIC_APP_URL}/auth/reset-password?token=${token}`;
    await sendPasswordResetEmail({
      to: email,
      name: user.name || 'User',
      resetUrl,
    });

    return { success: true };
  } catch (error) {
    console.error('Password reset request error:', error);
    return { error: 'An error occurred while processing your request' };
  }
}

// Reset password
export async function resetPassword(formData: FormData) {
  const token = formData.get('token') as string;
  const password = formData.get('password') as string;
  const confirmPassword = formData.get('confirmPassword') as string;

  try {
    // Validate input
    if (password !== confirmPassword) {
      return { error: 'Passwords do not match' };
    }

    // Verify token
    const resetToken = await db.verifyPasswordResetToken(token);
    if (!resetToken) {
      return { error: 'Invalid or expired token' };
    }

    // Find user
    const user = await db.findUserById(resetToken.userId);
    if (!user) {
      return { error: 'User not found' };
    }

    // Update password
    const hashedPassword = await hash(password, 12);
    await db.updateUserPassword(user.id, hashedPassword);

    // Delete used token
    await db.deletePasswordResetToken(token);

    // Log the user in
    await createSession(user.id);

    return { success: true };
  } catch (error) {
    console.error('Password reset error:', error);
    return { error: 'An error occurred while resetting your password' };
  }
}

// Get current user
export async function getCurrentUser() {
  const session = await getSession();
  if (!session) return null;

  return await db.findUserById(session.userId);
}

// Require authentication
export async function requireAuth() {
  const user = await getCurrentUser();
  if (!user) {
    redirect('/auth/login');
  }
  return user;
}

// OAuth callback
export async function handleOAuthCallback(
  provider: string,
  profile: {
    id: string;
    email: string;
    name?: string;
    image?: string;
  },
  accessToken?: string,
  refreshToken?: string
) {
  try {
    const user = await db.findOrCreateOAuthUser({
      email: profile.email,
      name: profile.name || profile.email.split('@')[0],
      image: profile.image,
      provider,
      providerAccountId: profile.id,
      access_token: accessToken,
      refresh_token: refreshToken,
    });

    // Create session
    await createSession(user.id);

    return { success: true };
  } catch (error) {
    console.error('OAuth callback error:', error);
    return { error: 'An error occurred during authentication' };
  }
}
