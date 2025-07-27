#!/usr/bin/env python3
"""
TYLER'S EMERGENCY API KEY TEST
Verify OpenAI key works before Dev implements
"""

import os
import sys
sys.path.append('..')

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv('../.env')

def test_openai_key():
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ NO OPENAI_API_KEY FOUND!")
        return False
    
    print(f"✅ Found API key: {api_key[:20]}...")
    
    # Test the key with a simple request
    try:
        client = OpenAI(api_key=api_key)
        
        # Simple test prompt
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a lead qualification expert."},
                {"role": "user", "content": "Score this lead (0-100): Sara Simmonds - CEO helping scale to $50M+"}
            ],
            max_tokens=50
        )
        
        print("\n✅ API KEY WORKS!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ API KEY ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔑 TYLER'S OPENAI KEY VERIFICATION")
    print("="*50)
    
    if test_openai_key():
        print("\n🎉 KEY IS VALID! Dev can proceed with real LLM implementation!")
        print("USER RAGE: 10/10 → 5/10 (halfway there!)")
    else:
        print("\n🚨 KEY ISSUES! Need to fix before implementing!")
        print("USER RAGE: Still 10/10!")