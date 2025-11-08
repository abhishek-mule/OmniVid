import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;
  const token = req.cookies.get('omni_session')?.value;

  // Protect /app/editor (and future /app/* if needed)
  if (pathname.startsWith('/app/editor')) {
    if (!token) {
      const loginUrl = req.nextUrl.clone();
      loginUrl.pathname = '/auth/login';
      loginUrl.search = `?next=${encodeURIComponent(pathname + (search || ''))}`;
      return NextResponse.redirect(loginUrl);
    }
    return NextResponse.next();
  }

  // If authenticated, redirect away from auth pages to next or /app/editor
  if (pathname.startsWith('/auth/login') || pathname.startsWith('/auth/signup')) {
    if (token) {
      const nextParam = req.nextUrl.searchParams.get('next');
      const dest = nextParam || '/app/editor';
      const url = req.nextUrl.clone();
      url.pathname = dest;
      url.search = '';
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/app/:path*',
    '/auth/:path*',
  ],
};