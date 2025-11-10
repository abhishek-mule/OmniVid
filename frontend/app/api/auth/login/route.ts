export const runtime = 'nodejs'
import { NextResponse } from 'next/server'; 
 import { 
   verifyPassword, 
   createSessionToken, 
   setSessionCookie, 
   isValidEmail 
 } from '@/lib/auth/utils'; 
 import { 
   findUserByEmail, 
   createSession 
 } from '@/lib/auth/db'; 
 
 export async function POST(request: Request) { 
   try { 
     const body = await request.json(); 
     const { email, password } = body || {}; 
 
     if (!email || !password) { 
       return NextResponse.json( 
         { message: 'Email and password are required' }, 
         { status: 400 } 
       ); 
     } 
 
     if (!isValidEmail(email)) { 
       return NextResponse.json( 
         { message: 'Invalid email address' }, 
         { status: 400 } 
       ); 
     } 
 
     const user = await findUserByEmail(email); 
 
     if (!user || !user.password) { 
       return NextResponse.json( 
         { message: 'Invalid email or password' }, 
         { status: 401 } 
       ); 
     } 
 
     const isValidPassword = await verifyPassword(password, user.password); 
 
     if (!isValidPassword) { 
       return NextResponse.json( 
         { message: 'Invalid email or password' }, 
         { status: 401 } 
       ); 
     } 
 
     // Create session in database 
     const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days 
     const sessionToken = crypto.randomUUID(); 
     
     const session = await createSession({ 
       userId: user.id, 
       sessionToken, 
       expires, 
     }); 
 
     // Create JWT token 
     const token = await createSessionToken({ 
       userId: user.id, 
       email: user.email, 
       sessionId: session.id, 
     }); 
 
     // Set cookie 
     await setSessionCookie(token); 
 
     return NextResponse.json({ 
       ok: true, 
       message: 'Logged in successfully', 
       user: { 
         id: user.id, 
         email: user.email, 
         name: user.name, 
         image: user.image, 
       }, 
     }); 
   } catch (error) { 
     console.error('Login error:', error); 
     return NextResponse.json( 
       { message: 'An error occurred during login' }, 
       { status: 500 } 
     ); 
   } 
 }