import { PrismaClient } from '@prisma/client';
declare global {
    var prisma: PrismaClient | undefined;
}
export declare const prisma: PrismaClient<import(".prisma/client").Prisma.PrismaClientOptions, never, import("@prisma/client/runtime/library").DefaultArgs>;
export declare function getUserByEmail(email: string): Promise<{
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
} | null>;
export declare function findUserByEmail(email: string): Promise<({
    accounts: {
        id: string;
        userId: string;
        type: string;
        provider: string;
        providerAccountId: string;
        refresh_token: string | null;
        access_token: string | null;
        expires_at: number | null;
        token_type: string | null;
        scope: string | null;
        id_token: string | null;
        session_state: string | null;
    }[];
} & {
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
}) | null>;
export declare function createUser(data: {
    email: string;
    name: string;
    password: string;
}): Promise<{
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
}>;
export declare function updateUser(id: string, data: {
    email?: string;
    name?: string;
    password?: string;
    emailVerified?: boolean;
}): Promise<{
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
}>;
export declare function createPasswordResetToken(userId: string): Promise<{
    id: string;
    expires: Date;
    createdAt: Date;
    userId: string;
    token: string;
    used: boolean;
}>;
export declare function verifyPasswordResetToken(token: string): Promise<{
    id: string;
    expires: Date;
    createdAt: Date;
    userId: string;
    token: string;
    used: boolean;
} | null>;
export declare function deletePasswordResetToken(token: string): Promise<void>;
export declare function getUserByAccount(provider: string, providerAccountId: string): Promise<{
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
} | null>;
export declare function linkAccount(userId: string, provider: string, providerAccountId: string, accessToken?: string, refreshToken?: string): Promise<void>;
export declare function findUserById(id: string): Promise<({
    accounts: {
        id: string;
        userId: string;
        type: string;
        provider: string;
        providerAccountId: string;
        refresh_token: string | null;
        access_token: string | null;
        expires_at: number | null;
        token_type: string | null;
        scope: string | null;
        id_token: string | null;
        session_state: string | null;
    }[];
} & {
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
}) | null>;
export declare function updateUserPassword(userId: string, password: string): Promise<{
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
}>;
export declare function deleteUserSessions(userId: string): Promise<import(".prisma/client").Prisma.BatchPayload>;
export declare function createSession(data: {
    userId: string;
    sessionToken: string;
    expires: Date;
}): Promise<{
    id: string;
    expires: Date;
    userId: string;
    sessionToken: string;
}>;
export declare function findSessionByToken(sessionToken: string): Promise<({
    user: {
        image: string | null;
        id: string;
        name: string | null;
        email: string;
        password: string | null;
        emailVerified: boolean;
        createdAt: Date;
        updatedAt: Date;
    };
} & {
    id: string;
    expires: Date;
    userId: string;
    sessionToken: string;
}) | null>;
export declare function deleteSession(sessionToken: string): Promise<{
    id: string;
    expires: Date;
    userId: string;
    sessionToken: string;
}>;
export declare function findPasswordResetToken(token: string): Promise<({
    user: {
        image: string | null;
        id: string;
        name: string | null;
        email: string;
        password: string | null;
        emailVerified: boolean;
        createdAt: Date;
        updatedAt: Date;
    };
} & {
    id: string;
    expires: Date;
    createdAt: Date;
    userId: string;
    token: string;
    used: boolean;
}) | null>;
export declare function markTokenAsUsed(tokenId: string): Promise<{
    id: string;
    expires: Date;
    createdAt: Date;
    userId: string;
    token: string;
    used: boolean;
}>;
export declare function findOrCreateOAuthUser(data: {
    email: string;
    name?: string;
    image?: string;
    provider: string;
    providerAccountId: string;
    access_token?: string;
    refresh_token?: string;
}): Promise<{
    image: string | null;
    id: string;
    name: string | null;
    email: string;
    password: string | null;
    emailVerified: boolean;
    createdAt: Date;
    updatedAt: Date;
}>;
