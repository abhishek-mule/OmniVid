import { NextResponse } from 'next/server'; 
 import { getSessionFromCookie } from '@/lib/auth/utils'; 
 import { findUserById } from '@/lib/auth/db'; 
 
 export async function GET() { 
   try { 
     const sessionPayload = await getSessionFromCookie(); 
 
     if (!sessionPayload) { 
       return NextResponse.json({ authenticated: false, user: null }); 
     } 
 
     // Verify session exists in database 
     const user = await findUserById(sessionPayload.userId); 
 
     if (!user) { 
       return NextResponse.json({ authenticated: false, user: null }); 
     } 
 
     return NextResponse.json({ 
       authenticated: true, 
       user: { 
         id: user.id, 
         email: user.email, 
         name: user.name, 
         image: user.image, 
         emailVerified: user.emailVerified, 
       }, 
     }); 
   } catch (error) { 
     console.error('Session check error:', error); 
     return NextResponse.json({ authenticated: false, user: null }); 
   } 
 } 
 
 export const dynamic = 'force-dynamic';