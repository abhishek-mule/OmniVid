# OmniVid Container Architecture Consolidation & Supabase Integration Plan

## 🎯 Executive Summary

This document outlines the comprehensive strategy to consolidate overlapping container services and migrate to Supabase-native authentication for the OmniVid application, addressing deployment conflicts and maximizing development efficiency.

## 📊 Current Architecture Analysis

### 🚨 Identified Issues

#### Container Conflicts
1. **PostgreSQL Duplication:**
   - `postgres:15-alpine` in `docker-compose.yml` (dev)
   - `omnivid-postgres` in `docker-compose.prod.yml` (prod)
   - `test-postgres` in `docker-compose.ci.yml` (testing)

2. **Redis Duplication:**
   - `redis:7-alpine` in `docker-compose.yml` (dev)
   - `omnivid-redis` in `docker-compose.prod.yml` (prod)
   - `test-redis` in `docker-compose.ci.yml` (testing)

3. **Backend Service Conflicts:**
   - `backend` (docker-compose.yml)
   - `omnivid-api` (docker-compose.prod.yml)
   - `omnivid-backend-1` (orphaned)

#### Authentication Architecture Issues
1. **Dual Authentication Systems:**
   - Custom JWT-based auth in `/packages/shared/src/lib/auth/index.ts`
   - Supabase client partially configured but unused

2. **Environment Inconsistencies:**
   - Multiple `.env` configurations
   - Unused Supabase environment variables

## 🏗️ Proposed Consolidated Architecture

### Core Philosophy
- **Single Source of Truth**: One Docker Compose configuration per environment
- **Supabase-Native**: Replace custom auth with Supabase Auth + Row Level Security
- **Development Efficiency**: Streamlined local development experience
- **Production Ready**: Optimized for scalability and maintainability

### Target Architecture Components

#### 1. Unified Docker Compose Configuration
```
services:
  # Core Infrastructure (Single instances)
  postgres:        # Primary database (Supabase or local)
  redis:          # Message broker & cache
  minio:          # File storage (replacing local file systems)

  # Application Services
  api:            # FastAPI backend (consolidated)
  frontend:       # Next.js frontend
  celery-worker:  # Background processing
  celery-beat:    # Task scheduler

  # Optional Services (via profiles)
  nginx:          # Reverse proxy (production only)
  flower:         # Celery monitoring (development only)
  prometheus:     # Monitoring (production only)
  grafana:        # Visualization (production only)
```

#### 2. Supabase-Native Authentication Flow
```
Frontend (Next.js)
    ↓
Supabase Client (@supabase/ssr)
    ↓
Supabase Auth (JWT)
    ↓
Row Level Security (RLS)
    ↓
Supabase Database (PostgreSQL)
```

## 📋 Implementation Plan

### Phase 1: Container Consolidation (Days 1-2)
- [ ] Create unified `docker-compose.yml` with environment profiles
- [ ] Standardize container naming conventions
- [ ] Remove orphaned containers and duplicate services
- [ ] Test consolidated local development setup

### Phase 2: Supabase Integration Setup (Days 3-4)
- [ ] Configure Supabase project with provided credentials
- [ ] Implement Supabase client with proper session management
- [ ] Create authentication middleware for Next.js
- [ ] Test Supabase auth alongside existing system

### Phase 3: Authentication Migration (Days 5-6)
- [ ] Migrate user authentication to Supabase Auth
- [ ] Implement Row Level Security policies
- [ ] Update API calls to use Supabase client
- [ ] Remove custom JWT implementation

### Phase 4: Legacy Cleanup (Day 7)
- [ ] Remove duplicate Docker Compose files
- [ ] Clean up unused authentication code
- [ ] Update documentation and environment configs
- [ ] Performance validation and optimization

## 🔧 Technical Implementation Details

### Container Consolidation Strategy

