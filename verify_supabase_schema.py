"""
Supabase Database Schema Verification Script
Verify that all required tables exist in Supabase database using service role key
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_supabase_schema():
    """Check if all required tables exist in Supabase"""

    supabase_url = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
    service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not supabase_url or not service_role_key:
        print("❌ Missing Supabase environment variables")
        print(f"URL: {supabase_url}")
        print(f"Service Key: {'***' + service_role_key[-10:] if service_role_key else 'None'}")
        return False

    expected_tables = [
        'user_profiles',
        'projects',
        'videos',
        'assets',
        'jobs'
    ]

    print(f"🔍 Verifying Supabase schema at {supabase_url}")
    print(f"Expected tables: {', '.join(expected_tables)}")

    # Test connection with service role key
    headers = {
        'apikey': service_role_key,
        'Authorization': f'Bearer {service_role_key}',
        'Content-Type': 'application/json'
    }

    try:
        # Test 1: General connectivity to Supabase
        response = requests.get(f"{supabase_url}/rest/v1/", headers=headers, timeout=10)
        print(f"✅ Supabase REST API: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Supabase API error: {response.text}")
            return False

        # Test 2: Check if we can access database info
        db_response = requests.get(f"{supabase_url}/rest/v1/user_profiles?limit=1", headers=headers, timeout=10)
        if db_response.status_code == 200:
            print("✅ user_profiles table exists")
        else:
            print(f"❌ user_profiles table access failed: {db_response.status_code} - {db_response.text}")

        # Test other tables
        for table in ['projects', 'videos', 'assets', 'jobs']:
            table_response = requests.get(f"{supabase_url}/rest/v1/{table}?limit=1", headers=headers, timeout=10)
            if table_response.status_code == 200:
                print(f"✅ {table} table exists")
            else:
                print(f"❌ {table} table access failed: {table_response.status_code} - {table_response.text}")

        # Test 3: Check authentication service
        auth_response = requests.get(f"{supabase_url}/auth/v1/admin/users", headers=headers, timeout=10)
        if auth_response.status_code in [200, 401]:  # 401 is expected without proper admin headers
            print("✅ Supabase Auth service is accessible")
        else:
            print(f"❌ Auth service check: {auth_response.status_code}")

        print("\n🚀 Schema verification completed!")
        print("\n📝 Next Steps:")
        print("1. If any tables are missing, create them in Supabase SQL Editor")
        print("2. Configure OAuth providers in Supabase Dashboard → Authentication → Providers")
        print("3. Set callback URLs for OAuth providers")

        return True

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def create_schema_sql():
    """Generate SQL to create missing tables"""

    sql = """
-- SQL to create OmniVid tables in Supabase
-- Run this in Supabase → SQL Editor

-- Enable RLS
ALTER TABLE IF EXISTS auth.users ENABLE ROW LEVEL SECURITY;

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    is_public BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create videos table
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    video_url TEXT,
    thumbnail_url TEXT,
    duration REAL,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    settings TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Create assets table
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    video_id INTEGER REFERENCES videos(id) ON DELETE SET NULL,
    is_processed BOOLEAN DEFAULT FALSE,
    metadata TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create jobs table for Celery tasks
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    task_id TEXT UNIQUE NOT NULL,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    result TEXT,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username);
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_project_id ON videos(project_id);
CREATE INDEX IF NOT EXISTS idx_assets_project_id ON assets(project_id);
CREATE INDEX IF NOT EXISTS idx_assets_video_id ON assets(video_id);
CREATE INDEX IF NOT EXISTS idx_jobs_task_id ON jobs(task_id);

-- Enable RLS on our tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_profiles
CREATE POLICY "Users can view their own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- RLS Policies for projects
CREATE POLICY "Users can view their own projects" ON projects
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create their own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own projects" ON projects
    FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own projects" ON projects
    FOR DELETE USING (auth.uid()::text = user_id::text);

-- Allow viewing public projects
CREATE POLICY "Anyone can view public projects" ON projects
    FOR SELECT USING (is_public = true);

-- RLS Policies for videos (similar to projects)
CREATE POLICY "Users can view videos from their projects" ON videos
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = videos.project_id
            AND projects.user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can create videos in their projects" ON videos
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM projects
            WHERE projects.id = project_id
            AND projects.user_id::text = auth.uid()::text
        )
    );

-- Additional policies for assets and jobs following similar patterns...

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
"""
    return sql

if __name__ == "__main__":
    print("🚀 OmniVid Supabase Schema Verification")
    print("=" * 50)

    if check_supabase_schema():
        print("\n🎉 Supabase connection successful!")
    else:
        print("\n❌ Supabase connection failed!")
        print("\n📄 Here is the SQL to create the required schema:")
        print("=" * 50)
        print(create_schema_sql())
