-- V2 Lead Generation - Phase 1 Logging System Database Schema
-- Guide's Vision: Comprehensive logging with prompt versioning and provenance tracking

-- Prompt Versions Table (Git-style versioning)
CREATE TABLE prompt_versions (
    version_hash VARCHAR(64) PRIMARY KEY,
    version_tag VARCHAR(32) NOT NULL, -- e.g., "v2.1.1-disciplined"
    prompt_content TEXT NOT NULL,
    tier_definitions JSONB NOT NULL,
    scoring_rules JSONB NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(version_tag)
);

-- Processing Logs Table (Run tracking with provenance)
CREATE TABLE processing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id VARCHAR(64) NOT NULL, -- Links related processing steps
    workflow_step VARCHAR(50) NOT NULL, -- e.g., "llm_qualification", "batch_processing"
    prompt_version_hash VARCHAR(64) REFERENCES prompt_versions(version_hash),
    input_data_hash VARCHAR(64),
    output_data_hash VARCHAR(64),
    processing_params JSONB, -- Model params, batch size, etc.
    execution_time_ms INTEGER,
    status VARCHAR(20) NOT NULL, -- success, error, timeout
    error_details JSONB,
    leads_processed INTEGER,
    leads_qualified INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Lead Results Table (Individual lead qualification results)
CREATE TABLE lead_qualification_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id VARCHAR(64) NOT NULL,
    prompt_version_hash VARCHAR(64) REFERENCES prompt_versions(version_hash),
    linkedin_url VARCHAR(500) NOT NULL,
    lead_name VARCHAR(255),
    lead_title VARCHAR(500),
    lead_company VARCHAR(500),
    engagement_type VARCHAR(20), -- reaction, comment
    llm_model VARCHAR(50),
    llm_score INTEGER,
    llm_reasoning TEXT,
    tier_classification VARCHAR(20), -- TIER_1, TIER_2, TIER_3, TIER_4
    is_qualified BOOLEAN,
    batch_number INTEGER,
    processing_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Processing Run Metadata
CREATE TABLE processing_runs (
    run_id VARCHAR(64) PRIMARY KEY,
    run_type VARCHAR(50) NOT NULL, -- full_pipeline, batch_reprocess, validation_test
    prompt_version_hash VARCHAR(64) REFERENCES prompt_versions(version_hash),
    total_leads INTEGER,
    total_qualified INTEGER,
    qualification_rate DECIMAL(5,2),
    started_by VARCHAR(50),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    status VARCHAR(20) -- running, completed, failed
);

-- Indexes for performance
CREATE INDEX idx_processing_logs_run_id ON processing_logs(run_id);
CREATE INDEX idx_processing_logs_workflow_step ON processing_logs(workflow_step);
CREATE INDEX idx_processing_logs_created_at ON processing_logs(created_at);
CREATE INDEX idx_lead_results_run_id ON lead_qualification_results(run_id);
CREATE INDEX idx_lead_results_linkedin_url ON lead_qualification_results(linkedin_url);
CREATE INDEX idx_lead_results_is_qualified ON lead_qualification_results(is_qualified);
CREATE INDEX idx_processing_runs_started_at ON processing_runs(started_at);

-- Insert initial prompt version (Tyler's 4-tier system)
INSERT INTO prompt_versions (
    version_hash, 
    version_tag, 
    prompt_content, 
    tier_definitions, 
    scoring_rules, 
    created_by
) VALUES (
    'sha256_disciplined_4tier_v2_1_1',
    'v2.1.1-disciplined',
    'You are a B2B lead qualifier for lead generation services. Use disciplined 4-tier buyer classification...',
    '{
        "TIER_1": {"range": "85-90", "description": "CEOs, VPs, Directors, C-level executives at companies who make purchasing decisions"},
        "TIER_2": {"range": "70-84", "description": "GTM teams, RevOps, Growth Marketers, Business Development, Sales Managers, Marketing Directors, Appointment Setters"},
        "TIER_3": {"range": "65-75", "description": "Clay Enterprise Partners, consultants at big firms (PwC, etc), AI/automation developers, system integrators"},
        "TIER_4": {"range": "20-40", "description": "Freelance copywriters, solo consultants, agencies offering lead gen services, ghostwriters, content creators"}
    }',
    '{
        "scoring_discipline": "Score conservatively - not everyone gets 80-90",
        "qualification_threshold": 70,
        "buyer_focus": "Focus on PURCHASING POWER, not job description similarity"
    }',
    'trinity_collective_intelligence'
);