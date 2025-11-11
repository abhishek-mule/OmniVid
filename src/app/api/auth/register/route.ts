import { NextResponse } from 'next/server';
import { register } from '@/lib/auth/server-actions';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const result = await register(formData);

    if (result.error) {
      return NextResponse.json(
        { error: result.error },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { success: true },
      { status: 201, headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Registration route error:', error);
    return NextResponse.json(
      { error: 'An error occurred during registration' },
      { status: 500 }
    );
  }
}
