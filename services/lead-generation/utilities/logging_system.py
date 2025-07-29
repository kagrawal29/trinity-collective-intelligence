#!/usr/bin/env python3
"""
V2 Lead Generation - Phase 1 Logging System
Guide's Vision: Comprehensive logging with prompt versioning and provenance tracking
"""

import hashlib
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class V2LoggingSystem:
    """Phase 1 Logging System with Guide's architectural vision"""
    
    def __init__(self):
        self.db_connection = None
        self.current_run_id = None
        self.current_prompt_version = None
        
    def connect_database(self):
        """Connect to PostgreSQL database - PRODUCTION ONLY"""
        try:
            self.db_connection = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'lead_generation_v2'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                cursor_factory=RealDictCursor
            )
            print("✅ Connected to production PostgreSQL database")
            return True
        except Exception as e:
            print(f"❌ CRITICAL: Database connection failed: {e}")
            print("❌ Cannot proceed without database connection")
            raise Exception(f"Database connection required for production operation: {e}")
    
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
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO prompt_versions 
                    (version_hash, version_tag, prompt_content, tier_definitions, scoring_rules, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (version_hash) DO NOTHING
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
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO processing_runs 
                    (run_id, run_type, prompt_version_hash, total_leads, started_by, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
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
        
        log_entry = {
            'id': log_id,
            'run_id': self.current_run_id,
            'workflow_step': workflow_step,
            'prompt_version_hash': self.current_prompt_version,
            'input_data_hash': input_hash,
            'output_data_hash': output_hash,
            'processing_params': processing_params,
            'execution_time_ms': execution_time_ms,
            'status': status,
            'error_details': error_details,
            'leads_processed': leads_processed,
            'leads_qualified': leads_qualified,
            'timestamp': datetime.now().isoformat()
        }
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for processing step logging")
            
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO processing_logs 
                    (id, run_id, workflow_step, prompt_version_hash, input_data_hash, 
                     output_data_hash, processing_params, execution_time_ms, status, 
                     error_details, leads_processed, leads_qualified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                             processing_order: int) -> str:
        """Log individual lead qualification result with full provenance"""
        
        result_id = str(uuid.uuid4())
        
        if not self.db_connection:
            raise Exception("❌ CRITICAL: Database connection required for lead qualification logging")
            
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO lead_qualification_results 
                    (id, run_id, prompt_version_hash, linkedin_url, lead_name, lead_title, 
                     lead_company, engagement_type, llm_model, llm_score, llm_reasoning, 
                     tier_classification, is_qualified, batch_number, processing_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (result_id, self.current_run_id, self.current_prompt_version,
                     linkedin_url, lead_name, lead_title, lead_company, engagement_type,
                     llm_model, llm_score, llm_reasoning, tier_classification, 
                     is_qualified, batch_number, processing_order))
                
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
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE processing_runs 
                    SET total_qualified = %s, qualification_rate = %s, 
                        completed_at = NOW(), status = 'completed'
                    WHERE run_id = %s
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
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT pr.*, pv.version_tag 
                    FROM processing_runs pr
                    LEFT JOIN prompt_versions pv ON pr.prompt_version_hash = pv.version_hash
                    ORDER BY pr.started_at DESC 
                    LIMIT %s
                """, (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error getting processing history: {e}")
            return []

# Example usage for Guide's review
if __name__ == "__main__":
    print("🚀 V2 Logging System - Phase 1 Demo")
    print("=" * 50)
    
    logger = V2LoggingSystem()
    
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
    run_id = logger.start_processing_run("demo_run", prompt_hash, 10)
    
    # Log processing step
    logger.log_processing_step(
        workflow_step="llm_qualification",
        input_data={"batch_size": 10, "leads": ["demo"]},
        output_data={"qualified": 7, "rate": 70.0},
        processing_params={"model": "gpt-4o-mini", "temperature": 0.3},
        execution_time_ms=5000,
        leads_processed=10,
        leads_qualified=7
    )
    
    # Complete run
    logger.complete_processing_run(7, 70.0)
    
    print("\n✅ Phase 1 Logging System Demo Complete!")
    print("Ready for Guide's orchestration and Tyler's chaos testing!")