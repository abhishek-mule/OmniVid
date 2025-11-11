import { createBrowserClient } from '@supabase/ssr';

export const createClient = () => {
  // Never create a real client on the server during prerender
  if (typeof window === 'undefined') {
    const noop = async () => ({ data: null, error: new Error('Supabase not available on server') });
    return {
      auth: {
        onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }),
        getSession: noop,
        signInWithPassword: noop,
        signUp: noop,
        signOut: async () => {},
        signInWithOAuth: noop,
        getUser: noop,
      },
    } as any;
  }

  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  // Guard missing or invalid env values
  const isValidUrl = !!url && /^(https?:)\/\//.test(url);
  if (!isValidUrl || !key) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('Supabase env missing or invalid; returning no-op client');
    }
    const noop = async () => ({ data: null, error: new Error('Supabase not configured') });
    return {
      auth: {
        onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }),
        getSession: noop,
        signInWithPassword: noop,
        signUp: noop,
        signOut: async () => {},
        signInWithOAuth: noop,
        getUser: noop,
      },
    } as any;
  }

  return createBrowserClient(url!, key!, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true,
    },
  });
};
