import { NextResponse } from 'next/server';
import { login } from '@omnivid/shared/lib/auth';
// import { cookies } from 'next/headers'; // We will use the Response.cookies API instead of this direct import

// Define the expected structure for the login result
interface LoginResult {
  success?: boolean;
  error?: string;
  user?: { email: string };
  message?: string;
}

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    // --- 1. Basic Input Validation ---
    if (!email || !password) {
      return NextResponse.json(
        { error: 'Email and password are required.' },
        { status: 400 }
      );
    }
    
    // Create form data for the login function
    const authFormData = new FormData();
    authFormData.append('email', email);
    authFormData.append('password', password);
    
    // --- 2. Call the Login Function ---
    // Assuming the login function performs authentication AND generates a session token/ID
    const result: LoginResult = await login(authFormData);

    // --- 3. Handle Login Errors ---
    if (!result.success || result.error) {
      return NextResponse.json(
        { error: result.error || 'Invalid credentials.' },
        { status: 401 }
      );
    }

    // --- 4. Secure Session Cookie Setup ---
    const responseBody = {
      success: true, 
      message: result.message || 'Login successful',
      user: result.user || { email }
    };

    return NextResponse.json(responseBody, { status: 200 });
    
  } catch (error) {
    console.error('API Route Error [POST /api/auth/login]:', error); 
    
    return NextResponse.json(
      { error: 'A server error occurred during authentication.' },
      { status: 500 }
    );
  }
}

// * NOTE: Removed unused 'cookies' import from 'next/headers' 
// to keep the code clean, as response.cookies.set is used instead.