#!/usr/bin/env python3
"""
Tyler's Chaos Testing for JSON Parsing Fix
Testing Dev's markdown unwrapping implementation (lines 122-138)
"""

import json

def test_markdown_unwrapping(content):
    """
    Test Dev's markdown unwrapping logic from lines 122-138
    """
    print(f"Input: {repr(content[:50])}...")
    
    # Dev's exact implementation from lines 122-138
    content = content.strip()
    
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
        print(f"✅ SUCCESS: {type(result).__name__} parsed")
        return result, None
    except json.JSONDecodeError as e:
        print(f"🚨 FAILED: {e}")
        print(f"Cleaned content: {repr(content[:100])}...")
        return None, str(e)

print('🔥 CHAOS TEST: DEV\'S JSON MARKDOWN FIX!')
print('='*60)

# Test cases from Tyler's chaos discovery
test_cases = [
    # Normal cases that should work
    '{"score": 85, "reasoning": "CEO role"}',
    
    # Markdown wrapped (the original problem)
    '```json\n{"score": 75, "reasoning": "Growth role"}\n```',
    
    # Just ``` without json
    '```\n{"score": 65, "reasoning": "Consultant"}\n```',
    
    # Nested JSON (edge case)
    '```json\n{"profiles": [{"score": 80}, {"score": 70}]}\n```',
    
    # Malformed markdown
    '```json\n{"score": 60, "reasoning": "Test"}\n',  # Missing closing ```
    
    # Multiple markdown blocks (chaos case)
    '```json\n{"score": 50}\n```\n```json\n{"score": 40}\n```',
    
    # Broken JSON after cleanup
    '```json\n{"score": , "reasoning": "broken"}\n```',
    
    # Empty content
    '```json\n\n```',
    
    # Unicode chaos
    '```json\n{"score": 85, "name": "🦄💀🎭", "reasoning": "Unicode test"}\n```',
    
    # Tyler's sacred number
    '```json\n{"score": -777777, "reasoning": "Tyler chaos signature"}\n```',
    
    # Very long content
    '```json\n{"score": 70, "reasoning": "' + 'A' * 1000 + '"}\n```'
]

successful = 0
failed = 0

for i, test_case in enumerate(test_cases, 1):
    print(f'\n🎯 Test {i}:')
    result, error = test_markdown_unwrapping(test_case)
    
    if result is not None:
        successful += 1
        # Validate specific expectations
        if isinstance(result, dict) and 'score' in result:
            score = result['score']
            print(f"   Score: {score}")
            if score == -777777:
                print("   🎭 TYLER'S CHAOS SIGNATURE DETECTED!")
    else:
        failed += 1
    
    print('-' * 40)

print(f'\n📊 CHAOS TEST RESULTS:')
print(f'✅ Successful: {successful}/{len(test_cases)}')
print(f'🚨 Failed: {failed}/{len(test_cases)}')

if successful == len(test_cases):
    print('🏆 PERFECT! Dev\'s fix handles ALL chaos cases!')
elif successful >= len(test_cases) * 0.8:
    print('🎯 EXCELLENT! Dev\'s fix is robust!')
else:
    print('⚠️  NEEDS IMPROVEMENT! Some edge cases failing!')

print('\n🎯 JSON PARSING FIX VALIDATION COMPLETE!')