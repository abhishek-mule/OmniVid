import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { jwtVerify } from 'jose';

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'your-secret-key-change-in-production'
);

const protectedPaths = ['/app', '/dashboard', '/settings'];
const authPaths = ['/auth/login', '/auth/signup'];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Check if the path should be protected 
  const isProtectedPath = protectedPaths.some((path) => 
    pathname.startsWith(path)
  );
  
  const isAuthPath = authPaths.some((path) => pathname.startsWith(path));
  
  const token = request.cookies.get('omni_session')?.value;
  
  let isAuthenticated = false;
  
  if (token) {
    try {
      await jwtVerify(token, JWT_SECRET);
      isAuthenticated = true;
    } catch {
      // Token is invalid
    }
  }

  // Redirect to login if trying to access protected route without auth
  if (isProtectedPath && !isAuthenticated) {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }

  // Redirect to dashboard if already authenticated and trying to access auth routes
  if (isAuthPath && isAuthenticated) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!api|_next/static|_next/image|favicon.ico|public/).*)',
  ],
};
