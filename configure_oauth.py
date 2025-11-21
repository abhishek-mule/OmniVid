"""
OAuth Provider Configuration Guide for OmniVid
This script provides instructions for setting up Google and GitHub OAuth
"""
import os
from dotenv import load_dotenv

load_dotenv()

def print_oauth_setup_instructions():
    """Print comprehensive OAuth setup instructions"""

    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL', 'https://your-project.supabase.co')
    project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '') if supabase_url != 'https://your-project.supabase.co' else 'your-project'

    print("🔐 OAUTH PROVIDER CONFIGURATION GUIDE")
    print("=" * 50)
    print(f"🔗 Supabase Project URL: {supabase_url}")
    print(f"📍 Project Reference: {project_ref}")
    print()

    # Development URLs
    dev_urls = [
        "http://localhost:3000/auth/callback",
        "http://localhost:3000/**"
    ]

    # Production URLs (customize based on your deployment)
    prod_urls = [
        "https://your-domain.com/auth/callback",
        "https://your-domain.com/**"
    ]

    print("📋 REQUIRED REDIRECT URIs:")
    print("\n🧪 Development:")
    for url in dev_urls:
        print(f"   {url}")

    print("\n🚀 Production:")
    for url in prod_urls:
        print(f"   {url}")
    print()

    print("🎯 SUPABASE OAUTH CONFIGURATION")
    print("=" * 50)
    print()

    print("1️⃣  GOOGLE OAUTH SETUP")
    print("-" * 30)
    print("1. Go to Google Cloud Console: https://console.cloud.google.com")
    print("2. Create a new project or select existing")
    print("3. Enable Google+ API")
    print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth client ID'")
    print("5. Set Application Type: 'Web application'")
    print("6. Add Authorized redirect URIs:")
    for url in dev_urls + prod_urls:
        if 'google' in url or '**' in url:
            print(f"   - {url.replace('**', 'auth/callback')}")
    print("7. Save Client ID and Client Secret")
    print()

    print("2️⃣  SUPABASE GOOGLE CONFIGURATION")
    print("-" * 30)
    print("1. Go to Supabase Dashboard → Authentication → Providers")
    print("2. Enable Google provider")
    print("3. Enter the Client ID and Client Secret from Google")
    print("4. Add redirect URLs:")
    print(f"   https://{project_ref}.supabase.co/auth/v1/callback")
    print()

    print("3️⃣  GITHUB OAUTH SETUP")
    print("-" * 30)
    print("1. Go to GitHub → Settings → Developer settings → OAuth Apps")
    print("2. Click 'New OAuth App'")
    print("3. Fill in:")
    print("   - Application name: 'OmniVid'")
    print("   - Homepage URL: 'http://localhost:3000' (or your production URL)")
    print("   - Authorization callback URL:")
    for url in dev_urls + prod_urls:
        if 'localhost' in url or '**' in url:
            callback_url = url.replace('**', 'auth/callback')
            print(f"     {callback_url}")
    print("4. Save to get Client ID and Client Secret")
    print()

    print("4️⃣  SUPABASE GITHUB CONFIGURATION")
    print("-" * 30)
    print("1. Go to Supabase Dashboard → Authentication → Providers")
    print("2. Enable GitHub provider")
    print("3. Enter the Client ID and Client Secret from GitHub")
    print("4. Add redirect URLs:")
    print(f"   https://{project_ref}.supabase.co/auth/v1/callback")
    print()

    print("✨ ENVIRONMENT VARIABLES")
    print("=" * 30)
    print("# Add to your .env.local or environment:")
    print("NEXT_PUBLIC_SUPABASE_URL=https://{project_ref}.supabase.co")
    print("NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key")
    print("SUPABASE_SERVICE_ROLE_KEY=your-service-role-key")
    print()

    print("🧪 TESTING OAUTH")
    print("=" * 20)
    print("1. Start your development server: npm run dev")
    print("2. Go to http://localhost:3000/auth/login")
    print("3. Click 'Continue with Google' or 'Continue with GitHub'")
    print("4. Complete OAuth flow")
    print("5. Verify redirect to /auth/callback")
    print("6. Check user session in browser console")
    print()

    print("🔧 TROUBLESHOOTING")
    print("=" * 20)
    print("❌ 'OAuth provider not configured': Enable provider in Supabase")
    print("❌ 'redirect_uri_mismatch': Check redirect URLs match exactly")
    print("❌ 'Invalid client': Verify Client ID and Secret are correct")
    print("❌ Callback page shows error: Check browser network tab for details")
    print()

    print("🛡️  SECURITY NOTES")
    print("=" * 20)
    print("✅ Never commit OAuth credentials to version control")
    print("✅ Use environment variables for all sensitive data")
    print("✅ Test in development before production deployment")
    print("✅ Regularly rotate OAuth credentials")
    print()

if __name__ == "__main__":
    print_oauth_setup_instructions()
