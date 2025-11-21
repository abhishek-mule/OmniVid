import type { Database } from '../types/index';
export declare const createClient: (supabaseUrl?: string, supabaseAnonKey?: string) => import("@supabase/supabase-js").SupabaseClient<Database, "public", "public", never, {
    PostgrestVersion: "12";
}>;
export declare const createServerClient: () => import("@supabase/supabase-js").SupabaseClient<Database, "public", "public", never, {
    PostgrestVersion: "12";
}>;
export type { Database };
export type { User as SupabaseUser, Session as SupabaseSession } from '@supabase/supabase-js';
