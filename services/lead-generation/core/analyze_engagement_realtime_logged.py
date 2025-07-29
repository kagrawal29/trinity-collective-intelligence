#!/usr/bin/env python3
"""
Real-time Engagement Analyzer with FULL LOGGING INTEGRATION
Fix for Tyler's Critical Logging Infrastructure Gap
Process LATEST engagement data and store leads with complete audit trail
"""

import json
import os
import sqlite3
import time
import glob
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI
from logging_system_sqlite import V2LoggingSystemSQLite

# Load environment variables
load_dotenv('../.env')

class RealTimeEngagementAnalyzerLogged:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.logger = V2LoggingSystemSQLite()
        self.batch_size = 10  # Process 10 leads at once
        self.run_id = None
        self.prompt_version_hash = None
        
    def initialize_logging(self):
        """Initialize logging system with Tyler's 4-tier prompt version"""
        # Connect to database
        self.logger.connect_database()
        
        # Register Tyler's disciplined 4-tier prompt version
        self.prompt_version_hash = self.logger.register_prompt_version(
            version_tag="tyler-4tier-realtime-v2.1",
            prompt_content="""You are a B2B lead qualifier for lead generation services. Use disciplined 4-tier buyer classification:

TIER 1 - ENTERPRISE BUYERS (Score 85-90): CEOs, VPs, Directors, C-level executives at companies who make purchasing decisions
TIER 2 - GROWTH ROLES (Score 70-84): GTM teams, RevOps, Growth Marketers, Business Development, Sales Managers, Marketing Directors, Appointment Setters
TIER 3 - ENTERPRISE PARTNERS (Score 65-75): Clay Enterprise Partners, consultants at big firms (PwC, etc), AI/automation developers, system integrators
TIER 4 - SERVICE PROVIDERS (Score 20-40): Freelance copywriters, solo consultants, agencies offering lead gen services, ghostwriters, content creators

STRICT SCORING DISCIPLINE:
- Score conservatively - not everyone gets 80-90
- Appointment Setters = TIER 2 (70-75) - They BUY lead generation tools
- Clay Enterprise Partners = TIER 3 (70-75) - They BUY data and automation tools  
- AI/automation developers = TIER 3 (70-75) - They BUY APIs and development tools
- Enterprise security with large user bases = TIER 1 (85-90)
- Investment bankers doing client outreach = TIER 2 (70-75)

DO NOT INFLATE SCORES. Most profiles should be 70-80, very few should get 85-90.""",
            tier_definitions={
                "TIER_1": {"range": "85-90", "description": "C-Level Executives with Budget Authority"},
                "TIER_2": {"range": "70-84", "description": "Growth Roles who Purchase Lead Tools"},
                "TIER_3": {"range": "65-75", "description": "Enterprise Partners who Buy Tools/APIs"},
                "TIER_4": {"range": "20-40", "description": "Service Providers who Sell Services"}
            },
            scoring_rules={
                "conservative_scoring": True,
                "qualification_threshold": 70,
                "tier_1_strict": "Only true C-level executives with budget authority",
                "tier_2_buyers": "Growth roles who actively purchase lead tools"
            },
            created_by="analyze_engagement_realtime_logged"
        )
        
        print(f"✅ Registered prompt version: {self.prompt_version_hash}")
        
    def start_processing_run(self, total_leads: int):
        """Start a new processing run with full logging"""
        self.run_id = self.logger.start_processing_run(
            run_type="realtime_engagement_analysis",
            prompt_version_hash=self.prompt_version_hash,
            total_leads=total_leads,
            started_by="analyze_engagement_realtime_logged"
        )
        
        print(f"🚀 Started processing run: {self.run_id}")
        return self.run_id
        
    def find_latest_engagement_file(self) -> str:
        """Find the most recent engagement file - WITH LOGGING"""
        start_time = time.time()
        
        try:
            pattern = "test_data/engagement_*.json"
            files = glob.glob(pattern)
            
            # Filter out summary files
            engagement_files = [f for f in files if 'summary' not in f]
            
            if not engagement_files:
                raise FileNotFoundError("No engagement files found")
            
            # Sort by modification time, get latest
            latest_file = max(engagement_files, key=os.path.getmtime)
            
            # LOG THE STEP
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.log_processing_step(
                workflow_step="file_discovery",
                input_data={"pattern": pattern, "search_path": "test_data/"},
                output_data={"selected_file": latest_file, "candidates_found": len(engagement_files)},
                processing_params={"filter_criteria": "exclude summary files", "selection_method": "latest_modification_time"},
                execution_time_ms=execution_time_ms,
                status="success"
            )
            
            print(f"📁 Using latest engagement file: {latest_file}")
            return latest_file
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.log_processing_step(
                workflow_step="file_discovery",
                input_data={"pattern": pattern},
                output_data={},
                processing_params={},
                execution_time_ms=execution_time_ms,
                status="error",
                error_details={"error": str(e), "error_type": type(e).__name__}
            )
            raise
    
    def extract_leads_from_new_format(self, data: Dict) -> List[Dict]:
        """Extract leads from NEW engagement data format - WITH LOGGING"""
        start_time = time.time()
        
        try:
            leads = []
            
            # Get post info for context
            post_url = data.get('post_url', '')
            post_details = data.get('post_details', {})
            influencer = post_details.get('influencer', {})
            post_content_preview = post_details.get('post_content', '')[:100] + '...'
            
            print(f"📊 Processing engagement from: {influencer.get('name', 'Unknown')}")
            print(f"📝 Post: {post_content_preview}")
            
            # Process reactions - NEW FORMAT
            reactions = data.get('reactions', [])
            print(f"👍 Processing {len(reactions)} reactions...")
            
            for reaction in reactions:
                # NEW format uses 'title' directly
                name = reaction.get('title', 'Unknown')
                subtitle = reaction.get('subtitle', '')
                url = reaction.get('navigationUrl', '')
                
                # Parse subtitle for title/company
                if '|' in subtitle:
                    parts = subtitle.split('|', 1)
                    title = parts[0].strip()
                    company = parts[1].strip()
                elif 'at ' in subtitle:
                    # Handle "Job Title at Company" format
                    parts = subtitle.split(' at ', 1)
                    title = parts[0].strip()
                    company = parts[1].strip() if len(parts) > 1 else ''
                else:
                    title = subtitle
                    company = ''
                
                leads.append({
                    'name': name,
                    'title': title,
                    'company': company,
                    'linkedin_url': url,
                    'engagement_type': 'reaction',
                    'source': 'reaction',
                    'post_url': post_url,
                    'influencer_name': influencer.get('name', ''),
                    'reaction_type': reaction.get('reactionType', 'LIKE')
                })
            
            # Process comments - NEW FORMAT
            comments = data.get('comments', [])
            print(f"💬 Processing {len(comments)} comments...")
            
            for comment in comments:
                # NEW format uses 'commenter' object
                commenter = comment.get('commenter', {})
                name = commenter.get('title', 'Unknown')
                subtitle = commenter.get('subtitle', '')
                url = commenter.get('navigationUrl', '')
                comment_text = comment.get('text', '')
                
                # Parse subtitle for title/company
                if '|' in subtitle:
                    parts = subtitle.split('|', 1)
                    title = parts[0].strip()
                    company = parts[1].strip()
                elif 'at ' in subtitle:
                    # Handle "Job Title at Company" format
                    parts = subtitle.split(' at ', 1)
                    title = parts[0].strip()
                    company = parts[1].strip() if len(parts) > 1 else ''
                else:
                    title = subtitle
                    company = ''
                
                leads.append({
                    'name': name,
                    'title': title,
                    'company': company,
                    'linkedin_url': url,
                    'engagement_type': 'comment',
                    'source': 'comment',
                    'post_url': post_url,
                    'influencer_name': influencer.get('name', ''),
                    'comment_text': comment_text[:100] + '...' if len(comment_text) > 100 else comment_text
                })
            
            # LOG THE EXTRACTION STEP
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.log_processing_step(
                workflow_step="engagement_extraction",
                input_data={
                    "post_url": post_url,
                    "reactions_count": len(reactions),
                    "comments_count": len(comments),
                    "influencer": influencer.get('name', 'Unknown')
                },
                output_data={
                    "total_leads_extracted": len(leads),
                    "reactions_processed": len(reactions),
                    "comments_processed": len(comments)
                },
                processing_params={
                    "extraction_method": "new_format_parsing",
                    "subtitle_parsing": "pipe_delimiter_and_at_pattern"
                },
                execution_time_ms=execution_time_ms,
                status="success",
                leads_processed=len(leads)
            )
            
            print(f"✅ Extracted {len(leads)} total leads from engagement data")
            return leads
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.log_processing_step(
                workflow_step="engagement_extraction",
                input_data={"data_keys": list(data.keys()) if data else []},
                output_data={},
                processing_params={},
                execution_time_ms=execution_time_ms,
                status="error",
                error_details={"error": str(e), "error_type": type(e).__name__}
            )
            raise
    
    def create_batch_prompt(self, leads: List[Dict]) -> str:
        """Create a single prompt with Tyler's 4-tier buyer classification system"""
        prompt = """You are a B2B lead qualifier for lead generation services. Use disciplined 4-tier buyer classification:

TIER 1 - ENTERPRISE BUYERS (Score 85-90): CEOs, VPs, Directors, C-level executives at companies who make purchasing decisions
TIER 2 - GROWTH ROLES (Score 70-84): GTM teams, RevOps, Growth Marketers, Business Development, Sales Managers, Marketing Directors, Appointment Setters
TIER 3 - ENTERPRISE PARTNERS (Score 65-75): Clay Enterprise Partners, consultants at big firms (PwC, etc), AI/automation developers, system integrators
TIER 4 - SERVICE PROVIDERS (Score 20-40): Freelance copywriters, solo consultants, agencies offering lead gen services, ghostwriters, content creators

STRICT SCORING DISCIPLINE:
- Score conservatively - not everyone gets 80-90
- Appointment Setters = TIER 2 (70-75) - They BUY lead generation tools
- Clay Enterprise Partners = TIER 3 (70-75) - They BUY data and automation tools  
- AI/automation developers = TIER 3 (70-75) - They BUY APIs and development tools
- Enterprise security with large user bases = TIER 1 (85-90)
- Investment bankers doing client outreach = TIER 2 (70-75)

PROFILES TO ANALYZE:
"""
        for i, lead in enumerate(leads, 1):
            prompt += f"""
{i}. Name: {lead['name']}
   Title: {lead['title']}
   Company: {lead['company']}
   Engagement: {lead['engagement_type']}
   Source Post: {lead['influencer_name']} (B2B lead-gen expert)
"""
        
        prompt += """
Return ONLY a JSON array with this exact format:
[
  {
    "profile_index": 1,
    "score": <20-90 based on tier>,
    "reasoning": "<brief explanation with tier classification>",
    "is_qualified": <true if score >= 70>
  },
  ...
]

REMEMBER - STRICT SCORING DISCIPLINE:
- TIER 1 (85-90): Only true C-level executives with budget authority
- TIER 2 (70-84): Growth roles who actively purchase lead tools
- TIER 3 (65-75): Enterprise partners and technical builders who buy tools/APIs
- TIER 4 (20-40): Service providers who sell services

DO NOT INFLATE SCORES. Most profiles should be 70-80, very few should get 85-90."""
        
        return prompt
    
    def process_batch(self, leads_batch: List[Dict], batch_number: int) -> List[Dict]:
        """Process a batch of leads with LLM - WITH FULL LOGGING"""
        start_time = time.time()
        
        try:
            prompt = self.create_batch_prompt(leads_batch)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse response - Tyler found critical bug: OpenAI wraps JSON in markdown blocks
            content = response.choices[0].message.content.strip()
            
            # Remove markdown JSON blocks if present
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.startswith('```'):
                content = content[3:]   # Remove ``` 
            if content.endswith('```'):
                content = content[:-3]  # Remove closing ```
            
            content = content.strip()
            
            try:
                result = json.loads(content)
                scores = result if isinstance(result, list) else result.get('profiles', [])
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed after markdown cleanup: {e}")
                print(f"Raw content: {content[:200]}...")
                raise
            
            # Merge scores with original leads
            qualified_count = 0
            for i, lead in enumerate(leads_batch):
                if i < len(scores):
                    score_data = scores[i]
                    lead['llm_score'] = score_data.get('score', 50)
                    lead['llm_reasoning'] = score_data.get('reasoning', 'Batch processing')
                    lead['is_qualified'] = score_data.get('is_qualified', lead['llm_score'] >= 70)
                    if lead['is_qualified']:
                        qualified_count += 1
                else:
                    # Fallback for missing scores
                    lead['llm_score'] = 50
                    lead['llm_reasoning'] = 'Batch processing incomplete'
                    lead['is_qualified'] = False
            
            # LOG THE BATCH PROCESSING STEP
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.log_processing_step(
                workflow_step=f"llm_batch_processing_{batch_number}",
                input_data={
                    "batch_number": batch_number,
                    "leads_in_batch": len(leads_batch),
                    "prompt_length": len(prompt)
                },
                output_data={
                    "leads_processed": len(leads_batch),
                    "leads_qualified": qualified_count,
                    "qualification_rate": qualified_count / len(leads_batch) * 100,
                    "scores_received": len(scores)
                },
                processing_params={
                    "model": "gpt-4o-mini",
                    "temperature": 0.3,
                    "response_format": "json_object",
                    "tier_system": "tyler_4tier_disciplined"
                },
                execution_time_ms=execution_time_ms,
                status="success",
                leads_processed=len(leads_batch),
                leads_qualified=qualified_count
            )
                    
            return leads_batch
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # LOG THE ERROR
            self.logger.log_processing_step(
                workflow_step=f"llm_batch_processing_{batch_number}",
                input_data={"batch_number": batch_number, "leads_in_batch": len(leads_batch)},
                output_data={},
                processing_params={"model": "gpt-4o-mini"},
                execution_time_ms=execution_time_ms,
                status="error",
                error_details={"error": str(e), "error_type": type(e).__name__},
                leads_processed=len(leads_batch),
                leads_qualified=0
            )
            
            print(f"❌ Batch processing error: {e}")
            # Fallback: basic scoring
            for lead in leads_batch:
                title_lower = lead['title'].lower()
                if any(role in title_lower for role in ['ceo', 'founder', 'vp', 'director']):
                    lead['llm_score'] = 80
                    lead['llm_reasoning'] = 'Leadership role (fallback)'
                    lead['is_qualified'] = True
                else:
                    lead['llm_score'] = 60
                    lead['llm_reasoning'] = 'Standard role (fallback)'
                    lead['is_qualified'] = False
            
            return leads_batch
    
    def store_leads_in_database(self, leads: List[Dict]) -> int:
        """Store processed leads in database - WITH LOGGING"""
        start_time = time.time()
        stored_count = 0
        
        try:
            # Ensure database is connected
            self.logger.connect_database()
            
            qualified_leads = [lead for lead in leads if lead.get('is_qualified', False)]
            
            for lead in qualified_leads:
                try:
                    # Register the lead in the database
                    lead_id = self.logger.register_lead(
                        name=lead['name'],
                        title=lead['title'],
                        company=lead['company'],
                        linkedin_url=lead['linkedin_url'],
                        source=f"{lead['engagement_type']} on {lead['influencer_name']} post",
                        tags=f"score:{lead['llm_score']},tier:qualified,engagement:{lead['engagement_type']}",
                        qualification_score=lead['llm_score'],
                        engagement_type=lead['engagement_type']
                    )
                    
                    print(f"✅ Stored lead {lead_id}: {lead['name']} - {lead['title']} (Score: {lead['llm_score']})")
                    stored_count += 1
                    
                except Exception as e:
                    print(f"❌ Failed to store lead {lead['name']}: {e}")
            
            # LOG THE STORAGE STEP
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.log_processing_step(
                workflow_step="lead_database_storage",
                input_data={
                    "total_leads": len(leads),
                    "qualified_leads": len(qualified_leads),
                    "qualification_threshold": 70
                },
                output_data={
                    "leads_stored": stored_count,
                    "storage_success_rate": stored_count / len(qualified_leads) * 100 if qualified_leads else 0
                },
                processing_params={
                    "storage_method": "register_lead",
                    "qualification_filter": "score >= 70"
                },
                execution_time_ms=execution_time_ms,
                status="success",
                leads_processed=len(qualified_leads),
                leads_qualified=stored_count
            )
            
            return stored_count
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.logger.log_processing_step(
                workflow_step="lead_database_storage",
                input_data={"total_leads": len(leads)},
                output_data={"leads_stored": stored_count},
                processing_params={},
                execution_time_ms=execution_time_ms,
                status="error",
                error_details={"error": str(e), "error_type": type(e).__name__}
            )
            raise

