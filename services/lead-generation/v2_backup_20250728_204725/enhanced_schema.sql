-- Enhanced SQLite Schema for Complete Influencer → Post → Lead Attribution
-- Addresses Guide's critical gap: influencer/post tracking for ROI analysis

-- 1. INFLUENCERS Table - Track content creators/influencers
CREATE TABLE IF NOT EXISTS influencers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    influencer_name TEXT NOT NULL,
    influencer_profile_url TEXT UNIQUE,
    influencer_followers INTEGER,
    influencer_industry TEXT,
    influencer_tier TEXT, -- nano, micro, macro, mega
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. POSTS Table - Track specific posts/content
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_url TEXT UNIQUE NOT NULL,
    influencer_id INTEGER,
    post_content TEXT,
    post_type TEXT, -- text, video, carousel, etc.
    post_timestamp DATETIME,
    total_reactions INTEGER DEFAULT 0,
    total_comments INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (influencer_id) REFERENCES influencers (id)
);

-- 3. CAMPAIGNS Table - Track marketing campaigns
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name TEXT NOT NULL,
    campaign_type TEXT, -- organic, paid, collaboration
    start_date DATE,
    end_date DATE,
    budget DECIMAL(10,2),
    target_audience TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 4. Enhanced LEAD_QUALIFICATION_RESULTS - Add attribution
CREATE TABLE IF NOT EXISTS lead_qualification_results_enhanced (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    prompt_version_hash TEXT,
    
    -- Lead Information (existing)
    linkedin_url TEXT NOT NULL,
    lead_name TEXT,
    lead_title TEXT,
    lead_company TEXT,
    engagement_type TEXT, -- reaction, comment
    
    -- NEW: Attribution Fields
    post_id INTEGER, -- Links to posts table
    influencer_id INTEGER, -- Links to influencers table  
    campaign_id INTEGER, -- Links to campaigns table
    engagement_timestamp DATETIME,
    
    -- LLM Analysis (existing)
    llm_model TEXT,
    llm_score INTEGER,
    llm_reasoning TEXT,
    tier_classification TEXT,
    is_qualified BOOLEAN,
    
    -- Processing Metadata (existing)
    batch_number INTEGER,
    processing_order INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (prompt_version_hash) REFERENCES prompt_versions (version_hash),
    FOREIGN KEY (post_id) REFERENCES posts (id),
    FOREIGN KEY (influencer_id) REFERENCES influencers (id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
);

-- 5. ROI_ANALYTICS View - For performance tracking
CREATE VIEW IF NOT EXISTS roi_analytics AS
SELECT 
    c.campaign_name,
    i.influencer_name,
    p.post_url,
    p.total_engagement as post_engagement,
    COUNT(l.id) as leads_generated,
    COUNT(CASE WHEN l.is_qualified = 1 THEN 1 END) as qualified_leads,
    AVG(l.llm_score) as avg_lead_score,
    (COUNT(CASE WHEN l.is_qualified = 1 THEN 1 END) * 100.0 / COUNT(l.id)) as qualification_rate
FROM lead_qualification_results_enhanced l
LEFT JOIN posts p ON l.post_id = p.id
LEFT JOIN influencers i ON l.influencer_id = i.id
LEFT JOIN campaigns c ON l.campaign_id = c.id
GROUP BY c.campaign_name, i.influencer_name, p.post_url;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_posts_influencer_id ON posts(influencer_id);
CREATE INDEX IF NOT EXISTS idx_posts_url ON posts(post_url);
CREATE INDEX IF NOT EXISTS idx_leads_enhanced_post_id ON lead_qualification_results_enhanced(post_id);
CREATE INDEX IF NOT EXISTS idx_leads_enhanced_influencer_id ON lead_qualification_results_enhanced(influencer_id);
CREATE INDEX IF NOT EXISTS idx_leads_enhanced_campaign_id ON lead_qualification_results_enhanced(campaign_id);

-- Sample data for the current post
INSERT OR IGNORE INTO posts (post_url, post_content, total_reactions, total_comments, total_engagement)
VALUES (
    'https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642',
    'LinkedIn post content about lead generation (extracted from scraper)',
    143,
    52, 
    195
);