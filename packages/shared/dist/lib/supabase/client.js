"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSupabaseClient = void 0;
var supabase_js_1 = require("@supabase/supabase-js");
var supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
var supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';
if (!supabaseUrl || !supabaseAnonKey) {
    console.error('Missing Supabase environment variables');
}
var getSupabaseClient = function () {
    return (0, supabase_js_1.createClient)(supabaseUrl, supabaseAnonKey, {
        auth: {
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: true,
        },
    });
};
exports.getSupabaseClient = getSupabaseClient;
//# sourceMappingURL=client.js.map