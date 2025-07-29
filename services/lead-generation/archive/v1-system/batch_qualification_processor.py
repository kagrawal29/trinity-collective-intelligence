#!/usr/bin/env python3
"""
Batch Lead Qualification Processor
Processes multiple leads from CSV and updates results directly in the file
"""

import csv
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List
import hashlib
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BatchQualificationProcessor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.cache_dir = 'profile_cache'
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        # Load service description
        with open('our-service-description.md', 'r') as f:
            self.service_description = f.read()
    
    def get_profile_cache_path(self, linkedin_url: str) -> str:
        """Generate cache filename based on LinkedIn URL"""
        url_hash = hashlib.md5(linkedin_url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.json")
    
    def fetch_linkedin_profile(self, linkedin_url: str) -> Dict[str, Any]:
        """Fetch LinkedIn profile with caching"""
        cache_path = self.get_profile_cache_path(linkedin_url)
        
        # Check cache first
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
                if cached_data.get('cached_at') and \
                   (time.time() - cached_data['cached_at']) < 86400:  # 24 hour cache
                    print(f"  Using cached profile")
                    return cached_data['data']
        
        # Fetch from API
        print(f"  Fetching profile from API...")
        import requests
        
        response = requests.post(
            "https://linkedin-data-scraper.p.rapidapi.com/person",
            headers={
                "Content-Type": "application/json",
                "x-rapidapi-host": "linkedin-data-scraper.p.rapidapi.com",
                "x-rapidapi-key": self.rapidapi_key
            },
            json={"link": linkedin_url}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                # Cache the successful response
                cache_data = {
                    'data': data['data'],
                    'cached_at': time.time()
                }
                with open(cache_path, 'w') as f:
                    json.dump(cache_data, f)
                return data['data']
        
        return None
    
    def analyze_decision_maker(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """LLM analysis for decision maker status"""
        prompt = f"""Based on the following LinkedIn profile data, determine if this person is a decision maker who could purchase our lead generation service.

Our Service: We provide an AI-powered lead generation platform for outbound sales teams to automate prospect research and qualification.

Profile Data:
- Name: {profile.get('fullName', 'Unknown')}
- Headline: {profile.get('headline', '')}
- Current Role: {profile.get('experiences', [{}])[0].get('title', '') if profile.get('experiences') else 'Unknown'}
- About: {profile.get('about', '')[:500]}

Analyze and return JSON with:
1. "is_decision_maker": true/false
2. "reasoning": brief explanation (max 100 chars)
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def analyze_competitor(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """LLM analysis for competitor status"""
        experiences_text = ""
        for exp in profile.get('experiences', [])[:3]:
            experiences_text += f"\n- {exp.get('title', '')} at {exp.get('subtitle', '')}"
        
        prompt = f"""Analyze if this person or their company is a competitor for our lead generation service.

Our Service: AI-powered lead generation platform for outbound sales teams.

Profile:
- Name: {profile.get('fullName', '')}
- Headline: {profile.get('headline', '')}
- Experience: {experiences_text[:500]}

Return JSON with:
1. "is_competitor": true/false
2. "reasoning": brief explanation (max 100 chars)
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def analyze_influencer(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """LLM analysis for influencer status"""
        post_count = len(profile.get('updates', []))
        
        prompt = f"""Determine if this person is an influencer (regular content creator with high engagement).

Profile:
- Followers: {profile.get('followers', 0):,}
- Recent Posts: {post_count}

Influencer criteria:
- Posts 2+ times/week (8+ posts/month)
- 10k+ followers preferred
- High engagement

Return JSON with:
1. "influencer_score": 0-100 (70+ = influencer)
2. "reasoning": brief explanation (max 100 chars)
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def process_lead(self, row: Dict[str, str]) -> Dict[str, str]:
        """Process a single lead and return updated row"""
        print(f"\nProcessing: {row['title']} - {row['subtitle']}")
        
        # Extract LinkedIn URL
        linkedin_url = row.get('navigationUrl', '')
        if not linkedin_url or 'linkedin.com/in/' not in linkedin_url:
            print("  ⚠️  No valid LinkedIn URL found")
            row.update({
                'decision_maker': 'ERROR',
                'decision_maker_reason': 'No LinkedIn URL',
                'competitor': 'ERROR',
                'competitor_reason': 'No LinkedIn URL',
                'influencer_score': 'ERROR',
                'influencer_reason': 'No LinkedIn URL',
                'qualified': 'FALSE',
                'qualification_summary': 'Cannot process without LinkedIn profile',
                'disqualification_reason': 'No valid LinkedIn URL'
            })
            return row
        
        # Fetch profile
        profile = self.fetch_linkedin_profile(linkedin_url)
        if not profile:
            print("  ⚠️  Failed to fetch profile")
            row.update({
                'decision_maker': 'ERROR',
                'decision_maker_reason': 'Profile fetch failed',
                'competitor': 'ERROR',
                'competitor_reason': 'Profile fetch failed',
                'influencer_score': 'ERROR',
                'influencer_reason': 'Profile fetch failed',
                'qualified': 'FALSE',
                'qualification_summary': 'Failed to fetch LinkedIn profile',
                'disqualification_reason': 'Profile fetch error'
            })
            return row
        
        # Analyze
        try:
            dm_analysis = self.analyze_decision_maker(profile)
            comp_analysis = self.analyze_competitor(profile)
            inf_analysis = self.analyze_influencer(profile)
            
            # Determine qualification
            is_dm = dm_analysis.get('is_decision_maker', False)
            is_comp = comp_analysis.get('is_competitor', False)
            inf_score = inf_analysis.get('influencer_score', 0)
            is_qualified = is_dm and not is_comp and inf_score < 70
            
            # Build disqualification reasons
            disqual_reasons = []
            if not is_dm:
                disqual_reasons.append("Not a decision maker")
            if is_comp:
                disqual_reasons.append("Competitor")
            if inf_score >= 70:
                disqual_reasons.append(f"Influencer (score: {inf_score})")
            
            # Update row
            row.update({
                'decision_maker': 'TRUE' if is_dm else 'FALSE',
                'decision_maker_reason': dm_analysis.get('reasoning', '')[:100],
                'competitor': 'TRUE' if is_comp else 'FALSE',
                'competitor_reason': comp_analysis.get('reasoning', '')[:100],
                'influencer_score': str(inf_score),
                'influencer_reason': inf_analysis.get('reasoning', '')[:100],
                'qualified': 'TRUE' if is_qualified else 'FALSE',
                'qualification_summary': f"DM:{is_dm}, Comp:{is_comp}, Inf:{inf_score} - {'Qualified' if is_qualified else 'Not qualified'}",
                'disqualification_reason': '; '.join(disqual_reasons) if disqual_reasons else 'N/A'
            })
            
            print(f"  ✅ Qualified: {'YES' if is_qualified else 'NO'}")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            row.update({
                'decision_maker': 'ERROR',
                'decision_maker_reason': str(e)[:50],
                'competitor': 'ERROR',
                'competitor_reason': str(e)[:50],
                'influencer_score': 'ERROR',
                'influencer_reason': str(e)[:50],
                'qualified': 'FALSE',
                'qualification_summary': 'Analysis error',
                'disqualification_reason': f'Error: {str(e)[:50]}'
            })
        
        return row
    
    def process_csv(self, input_file: str, output_file: str = None, limit: int = None):
        """Process leads from CSV file"""
        if output_file is None:
            output_file = input_file.replace('.csv', '_qualified.csv')
        
        # Read existing data
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames
        
        # Add new fields if not present
        new_fields = [
            'decision_maker', 'decision_maker_reason',
            'competitor', 'competitor_reason',
            'influencer_score', 'influencer_reason',
            'qualified', 'qualification_summary', 'disqualification_reason'
        ]
        
        for field in new_fields:
            if field not in fieldnames:
                fieldnames.append(field)
        
        # Process leads
        processed_rows = []
        total = min(len(rows), limit) if limit else len(rows)
        
        print(f"Processing {total} leads...")
        print("="*50)
        
        for i, row in enumerate(rows[:total]):
            processed_row = self.process_lead(row)
            processed_rows.append(processed_row)
            
            # Save progress every 10 leads
            if (i + 1) % 10 == 0:
                self.save_progress(output_file, fieldnames, processed_rows, rows[total:])
                print(f"\n💾 Progress saved: {i+1}/{total} leads processed")
            
            # Rate limiting
            time.sleep(1)  # Avoid hitting API limits
        
        # Final save
        self.save_progress(output_file, fieldnames, processed_rows, rows[total:])
        
        # Summary
        qualified_count = sum(1 for r in processed_rows if r.get('qualified') == 'TRUE')
        print(f"\n{'='*50}")
        print(f"PROCESSING COMPLETE")
        print(f"Total processed: {len(processed_rows)}")
        print(f"Qualified leads: {qualified_count} ({qualified_count/len(processed_rows)*100:.1f}%)")
        print(f"Results saved to: {output_file}")
    
    def save_progress(self, output_file: str, fieldnames: List[str], 
                     processed_rows: List[Dict], remaining_rows: List[Dict]):
        """Save current progress to file"""
        all_rows = processed_rows + remaining_rows
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch process lead qualification')
    parser.add_argument('--input', default='leads.csv', help='Input CSV file')
    parser.add_argument('--output', help='Output CSV file (default: input_qualified.csv)')
    parser.add_argument('--limit', type=int, help='Limit number of leads to process')
    
    args = parser.parse_args()
    
    processor = BatchQualificationProcessor()
    processor.process_csv(args.input, args.output, args.limit)