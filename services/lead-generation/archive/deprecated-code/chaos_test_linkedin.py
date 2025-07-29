#!/usr/bin/env python3
"""
Tyler's Chaos Testing for LinkedIn API
Testing impossible URLs and edge cases
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('RAPIDAPI_KEY')

print('🔥 CHAOS TEST 1: IMPOSSIBLE LINKEDIN URLS!')
print('='*50)

chaos_urls = [
    'https://linkedin.com/in/-777777',
    'https://linkedin.com/in/null',
    'https://linkedin.com/in/undefined',
    'https://linkedin.com/in/',
    'not-a-url-at-all',
    'https://linkedin.com/in/' + 'a' * 100,
    'https://linkedin.com/in/../../etc/passwd',
    'https://linkedin.com/in/SELECT%20*%20FROM%20users'
]

for i, chaos_url in enumerate(chaos_urls, 1):
    print(f'Test {i}: {chaos_url[:50]}...')
    
    try:
        url = 'https://linkedin-data-scraper2.p.rapidapi.com/person_deep_profile'
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'linkedin-data-scraper2.p.rapidapi.com',
            'Content-Type': 'application/json'
        }
        
        payload = {'profile_url': chaos_url}
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        print(f'  Status: {response.status_code}')
        if response.status_code != 200:
            print(f'  Response: {response.text[:100]}...')
        else:
            print('  🚨 UNEXPECTED SUCCESS!')
            data = response.json()
            print(f'  Data keys: {list(data.keys()) if isinstance(data, dict) else "Not dict"}')
            
    except Exception as e:
        print(f'  Error: {str(e)[:80]}...')
    
    print('-' * 30)

print('\n🎯 CHAOS DISCOVERY COMPLETE!')