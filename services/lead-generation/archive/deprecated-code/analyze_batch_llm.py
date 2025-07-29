#!/usr/bin/env python3
"""
Batch LLM Analysis with Incremental Storage
Process leads in batches and save results immediately
"""

import json
import os
import time
from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv('../.env')

class BatchLLMAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.batch_size = 10  # Process 10 leads at once
        
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
    
    def process_batch(self, leads_batch: List[Dict]) -> List[Dict]:
        """Process a batch of leads with LLM"""
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
            for i, lead in enumerate(leads_batch):
                if i < len(scores):
                    score_data = scores[i]
                    lead['llm_score'] = score_data.get('score', 50)
                    lead['llm_reasoning'] = score_data.get('reasoning', 'Batch processing')
                    lead['is_qualified'] = score_data.get('is_qualified', lead['llm_score'] >= 70)
                else:
                    # Fallback for missing scores
                    lead['llm_score'] = 50
                    lead['llm_reasoning'] = 'Batch processing incomplete'
                    lead['is_qualified'] = False
                    
            return leads_batch
            
        except Exception as e:
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
    """Run batch LLM analysis with incremental storage"""
    
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
    
    print(f"🎯 BATCH LLM ANALYSIS")
    print(f"Total leads to process: {len(leads)}")
    print(f"Batch size: 10 leads per API call")
    print("=" * 60)
    
    analyzer = BatchLLMAnalyzer()
    processed_leads = []
    
    # Process in batches
    for i in range(0, len(leads), analyzer.batch_size):
        batch = leads[i:i + analyzer.batch_size]
        batch_num = (i // analyzer.batch_size) + 1
        total_batches = (len(leads) + analyzer.batch_size - 1) // analyzer.batch_size
        
        print(f"\n🤖 Processing batch {batch_num}/{total_batches} ({len(batch)} leads)...")
        
        start_time = time.time()
        processed_batch = analyzer.process_batch(batch)
        batch_time = time.time() - start_time
        
        processed_leads.extend(processed_batch)
        
        print(f"✅ Batch {batch_num} completed in {batch_time:.1f}s")
        
        # Save progress immediately
        progress_file = f"test_data/llm_progress_batch_{batch_num}.json"
        with open(progress_file, 'w') as f:
            json.dump(processed_batch, f, indent=2)
        
        print(f"💾 Progress saved to {progress_file}")
    
    # Generate final results
    qualified_leads = [lead for lead in processed_leads if lead.get('is_qualified', False)]
    qualification_rate = len(qualified_leads) / len(processed_leads) * 100
    
    final_results = {
        'analysis_timestamp': time.strftime('%Y%m%d_%H%M%S'),
        'model_used': 'gpt-4o-mini',
        'total_leads': len(processed_leads),
        'qualified_leads': len(qualified_leads),
        'qualification_rate': qualification_rate,
        'batch_processing': True,
        'leads': processed_leads,
        'qualified_only': qualified_leads
    }
    
    # Save final results
    output_file = f"test_data/batch_llm_results_{time.strftime('%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"Total Leads: {len(processed_leads)}")
    print(f"Qualified Leads: {len(qualified_leads)}")
    print(f"Qualification Rate: {qualification_rate:.1f}%")
    print(f"Model Used: gpt-4o-mini")
    print(f"Processing Method: Batch (10 leads per call)")
    
    print(f"\n💾 Final results saved to: {output_file}")
    print("✅ BATCH ANALYSIS COMPLETE!")
    
    # Show top qualified leads
    qualified_sorted = sorted(qualified_leads, key=lambda x: x.get('llm_score', 0), reverse=True)
    print(f"\n🏆 TOP 5 QUALIFIED LEADS:")
    for i, lead in enumerate(qualified_sorted[:5], 1):
        print(f"{i}. {lead['name']} - {lead['title']}")
        print(f"   Score: {lead.get('llm_score', 0)}/100")
        print(f"   Reason: {lead.get('llm_reasoning', 'N/A')}")

if __name__ == "__main__":
    main()