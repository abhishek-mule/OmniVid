import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, password, name } = body || {};

    if (!email || !password) {
      return NextResponse.json({ message: 'Email and password are required' }, { status: 400 });
    }

    // In a real app, create user and optionally send verification email.
    const token = crypto.randomUUID();

    const res = NextResponse.json({ ok: true, message: 'Registered', token });
    res.cookies.set('omni_session', token, {
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      path: '/',
      maxAge: 60 * 60 * 24 * 7,
    });
    return res;
  } catch (e) {
    return NextResponse.json({ message: 'Invalid request' }, { status: 400 });
  }
}