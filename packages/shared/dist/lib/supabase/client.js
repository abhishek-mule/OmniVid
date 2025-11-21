"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createServerClient = exports.createClient = void 0;
var supabase_js_1 = require("@supabase/supabase-js");
var createClient = function (supabaseUrl, supabaseAnonKey) {
    var url = supabaseUrl || process.env.NEXT_PUBLIC_SUPABASE_URL;
    var key = supabaseAnonKey || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if (!url || !key) {
        throw new Error('Missing Supabase environment variables');
    }
    return (0, supabase_js_1.createClient)(url, key, {
        auth: {
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: true,
            flowType: 'pkce',
        },
    });
};
exports.createClient = createClient;
// For server-side use
var createServerClient = function () {
    var supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    var supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
    if (!supabaseUrl || !supabaseAnonKey) {
        throw new Error('Missing Supabase environment variables');
    }
    return (0, supabase_js_1.createClient)(supabaseUrl, supabaseAnonKey, {
        auth: {
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: true,
            flowType: 'pkce',
        },
    });
};
exports.createServerClient = createServerClient;
//# sourceMappingURL=client.js.map