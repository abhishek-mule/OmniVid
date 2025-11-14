import 'server-only';
import { z } from 'zod';
export declare function encrypt(payload: any): Promise<any>;
export declare function decrypt(input: string): Promise<any>;
export declare function createSession(userId: string): Promise<void>;
export declare function deleteSession(): void;
export declare function getSession(): Promise<any>;
export declare const loginSchema: z.ZodObject<{
    email: z.ZodString;
    password: z.ZodString;
}, "strip", z.ZodTypeAny, {
    email: string;
    password: string;
}, {
    email: string;
    password: string;
}>;
export declare const registerSchema: z.ZodObject<{
    name: z.ZodString;
    email: z.ZodString;
    password: z.ZodString;
}, "strip", z.ZodTypeAny, {
    name: string;
    email: string;
    password: string;
}, {
    name: string;
    email: string;
    password: string;
}>;
export declare const resetPasswordSchema: z.ZodObject<{
    email: z.ZodString;
}, "strip", z.ZodTypeAny, {
    email: string;
}, {
    email: string;
}>;
export declare const newPasswordSchema: z.ZodEffects<z.ZodObject<{
    password: z.ZodString;
    confirmPassword: z.ZodString;
}, "strip", z.ZodTypeAny, {
    password: string;
    confirmPassword: string;
}, {
    password: string;
    confirmPassword: string;
}>, {
    password: string;
    confirmPassword: string;
}, {
    password: string;
    confirmPassword: string;
}>;
export declare function hashPassword(password: string): Promise<any>;
export declare function verifyPassword(password: string, hashed: string): Promise<any>;
export declare function isValidEmail(email: string): boolean;
export declare function isStrongPassword(password: string): {
    valid: boolean;
    message?: string;
};
export declare function createSessionToken(payload: {
    userId: string;
    email: string;
    sessionId: string;
}): Promise<any>;
export declare function setSessionCookie(token: string): Promise<void>;
export declare function getSessionFromCookie(): Promise<any>;
export declare function clearSessionCookie(): void;
