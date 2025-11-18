# Supabase Configuration Guide

## 🚀 Step-by-Step Setup Guide

This guide will walk you through setting up Supabase authentication for the OmniVid project.

## Prerequisites

1. **Supabase Account**: Create an account at [supabase.com](https://supabase.com)
2. **GitHub Repository**: You'll need a GitHub repository to push your code
3. **Basic Knowledge**: Familiarity with environment variables and deployment

## Step 1: Create a Supabase Project

### 1.1 Sign Up for Supabase
1. Go to [supabase.com](https://supabase.com)
2. Sign up with your GitHub or Google account
3. Click "New Project"

### 1.2 Configure Your Project
1. **Project Name**: `omnivid` (or your preferred name)
2. **Database Password**: Choose a strong password (save this!)
3. **Region**: Select the region closest to your users
4. **Pricing Plan**: Start with the Free tier (sufficient for development)

### 1.3 Wait for Project Creation
- Supabase will take 1-2 minutes to set up your project
- Once ready, you'll see the project dashboard

## Step 2: Get Your Supabase Keys

### 2.1 Navigate to Project Settings
1. Go to your Supabase project dashboard
2. Click **Settings** in the left sidebar
3. Click **API** in the settings menu

### 2.2 Copy Your API Keys
You'll see two important keys:

1. **Project URL** (looks like): `https://abcdefgh.supabase.co`
2. **anon public key** (starts with): `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0`

**⚠️ IMPORTANT**: 
- The **anon public key** is safe to use in client-side code
- **NEVER** put your service role key in client-side code

## Step 3: Configure Environment Variables

You need to add these environment variables in **multiple places**:

### 3.1 Local Development (.env file)

Create or update your `.env` file in the project root:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Authentication Mode
USE_SUPABASE=true
AUTH_MODE=hybrid
ENABLE_DUAL_AUTH=true

# Database Configuration (for backend)
DATABASE_URL=postgresql://postgres:your-password@db.your-project-ref.supabase.co:5432/postgres

# Security
SECRET_KEY=your-super-secret-jwt-key-here
```

### 3.2 Frontend Environment Variables

Add to your frontend deployment environment:

```bash
# Vercel (if using Vercel)
# Go to Project Settings > Environment Variables

NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Netlify
# Add in Site Settings > Environment Variables

# Docker Compose
# Already configured in docker-compose.unified.yml
```

### 3.3 Backend Environment Variables

Add to your backend deployment environment:

```bash
# For backend API service
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # Get this from Settings > API > service_role key
```

## Step 4: GitHub Repository Setup

### 4.1 Create GitHub Repository
1. Go to [github.com](https://github.com) and sign in
2. Click the "+" icon in the top right
3. Select "New repository"
4. Name it `omnivid-supabase-auth`
5. Make it Public or Private (your choice)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)

### 4.2 Push Your Code

Run these commands in your project directory:

```bash
# Add all files to git
git add .

# Create your first commit
git commit -m "Initial commit: Supabase authentication migration

- Implement Supabase-native authentication
- Add migration strategy and documentation
- Create deployment conflict mitigation
- Add comprehensive testing framework"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/omnivid-supabase-auth.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 4.3 Protect Sensitive Files

Your `.gitignore` already includes protection for:
- ✅ `.env*` files (environment variables)
- ✅ `node_modules/`
- ✅ `.supabase/` directory
- ✅ Database files

**⚠️ NEVER commit these files:**
- Your actual `.env` file with real Supabase keys
- Database passwords
- Service role keys

## Step 5: Configure OAuth Providers (Optional)

### 5.1 Google OAuth Setup

1. **Create Google OAuth App**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URI: `https://your-project-ref.supabase.co/auth/v1/callback`

2. **Configure in Supabase**:
   - Go to Authentication > Providers in Supabase
   - Enable Google
   - Enter your Google Client ID and Client Secret

### 5.2 GitHub OAuth Setup

1. **Create GitHub OAuth App**:
   - Go to GitHub > Settings > Developer settings > OAuth Apps
   - Create a new OAuth App
   - Authorization callback URL: `https://your-project-ref.supabase.co/auth/v1/callback`

2. **Configure in Supabase**:
   - Enable GitHub provider in Supabase
   - Enter your GitHub Client ID and Client Secret

## Step 6: Deployment Configuration

### 6.1 Vercel Deployment

1. **Install Vercel CLI**:
```bash
npm i -g vercel
```

2. **Deploy**:
```bash
vercel login
vercel --prod
```

3. **Configure Environment Variables in Vercel**:
   - Go to your project dashboard
   - Settings > Environment Variables
   - Add your Supabase keys

### 6.2 Netlify Deployment

1. **Connect Repository**:
   - Go to [netlify.com](https://netlify.com)
   - "New site from Git"
   - Connect your GitHub repository

2. **Configure Build Settings**:
   - Build command: `npm run build`
   - Publish directory: `out` (for Next.js export)

3. **Environment Variables**:
   - Site settings > Environment variables
   - Add your Supabase configuration

### 6.3 Docker Deployment

Update your `docker-compose.unified.yml`:

```yaml
frontend:
  environment:
    - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
    - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}

api:
  environment:
    - SUPABASE_URL=${SUPABASE_URL}
    - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
```

## Step 7: Test Your Setup

### 7.1 Local Testing

1. **Start Development Server**:
```bash
npm run dev
```

2. **Test Authentication**:
   - Go to `/auth/login`
   - Try creating a new account
   - Test login with your credentials
   - Verify profile creation

### 7.2 Production Testing

1. **Deploy your application**
2. **Test all authentication flows**
3. **Verify OAuth integration**
4. **Check error handling**

## Troubleshooting

### Common Issues

**1. "Invalid API Key" Error**
- ✅ Check your Supabase URL and anon key
- ✅ Ensure no extra spaces or characters
- ✅ Verify environment variables are loaded

**2. "CORS Policy" Errors**
- ✅ Add your domain to Supabase Auth > Settings > Site URL
- ✅ Update redirect URLs in OAuth providers

**3. "Database Connection" Errors**
- ✅ Check your DATABASE_URL format
- ✅ Verify Supabase project is active
- ✅ Ensure service role key is correct

**4. "OAuth Provider" Errors**
- ✅ Verify redirect URLs match exactly
- ✅ Check OAuth app configuration
- ✅ Ensure providers are enabled in Supabase

### Getting Help

1. **Supabase Documentation**: [docs.supabase.com](https://docs.supabase.com)
2. **Supabase Discord**: [discord.supabase.com](https://discord.supabase.com)
3. **GitHub Issues**: Create issues in this repository

## Security Best Practices

✅ **DO:**
- Use environment variables for all sensitive data
- Enable RLS (Row Level Security) in Supabase
- Regularly rotate your API keys
- Monitor authentication logs
- Use HTTPS in production

❌ **DON'T:**
- Commit API keys to version control
- Use the service role key in client-side code
- Disable security features in production
- Share your Supabase project URL publicly
- Use weak passwords for admin accounts

## Success Checklist

- [ ] Supabase project created
- [ ] API keys obtained and secured
- [ ] Environment variables configured
- [ ] Code pushed to GitHub
- [ ] OAuth providers configured (optional)
- [ ] Local testing completed
- [ ] Production deployment successful
- [ ] Authentication flows working
- [ ] Error handling tested

🎉 **Congratulations!** Your Supabase authentication is now configured and ready for production use!