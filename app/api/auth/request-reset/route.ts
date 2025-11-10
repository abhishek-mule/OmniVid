export const runtime = 'nodejs'
import { NextResponse } from 'next/server'; 
 import { isValidEmail } from '@/lib/auth/utils'; 
 import { 
   findUserByEmail, 
   createPasswordResetToken, 
 } from '@/lib/auth/db'; 
 import { sendPasswordResetEmail } from '@/lib/email'; 
 
 export async function POST(request: Request) { 
   try { 
     const body = await request.json(); 
     const { email } = body || {}; 
 
     if (!email) { 
       return NextResponse.json( 
         { message: 'Email is required' }, 
         { status: 400 } 
       ); 
     } 
 
     if (!isValidEmail(email)) { 
       return NextResponse.json( 
         { message: 'Invalid email address' }, 
         { status: 400 } 
       ); 
     } 
 
     // Always return success to prevent email enumeration 
     const successResponse = NextResponse.json({
       ok: true, 
       message: 'If an account exists, a password reset email has been sent', 
     }); 
 
     const user = await findUserByEmail(email); 
 
     // If user doesn't exist or has no password (OAuth only), silently succeed 
     if (!user || !user.password) { 
       return successResponse; 
     } 
 
     // Create password reset token 
     const resetToken = await createPasswordResetToken(user.id); 
 
     // Send reset email 
     const resetUrl = `${process.env.NEXT_PUBLIC_APP_URL}/auth/reset?token=${resetToken.token}`; 
     
     try { 
       await sendPasswordResetEmail({ 
         to: user.email, 
         name: user.name || 'User', 
         resetUrl, 
       }); 
     } catch (emailError) { 
       console.error('Failed to send password reset email:', emailError); 
       // Still return success to user 
     } 
 
     return successResponse; 
   } catch (error) { 
     console.error('Password reset request error:', error); 
     return NextResponse.json( 
       { message: 'An error occurred' }, 
       { status: 500 } 
     ); 
   } 
 }