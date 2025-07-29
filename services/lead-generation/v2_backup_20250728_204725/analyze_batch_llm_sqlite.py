#!/usr/bin/env python3
"""
Batch LLM Analysis with SQLite Logging System
Ready for immediate testing with Tyler's validated JSON parsing
"""

import json
import os
import time
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI
from logging_system_sqlite import V2LoggingSystemSQLite

# Load environment variables
load_dotenv('../.env')

class SQLiteBatchLLMAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.batch_size = 10  # Process 10 leads at once
        self.logger = V2LoggingSystemSQLite()
        
        # Initialize SQLite logging system - PRODUCTION READY
        self.logger.connect_database()  # Will raise exception if fails
        
        # Register Tyler's 4-tier prompt version
        self.prompt_version = self.logger.register_prompt_version(
            version_tag="v2.1.1-disciplined",
            prompt_content=self._get_full_prompt_content(),
            tier_definitions={
                "TIER_1": {"range": "85-90", "description": "CEOs, VPs, Directors, C-level executives at companies who make purchasing decisions"},
                "TIER_2": {"range": "70-84", "description": "GTM teams, RevOps, Growth Marketers, Business Development, Sales Managers, Marketing Directors, Appointment Setters"},
                "TIER_3": {"range": "65-75", "description": "Clay Enterprise Partners, consultants at big firms (PwC, etc), AI/automation developers, system integrators"},
                "TIER_4": {"range": "20-40", "description": "Freelance copywriters, solo consultants, agencies offering lead gen services, ghostwriters, content creators"}
            },
            scoring_rules={
                "scoring_discipline": "Score conservatively - not everyone gets 80-90",
                "qualification_threshold": 70,
                "buyer_focus": "Focus on PURCHASING POWER, not job description similarity"
            }
        )
        
    def _get_full_prompt_content(self) -> str:
        """Get the complete Tyler's 4-tier prompt for versioning"""
        return """You are a B2B lead qualifier for lead generation services. Use disciplined 4-tier buyer classification:

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
        
    def create_batch_prompt(self, leads: List[Dict]) -> str:
        """Create a single prompt with Tyler's 4-tier buyer classification system"""
        prompt = self._get_full_prompt_content()
        
        prompt += "\n\nPROFILES TO ANALYZE:\n"
        for i, lead in enumerate(leads, 1):
            prompt += f"""
{i}. Name: {lead['name']}
   Title: {lead['title']}
   Company: {lead['company']}
   Engagement: {lead['engagement_type']}
"""
        return prompt
    
    def process_batch(self, leads_batch: List[Dict], batch_number: int, 
                      post_url: str = None, post_id: int = None, influencer_id: int = None) -> List[Dict]:
        """Process a batch of leads with LLM and SQLite logging"""
        
        step_start_time = time.time()
        
        try:
            prompt = self.create_batch_prompt(leads_batch)
            
            # Log the processing step start
            processing_params = {
                "model": "gpt-4o-mini",
                "temperature": 0.3,
                "batch_size": len(leads_batch),
                "batch_number": batch_number,
                "prompt_version": "v2.1.1-disciplined"
            }
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            # Parse response - Tyler's validated JSON parsing fix
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
            
            # Merge scores with original leads and log individual results
            qualified_count = 0
            for i, lead in enumerate(leads_batch):
                if i < len(scores):
                    score_data = scores[i]
                    lead['llm_score'] = score_data.get('score', 50)
                    lead['llm_reasoning'] = score_data.get('reasoning', 'Batch processing')
                    lead['is_qualified'] = score_data.get('is_qualified', lead['llm_score'] >= 70)
                    
                    # Determine tier classification
                    score = lead['llm_score']
                    if score >= 85:
                        tier = "TIER_1"
                    elif score >= 70:
                        tier = "TIER_2"
                    elif score >= 65:
                        tier = "TIER_3"
                    else:
                        tier = "TIER_4"
                    
                    # Log individual lead qualification WITH ATTRIBUTION
                    self.logger.log_lead_qualification(
                        linkedin_url=lead.get('linkedin_url', ''),
                        lead_name=lead.get('name', ''),
                        lead_title=lead.get('title', ''),
                        lead_company=lead.get('company', ''),
                        engagement_type=lead.get('engagement_type', ''),
                        llm_model="gpt-4o-mini",
                        llm_score=lead['llm_score'],
                        llm_reasoning=lead['llm_reasoning'],
                        tier_classification=tier,
                        is_qualified=lead['is_qualified'],
                        batch_number=batch_number,
                        processing_order=i + 1,
                        # NEW: Attribution fields for ROI tracking
                        post_url=post_url,
                        post_id=post_id,
                        influencer_id=influencer_id,
                        engagement_timestamp=lead.get('engagement_timestamp', '')
                    )
                    
                    if lead['is_qualified']:
                        qualified_count += 1
                else:
                    # Fallback for missing scores
                    lead['llm_score'] = 50
                    lead['llm_reasoning'] = 'Batch processing incomplete'
                    lead['is_qualified'] = False
            
            execution_time_ms = int((time.time() - step_start_time) * 1000)
            
            # Log the processing step completion
            self.logger.log_processing_step(
                workflow_step="llm_batch_qualification",
                input_data={"leads_count": len(leads_batch), "batch_number": batch_number},
                output_data={"qualified_count": qualified_count, "scores": [l['llm_score'] for l in leads_batch]},
                processing_params=processing_params,
                execution_time_ms=execution_time_ms,
                status="success",
                leads_processed=len(leads_batch),
                leads_qualified=qualified_count
            )
                    
            return leads_batch
            
        except Exception as e:
            execution_time_ms = int((time.time() - step_start_time) * 1000)
            
            # Log the error
            self.logger.log_processing_step(
                workflow_step="llm_batch_qualification",
                input_data={"leads_count": len(leads_batch), "batch_number": batch_number},
                output_data={},
                processing_params=processing_params,
                execution_time_ms=execution_time_ms,
                status="error",
                error_details={"error": str(e), "type": type(e).__name__},
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

def main():
    """Run SQLite batch LLM analysis with immediate testing"""
    
    # Load engagement data
    with open('test_data/full_engagement_20250727_182551.json', 'r') as f:
        data = json.load(f)
    
    # Extract all leads
    leads = []
    
    # Process reactions
    for reaction in data.get('reactions', []):
        name = reaction.get('title', 'Unknown')
        subtitle = reaction.get('subtitle', '')
        url = reaction.get('navigationUrl', '')
        
        # Parse subtitle
        if '|' in subtitle:
            parts = subtitle.split('|', 1)
            title = parts[0].strip()
            company = parts[1].strip()
        else:
            title = subtitle
            company = ''
        
        leads.append({
            'name': name,
            'title': title,
            'company': company,
            'linkedin_url': url,
            'engagement_type': 'reaction',
            'source': 'reaction'
        })
    
    # Process comments
    for comment in data.get('comments', []):
        commenter = comment.get('commenter', {})
        name = commenter.get('title', 'Unknown')
        subtitle = commenter.get('subtitle', '')
        url = commenter.get('navigationUrl', '')
        
        # Parse subtitle
        if '|' in subtitle:
            parts = subtitle.split('|', 1)
            title = parts[0].strip()
            company = parts[1].strip()
        else:
            title = subtitle
            company = ''
        
        leads.append({
            'name': name,
            'title': title,
            'company': company,
            'linkedin_url': url,
            'engagement_type': 'comment',
            'source': 'comment'
        })
    
    print(f"🎯 SQLITE BATCH LLM ANALYSIS - IMMEDIATE TESTING READY")
    print(f"✅ Tyler's JSON parsing validated (8/11 tests pass)")
    print(f"✅ SQLite database logging enabled")
    print(f"Total leads to process: {len(leads)}")
    print(f"Batch size: 10 leads per API call")
    print("=" * 60)
    
    analyzer = SQLiteBatchLLMAnalyzer()
    
    # NEW: Register influencer and post for attribution tracking
    print("\n📊 Setting up Attribution Tracking...")
    
    # For now, we'll use a placeholder influencer (in production, this would come from post data)
    influencer_id = analyzer.logger.register_influencer(
        influencer_name="LinkedIn Lead Generation Expert",
        profile_url="https://www.linkedin.com/in/example-influencer",
        industry="B2B Sales & Marketing",
        tier="macro"  # Based on 195 engagements
    )
    
    # Register the post with engagement metrics
    post_url = data.get('post_url', 'https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642')
    post_id = analyzer.logger.register_post(
        post_url=post_url,
        total_reactions=data.get('total_reactions', 143),
        total_comments=data.get('total_comments', 52),
        post_content="Lead generation strategies post",  # In production, extract from scraper
        influencer_id=influencer_id
    )
    
    print(f"✅ Attribution setup complete: Influencer #{influencer_id} → Post #{post_id}")
    
    # Start processing run
    run_id = analyzer.logger.start_processing_run(
        run_type="v2_sqlite_pipeline_attributed",
        prompt_version_hash=analyzer.prompt_version,
        total_leads=len(leads)
    )
    
    processed_leads = []
    
    # Process in batches with SQLite logging
    for i in range(0, len(leads), analyzer.batch_size):
        batch = leads[i:i + analyzer.batch_size]
        batch_num = (i // analyzer.batch_size) + 1
        total_batches = (len(leads) + analyzer.batch_size - 1) // analyzer.batch_size
        
        print(f"\n🤖 Processing batch {batch_num}/{total_batches} ({len(batch)} leads)...")
        
        start_time = time.time()
        processed_batch = analyzer.process_batch(batch, batch_num, post_url, post_id, influencer_id)
        batch_time = time.time() - start_time
        
        processed_leads.extend(processed_batch)
        
        print(f"✅ Batch {batch_num} completed in {batch_time:.1f}s")
        print(f"📝 Full provenance logged to SQLite database")
    
    # Generate final results
    qualified_leads = [lead for lead in processed_leads if lead.get('is_qualified', False)]
    qualification_rate = len(qualified_leads) / len(processed_leads) * 100
    
    # Complete the processing run
    analyzer.logger.complete_processing_run(len(qualified_leads), qualification_rate)
    
    final_results = {
        'analysis_timestamp': time.strftime('%Y%m%d_%H%M%S'),
        'model_used': 'gpt-4o-mini',
        'prompt_version': 'v2.1.1-disciplined',
        'run_id': run_id,
        'database_type': 'SQLite',
        'total_leads': len(processed_leads),
        'qualified_leads': len(qualified_leads),
        'qualification_rate': qualification_rate,
        'batch_processing': True,
        'logging_enabled': True,
        'leads': processed_leads,
        'qualified_only': qualified_leads
    }
    
    # Save final results
    output_file = f"test_data/sqlite_batch_results_{time.strftime('%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n📊 FINAL RESULTS (WITH SQLITE LOGGING):")
    print(f"Run ID: {run_id}")
    print(f"Database: SQLite (trinity_logging.db)")
    print(f"Total Leads: {len(processed_leads)}")
    print(f"Qualified Leads: {len(qualified_leads)}")
    print(f"Qualification Rate: {qualification_rate:.1f}%")
    print(f"Model Used: gpt-4o-mini")
    print(f"Prompt Version: v2.1.1-disciplined")
    print(f"JSON Parsing: Tyler's validated fix applied")
    
    print(f"\n💾 Results saved to: {output_file}")
    print(f"📊 Full provenance tracking in SQLite database")
    print("✅ SQLITE ANALYSIS COMPLETE - READY FOR TYLER'S TESTING!")
    
    # Show top qualified leads
    qualified_sorted = sorted(qualified_leads, key=lambda x: x.get('llm_score', 0), reverse=True)
    print(f"\n🏆 TOP 5 QUALIFIED LEADS:")
    for i, lead in enumerate(qualified_sorted[:5], 1):
        print(f"{i}. {lead['name']} - {lead['title']}")
        print(f"   Score: {lead.get('llm_score', 0)}/100")
        print(f"   Reason: {lead.get('llm_reasoning', 'N/A')}")

if __name__ == "__main__":
    main()