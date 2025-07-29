"""Profile fetcher with database caching"""

import os
import time
import requests
from typing import Dict, Any, Optional
from datetime import datetime

from database.models import Profile
from database.manager import DatabaseManager


class ProfileFetcher:
    """Fetches LinkedIn profiles with intelligent caching"""
    
    def __init__(self, db_manager: DatabaseManager, api_key: str = None):
        self.db = db_manager
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY')
        self.api_url = "https://linkedin-data-scraper.p.rapidapi.com/person"
        self.headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": "linkedin-data-scraper.p.rapidapi.com",
            "x-rapidapi-key": self.api_key
        }
        self.requests_made = 0
        self.cache_hits = 0
    
    def fetch_profile(self, linkedin_url: str, force_refresh: bool = False) -> Optional[Profile]:
        """
        Fetch profile with smart caching
        
        Args:
            linkedin_url: LinkedIn profile URL
            force_refresh: Force API fetch even if cached
            
        Returns:
            Profile object or None if failed
        """
        # Normalize URL
        linkedin_url = self._normalize_url(linkedin_url)
        
        # Check database cache first
        if not force_refresh:
            cached_profile = self.db.get_profile_by_url(linkedin_url)
            if cached_profile:
                # Check if data is stale (default 30 days)
                if not self.db.is_profile_stale(cached_profile):
                    self.cache_hits += 1
                    print(f"  📋 Cache hit for {cached_profile.full_name}")
                    return cached_profile
                else:
                    print(f"  🔄 Cache stale for {cached_profile.full_name}, refreshing...")
        
        # Fetch from API
        print(f"  🌐 Fetching from API...")
        api_response = self._fetch_from_api(linkedin_url)
        
        if api_response and api_response.get('success') and api_response.get('data'):
            # Create Profile object
            profile = Profile.from_api_response(linkedin_url, api_response['data'])
            
            # Save to database
            profile.id = self.db.save_profile(profile)
            
            print(f"  ✅ Fetched and cached: {profile.full_name}")
            return profile
        else:
            error_msg = api_response.get('error', 'Unknown error') if api_response else 'API request failed'
            if '404' in str(error_msg):
                print(f"  ⚠️  Profile not found (404) - skipping")
            else:
                print(f"  ❌ Failed to fetch profile: {error_msg}")
            return None
    
    def _normalize_url(self, url: str) -> str:
        """Normalize LinkedIn URL format"""
        # Remove trailing slashes and parameters
        url = url.rstrip('/').split('?')[0]
        
        # Ensure proper format
        if not url.startswith('http'):
            url = f"https://{url}"
        
        # Handle different LinkedIn URL formats
        if '/in/' in url:
            # Extract username and rebuild clean URL
            username = url.split('/in/')[-1].strip('/')
            url = f"https://www.linkedin.com/in/{username}"
        
        return url
    
    def _fetch_from_api(self, linkedin_url: str, retry_count: int = 0) -> Optional[Dict[str, Any]]:
        """Make API request to fetch profile with rate limit handling"""
        try:
            self.requests_made += 1
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={"link": linkedin_url},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                # Rate limit hit
                if retry_count < 3:
                    wait_time = (retry_count + 1) * 30  # 30s, 60s, 90s
                    print(f"  ⏳ Rate limit hit (429). Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    return self._fetch_from_api(linkedin_url, retry_count + 1)
                else:
                    return {
                        'success': False,
                        'error': 'API rate limit exceeded after 3 retries'
                    }
            else:
                return {
                    'success': False,
                    'error': f"API returned status {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': f"Unexpected error: {str(e)}"}
    
    def get_stats(self) -> Dict[str, int]:
        """Get fetcher statistics"""
        return {
            'api_requests': self.requests_made,
            'cache_hits': self.cache_hits,
            'total_fetches': self.requests_made + self.cache_hits,
            'cache_hit_rate': (self.cache_hits / (self.requests_made + self.cache_hits) * 100) 
                             if (self.requests_made + self.cache_hits) > 0 else 0
        }
    
    def bulk_fetch(self, linkedin_urls: list, delay: float = 1.0) -> Dict[str, Profile]:
        """
        Fetch multiple profiles with rate limiting
        
        Args:
            linkedin_urls: List of LinkedIn URLs
            delay: Delay between API requests in seconds
            
        Returns:
            Dictionary mapping URL to Profile
        """
        results = {}
        
        for i, url in enumerate(linkedin_urls):
            print(f"\n[{i+1}/{len(linkedin_urls)}] Processing {url}")
            
            profile = self.fetch_profile(url)
            if profile:
                results[url] = profile
            
            # Rate limiting (only for API calls, not cache hits)
            if i < len(linkedin_urls) - 1 and self.requests_made > 0:
                print(f"  ⏳ Rate limiting: waiting {delay}s...")
                time.sleep(delay)
        
        # Print statistics
        stats = self.get_stats()
        print(f"\n📊 Fetch Statistics:")
        print(f"  - Total profiles: {len(linkedin_urls)}")
        print(f"  - Successful: {len(results)}")
        print(f"  - API requests: {stats['api_requests']}")
        print(f"  - Cache hits: {stats['cache_hits']}")
        print(f"  - Cache hit rate: {stats['cache_hit_rate']:.1f}%")
        
        return results