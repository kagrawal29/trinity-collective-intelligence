-- V2 LEAD GENERATION - MINIMAL SCHEMA
-- Purpose: Store only essential data for testing influencer-based lead generation
-- Philosophy: Start lean, expand based on real needs

-- Drop existing tables if needed (for clean testing)
DROP TABLE IF EXISTS engaged_prospects CASCADE;
DROP TABLE IF EXISTS influencer_posts CASCADE;
DROP TABLE IF EXISTS influencers CASCADE;
DROP TABLE IF EXISTS test_sessions CASCADE;

-- 1. Influencers table - Core profiles we're analyzing
CREATE TABLE influencers (
    id SERIAL PRIMARY KEY,
    linkedin_url VARCHAR(500) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    headline TEXT,
    follower_count INTEGER DEFAULT 0,
    -- JSONB for flexibility - store complete API response
    raw_profile_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Posts table - Content that drives engagement
CREATE TABLE influencer_posts (
    id SERIAL PRIMARY KEY,
    influencer_id INTEGER NOT NULL REFERENCES influencers(id) ON DELETE CASCADE,
    post_url VARCHAR(500) UNIQUE NOT NULL,
    post_text TEXT,
    reactions_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    -- URNs needed for fetching engagement data
    reactions_urn VARCHAR(500),
    comments_urn VARCHAR(500),
    -- Store complete post data
    raw_post_data JSONB,
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Engaged prospects - People who reacted to posts
CREATE TABLE engaged_prospects (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES influencer_posts(id) ON DELETE CASCADE,
    profile_url VARCHAR(500) NOT NULL,
    full_name VARCHAR(255),
    title VARCHAR(500),           -- Job title is KEY for qualification
    subtitle VARCHAR(500),        -- Usually company name
    reaction_type VARCHAR(50),    -- LIKE, CELEBRATE, SUPPORT, etc.
    -- Qualification fields
    is_relevant BOOLEAN DEFAULT NULL,      -- NULL = not evaluated yet
    qualification_score INTEGER DEFAULT NULL,  -- 0-100 scale
    qualification_notes TEXT,              -- Why qualified/disqualified
    -- Tracking
    created_at TIMESTAMP DEFAULT NOW(),
    qualified_at TIMESTAMP,
    
    -- Prevent duplicate entries
    UNIQUE(post_id, profile_url)
);

-- 4. Test sessions - Track our testing/processing runs
CREATE TABLE test_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    influencer_id INTEGER REFERENCES influencers(id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    posts_analyzed INTEGER DEFAULT 0,
    prospects_found INTEGER DEFAULT 0,
    prospects_qualified INTEGER DEFAULT 0,
    errors JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance (only essential ones)
CREATE INDEX idx_influencers_url ON influencers(linkedin_url);
CREATE INDEX idx_posts_influencer ON influencer_posts(influencer_id);
CREATE INDEX idx_posts_reactions ON influencer_posts(reactions_count DESC);
CREATE INDEX idx_prospects_post ON engaged_prospects(post_id);
CREATE INDEX idx_prospects_relevant ON engaged_prospects(is_relevant) WHERE is_relevant IS NOT NULL;
CREATE INDEX idx_prospects_score ON engaged_prospects(qualification_score DESC) WHERE qualification_score IS NOT NULL;

-- Helper views for common queries

-- View: High-engagement posts
CREATE VIEW high_engagement_posts AS
SELECT 
    p.*,
    i.full_name as influencer_name,
    i.follower_count as influencer_followers
FROM influencer_posts p
JOIN influencers i ON p.influencer_id = i.id
WHERE p.reactions_count > 50
ORDER BY p.reactions_count DESC;

-- View: Qualified prospects summary
CREATE VIEW qualified_prospects_summary AS
SELECT 
    ep.full_name,
    ep.title,
    ep.subtitle as company,
    ep.qualification_score,
    ep.profile_url,
    i.full_name as discovered_via_influencer,
    p.post_url as discovered_via_post
FROM engaged_prospects ep
JOIN influencer_posts p ON ep.post_id = p.id
JOIN influencers i ON p.influencer_id = i.id
WHERE ep.is_relevant = true
ORDER BY ep.qualification_score DESC;

-- Comments explaining design decisions:
-- 1. We use JSONB for raw data to preserve all API response fields
-- 2. We extract only essential fields as columns for querying
-- 3. No complex relationships yet - keep it simple
-- 4. Qualification is a simple boolean + score + notes
-- 5. Test sessions help track our experiments
-- 6. Views provide easy access to common queries