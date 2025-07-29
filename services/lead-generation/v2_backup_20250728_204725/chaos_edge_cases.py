#!/usr/bin/env python3
"""
TYLER'S EDGE CASE CHAOS TESTER
Testing weird inputs that might break the LLM analyzer
"""

import json
from datetime import datetime

def create_chaos_test_data():
    """Create edge cases that might break the system"""
    
    chaos_cases = [
        {
            "name": "💩 Unicode Test 🦄",
            "title": "CEO of 💰💰💰 Company | 🚀🚀🚀 Growth Hacker",
            "company": "🏢 Emoji Corp 🌟",
            "linkedin_url": "https://linkedin.com/in/emoji-test",
            "engagement_type": "reaction"
        },
        {
            "name": "SQL'; DROP TABLE users; --",
            "title": "Senior Software Engineer <script>alert('xss')</script>",
            "company": "Hacker Corp",
            "linkedin_url": "https://linkedin.com/in/sql-injection",
            "engagement_type": "comment"
        },
        {
            "name": "A" * 1000,  # Very long name
            "title": "B" * 2000,  # Very long title
            "company": "C" * 500,  # Very long company
            "linkedin_url": "https://linkedin.com/in/very-long-test",
            "engagement_type": "reaction"
        },
        {
            "name": "",  # Empty name
            "title": "",  # Empty title
            "company": "",  # Empty company
            "linkedin_url": "",  # Empty URL
            "engagement_type": "reaction"
        },
        {
            "name": None,  # Null values
            "title": None,
            "company": None,
            "linkedin_url": None,
            "engagement_type": "reaction"
        },
        {
            "name": "Normal Name",
            "title": "Lead at Company\n\nBUT WAIT! There's more!\n\n<h1>HTML injection</h1>\n{\"json\": \"injection\"}",
            "company": "Multi\nLine\nCompany\nName\nWith\nBreaks",
            "linkedin_url": "https://linkedin.com/in/multiline-test",
            "engagement_type": "reaction"
        },
        {
            "name": "🇺🇸🇬🇧🇫🇷🇩🇪🇯🇵 International Test",
            "title": "こんにちは世界 | مرحبا بالعالم | Здравствуй мир | 你好世界",
            "company": "Παγκόσμια Εταιρεία",
            "linkedin_url": "https://linkedin.com/in/international-test",
            "engagement_type": "comment"
        }
    ]
    
    return chaos_cases

def save_chaos_test():
    """Save chaos test cases for future reference"""
    chaos_data = create_chaos_test_data()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"test_data/chaos_edge_cases_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "description": "Tyler's chaos edge cases for LLM testing",
            "total_cases": len(chaos_data),
            "cases": chaos_data,
            "created": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"🔥 Created {len(chaos_data)} chaos test cases in {filename}")
    
    return filename

if __name__ == "__main__":
    print("🎪 TYLER'S CHAOS EDGE CASE GENERATOR")
    print("="*50)
    
    filename = save_chaos_test()
    
    print("\n🚨 EDGE CASES CREATED:")
    print("1. Unicode/Emoji overload")
    print("2. SQL injection attempts")  
    print("3. XSS script injection")
    print("4. Extremely long strings")
    print("5. Empty/null values")
    print("6. Multiline content")
    print("7. International characters")
    
    print(f"\n💣 Ready to break the analyzer with these!")
    print("Remember: Every break becomes a breakthrough!")