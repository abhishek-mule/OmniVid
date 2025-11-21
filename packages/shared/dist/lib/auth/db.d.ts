import { PrismaClient } from '@prisma/client';
declare global {
    var prisma: PrismaClient | undefined;
}
export declare const prisma: any;
export declare function getUserByEmail(email: string): Promise<any>;
export declare function findUserByEmail(email: string): Promise<any>;
export declare function createUser(data: {
    email: string;
    name: string;
    password: string;
}): Promise<any>;
export declare function updateUser(id: string, data: {
    email?: string;
    name?: string;
    password?: string;
    emailVerified?: boolean;
}): Promise<any>;
export declare function createPasswordResetToken(userId: string): Promise<any>;
export declare function verifyPasswordResetToken(token: string): Promise<any>;
export declare function deletePasswordResetToken(token: string): Promise<void>;
export declare function getUserByAccount(provider: string, providerAccountId: string): Promise<any>;
export declare function linkAccount(userId: string, provider: string, providerAccountId: string, accessToken?: string, refreshToken?: string): Promise<void>;
export declare function findUserById(id: string): Promise<any>;
export declare function updateUserPassword(userId: string, password: string): Promise<any>;
export declare function deleteUserSessions(userId: string): Promise<any>;
export declare function createSession(data: {
    userId: string;
    sessionToken: string;
    expires: Date;
}): Promise<any>;
export declare function findSessionByToken(sessionToken: string): Promise<any>;
export declare function deleteSession(sessionToken: string): Promise<any>;
export declare function findPasswordResetToken(token: string): Promise<any>;
export declare function markTokenAsUsed(tokenId: string): Promise<any>;
export declare function findOrCreateOAuthUser(data: {
    email: string;
    name?: string;
    image?: string;
    provider: string;
    providerAccountId: string;
    access_token?: string;
    refresh_token?: string;
}): Promise<any>;
