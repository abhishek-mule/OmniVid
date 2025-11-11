import { NextResponse } from 'next/server'; 
 import { 
   hashPassword, 
   isStrongPassword, 
 } from '@/lib/auth/utils'; 
 import { 
   findPasswordResetToken, 
   updateUserPassword, 
   markTokenAsUsed, 
   deleteUserSessions, 
 } from '@/lib/auth/db'; 
 
 export async function POST(request: Request) { 
   try { 
     const body = await request.json(); 
     const { token, password } = body || {}; 
 
     if (!token || !password) { 
       return NextResponse.json( 
         { message: 'Token and password are required' }, 
         { status: 400 } 
       ); 
     } 
 
     const passwordCheck = isStrongPassword(password); 
     if (!passwordCheck.valid) { 
       return NextResponse.json( 
         { message: passwordCheck.message }, 
         { status: 400 } 
       ); 
     } 
 
     // Find and validate token 
     const resetToken = await findPasswordResetToken(token); 
 
     if (!resetToken) { 
       return NextResponse.json( 
         { message: 'Invalid or expired reset token' }, 
         { status: 400 } 
       ); 
     } 
 
     if (resetToken.used) { 
       return NextResponse.json( 
         { message: 'This reset token has already been used' }, 
         { status: 400 } 
       ); 
     } 
 
     if (resetToken.expires < new Date()) { 
       return NextResponse.json( 
         { message: 'Reset token has expired' }, 
         { status: 400 } 
       ); 
     } 
 
     // Hash new password and update user 
     const hashedPassword = await hashPassword(password); 
     await updateUserPassword(resetToken.userId, hashedPassword); 
 
     // Mark token as used 
     await markTokenAsUsed(resetToken.id); 
 
     // Invalidate all existing sessions for security 
     await deleteUserSessions(resetToken.userId); 
 
     return NextResponse.json({ 
       ok: true, 
       message: 'Password updated successfully', 
     }); 
   } catch (error) { 
     console.error('Password reset error:', error); 
     return NextResponse.json( 
       { message: 'An error occurred' }, 
       { status: 500 } 
     ); 
   } 
 }