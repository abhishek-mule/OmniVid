import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(req: NextRequest) {
  const url = req.nextUrl;
  const origin = url.origin;
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');

  const cookieStore = await cookies();
  const savedState = cookieStore.get('oauth_state_google')?.value;
  const nextParam = cookieStore.get('oauth_next')?.value || '/app/editor';

  if (!code || !state) {
    return NextResponse.redirect(`${origin}/auth/login?error=missing_code_state`);
  }
  if (!savedState || state !== savedState) {
    return NextResponse.redirect(`${origin}/auth/login?error=invalid_state`);
  }

  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const redirectUri = `${origin}/api/auth/callback/google`;

  if (!clientId || !clientSecret) {
    return NextResponse.redirect(`${origin}/auth/login?error=google_oauth_not_configured`);
  }

  try {
    const body = new URLSearchParams({
      code,
      client_id: clientId,
      client_secret: clientSecret!,
      redirect_uri: redirectUri,
      grant_type: 'authorization_code',
    });

    const tokenRes = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    });

    const tokenJson = await tokenRes.json();
    if (!tokenRes.ok) {
      const err = tokenJson?.error || 'token_exchange_failed';
      return NextResponse.redirect(`${origin}/auth/login?error=${encodeURIComponent(err)}`);
    }

    const accessToken: string | undefined = tokenJson.access_token;
    if (!accessToken) {
      return NextResponse.redirect(`${origin}/auth/login?error=missing_access_token`);
    }

    const userRes = await fetch('https://openidconnect.googleapis.com/v1/userinfo', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    const user = await userRes.json();
    if (!userRes.ok) {
      const err = user?.error || 'userinfo_failed';
      return NextResponse.redirect(`${origin}/auth/login?error=${encodeURIComponent(err)}`);
    }

    // Issue app session (simple opaque token). In a real app, you'd create/find the user in DB.
    const sessionToken = `google_${user.sub}_${crypto.randomUUID()}`;

    const res = NextResponse.redirect(`${origin}${nextParam}`);
    res.cookies.set('omni_session', sessionToken, {
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      path: '/',
      maxAge: 60 * 60 * 24 * 7, // 7 days
    });

    // Clear temporary cookies
    res.cookies.set('oauth_state_google', '', { path: '/', maxAge: 0 });
    res.cookies.set('oauth_next', '', { path: '/', maxAge: 0 });

    return res;
  } catch (e) {
    return NextResponse.redirect(`${origin}/auth/login?error=unexpected_oauth_error`);
  }
}