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
       isAuthenticated = false; 
     } 
   } 
   
   // Redirect unauthenticated users from protected paths 
   if (isProtectedPath && !isAuthenticated) { 
     const url = new URL('/auth/login', request.url); 
     url.searchParams.set('next', pathname); 
     return NextResponse.redirect(url); 
   } 
   
   // Redirect authenticated users from auth pages 
   if (isAuthPath && isAuthenticated) { 
     return NextResponse.redirect(new URL('/app/editor', request.url)); 
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
      */ 
     '/((?!api|_next/static|_next/image|favicon.ico).*)', 
   ], 
 };