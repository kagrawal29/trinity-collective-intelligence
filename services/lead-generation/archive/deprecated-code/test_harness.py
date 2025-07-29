#!/usr/bin/env python3
"""
Test Harness for LinkedIn API - Systematic Testing Framework
Dev's precision approach to API testing
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import requests
from dataclasses import dataclass, asdict
from enum import Enum

# Configuration
API_KEY = os.getenv('RAPIDAPI_KEY', '')
BASE_HOST = 'linkedin-data-scraper.p.rapidapi.com'
BASE_HEADERS = {
    'x-rapidapi-key': API_KEY,
    'x-rapidapi-host': BASE_HOST,
    'Content-Type': 'application/json'
}

class APIEndpoint(Enum):
    """All available API endpoints"""
    PERSON_DEEP = 'person_deep'
    PROFILE_UPDATES = 'profile_updates'
    POST = 'post'
    POST_REACTIONS = 'post_reactions'
    POST_COMMENTS = 'post_comments'
    COMPANY = 'company'
    COMPANY_UPDATES = 'company_updates'
    SIMILAR_PROFILES = 'similar_profiles'

@dataclass
class APIResponse:
    """Structured API response"""
    endpoint: str
    url: str
    method: str
    params: Optional[Dict] = None
    data: Optional[Dict] = None
    status_code: int = 0
    duration_seconds: float = 0.0
    response_data: Any = None
    error: Optional[str] = None
    rate_limit: Optional[Dict] = None
    timestamp: str = ""
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        result['timestamp'] = self.timestamp or datetime.now().isoformat()
        return result

class LinkedInAPITester:
    """Systematic API testing framework"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(BASE_HEADERS)
        self.responses: List[APIResponse] = []
        self.test_data_dir = "test_data"
        self._ensure_test_dir()
        
    def _ensure_test_dir(self):
        """Create test data directory if not exists"""
        os.makedirs(self.test_data_dir, exist_ok=True)
        
    def test_endpoint(self, 
                     endpoint: APIEndpoint,
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None,
                     save_response: bool = True) -> APIResponse:
        """
        Test a single API endpoint systematically
        """
        # Map endpoint to URL
        endpoint_map = {
            APIEndpoint.PERSON_DEEP: ('POST', f'https://{BASE_HOST}/person_deep'),
            APIEndpoint.PROFILE_UPDATES: ('GET', f'https://{BASE_HOST}/profile_updates'),
            APIEndpoint.POST: ('POST', f'https://{BASE_HOST}/post'),
            APIEndpoint.POST_REACTIONS: ('POST', f'https://{BASE_HOST}/post_reactions'),
            APIEndpoint.POST_COMMENTS: ('POST', f'https://{BASE_HOST}/post_comments'),
            APIEndpoint.COMPANY: ('POST', f'https://{BASE_HOST}/company'),
            APIEndpoint.COMPANY_UPDATES: ('GET', f'https://{BASE_HOST}/company_updates'),
            APIEndpoint.SIMILAR_PROFILES: ('GET', f'https://{BASE_HOST}/similar_profiles'),
        }
        
        method, url = endpoint_map[endpoint]
        
        # Create response object
        response = APIResponse(
            endpoint=endpoint.value,
            url=url,
            method=method,
            params=params,
            data=data,
            timestamp=datetime.now().isoformat()
        )
        
        print(f"\n🧪 Testing: {endpoint.value}")
        print(f"Method: {method}")
        print(f"URL: {url}")
        if params:
            print(f"Params: {json.dumps(params, indent=2)}")
        if data:
            print(f"Data: {json.dumps(data, indent=2)}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Make the request
            if method == 'GET':
                r = self.session.get(url, params=params)
            else:
                r = self.session.post(url, json=data)
            
            response.duration_seconds = round(time.time() - start_time, 3)
            response.status_code = r.status_code
            
            # Extract rate limit info
            response.rate_limit = {
                'limit': r.headers.get('x-ratelimit-limit'),
                'remaining': r.headers.get('x-ratelimit-remaining'),
                'reset': r.headers.get('x-ratelimit-reset')
            }
            
            # Parse response
            if r.status_code == 200:
                response.response_data = r.json()
                print(f"✅ Success! Status: {r.status_code}")
            else:
                response.error = f"HTTP {r.status_code}: {r.text}"
                print(f"❌ Failed! Status: {r.status_code}")
                print(f"Error: {r.text[:200]}...")
                
        except Exception as e:
            response.duration_seconds = round(time.time() - start_time, 3)
            response.error = str(e)
            print(f"❌ Exception: {str(e)}")
            
        # Display results
        print(f"Duration: {response.duration_seconds}s")
        print(f"Rate Limit: {response.rate_limit}")
        
        # Save response
        if save_response:
            filename = f"{endpoint.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.test_data_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(response.to_dict(), f, indent=2)
            print(f"💾 Saved: {filepath}")
            
        self.responses.append(response)
        return response
        
    def test_influencer_flow(self, linkedin_url: str) -> Dict[str, Any]:
        """
        Test complete influencer data flow
        Returns structured data for schema design
        """
        print(f"\n🎯 TESTING INFLUENCER FLOW")
        print(f"Target: {linkedin_url}")
        print("=" * 80)
        
        results = {
            'influencer_url': linkedin_url,
            'timestamp': datetime.now().isoformat(),
            'profile': None,
            'posts': None,
            'selected_post': None,
            'reactions': None,
            'errors': []
        }
        
        # Step 1: Get profile
        print("\n📋 STEP 1: Fetching Profile Data")
        profile_response = self.test_endpoint(
            APIEndpoint.PERSON_DEEP,
            data={'link': linkedin_url}
        )
        
        if profile_response.status_code == 200:
            results['profile'] = profile_response.response_data
            print(f"\n✨ Profile Summary:")
            data = profile_response.response_data.get('data', {})
            print(f"Name: {data.get('fullName')}")
            print(f"Headline: {data.get('headline')}")
            print(f"Followers: {data.get('followerCount', 0):,}")
        else:
            results['errors'].append(f"Profile fetch failed: {profile_response.error}")
            return results
            
        # Wait for rate limit
        print("\n⏳ Waiting 2 seconds for rate limit...")
        time.sleep(2)
        
        # Step 2: Get posts
        print("\n📋 STEP 2: Fetching Posts")
        posts_response = self.test_endpoint(
            APIEndpoint.PROFILE_UPDATES,
            params={
                'profile_url': linkedin_url,
                'page': 1,
                'paginationToken': ''
            }
        )
        
        if posts_response.status_code == 200:
            results['posts'] = posts_response.response_data
            posts = posts_response.response_data.get('data', {}).get('posts', [])
            print(f"\n✨ Found {len(posts)} posts")
            
            # Find relevant post
            relevant_posts = self._find_relevant_posts(posts)
            if relevant_posts:
                results['selected_post'] = relevant_posts[0]
                print(f"\n🎯 Selected post with {relevant_posts[0]['reactions']} reactions")
        else:
            results['errors'].append(f"Posts fetch failed: {posts_response.error}")
            
        return results
        
    def _find_relevant_posts(self, posts: List[Dict]) -> List[Dict]:
        """Find posts relevant to lead generation"""
        relevant = []
        keywords = ['lead', 'outbound', 'sales', 'sdr', 'pipeline', 'prospect', 'outreach']
        
        for post in posts[:20]:  # Check first 20
            text = post.get('text', '').lower()
            if any(kw in text for kw in keywords):
                relevant.append({
                    'url': post.get('url'),
                    'text': text[:150] + '...',
                    'reactions': post.get('reactionsCount', 0),
                    'comments': post.get('commentsCount', 0),
                    'reactions_urn': post.get('reactionsUrn'),
                    'comments_urn': post.get('commentsUrn')
                })
                
        # Sort by engagement
        relevant.sort(key=lambda x: x['reactions'], reverse=True)
        return relevant[:5]  # Top 5
        
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        report = {
            'test_session': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.responses),
                'successful': sum(1 for r in self.responses if r.status_code == 200),
                'failed': sum(1 for r in self.responses if r.status_code != 200)
            },
            'endpoints_tested': list(set(r.endpoint for r in self.responses)),
            'average_response_time': sum(r.duration_seconds for r in self.responses) / len(self.responses) if self.responses else 0,
            'rate_limits_observed': [r.rate_limit for r in self.responses if r.rate_limit],
            'errors': [{'endpoint': r.endpoint, 'error': r.error} for r in self.responses if r.error]
        }
        
        # Save report
        report_path = os.path.join(self.test_data_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📊 Test Report saved: {report_path}")
        return report
        
    def propose_minimal_schema(self, test_results: Dict[str, Any]) -> str:
        """Propose minimal database schema based on test results"""
        schema = """
-- MINIMAL SCHEMA FOR V2 LEAD GENERATION
-- Based on actual API responses

-- Store influencer profiles with essential fields only
CREATE TABLE influencers (
    id SERIAL PRIMARY KEY,
    linkedin_url VARCHAR(500) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    headline TEXT,
    follower_count INTEGER DEFAULT 0,
    -- Store complete response for future fields
    raw_profile_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Store posts for engagement analysis
CREATE TABLE influencer_posts (
    id SERIAL PRIMARY KEY,
    influencer_id INTEGER REFERENCES influencers(id),
    post_url VARCHAR(500) UNIQUE,
    post_text TEXT,
    reactions_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    reactions_urn VARCHAR(500),  -- For fetching reactions
    comments_urn VARCHAR(500),   -- For fetching comments
    raw_post_data JSONB,
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Store engaged prospects (from reactions)
CREATE TABLE engaged_prospects (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES influencer_posts(id),
    profile_url VARCHAR(500),
    full_name VARCHAR(255),
    title VARCHAR(500),      -- Job title from reaction
    subtitle VARCHAR(500),   -- Company from reaction
    reaction_type VARCHAR(50),
    is_relevant BOOLEAN DEFAULT NULL,  -- Pre-qualification result
    qualification_score INTEGER DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Prevent duplicates
    UNIQUE(post_id, profile_url)
);

-- Indexes for performance
CREATE INDEX idx_influencers_url ON influencers(linkedin_url);
CREATE INDEX idx_posts_influencer ON influencer_posts(influencer_id);
CREATE INDEX idx_prospects_post ON engaged_prospects(post_id);
CREATE INDEX idx_prospects_relevant ON engaged_prospects(is_relevant);
"""
        return schema


def main():
    """Run the test harness"""
    if not API_KEY:
        print("❌ ERROR: Set RAPIDAPI_KEY environment variable!")
        return
        
    tester = LinkedInAPITester()
    
    # Test with Suprava's profile
    INFLUENCER_URL = "https://www.linkedin.com/in/suprava-sabat-saasleadgen/"
    
    # Run complete test flow
    results = tester.test_influencer_flow(INFLUENCER_URL)
    
    # Generate report
    report = tester.generate_test_report()
    
    # Propose schema
    schema = tester.propose_minimal_schema(results)
    schema_path = os.path.join(tester.test_data_dir, "proposed_schema.sql")
    with open(schema_path, 'w') as f:
        f.write(schema)
    
    print(f"\n💾 Proposed schema saved: {schema_path}")
    print("\n✅ TEST HARNESS COMPLETE!")
    print("\nNext steps:")
    print("1. Review test_data/ directory for API responses")
    print("2. Check proposed_schema.sql for minimal database design")
    print("3. Share findings with Guide for approval")


if __name__ == "__main__":
    main()