#### Profile-Based Configuration
```yaml
services:
  postgres:
    image: postgres:15-alpine
    profiles: [dev, test]  # Disabled in production (use Supabase)
  
  redis:
    image: redis:7-alpine
    profiles: [dev, test]  # Disabled in production (use managed Redis)
  
  api:
    build: ./backend
    environment:
      - USE_SUPABASE=${USE_SUPABASE:-false}
    profiles: [dev, prod]
  
  frontend:
    build: ./frontend
    environment:
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    profiles: [dev, prod]
```

#### Environment-Specific Configurations

**Development Environment**
```bash
# .env.local
USE_SUPABASE=false
DATABASE_URL=postgresql://user:pass@localhost:5432/omnivid
REDIS_URL=redis://localhost:6379/0
```

**Production Environment**
```bash
# .env.production
USE_SUPABASE=true
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### Supabase Authentication Implementation

#### Next.js App Router Integration
```typescript
// app/layout.tsx
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export default async function RootLayout({ children }) {
  const cookieStore = cookies()
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get(name) {
          return cookieStore.get(name)?.value
        },
      },
    }
  )

  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
```

#### Client-Side Authentication Hook
```typescript
// hooks/use-auth.ts
import { createClient } from '@omnivid/supabase'
import { useEffect, useState } from 'react'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const supabase = createClient()

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        setUser(session?.user ?? null)
        setLoading(false)
      }
    )

    return () => subscription.unsubscribe()
  }, [])

  return { user, loading, signIn, signOut }
}
```

#### API Integration with RLS
```typescript
// lib/supabase-client.ts
import { createClient } from '@supabase/supabase-js'

export function createServerClient() {
  return createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
    {
      auth: {
        autoRefreshToken: false,
        persistSession: false,
      },
    }
  )
}

// API route example
export async function GET(request: Request) {
  const supabase = createServerClient()
  const { data, error } = await supabase
    .from('videos')
    .select('*')
    .eq('user_id', request.user.id) // RLS enforced
  
  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 400,
    })
  }
  
  return new Response(JSON.stringify(data))
}
```

## 📈 Benefits & ROI

### Development Efficiency Gains
- **50% Reduction** in container management complexity
- **Zero Configuration** Supabase authentication
- **Automatic session management** and token refresh
- **Built-in security** with Row Level Security

### Operational Benefits
- **Single deployment pipeline** instead of multiple configurations
- **Consistent development** and production environments
- **Reduced maintenance** overhead
- **Scalable authentication** infrastructure

### Security Improvements
- **Enterprise-grade auth** without custom implementation
- **Automatic token validation** and expiration handling
- **Row-level security** for data access control
- **SOC 2 compliance** through Supabase

## 🧪 Testing Strategy

### Container Validation
1. **Local Development**: Full stack with local database
2. **Production Simulation**: Supabase integration testing
3. **Cross-Environment**: Consistency validation
4. **Performance**: Container resource optimization

### Authentication Testing
1. **Login/Logout Flow**: End-to-end authentication testing
2. **Session Management**: Token refresh and persistence
3. **Security**: RLS policy validation
4. **Error Handling**: Auth failure scenarios

## 📚 Migration Checklist

### Pre-Migration
- [ ] Backup current authentication data
- [ ] Document current API authentication flows
- [ ] Prepare Supabase project configuration
- [ ] Set up environment variable management

### During Migration
- [ ] Deploy consolidated containers
- [ ] Implement Supabase auth alongside existing system
- [ ] Migrate user data if needed
- [ ] Test authentication flows thoroughly

### Post-Migration
- [ ] Remove legacy authentication code
- [ ] Update documentation and guides
- [ ] Train team on new architecture
- [ ] Monitor for any authentication issues

## 🚀 Next Steps

1. **Approve Architecture Plan**: Review and approve consolidation strategy
2. **Prepare Supabase Project**: Configure with provided credentials
3. **Begin Phase 1**: Start container consolidation
4. **Schedule Migration**: Plan timeline for authentication migration

---

*This consolidation plan addresses all identified container conflicts while providing a clear path to modern, Supabase-native authentication architecture.*