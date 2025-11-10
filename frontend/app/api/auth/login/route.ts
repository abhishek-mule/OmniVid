import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password } = body || {};

    if (!email || !password) {
      return NextResponse.json({ message: 'Email and password are required' }, { status: 400 });
    }

    // In a real app, verify email/password against your user store.
    // Here we accept any valid inputs to set a session cookie.
    const token = crypto.randomUUID();

    const res = NextResponse.json({ ok: true, message: 'Logged in', token });
    res.cookies.set('omni_session', token, {
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      path: '/',
      maxAge: 60 * 60 * 24 * 7, // 7 days
    });
    return res;
  } catch (e) {
    return NextResponse.json({ message: 'Invalid request' }, { status: 400 });
  }
}