def main():
    """Run real-time engagement analysis with FULL LOGGING - FIXES TYLER'S CRITICAL GAP!"""
    
    print("🚨 REAL-TIME ENGAGEMENT ANALYZER - WITH FULL LOGGING INTEGRATION!")
    print("=== FIXING TYLER'S CRITICAL LOGGING INFRASTRUCTURE GAP ===")
    print("=" * 80)
    
    analyzer = RealTimeEngagementAnalyzerLogged()
    
    try:
        # Initialize logging system
        analyzer.initialize_logging()
        
        # Find and load latest engagement file
        latest_file = analyzer.find_latest_engagement_file()
        
        with open(latest_file, 'r') as f:
            data = json.load(f)
        
        # Extract leads using new format
        leads = analyzer.extract_leads_from_new_format(data)
        
        if not leads:
            print("❌ No leads found in engagement data")
            return
        
        # Start processing run
        analyzer.start_processing_run(len(leads))
        
        print(f"\n🎯 BATCH LLM ANALYSIS WITH FULL LOGGING")
        print(f"Total leads to process: {len(leads)}")
        print(f"Batch size: {analyzer.batch_size} leads per API call")
        print("=" * 60)
        
        processed_leads = []
        
        # Process in batches
        for i in range(0, len(leads), analyzer.batch_size):
            batch = leads[i:i + analyzer.batch_size]
            batch_num = (i // analyzer.batch_size) + 1
            total_batches = (len(leads) + analyzer.batch_size - 1) // analyzer.batch_size
            
            print(f"\n🤖 Processing batch {batch_num}/{total_batches} ({len(batch)} leads)...")
            
            start_time = time.time()
            processed_batch = analyzer.process_batch(batch, batch_num)
            batch_time = time.time() - start_time
            
            processed_leads.extend(processed_batch)
            
            print(f"✅ Batch {batch_num} completed in {batch_time:.1f}s")
        
        # Store qualified leads in database
        qualified_leads = [lead for lead in processed_leads if lead.get('is_qualified', False)]
        qualification_rate = len(qualified_leads) / len(processed_leads) * 100
        
        print(f"\n💾 STORING QUALIFIED LEADS IN DATABASE...")
        stored_count = analyzer.store_leads_in_database(qualified_leads)
        
        # Complete the processing run
        analyzer.logger.complete_processing_run(
            total_qualified=stored_count,
            qualification_rate=qualification_rate
        )
        
        # Save analysis results
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        final_results = {
            'analysis_timestamp': timestamp,
            'run_id': analyzer.run_id,
            'prompt_version_hash': analyzer.prompt_version_hash,
            'source_file': latest_file,
            'model_used': 'gpt-4o-mini',
            'total_leads': len(processed_leads),
            'qualified_leads': len(qualified_leads),
            'stored_in_database': stored_count,
            'qualification_rate': qualification_rate,
            'logging_complete': True,
            'leads': processed_leads,
            'qualified_only': qualified_leads
        }
        
        output_file = f"test_data/realtime_analysis_logged_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(final_results, f, indent=2)
        
        print(f"\n🎉 LOGGING INFRASTRUCTURE FIXED! FINAL RESULTS:")
        print(f"📊 Total Leads: {len(processed_leads)}")
        print(f"🎯 Qualified Leads: {len(qualified_leads)}")
        print(f"💾 Stored in Database: {stored_count}")
        print(f"📈 Qualification Rate: {qualification_rate:.1f}%")
        print(f"🔧 Run ID: {analyzer.run_id}")
        print(f"📝 All steps logged to processing_logs table!")
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Show top qualified leads
        qualified_sorted = sorted(qualified_leads, key=lambda x: x.get('llm_score', 0), reverse=True)
        print(f"\n🏆 TOP 5 QUALIFIED LEADS STORED:")
        for i, lead in enumerate(qualified_sorted[:5], 1):
            print(f"{i}. {lead['name']} - {lead['title']}")
            print(f"   Company: {lead['company']}")
            print(f"   Score: {lead.get('llm_score', 0)}/100")
            print(f"   Reason: {lead.get('llm_reasoning', 'N/A')}")
        
        print("\n✅ TYLER'S LOGGING INFRASTRUCTURE GAP RESOLVED!")
        print("📋 Check processing_logs table for complete audit trail!")
        
    except Exception as e:
        print(f"❌ Real-time analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()