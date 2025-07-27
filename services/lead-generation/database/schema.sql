-- Lead Qualification Database Schema

-- Profiles table: Stores LinkedIn profile data
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    linkedin_url TEXT UNIQUE NOT NULL,
    full_name TEXT,
    headline TEXT,
    followers INTEGER DEFAULT 0,
    connections INTEGER DEFAULT 0,
    about TEXT,
    profile_data JSON,  -- Full API response stored as JSON
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_profiles_linkedin_url ON profiles(linkedin_url);

-- Qualifications table: Stores analysis results
CREATE TABLE IF NOT EXISTS qualifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    decision_maker BOOLEAN,
    decision_maker_reason TEXT,
    decision_maker_confidence INTEGER,
    competitor BOOLEAN,
    competitor_reason TEXT,
    competitor_confidence INTEGER,
    influencer_score INTEGER,
    influencer_reason TEXT,
    posting_frequency TEXT,
    is_qualified BOOLEAN,
    qualification_summary TEXT,
    disqualification_reason TEXT,
    overall_score INTEGER,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

-- Create index for profile lookups
CREATE INDEX IF NOT EXISTS idx_qualifications_profile_id ON qualifications(profile_id);

-- Leads table: Tracks processing status
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER,
    source_file TEXT,
    source_row_number INTEGER,
    linkedin_url TEXT,
    original_data JSON,  -- Original CSV row data
    processing_status TEXT DEFAULT 'pending',  -- pending, processing, completed, error
    error_message TEXT,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

-- Create indices for lead tracking
CREATE INDEX IF NOT EXISTS idx_leads_source_file ON leads(source_file);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(processing_status);
CREATE INDEX IF NOT EXISTS idx_leads_linkedin_url ON leads(linkedin_url);

-- Processing batches table: Track batch runs
CREATE TABLE IF NOT EXISTS processing_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    total_leads INTEGER,
    processed_leads INTEGER DEFAULT 0,
    qualified_leads INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running'  -- running, completed, failed
);

-- Create a view for easy qualified lead exports
CREATE VIEW IF NOT EXISTS qualified_leads_view AS
SELECT 
    p.full_name,
    p.headline,
    p.linkedin_url,
    p.followers,
    p.connections,
    q.decision_maker,
    q.decision_maker_reason,
    q.competitor,
    q.competitor_reason,
    q.influencer_score,
    q.influencer_reason,
    q.is_qualified,
    q.qualification_summary,
    q.overall_score,
    l.source_file,
    q.analyzed_at
FROM profiles p
JOIN qualifications q ON p.id = q.profile_id
JOIN leads l ON p.id = l.profile_id
WHERE q.is_qualified = 1;