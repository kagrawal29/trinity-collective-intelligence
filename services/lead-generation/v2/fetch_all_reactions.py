#!/usr/bin/env python3
"""
Fetch ALL Reactions with Pagination
Systematic approach to getting all 144 reactions from Suprava's post
"""

import json
import requests
import os
import time
from datetime import datetime
from typing import List, Dict, Any

# Configuration
API_KEY = os.getenv('RAPIDAPI_KEY', '')
POST_URL = "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642"

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

class ReactionsFetcher:
    """Systematically fetch all reactions with pagination"""
    
    def __init__(self):
        self.all_reactions = []
        self.test_data_dir = "test_data"
        self.ensure_dir()
        
    def ensure_dir(self):
        """Create test data directory if needed"""
        os.makedirs(self.test_data_dir, exist_ok=True)
    
    def get_post_data(self) -> Dict[str, Any]:
        """First get the post data to extract reactions URN"""
        print("📋 STEP 1: Getting post data...")
        
        response = requests.post(
            'https://linkedin-data-scraper.p.rapidapi.com/post',
            headers=HEADERS,
            json={'link': POST_URL}
        )
        
        if response.status_code == 200:
            data = response.json()
            post_data = data.get('data', {})
            reactions_urn = post_data.get('reactionsUrn')
            print(f"✅ Got reactions URN: {reactions_urn}")
            print(f"Total reactions count: {post_data.get('reactionsCount', 0)}")
            return reactions_urn
        else:
            print(f"❌ Failed to get post data: {response.status_code}")
            return None
    
    def fetch_reactions_page(self, reactions_urn: str, page: int) -> Dict[str, Any]:
        """Fetch a single page of reactions"""
        print(f"\n📄 Fetching page {page}...")
        
        response = requests.post(
            'https://linkedin-data-scraper.p.rapidapi.com/post_reactions',
            headers=HEADERS,
            json={
                'reactionsUrn': reactions_urn,
                'page': page
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            reactions = data.get('reactions', [])
            print(f"✅ Got {len(reactions)} reactions on page {page}")
            
            # Check rate limit
            rate_limit = {
                'limit': response.headers.get('x-ratelimit-limit'),
                'remaining': response.headers.get('x-ratelimit-remaining')
            }
            print(f"Rate limit: {rate_limit}")
            
            return {
                'success': True,
                'reactions': reactions,
                'page': page,
                'has_more': len(reactions) > 0  # If we got reactions, there might be more
            }
        else:
            print(f"❌ Failed on page {page}: {response.status_code}")
            return {
                'success': False,
                'reactions': [],
                'page': page,
                'has_more': False
            }
    
    def fetch_all_reactions(self, reactions_urn: str) -> List[Dict]:
        """Fetch ALL reactions across all pages"""
        print("\n🚀 FETCHING ALL REACTIONS")
        print("=" * 60)
        
        page = 1
        total_fetched = 0
        
        while True:
            # Fetch page
            result = self.fetch_reactions_page(reactions_urn, page)
            
            if not result['success']:
                print(f"⚠️ Stopping due to error on page {page}")
                break
            
            reactions = result['reactions']
            if not reactions:
                print(f"✅ No more reactions. Completed at page {page-1}")
                break
            
            # Add to collection
            self.all_reactions.extend(reactions)
            total_fetched += len(reactions)
            
            print(f"Progress: {total_fetched} total reactions collected")
            
            # Check if we should continue
            if len(reactions) < 10:  # LinkedIn usually returns 10 per page
                print("✅ Reached last page (partial page)")
                break
            
            # Rate limit delay
            print("⏳ Waiting 2 seconds for rate limit...")
            time.sleep(2)
            
            page += 1
            
            # Safety limit
            if page > 20:  # 20 pages * 10 = 200 max
                print("⚠️ Safety limit reached (20 pages)")
                break
        
        return self.all_reactions
    
    def save_all_reactions(self):
        """Save all fetched reactions"""
        filename = f"all_reactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.test_data_dir, filename)
        
        output = {
            'post_url': POST_URL,
            'total_reactions': len(self.all_reactions),
            'fetch_timestamp': datetime.now().isoformat(),
            'reactions': self.all_reactions
        }
        
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Saved {len(self.all_reactions)} reactions to: {filepath}")
        return filepath
    
    def analyze_quick_stats(self):
        """Quick analysis of fetched reactions"""
        print("\n📊 QUICK ANALYSIS")
        print("-" * 40)
        
        # Extract titles
        titles = []
        for reaction in self.all_reactions:
            subtitle = reaction.get('subtitle', '')
            if '|' in subtitle:
                title = subtitle.split('|')[0].strip()
            else:
                title = subtitle
            titles.append(title.lower())
        
        # Count relevant keywords
        relevant_keywords = ['sales', 'marketing', 'growth', 'revenue', 'business development', 
                           'sdr', 'bdr', 'appointment', 'lead', 'demand']
        
        relevant_count = 0
        for title in titles:
            if any(keyword in title for keyword in relevant_keywords):
                relevant_count += 1
        
        print(f"Total reactions: {len(self.all_reactions)}")
        print(f"Potentially relevant: {relevant_count}")
        print(f"Relevance rate: {relevant_count/len(self.all_reactions)*100:.1f}%")
        print(f"Expected qualified leads: ~{int(relevant_count * 0.7)}")

def main():
    """Execute the full pagination fetch"""
    if not API_KEY:
        print("❌ ERROR: Set RAPIDAPI_KEY environment variable!")
        return
    
    fetcher = ReactionsFetcher()
    
    # Step 1: Get reactions URN
    reactions_urn = fetcher.get_post_data()
    if not reactions_urn:
        print("❌ Failed to get reactions URN")
        return
    
    # Wait before starting pagination
    print("\n⏳ Waiting 2 seconds before pagination...")
    time.sleep(2)
    
    # Step 2: Fetch all reactions
    all_reactions = fetcher.fetch_all_reactions(reactions_urn)
    
    # Step 3: Save results
    saved_file = fetcher.save_all_reactions()
    
    # Step 4: Quick analysis
    fetcher.analyze_quick_stats()
    
    print("\n✅ PAGINATION COMPLETE!")
    print("\nNEXT STEPS:")
    print(f"1. Run: python3 analyze_leads.py (update to use {saved_file})")
    print("2. Review qualified leads")
    print("3. Generate personalized messages")
    print("4. Deliver to sales team!")

if __name__ == "__main__":
    main()