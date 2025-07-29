#!/usr/bin/env python3
"""
Fetch ALL Engagement Data (Reactions + Comments) with Robust Rate Limiting
Complete engagement data collection with exponential backoff
"""

import json
import requests
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import sys

# Configuration
API_KEY = os.getenv('RAPIDAPI_KEY', '')
POST_URL = "https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642"

HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': 'linkedin-data-scraper.p.rapidapi.com',
    'Content-Type': 'application/json'
}

@dataclass
class RateLimitStatus:
    """Track rate limit status"""
    endpoint: str
    limit: int
    remaining: int
    reset_time: datetime
    last_429: datetime = None
    consecutive_429s: int = 0
    current_delay: float = 2.0  # Start with 2 second delay

class FullEngagementFetcher:
    """Fetch all engagement data with robust error handling"""
    
    def __init__(self):
        self.all_reactions = []
        self.all_comments = []
        self.test_data_dir = "test_data"
        self.ensure_dir()
        self.rate_limits = {}
        self.total_api_calls = 0
        self.failed_calls = []
        
    def ensure_dir(self):
        """Create test data directory if needed"""
        os.makedirs(self.test_data_dir, exist_ok=True)
        
    def handle_rate_limit(self, endpoint: str, response: requests.Response) -> float:
        """Handle rate limit with exponential backoff"""
        if endpoint not in self.rate_limits:
            self.rate_limits[endpoint] = RateLimitStatus(
                endpoint=endpoint,
                limit=100,
                remaining=100,
                reset_time=datetime.now()
            )
        
        status = self.rate_limits[endpoint]
        
        # Update from headers
        if 'x-ratelimit-limit' in response.headers:
            status.limit = int(response.headers['x-ratelimit-limit'])
        if 'x-ratelimit-remaining' in response.headers:
            status.remaining = int(response.headers['x-ratelimit-remaining'])
        if 'x-ratelimit-reset' in response.headers:
            status.reset_time = datetime.fromtimestamp(int(response.headers['x-ratelimit-reset']))
        
        # Handle 429 error
        if response.status_code == 429:
            status.last_429 = datetime.now()
            status.consecutive_429s += 1
            
            # Exponential backoff
            delay = min(status.current_delay * (2 ** status.consecutive_429s), 60)  # Max 60s
            
            print(f"\n🚨 RATE LIMIT HIT on {endpoint}!")
            print(f"Status Code: 429")
            print(f"Error: {response.text[:200]}")
            print(f"Consecutive 429s: {status.consecutive_429s}")
            print(f"Backing off for {delay} seconds...")
            
            # Log to file
            self.log_rate_limit_error(endpoint, response, delay)
            
            return delay
        else:
            # Reset on success
            status.consecutive_429s = 0
            status.current_delay = 2.0
            
            # Calculate smart delay
            if status.remaining < 10:
                return 5.0  # Slow down when low
            elif status.remaining < 20:
                return 3.0
            else:
                return 2.0
    
    def log_rate_limit_error(self, endpoint: str, response: requests.Response, delay: float):
        """Log rate limit errors for analysis"""
        error_log = {
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'status_code': response.status_code,
            'error_text': response.text[:500],
            'headers': dict(response.headers),
            'delay_seconds': delay,
            'total_api_calls': self.total_api_calls
        }
        
        log_file = os.path.join(self.test_data_dir, 'rate_limit_errors.json')
        
        # Append to log file
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(error_log)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def show_progress(self, current: int, total: int, type_: str):
        """Show progress bar"""
        if total == 0:
            return
            
        progress = current / total
        bar_length = 40
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        sys.stdout.write(f'\r{type_}: [{bar}] {current}/{total} ({progress*100:.1f}%)')
        sys.stdout.flush()
    
    def get_post_data(self) -> Tuple[str, str]:
        """Get post data to extract URNs"""
        print("📋 Getting post data...")
        self.total_api_calls += 1
        
        response = requests.post(
            'https://linkedin-data-scraper.p.rapidapi.com/post',
            headers=HEADERS,
            json={'link': POST_URL}
        )
        
        if response.status_code == 200:
            data = response.json()
            post_data = data.get('data', {})
            reactions_urn = post_data.get('reactionsUrn')
            comments_urn = post_data.get('commentsUrn')
            
            print(f"✅ Got URNs!")
            print(f"Reactions: {post_data.get('reactionsCount', 0)}")
            print(f"Comments: {post_data.get('commentsCount', 0)}")
            
            return reactions_urn, comments_urn
        else:
            print(f"❌ Failed to get post data: {response.status_code}")
            return None, None
    
    def fetch_reactions_with_retry(self, reactions_urn: str, page: int, max_retries: int = 3) -> Dict[str, Any]:
        """Fetch reactions with retry logic"""
        endpoint = 'post_reactions'
        
        for attempt in range(max_retries):
            self.total_api_calls += 1
            
            try:
                response = requests.post(
                    'https://linkedin-data-scraper.p.rapidapi.com/post_reactions',
                    headers=HEADERS,
                    json={'reactionsUrn': reactions_urn, 'page': page},
                    timeout=30
                )
                
                # Handle rate limit
                delay = self.handle_rate_limit(endpoint, response)
                
                if response.status_code == 200:
                    data = response.json()
                    reactions = data.get('reactions', [])
                    return {
                        'success': True,
                        'reactions': reactions,
                        'page': page
                    }
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    time.sleep(delay)
                    continue
                else:
                    # Other error
                    self.failed_calls.append({
                        'endpoint': endpoint,
                        'page': page,
                        'status': response.status_code,
                        'error': response.text[:200]
                    })
                    return {'success': False, 'reactions': [], 'page': page}
                    
            except Exception as e:
                print(f"\n❌ Exception on page {page}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                    
        return {'success': False, 'reactions': [], 'page': page}
    
    def fetch_comments_with_retry(self, comments_urn: str, page: int, max_retries: int = 3) -> Dict[str, Any]:
        """Fetch comments with retry logic"""
        endpoint = 'post_comments'
        
        for attempt in range(max_retries):
            self.total_api_calls += 1
            
            try:
                response = requests.post(
                    'https://linkedin-data-scraper.p.rapidapi.com/post_comments',
                    headers=HEADERS,
                    json={'commentsUrn': comments_urn, 'page': page},
                    timeout=30
                )
                
                # Handle rate limit
                delay = self.handle_rate_limit(endpoint, response)
                
                if response.status_code == 200:
                    data = response.json()
                    comments = data.get('comments', [])
                    return {
                        'success': True,
                        'comments': comments,
                        'page': page
                    }
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    time.sleep(delay)
                    continue
                else:
                    # Other error
                    self.failed_calls.append({
                        'endpoint': endpoint,
                        'page': page,
                        'status': response.status_code,
                        'error': response.text[:200]
                    })
                    return {'success': False, 'comments': [], 'page': page}
                    
            except Exception as e:
                print(f"\n❌ Exception on page {page}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                    
        return {'success': False, 'comments': [], 'page': page}
    
    def fetch_all_reactions(self, reactions_urn: str) -> List[Dict]:
        """Fetch all reactions with progress tracking"""
        print("\n\n📊 FETCHING ALL REACTIONS")
        print("=" * 60)
        
        page = 1
        estimated_total = 144  # From previous test
        
        while True:
            result = self.fetch_reactions_with_retry(reactions_urn, page)
            
            if not result['success']:
                print(f"\n⚠️ Failed on page {page}, continuing...")
                page += 1
                if page > 20:  # Safety limit
                    break
                continue
            
            reactions = result['reactions']
            if not reactions:
                print(f"\n✅ Completed reactions at page {page-1}")
                break
            
            self.all_reactions.extend(reactions)
            self.show_progress(len(self.all_reactions), estimated_total, "Reactions")
            
            if len(reactions) < 10:  # Partial page
                print(f"\n✅ Last page of reactions")
                break
            
            page += 1
            time.sleep(2)  # Base delay
        
        print(f"\n✅ Total reactions fetched: {len(self.all_reactions)}")
        return self.all_reactions
    
    def fetch_all_comments(self, comments_urn: str) -> List[Dict]:
        """Fetch all comments with progress tracking"""
        print("\n\n💬 FETCHING ALL COMMENTS")
        print("=" * 60)
        
        page = 1
        
        while True:
            result = self.fetch_comments_with_retry(comments_urn, page)
            
            if not result['success']:
                print(f"\n⚠️ Failed on page {page}, continuing...")
                page += 1
                if page > 20:  # Safety limit
                    break
                continue
            
            comments = result['comments']
            if not comments:
                print(f"\n✅ Completed comments at page {page-1}")
                break
            
            self.all_comments.extend(comments)
            print(f"\rComments: {len(self.all_comments)} fetched...", end='')
            
            if len(comments) < 10:  # Partial page
                print(f"\n✅ Last page of comments")
                break
            
            page += 1
            time.sleep(2)  # Base delay
        
        print(f"\n✅ Total comments fetched: {len(self.all_comments)}")
        return self.all_comments
    
    def save_all_engagement(self):
        """Save all engagement data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save full engagement data
        engagement_file = os.path.join(self.test_data_dir, f'full_engagement_{timestamp}.json')
        
        output = {
            'post_url': POST_URL,
            'fetch_timestamp': datetime.now().isoformat(),
            'total_reactions': len(self.all_reactions),
            'total_comments': len(self.all_comments),
            'total_engagement': len(self.all_reactions) + len(self.all_comments),
            'total_api_calls': self.total_api_calls,
            'failed_calls': len(self.failed_calls),
            'reactions': self.all_reactions,
            'comments': self.all_comments
        }
        
        with open(engagement_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Saved full engagement to: {engagement_file}")
        
        # Save rate limit summary
        if self.rate_limits:
            rate_limit_file = os.path.join(self.test_data_dir, f'rate_limit_summary_{timestamp}.json')
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'total_api_calls': self.total_api_calls,
                'endpoints': {}
            }
            
            for endpoint, status in self.rate_limits.items():
                summary['endpoints'][endpoint] = {
                    'limit': status.limit,
                    'remaining': status.remaining,
                    'reset_time': status.reset_time.isoformat() if status.reset_time else None,
                    'hit_429': status.last_429 is not None,
                    'consecutive_429s': status.consecutive_429s
                }
            
            with open(rate_limit_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            print(f"💾 Saved rate limit summary to: {rate_limit_file}")
        
        return engagement_file

def main():
    """Execute full engagement fetch"""
    if not API_KEY:
        print("❌ ERROR: Set RAPIDAPI_KEY environment variable!")
        return
    
    fetcher = FullEngagementFetcher()
    
    print("🚀 FULL ENGAGEMENT DATA FETCHER")
    print("=" * 60)
    print("Target: Suprava's viral post")
    print("Goal: ALL reactions + ALL comments")
    print("Rate limiting: Exponential backoff enabled")
    print("=" * 60)
    
    # Step 1: Get URNs
    reactions_urn, comments_urn = fetcher.get_post_data()
    if not reactions_urn:
        print("❌ Failed to get URNs")
        return
    
    # Step 2: Fetch all reactions
    fetcher.fetch_all_reactions(reactions_urn)
    
    # Step 3: Fetch all comments
    if comments_urn:
        fetcher.fetch_all_comments(comments_urn)
    else:
        print("⚠️ No comments URN available")
    
    # Step 4: Save everything
    saved_file = fetcher.save_all_engagement()
    
    # Step 5: Summary
    print("\n📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"Total API calls: {fetcher.total_api_calls}")
    print(f"Failed calls: {len(fetcher.failed_calls)}")
    print(f"Reactions collected: {len(fetcher.all_reactions)}")
    print(f"Comments collected: {len(fetcher.all_comments)}")
    print(f"Total engagement: {len(fetcher.all_reactions) + len(fetcher.all_comments)}")
    
    if fetcher.failed_calls:
        print(f"\n⚠️ Failed calls logged in: test_data/failed_calls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(f"test_data/failed_calls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(fetcher.failed_calls, f, indent=2)
    
    print("\n✅ COMPLETE! Next step: Run analyze_full_engagement.py")

if __name__ == "__main__":
    main()