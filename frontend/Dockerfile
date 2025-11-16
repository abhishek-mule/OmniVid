# Stage 1: Dependencies
FROM node:20-alpine AS deps

# Install system dependencies and setup pnpm
RUN apk add --no-cache libc6-compat
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy package files and lib directory
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages/shared/package.json ./packages/shared/package.json
COPY frontend/package.json ./frontend/package.json
COPY frontend/lib ./frontend/lib

# Install dependencies
RUN pnpm install --frozen-lockfile

# Stage 2: Builder
FROM node:20-alpine AS builder

# Install pnpm in builder
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy package files and install dependencies
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/packages/shared/node_modules ./packages/shared/node_modules
COPY --from=deps /app/pnpm-lock.yaml ./
COPY --from=deps /app/package.json ./
COPY --from=deps /app/packages/shared/package.json ./packages/shared/package.json
COPY --from=deps /app/frontend/package.json ./frontend/package.json

# Install production dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build shared package
WORKDIR /app/packages/shared
RUN pnpm build

# Build frontend
WORKDIR /app/frontend
# Copy the lib directory to ensure path aliases work
COPY --from=deps /app/frontend/lib ./lib
# Install and build
RUN pnpm install && pnpm build

# Stage 3: Runner
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Install production dependencies
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy necessary files from builder
COPY --from=builder /app/frontend/.next/standalone ./
COPY --from=builder /app/frontend/.next/static ./frontend/.next/static
COPY --from=builder /app/frontend/public ./frontend/public
COPY --from=builder /app/packages/shared/dist ./packages/shared/dist

# Create a non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs && \
    chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

# Start the application
CMD ["node", "server.js"]
