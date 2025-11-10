import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET() {
  const cookieStore = await cookies();
  const token = cookieStore.get('omni_session')?.value;
  return NextResponse.json({ authenticated: !!token });
}

export const dynamic = 'force-dynamic';