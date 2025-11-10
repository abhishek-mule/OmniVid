import { PrismaClient } from '@prisma/client';

declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined;
}

export const prisma = global.prisma || new PrismaClient();

if (process.env.NODE_ENV !== 'production') {
  global.prisma = prisma;
}

// Helper function to get user by email
export async function getUserByEmail(email: string) {
  return prisma.user.findUnique({
    where: { email },
  });
}

// Alias to match API imports
export async function findUserByEmail(email: string) {
  return prisma.user.findUnique({
    where: { email },
    include: { accounts: true },
  });
}

// Helper function to create a new user
export async function createUser(data: {
  email: string;
  name: string;
  password: string;
}) {
  return prisma.user.create({
    data,
  });
}

// Helper function to update user
export async function updateUser(
  id: string,
  data: {
    email?: string;
    name?: string;
    password?: string;
    emailVerified?: boolean;
  }
) {
  return prisma.user.update({
    where: { id },
    data,
  });
}

// Helper function to create password reset token
export async function createPasswordResetToken(userId: string) {
  const token = crypto.randomUUID();
  const expires = new Date(Date.now() + 60 * 60 * 1000); // 1 hour

  const created = await prisma.passwordResetToken.create({
    data: { userId, token, expires, used: false },
  });

  return created;
}

// Helper function to verify password reset token
export async function verifyPasswordResetToken(token: string) {
  const resetToken = await prisma.passwordResetToken.findUnique({
    where: { token },
  });

  if (!resetToken) return null;
  if (new Date() > resetToken.expires) return null;

  return resetToken;
}

// Helper function to delete password reset token
export async function deletePasswordResetToken(token: string) {
  await prisma.passwordResetToken.delete({
    where: { token },
  });
}

// Helper function to get user by account
export async function getUserByAccount(provider: string, providerAccountId: string) {
  const account = await prisma.account.findUnique({
    where: {
      provider_providerAccountId: {
        provider,
        providerAccountId,
      },
    },
    select: { user: true },
  });
  return account?.user ?? null;
}

// Helper function to link account to user
export async function linkAccount(
  userId: string,
  provider: string,
  providerAccountId: string,
  accessToken?: string,
  refreshToken?: string
) {
  await prisma.account.upsert({
    where: {
      provider_providerAccountId: {
        provider,
        providerAccountId,
      },
    },
    update: {
      access_token: accessToken,
      refresh_token: refreshToken,
    },
    create: {
      userId,
      type: 'oauth',
      provider,
      providerAccountId,
      access_token: accessToken,
      refresh_token: refreshToken,
    },
  });
}

// Added exports to support API routes
export async function findUserById(id: string) {
  return prisma.user.findUnique({
    where: { id },
    include: { accounts: true },
  });
}

export async function updateUserPassword(userId: string, password: string) {
  return prisma.user.update({
    where: { id: userId },
    data: { password },
  });
}

export async function deleteUserSessions(userId: string) {
  return prisma.session.deleteMany({
    where: { userId },
  });
}

export async function createSession(data: {
  userId: string;
  sessionToken: string;
  expires: Date;
}) {
  return prisma.session.create({
    data,
  });
}

export async function findSessionByToken(sessionToken: string) {
  return prisma.session.findUnique({
    where: { sessionToken },
    include: { user: true },
  });
}

export async function deleteSession(sessionToken: string) {
  return prisma.session.delete({
    where: { sessionToken },
  });
}

export async function findPasswordResetToken(token: string) {
  return prisma.passwordResetToken.findUnique({
    where: { token },
    include: { user: true },
  });
}

export async function markTokenAsUsed(tokenId: string) {
  return prisma.passwordResetToken.update({
    where: { id: tokenId },
    data: { used: true },
  });
}

export async function findOrCreateOAuthUser(data: {
  email: string;
  name?: string;
  image?: string;
  provider: string;
  providerAccountId: string;
  access_token?: string;
  refresh_token?: string;
}) {
  const existingAccount = await prisma.account.findUnique({
    where: {
      provider_providerAccountId: {
        provider: data.provider,
        providerAccountId: data.providerAccountId,
      },
    },
    include: { user: true },
  });

  if (existingAccount) {
    return existingAccount.user;
  }

  const existingUser = await getUserByEmail(data.email);

  if (existingUser) {
    await linkAccount(
      existingUser.id,
      data.provider,
      data.providerAccountId,
      data.access_token,
      data.refresh_token
    );
    return existingUser;
  }

  const newUser = await prisma.user.create({
    data: {
      email: data.email,
      name: data.name,
      image: data.image,
      emailVerified: true,
      accounts: {
        create: {
          type: 'oauth',
          provider: data.provider,
          providerAccountId: data.providerAccountId,
          access_token: data.access_token,
          refresh_token: data.refresh_token,
        },
      },
    },
  });

  return newUser;
}
