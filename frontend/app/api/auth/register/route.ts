import { NextResponse } from 'next/server'; 
 import { 
   hashPassword, 
   createSessionToken, 
   setSessionCookie, 
   isValidEmail, 
   isStrongPassword, 
 } from '@/lib/auth/utils'; 
 import { createUser, findUserByEmail, createSession } from '@/lib/auth/db'; 
 
 export async function POST(request: Request) { 
   try { 
     const body = await request.json(); 
     const { email, password, name } = body || {}; 
 
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
 
     const passwordCheck = isStrongPassword(password); 
     if (!passwordCheck.valid) { 
       return NextResponse.json( 
         { message: passwordCheck.message }, 
         { status: 400 } 
       ); 
     } 
 
     const existingUser = await findUserByEmail(email); 
     if (existingUser) { 
       return NextResponse.json( 
         { message: 'Email already registered' }, 
         { status: 409 } 
       ); 
     } 
 
     const hashedPassword = await hashPassword(password); 
 
     const user = await createUser({ 
       email, 
       password: hashedPassword, 
       name, 
     }); 
 
     // Create session 
     const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); 
     const sessionToken = crypto.randomUUID(); 
 
     const session = await createSession({ 
       userId: user.id, 
       sessionToken, 
       expires, 
     }); 
 
     const token = await createSessionToken({ 
       userId: user.id, 
       email: user.email, 
       sessionId: session.id, 
     }); 
 
     await setSessionCookie(token); 
 
     // TODO: Send verification email here 
     // await sendVerificationEmail(user.email, verificationToken); 
 
     return NextResponse.json({ 
       ok: true, 
       message: 'Account created successfully', 
       user: { 
         id: user.id, 
         email: user.email, 
         name: user.name, 
       }, 
     }); 
   } catch (error) { 
     console.error('Registration error:', error); 
     return NextResponse.json( 
       { message: 'An error occurred during registration' }, 
       { status: 500 } 
     ); 
   } 
 }