#!/usr/bin/env python3
"""
V2 Lead Generation - SQLite Logging System
Quick alternative to PostgreSQL for immediate testing
Maintains same interface as PostgreSQL version
"""

import hashlib
import json
import time
import uuid
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv

load_dotenv()

class V2LoggingSystemSQLite:
    """SQLite Implementation of Phase 1 Logging System"""
    
    def __init__(self, db_path: str = "trinity_logging.db"):
        self.db_path = db_path
        self.db_connection = None
        self.current_run_id = None
        self.current_prompt_version = None
        
    def connect_database(self):
        """Connect to SQLite database - PRODUCTION READY"""
        try:
            self.db_connection = sqlite3.connect(self.db_path)
            self.db_connection.row_factory = sqlite3.Row  # Enable dict-like access
            
            # Create tables if they don't exist
            self._create_tables()
            
            print(f"✅ Connected to SQLite database: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ CRITICAL: Database connection failed: {e}")
            print("❌ Cannot proceed without database connection")
            raise Exception(f"Database connection required for production operation: {e}")
    
    def _create_tables(self):
        """Create all required tables with enhanced schema for influencer/post attribution"""
        
        cursor = self.db_connection.cursor()
        
        # 1. Influencers Table - Track content creators/influencers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS influencers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                influencer_name TEXT NOT NULL,
                influencer_profile_url TEXT UNIQUE,
                influencer_followers INTEGER,
                influencer_industry TEXT,
                influencer_tier TEXT, -- nano, micro, macro, mega
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Posts Table - Track specific posts/content
        cursor.execute("""
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
            )
        """)
        
        # 3. Campaigns Table - Track marketing campaigns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_name TEXT NOT NULL,
                campaign_type TEXT, -- organic, paid, collaboration
                start_date DATE,
                end_date DATE,
                budget DECIMAL(10,2),
                target_audience TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. Prompt Versions Table (existing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompt_versions (
                version_hash TEXT PRIMARY KEY,
                version_tag TEXT NOT NULL UNIQUE,
                prompt_content TEXT NOT NULL,
                tier_definitions TEXT NOT NULL,  -- JSON as TEXT
                scoring_rules TEXT NOT NULL,     -- JSON as TEXT
                created_by TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. Processing Logs Table (existing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_logs (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                workflow_step TEXT NOT NULL,
                prompt_version_hash TEXT,
                input_data_hash TEXT,
                output_data_hash TEXT,
                processing_params TEXT,  -- JSON as TEXT
                execution_time_ms INTEGER,
                status TEXT NOT NULL,
                error_details TEXT,      -- JSON as TEXT
                leads_processed INTEGER,
                leads_qualified INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prompt_version_hash) REFERENCES prompt_versions (version_hash)
            )
        """)
        
        # 6. Enhanced Lead Qualification Results - WITH ATTRIBUTION
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lead_qualification_results (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                prompt_version_hash TEXT,
                
                -- Lead Information
                linkedin_url TEXT NOT NULL,
                lead_name TEXT,
                lead_title TEXT,
                lead_company TEXT,
                engagement_type TEXT, -- reaction, comment
                
                -- NEW: Attribution Fields for ROI tracking
                post_id INTEGER, -- Links to posts table
                influencer_id INTEGER, -- Links to influencers table  
                campaign_id INTEGER, -- Links to campaigns table
                engagement_timestamp DATETIME,
                post_url TEXT, -- Direct URL for immediate reference
                
                -- LLM Analysis
                llm_model TEXT,
                llm_score INTEGER,
                llm_reasoning TEXT,
                tier_classification TEXT,
                is_qualified BOOLEAN,
                
                -- Processing Metadata
                batch_number INTEGER,
                processing_order INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (prompt_version_hash) REFERENCES prompt_versions (version_hash),
                FOREIGN KEY (post_id) REFERENCES posts (id),
                FOREIGN KEY (influencer_id) REFERENCES influencers (id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            )
        """)
        
        # 7. Processing Runs Table (existing)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_runs (
                run_id TEXT PRIMARY KEY,
                run_type TEXT NOT NULL,
                prompt_version_hash TEXT,
                total_leads INTEGER,
                total_qualified INTEGER,
                qualification_rate REAL,
                started_by TEXT,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                status TEXT,
                FOREIGN KEY (prompt_version_hash) REFERENCES prompt_versions (version_hash)
            )
        """)
        
        # 8. Post Qualifications Table - Store LLM qualification results for posts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_qualifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                run_id TEXT NOT NULL,
                prompt_version_hash TEXT,
                
                -- LLM Qualification Results
                overall_score INTEGER,
                target_audience_score INTEGER,
                topic_relevance_score INTEGER,
                lead_quality_score INTEGER,
                action_trigger_score INTEGER,
                qualification_status TEXT, -- QUALIFIED, NOT_QUALIFIED, ERROR
                llm_reasoning TEXT,
                key_indicators TEXT, -- JSON array as TEXT
                recommended_action TEXT, -- PROCESS, SKIP
                
                -- Processing Metadata
                llm_model TEXT,
                evaluated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                processing_time_ms INTEGER,
                
                FOREIGN KEY (post_id) REFERENCES posts (id),
                FOREIGN KEY (prompt_version_hash) REFERENCES prompt_versions (version_hash)
            )
        """)

        # 9. ROI Analytics View - For performance tracking
        cursor.execute("""
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
            FROM lead_qualification_results l
            LEFT JOIN posts p ON l.post_id = p.id
            LEFT JOIN influencers i ON l.influencer_id = i.id
            LEFT JOIN campaigns c ON l.campaign_id = c.id
            GROUP BY c.campaign_name, i.influencer_name, p.post_url
        """)
        
        # Enhanced indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_influencer_id ON posts(influencer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_url ON posts(post_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processing_logs_run_id ON processing_logs(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processing_logs_workflow_step ON processing_logs(workflow_step)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lead_results_run_id ON lead_qualification_results(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lead_results_linkedin_url ON lead_qualification_results(linkedin_url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lead_results_is_qualified ON lead_qualification_results(is_qualified)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lead_results_post_id ON lead_qualification_results(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lead_results_influencer_id ON lead_qualification_results(influencer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lead_results_campaign_id ON lead_qualification_results(campaign_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_qualifications_post_id ON post_qualifications(post_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_qualifications_run_id ON post_qualifications(run_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_qualifications_score ON post_qualifications(overall_score)")
        
        self.db_connection.commit()
        print("✅ Enhanced SQLite tables created with post qualification tracking")
    
    def generate_run_id(self, run_type: str = "batch_processing") -> str:
        """Generate unique run ID for processing session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        self.current_run_id = f"{run_type}_{timestamp}_{unique_id}"
        return self.current_run_id
    
    def hash_content(self, content: Any) -> str:
        """Generate SHA256 hash of content for versioning"""
        if isinstance(content, dict):
            content = json.dumps(content, sort_keys=True)
        elif isinstance(content, list):
            content = json.dumps(content, sort_keys=True)
        else:
            content = str(content)
        
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def register_prompt_version(self, 
                              version_tag: str,
                              prompt_content: str, 
                              tier_definitions: Dict,
                              scoring_rules: Dict,
                              created_by: str = "trinity_collective_intelligence") -> str:
        """Register new prompt version with git-style versioning"""
        
        version_hash = self.hash_content({
            'prompt': prompt_content,
            'tiers': tier_definitions,
            'rules': scoring_rules
        })
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for prompt versioning")
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO prompt_versions 
                (version_hash, version_tag, prompt_content, tier_definitions, scoring_rules, created_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (version_hash, version_tag, prompt_content, 
                 json.dumps(tier_definitions), json.dumps(scoring_rules), created_by))
            
            self.db_connection.commit()
            self.current_prompt_version = version_hash
            print(f"✅ Prompt version registered: {version_tag} ({version_hash})")
            
        except Exception as e:
            print(f"Error registering prompt version: {e}")
            
        return version_hash
    
    def start_processing_run(self, 
                           run_type: str,
                           prompt_version_hash: str,
                           total_leads: int) -> str:
        """Start new processing run with metadata"""
        
        run_id = self.generate_run_id(run_type)
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for processing run tracking")
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO processing_runs 
                (run_id, run_type, prompt_version_hash, total_leads, started_by, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (run_id, run_type, prompt_version_hash, total_leads, 
                 "trinity_collective_intelligence", "running"))
            
            self.db_connection.commit()
            print(f"🚀 Processing run started: {run_id}")
            
        except Exception as e:
            print(f"Error starting processing run: {e}")
            
        return run_id
    
    def log_processing_step(self,
                          workflow_step: str,
                          input_data: Any,
                          output_data: Any,
                          processing_params: Dict,
                          execution_time_ms: int,
                          status: str = "success",
                          error_details: Optional[Dict] = None,
                          leads_processed: int = 0,
                          leads_qualified: int = 0) -> str:
        """Log individual processing step with full provenance"""
        
        log_id = str(uuid.uuid4())
        input_hash = self.hash_content(input_data)
        output_hash = self.hash_content(output_data)
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for processing step logging")
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO processing_logs 
                (id, run_id, workflow_step, prompt_version_hash, input_data_hash, 
                 output_data_hash, processing_params, execution_time_ms, status, 
                 error_details, leads_processed, leads_qualified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (log_id, self.current_run_id, workflow_step, self.current_prompt_version,
                 input_hash, output_hash, json.dumps(processing_params), 
                 execution_time_ms, status, json.dumps(error_details) if error_details else None,
                 leads_processed, leads_qualified))
            
            self.db_connection.commit()
            print(f"📝 Logged: {workflow_step} - {status} ({execution_time_ms}ms)")
            
        except Exception as e:
            print(f"Error logging processing step: {e}")
            
        return log_id
    
    def log_lead_qualification(self,
                             linkedin_url: str,
                             lead_name: str,
                             lead_title: str,
                             lead_company: str,
                             engagement_type: str,
                             llm_model: str,
                             llm_score: int,
                             llm_reasoning: str,
                             tier_classification: str,
                             is_qualified: bool,
                             batch_number: int,
                             processing_order: int,
                             # NEW: Attribution fields for ROI tracking
                             post_url: str = None,
                             post_id: int = None,
                             influencer_id: int = None,
                             campaign_id: int = None,
                             engagement_timestamp: str = None) -> str:
        """Log individual lead qualification result with full provenance"""
        
        result_id = str(uuid.uuid4())
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for lead qualification logging")
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO lead_qualification_results 
                (id, run_id, prompt_version_hash, linkedin_url, lead_name, lead_title, 
                 lead_company, engagement_type, llm_model, llm_score, llm_reasoning, 
                 tier_classification, is_qualified, batch_number, processing_order,
                 post_url, post_id, influencer_id, campaign_id, engagement_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (result_id, self.current_run_id, self.current_prompt_version,
                 linkedin_url, lead_name, lead_title, lead_company, engagement_type,
                 llm_model, llm_score, llm_reasoning, tier_classification, 
                 is_qualified, batch_number, processing_order,
                 post_url, post_id, influencer_id, campaign_id, engagement_timestamp))
            
            self.db_connection.commit()
            status = "✅ QUALIFIED" if is_qualified else "❌ UNQUALIFIED"
            print(f"👤 Logged lead: {lead_name} - {llm_score}/100 {status}")
            
        except Exception as e:
            print(f"Error logging lead qualification: {e}")
            
        return result_id
    
    def complete_processing_run(self, total_qualified: int, qualification_rate: float):
        """Complete processing run with final statistics"""
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for processing run completion")
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE processing_runs 
                SET total_qualified = ?, qualification_rate = ?, 
                    completed_at = CURRENT_TIMESTAMP, status = 'completed'
                WHERE run_id = ?
            """, (total_qualified, qualification_rate, self.current_run_id))
            
            self.db_connection.commit()
            print(f"🎯 Processing run completed: {total_qualified} qualified ({qualification_rate:.1f}%)")
            
        except Exception as e:
            print(f"Error completing processing run: {e}")
    
    def get_processing_history(self, limit: int = 10) -> List[Dict]:
        """Get recent processing run history"""
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for processing history")
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT pr.*, pv.version_tag 
                FROM processing_runs pr
                LEFT JOIN prompt_versions pv ON pr.prompt_version_hash = pv.version_hash
                ORDER BY pr.started_at DESC 
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error getting processing history: {e}")
            return []
    
    def register_post(self, post_url: str, total_reactions: int = 0, 
                     total_comments: int = 0, post_content: str = None,
                     influencer_id: int = None) -> int:
        """Register a post and return its ID"""
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for post registration")
            
        try:
            cursor = self.db_connection.cursor()
            
            # Check if post already exists
            cursor.execute("SELECT id FROM posts WHERE post_url = ?", (post_url,))
            result = cursor.fetchone()
            
            if result:
                return result[0]  # Return existing ID
            
            # Insert new post
            total_engagement = total_reactions + total_comments
            cursor.execute("""
                INSERT INTO posts (post_url, influencer_id, post_content, 
                                 total_reactions, total_comments, total_engagement)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (post_url, influencer_id, post_content, total_reactions, 
                 total_comments, total_engagement))
            
            post_id = cursor.lastrowid
            self.db_connection.commit()
            
            print(f"✅ Post registered: {post_url} (ID: {post_id})")
            return post_id
            
        except Exception as e:
            print(f"Error registering post: {e}")
            return None
    
    def register_influencer(self, influencer_name: str, profile_url: str = None,
                          followers: int = None, industry: str = None,
                          tier: str = "unknown") -> int:
        """Register an influencer and return their ID"""
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for influencer registration")
            
        try:
            cursor = self.db_connection.cursor()
            
            # Check if influencer already exists
            if profile_url:
                cursor.execute("SELECT id FROM influencers WHERE influencer_profile_url = ?", (profile_url,))
            else:
                cursor.execute("SELECT id FROM influencers WHERE influencer_name = ?", (influencer_name,))
            
            result = cursor.fetchone()
            if result:
                return result[0]  # Return existing ID
            
            # Insert new influencer
            cursor.execute("""
                INSERT INTO influencers (influencer_name, influencer_profile_url, 
                                       influencer_followers, influencer_industry, influencer_tier)
                VALUES (?, ?, ?, ?, ?)
            """, (influencer_name, profile_url, followers, industry, tier))
            
            influencer_id = cursor.lastrowid
            self.db_connection.commit()
            
            print(f"✅ Influencer registered: {influencer_name} (ID: {influencer_id})")
            return influencer_id
            
        except Exception as e:
            print(f"Error registering influencer: {e}")
            return None
    
    def get_roi_analytics(self) -> List[Dict]:
        """Get ROI analytics from the view"""
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for ROI analytics")
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM roi_analytics")
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error getting ROI analytics: {e}")
            return []
    
    def log_post_qualification(self, post_id: int, qualification_result: Dict, 
                              processing_time_ms: int) -> int:
        """Log post qualification results to dedicated table"""
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for post qualification logging")
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO post_qualifications 
                (post_id, run_id, prompt_version_hash, overall_score, target_audience_score,
                 topic_relevance_score, lead_quality_score, action_trigger_score,
                 qualification_status, llm_reasoning, key_indicators, recommended_action,
                 llm_model, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id, 
                self.current_run_id, 
                self.current_prompt_version,
                qualification_result.get('overall_score', 0),
                qualification_result.get('target_audience_score', 0),
                qualification_result.get('topic_relevance_score', 0),
                qualification_result.get('lead_quality_score', 0),
                qualification_result.get('action_trigger_score', 0),
                qualification_result.get('qualification', 'UNKNOWN'),
                qualification_result.get('reasoning', ''),
                json.dumps(qualification_result.get('key_indicators', [])),
                qualification_result.get('recommended_action', 'SKIP'),
                qualification_result.get('model_used', 'gpt-4o-mini'),
                processing_time_ms
            ))
            
            qualification_id = cursor.lastrowid
            self.db_connection.commit()
            
            score = qualification_result.get('overall_score', 0)
            status = qualification_result.get('qualification', 'UNKNOWN')
            print(f"📊 Post qualification logged: {score}/100 {status}")
            
            return qualification_id
            
        except Exception as e:
            print(f"Error logging post qualification: {e}")
            return None
    
    def get_qualified_posts(self, threshold: int = 70) -> List[Dict]:
        """Get all posts that meet qualification threshold with full details"""
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for qualified posts query")
            
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    p.id as post_id,
                    p.post_url,
                    p.post_content,
                    p.total_engagement,
                    i.influencer_name,
                    i.influencer_profile_url,
                    pq.overall_score,
                    pq.qualification_status,
                    pq.llm_reasoning,
                    pq.recommended_action,
                    pq.evaluated_at
                FROM posts p
                LEFT JOIN influencers i ON p.influencer_id = i.id
                LEFT JOIN post_qualifications pq ON p.id = pq.post_id
                WHERE pq.overall_score >= ?
                ORDER BY pq.overall_score DESC, p.total_engagement DESC
            """, (threshold,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"Error getting qualified posts: {e}")
            return []
    
    def register_lead(self, name: str, title: str, company: str, linkedin_url: str, 
                     source: str, tags: str = "", post_id: int = None, 
                     engagement_type: str = "unknown", qualification_score: int = 0) -> int:
        """Register a qualified lead in the database - CRITICAL METHOD FOR analyze_engagement_realtime.py"""
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for lead registration")
        
        try:
            cursor = self.db_connection.cursor()
            
            # Ensure leads table exists with Guide's emergency schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id INTEGER,
                    name TEXT,
                    job_title TEXT,
                    company TEXT,
                    profile_url TEXT,
                    profile_urn TEXT,
                    engagement_type TEXT,
                    source_type TEXT,
                    qualification_score INTEGER,
                    qualification_status TEXT,
                    comment_text TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts (id)
                )
            ''')
            
            # Insert the lead
            cursor.execute('''
                INSERT INTO leads (
                    post_id, name, job_title, company, profile_url, 
                    engagement_type, source_type, qualification_score, 
                    qualification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post_id,
                name,
                title,
                company, 
                linkedin_url,
                engagement_type,
                source,
                qualification_score,
                'QUALIFIED' if qualification_score >= 70 else 'NOT_QUALIFIED'
            ))
            
            lead_id = cursor.lastrowid
            self.db_connection.commit()
            
            return lead_id
            
        except Exception as e:
            print(f"❌ Error registering lead {name}: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            raise

# Example usage and testing
if __name__ == "__main__":
    print("🚀 V2 SQLite Logging System - Immediate Testing Ready")
    print("=" * 60)
    
    logger = V2LoggingSystemSQLite()
    logger.connect_database()
    
    # Register Tyler's 4-tier prompt version
    prompt_hash = logger.register_prompt_version(
        version_tag="v2.1.1-disciplined",
        prompt_content="Tyler's disciplined 4-tier buyer classification system...",
        tier_definitions={
            "TIER_1": {"range": "85-90", "description": "CEOs, VPs, Directors"},
            "TIER_2": {"range": "70-84", "description": "GTM teams, RevOps, Growth Marketers"},
            "TIER_3": {"range": "65-75", "description": "Clay Enterprise Partners, AI developers"},
            "TIER_4": {"range": "20-40", "description": "Service providers, copywriters"}
        },
        scoring_rules={
            "scoring_discipline": "Score conservatively - not everyone gets 80-90",
            "qualification_threshold": 70
        }
    )
    
    # Start processing run
    run_id = logger.start_processing_run("sqlite_test", prompt_hash, 5)
    
    # Log processing step
    logger.log_processing_step(
        workflow_step="sqlite_qualification_test",
        input_data={"batch_size": 5, "leads": ["test"]},
        output_data={"qualified": 3, "rate": 60.0},
        processing_params={"model": "gpt-4o-mini", "temperature": 0.3},
        execution_time_ms=2500,
        leads_processed=5,
        leads_qualified=3
    )
    
    # Log sample lead qualification
    logger.log_lead_qualification(
        linkedin_url="https://linkedin.com/in/test-lead",
        lead_name="Test Lead",
        lead_title="VP of Growth",
        lead_company="Test Company",
        engagement_type="reaction",
        llm_model="gpt-4o-mini",
        llm_score=82,
        llm_reasoning="VP role with growth focus - TIER 2 classification",
        tier_classification="TIER_2",
        is_qualified=True,
        batch_number=1,
        processing_order=1
    )
    
    # Complete run
    logger.complete_processing_run(3, 60.0)
    
    print("\n✅ SQLite Logging System Ready for Production Testing!")
    print("🎯 Tyler can now test JSON parsing with real database logging!")
    print("📊 Guide can verify full provenance tracking!")