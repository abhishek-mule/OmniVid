-- PostgreSQL initialization script for Omnivid
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create database user if not exists (handled by environment variables)
-- DO $$ 
-- BEGIN
--    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'omnivid') THEN
--       CREATE ROLE omnivid LOGIN PASSWORD 'omnivid_password' SUPERUSER CREATEDB CREATEROLE;
--    END IF;
-- END
-- $$;

-- Set timezone
SET timezone = 'UTC';

-- Create custom types/enums if needed
DO $$
BEGIN
    -- Video status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'video_status') THEN
        CREATE TYPE video_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
    END IF;
    
    -- Project visibility enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'project_visibility') THEN
        CREATE TYPE project_visibility AS ENUM ('private', 'public', 'team');
    END IF;
    
    -- User role enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator');
    END IF;
END
$$;

-- Performance optimizations
-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_videos_project_id ON videos(project_id);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at);
CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);

CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_visibility ON projects(is_public);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

CREATE INDEX IF NOT EXISTS idx_jobs_video_id ON jobs(video_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);

CREATE INDEX IF NOT EXISTS idx_assets_project_id ON assets(project_id);
CREATE INDEX IF NOT EXISTS idx_assets_file_type ON assets(file_type);
CREATE INDEX IF NOT EXISTS idx_assets_uploaded_at ON assets(uploaded_at);

-- Create materialized views for dashboard analytics (optional)
-- These can be refreshed periodically for better performance
DO $$
BEGIN
    -- User dashboard statistics
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'user_dashboard_stats') THEN
        CREATE MATERIALIZED VIEW user_dashboard_stats AS
        SELECT 
            u.id as user_id,
            u.email,
            u.username,
            COUNT(DISTINCT p.id) as project_count,
            COUNT(DISTINCT v.id) as video_count,
            COUNT(DISTINCT CASE WHEN v.status = 'completed' THEN v.id END) as completed_videos,
            COUNT(DISTINCT CASE WHEN v.status = 'processing' THEN v.id END) as processing_videos,
            COALESCE(SUM(CASE WHEN v.status = 'completed' THEN v.file_size ELSE 0 END), 0) as total_storage_used
        FROM users u
        LEFT JOIN projects p ON p.user_id = u.id
        LEFT JOIN videos v ON v.project_id = p.id
        GROUP BY u.id, u.email, u.username
        WITH NO DATA;
        
        CREATE UNIQUE INDEX ON user_dashboard_stats(user_id);
    END IF;
    
    -- Video processing queue stats
    IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'processing_queue_stats') THEN
        CREATE MATERIALIZED VIEW processing_queue_stats AS
        SELECT 
            status,
            COUNT(*) as count,
            AVG(progress) as avg_progress,
            MIN(created_at) as oldest_task,
            MAX(created_at) as newest_task
        FROM videos 
        WHERE status IN ('pending', 'processing')
        GROUP BY status
        WITH NO DATA;
    END IF;
END
$$;

-- Create functions for common operations
CREATE OR REPLACE FUNCTION get_user_video_count(user_id_param INTEGER)
RETURNS INTEGER AS $$
DECLARE
    video_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO video_count
    FROM videos v
    JOIN projects p ON v.project_id = p.id
    WHERE p.user_id = user_id_param;
    
    RETURN video_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to update video progress safely
CREATE OR REPLACE FUNCTION update_video_progress_safe(
    video_id_param INTEGER,
    progress_param INTEGER,
    status_param video_status,
    stage_param TEXT DEFAULT NULL
)
RETURNS videos AS $$
DECLARE
    updated_video videos;
BEGIN
    UPDATE videos 
    SET 
        progress = progress_param,
        status = status_param,
        current_stage = stage_param,
        updated_at = CURRENT_TIMESTAMP,
        completed_at = CASE WHEN status_param = 'completed' THEN CURRENT_TIMESTAMP ELSE completed_at END
    WHERE id = video_id_param
    RETURNING * INTO updated_video;
    
    RETURN updated_video;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create function to clean up old data
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS TABLE(
    videos_deleted INTEGER,
    jobs_deleted INTEGER,
    assets_deleted INTEGER
) AS $$
DECLARE
    videos_count INTEGER := 0;
    jobs_count INTEGER := 0;
    assets_count INTEGER := 0;
    cutoff_date TIMESTAMP;
BEGIN
    cutoff_date := CURRENT_DATE - INTERVAL '30 days';
    
    -- Clean up old completed/failed videos (older than 30 days)
    DELETE FROM videos 
    WHERE status IN ('completed', 'failed', 'cancelled') 
    AND updated_at < cutoff_date;
    
    GET DIAGNOSTICS videos_count = ROW_COUNT;
    
    -- Clean up old jobs
    DELETE FROM jobs 
    WHERE status IN ('completed', 'failed', 'cancelled') 
    AND updated_at < cutoff_date;
    
    GET DIAGNOSTICS jobs_count = ROW_COUNT;
    
    -- Clean up old temporary assets (optional)
    DELETE FROM assets 
    WHERE file_type = 'temporary' 
    AND uploaded_at < cutoff_date;
    
    GET DIAGNOSTICS assets_count = ROW_COUNT;
    
    RETURN QUERY SELECT videos_count, jobs_count, assets_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Set up database triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to tables
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_videos_updated_at') THEN
        CREATE TRIGGER update_videos_updated_at
            BEFORE UPDATE ON videos
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_projects_updated_at') THEN
        CREATE TRIGGER update_projects_updated_at
            BEFORE UPDATE ON projects
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_users_updated_at') THEN
        CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_jobs_updated_at') THEN
        CREATE TRIGGER update_jobs_updated_at
            BEFORE UPDATE ON jobs
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END
$$;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO omnivid;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO omnivid;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO omnivid;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO omnivid;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Omnivid database initialized successfully at %', CURRENT_TIMESTAMP;
END
$$;