-- Migration: Better Auth Schema Integration
-- Purpose: Rename legacy users table and create user_stats for Better Auth integration
-- Date: 2026-02-06

-- Step 1: Rename old users table to users_legacy
ALTER TABLE users RENAME TO users_legacy;

-- Step 2: Create user_stats table for Better Auth user statistics
CREATE TABLE IF NOT EXISTS user_stats (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id VARCHAR NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    query_count_today INTEGER DEFAULT 0,
    last_query_date DATE,
    api_key VARCHAR(64) UNIQUE,
    api_key_created_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Step 3: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_user_stats_api_key ON user_stats(api_key);
