export const runtime = 'nodejs'
import { NextResponse } from 'next/server'; 
 import { getSessionFromCookie, clearSessionCookie } from '@/lib/auth/utils'; 
 import { deleteSession } from '@/lib/auth/db'; 
 
 export async function POST() { 
   try { 
     const sessionPayload = await getSessionFromCookie(); 
 
     if (sessionPayload?.sessionId) { 
       // Delete session from database 
       try { 
         await deleteSession(sessionPayload.sessionId); 
       } catch (error) { 
         console.error('Failed to delete session:', error); 
       } 
     } 
 
     // Clear cookie 
     await clearSessionCookie(); 
 
     return NextResponse.json({ ok: true, message: 'Logged out successfully' }); 
   } catch (error) { 
     console.error('Logout error:', error); 
     
     // Still clear the cookie even if there's an error 
     await clearSessionCookie(); 
     
     return NextResponse.json({ ok: true, message: 'Logged out' }); 
   } 
 }