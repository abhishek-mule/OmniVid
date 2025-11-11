export const runtime = 'nodejs'
import { NextRequest, NextResponse } from 'next/server'; 
 import { cookies } from 'next/headers'; 
 import {  
  createSessionToken  
} from '@/lib/auth/utils'; 
 import {  
   findOrCreateOAuthUser,  
   createSession  
 } from '@/lib/auth/db'; 
  
 interface GoogleUserInfo { 
   sub: string; 
   email: string; 
   email_verified: boolean; 
   name?: string; 
   picture?: string; 
   given_name?: string; 
   family_name?: string; 
 } 
  
 interface GoogleTokenResponse { 
   access_token: string; 
   expires_in: number; 
   refresh_token?: string; 
   scope: string; 
   token_type: string; 
   id_token?: string; 
 } 
  
 export async function GET(req: NextRequest) { 
   const url = req.nextUrl; 
   const origin = url.origin; 
   const code = url.searchParams.get('code'); 
   const state = url.searchParams.get('state'); 
   const error = url.searchParams.get('error'); 
  
   const cookieStore = await cookies(); 
   const savedState = cookieStore.get('oauth_state_google')?.value; 
   const nextParam = cookieStore.get('oauth_next')?.value || '/app/editor'; 
  
   // Handle OAuth errors 
   if (error) { 
     console.error('Google OAuth error:', error); 
     return NextResponse.redirect( 
       `${origin}/auth/login?error=${encodeURIComponent(error)}` 
     ); 
   } 
  
   // Validate required parameters 
   if (!code || !state) { 
     return NextResponse.redirect( 
       `${origin}/auth/login?error=missing_code_state` 
     ); 
   } 
  
   // Verify state for CSRF protection 
   if (!savedState || state !== savedState) { 
     return NextResponse.redirect( 
       `${origin}/auth/login?error=invalid_state` 
     ); 
   } 
  
   const clientId = process.env.GOOGLE_CLIENT_ID; 
   const clientSecret = process.env.GOOGLE_CLIENT_SECRET; 
   const redirectUri = `${origin}/api/auth/callback/google`; 
  
   if (!clientId || !clientSecret) { 
     console.error('Google OAuth not configured'); 
     return NextResponse.redirect( 
       `${origin}/auth/login?error=oauth_not_configured` 
     ); 
   } 
  
   try { 
     // Exchange authorization code for tokens 
     const tokenBody = new URLSearchParams({ 
       code, 
       client_id: clientId, 
       client_secret: clientSecret, 
       redirect_uri: redirectUri, 
       grant_type: 'authorization_code', 
     }); 
  
     const tokenRes = await fetch('https://oauth2.googleapis.com/token', { 
       method: 'POST', 
       headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, 
       body: tokenBody, 
     }); 
  
     if (!tokenRes.ok) { 
       const errorData = await tokenRes.json(); 
       console.error('Token exchange failed:', errorData); 
       return NextResponse.redirect( 
         `${origin}/auth/login?error=token_exchange_failed` 
       ); 
     } 
  
     const tokenData: GoogleTokenResponse = await tokenRes.json(); 
  
     if (!tokenData.access_token) { 
       return NextResponse.redirect( 
         `${origin}/auth/login?error=missing_access_token` 
       ); 
     } 
  
     // Fetch user information 
     const userRes = await fetch( 
       'https://www.googleapis.com/oauth2/v2/userinfo', 
       { 
         headers: { Authorization: `Bearer ${tokenData.access_token}` }, 
       } 
     ); 
  
     if (!userRes.ok) { 
       const errorData = await userRes.json(); 
       console.error('User info fetch failed:', errorData); 
       return NextResponse.redirect( 
         `${origin}/auth/login?error=userinfo_failed` 
       ); 
     } 
  
     const googleUser: GoogleUserInfo = await userRes.json(); 
  
     if (!googleUser.email) { 
       return NextResponse.redirect( 
         `${origin}/auth/login?error=missing_email` 
       ); 
     } 
  
     // Find or create user in database 
     const user = await findOrCreateOAuthUser({ 
       email: googleUser.email, 
       name: googleUser.name || googleUser.given_name, 
       image: googleUser.picture, 
       provider: 'google', 
       providerAccountId: googleUser.sub, 
       access_token: tokenData.access_token, 
       refresh_token: tokenData.refresh_token, 
     }); 
  
     // Create session in database 
     const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); 
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
  
     // Set session cookie 
     const res = NextResponse.redirect(`${origin}${nextParam}`); 
      
     res.cookies.set('omni_session', token, { 
       httpOnly: true, 
       sameSite: 'lax', 
       secure: process.env.NODE_ENV === 'production', 
       path: '/', 
       maxAge: 60 * 60 * 24 * 7, // 7 days 
     }); 
  
     // Clear temporary OAuth cookies 
     res.cookies.set('oauth_state_google', '', { path: '/', maxAge: 0 }); 
     res.cookies.set('oauth_next', '', { path: '/', maxAge: 0 }); 
  
     return res; 
   } catch (error) { 
     console.error('OAuth callback error:', error); 
     return NextResponse.redirect( 
       `${origin}/auth/login?error=oauth_error` 
     ); 
   } 
 }