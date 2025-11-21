# Troubleshooting Supabase "Failed to Fetch" Error

## Common Causes and Solutions

### 1. CORS Configuration (Most Common)

**Issue**: Supabase blocks requests from your domain due to CORS policy.

**Solution**: Update your Supabase project settings:

1. Go to your Supabase dashboard
2. Navigate to **Authentication** → **Settings**
3. Add your domain to "Site URL":
   - Local development: `http://localhost:3000`
   - Production: `https://yourdomain.com`
4. Add redirect URLs:
   - `http://localhost:3000/**`
   - `https://yourdomain.com/**`

### 2. Authentication Settings

**Issue**: Email confirmation might be enabled, causing signup failures.

**Solution**: 
1. Go to **Authentication** → **Settings**
2. Disable **"Enable email confirmations"** for development
3. Or configure SMTP settings for production

### 3. Supabase Project Status

**Issue**: Supabase project might be paused or have connectivity issues.

**Solution**:
1. Check if your Supabase project is active (not paused)
2. Verify your database is running
3. Test the Supabase URL directly in browser

### 4. Network/Connectivity Issues

**Issue**: Network firewall or proxy blocking requests.

**Solution**:
1. Test with a different network
2. Check if VPN is causing issues
3. Verify firewall settings

### 5. Environment Variables

**Issue**: Supabase keys might be invalid or incorrectly formatted.

**Solution**:
- Ensure no extra spaces in the keys
- Verify the URL starts with `https://`
- Check the anon key format (should start with `eyJ...`)

## Quick Fix Steps

### Step 1: Check Supabase Dashboard
1. Log into [supabase.com](https://supabase.com)
2. Go to your project
3. Check if there are any error notifications
4. Verify the project status (should be green)

### Step 2: Configure Authentication
1. **Authentication** → **Settings**
2. **Site URL**: Add `http://localhost:3000` (for local dev)
3. **Redirect URLs**: Add `http://localhost:3000/**`
4. **Email confirmations**: Disable for development

### Step 3: Test Connection
Open browser console and run:
```javascript
fetch('https://your-project.supabase.co/rest/v1/', {
  headers: {
    'apikey': 'your-anon-key-here'
  }
})
```

If this fails, the issue is with Supabase configuration.

### Step 4: Check Browser Network Tab
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Try creating an account
4. Look for failed requests (red status)
5. Check the exact error message

## Immediate Test

Let me create a simple test to verify your Supabase connection: