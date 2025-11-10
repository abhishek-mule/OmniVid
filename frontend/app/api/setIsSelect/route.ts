import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

export async function GET() {
  return NextResponse.json({ success: true });
}

export async function POST(req: Request) {
  try {
    const contentType = req.headers.get('content-type') || '';
    let payload: any = {};

    if (contentType.includes('application/json')) {
      payload = await req.json();
    } else if (contentType.includes('application/x-www-form-urlencoded')) {
      const formData = await req.formData();
      payload = Object.fromEntries(formData.entries());
    } else if (contentType.includes('multipart/form-data')) {
      const formData = await req.formData();
      payload = Object.fromEntries(formData.entries());
    } else {
      // Best-effort parse
      try {
        payload = await req.json();
      } catch {
        payload = {};
      }
    }

    return NextResponse.json({ success: true, received: payload });
  } catch (e) {
    return NextResponse.json({ success: true });
  }
}

export async function OPTIONS() {
  return new Response(null, {
    status: 204,
    headers: {
      'Allow': 'GET,POST,OPTIONS',
    },
  });
}