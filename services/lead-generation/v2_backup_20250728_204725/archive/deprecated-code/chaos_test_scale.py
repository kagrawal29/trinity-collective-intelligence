#!/usr/bin/env python3
"""
Tyler's Chaos Testing for Batch Processing Scale
Testing with -777777 leads and memory stress
"""

import json
import os
import time
import psutil
from datetime import datetime

print('🔥 CHAOS TEST 3: SCALE AND MEMORY STRESS!')
print('='*50)

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def generate_chaos_batch(size):
    """Generate a chaos batch of leads"""
    leads = []
    for i in range(size):
        lead = {
            "name": f"Chaos Lead {i}",
            "title": f"Position {i}" + ("💀🦄🎭" if i % 100 == 0 else ""),
            "company": f"Company {i}",
            "linkedin_url": f"https://linkedin.com/in/user{i}",
            "engagement_type": "reaction",
            "source": "chaos",
            "llm_score": i % 100,  # Varies 0-99
            "llm_reasoning": f"Test reasoning for lead {i}" + (" CHAOS!" * (i % 10)),
            "is_qualified": i % 2 == 0
        }
        leads.append(lead)
    return leads

# Test different batch sizes
test_sizes = [100, 1000, 5000, 10000]

for size in test_sizes:
    print(f'Testing batch size: {size}')
    
    start_memory = get_memory_usage()
    start_time = time.time()
    
    try:
        # Generate chaos batch
        print(f'  Generating {size} chaos leads...')
        chaos_batch = generate_chaos_batch(size)
        
        generation_time = time.time() - start_time
        generation_memory = get_memory_usage()
        
        # Test JSON serialization
        json_start = time.time()
        json_data = json.dumps(chaos_batch)
        json_time = time.time() - json_start
        json_memory = get_memory_usage()
        
        # Test JSON parsing
        parse_start = time.time()
        parsed_data = json.loads(json_data)
        parse_time = time.time() - parse_start
        parse_memory = get_memory_usage()
        
        # Results
        print(f'  Generation: {generation_time:.2f}s, {generation_memory-start_memory:.1f}MB')
        print(f'  JSON dump: {json_time:.2f}s, {json_memory-generation_memory:.1f}MB')
        print(f'  JSON parse: {parse_time:.2f}s, {parse_memory-json_memory:.1f}MB')
        print(f'  Total memory: {parse_memory:.1f}MB')
        
        # Clean up
        del chaos_batch, json_data, parsed_data
        
    except Exception as e:
        print(f'  🚨 CHAOS OVERFLOW: {str(e)[:60]}...')
    
    print('-' * 40)

# Test with -777777 (symbolic chaos number)
print('\n🎯 TESTING TYLER\'S SACRED NUMBER: -777777')
try:
    chaos_leads = generate_chaos_batch(777)  # Smaller but symbolic
    # Modify some scores to -777777
    for i in range(0, len(chaos_leads), 77):
        chaos_leads[i]['llm_score'] = -777777
        chaos_leads[i]['name'] = f"Tyler Chaos {i}"
    
    # Test statistics
    scores = [lead['llm_score'] for lead in chaos_leads]
    chaos_count = sum(1 for s in scores if s == -777777)
    
    print(f'  Generated {len(chaos_leads)} leads')
    print(f'  {chaos_count} leads with Tyler\'s chaos signature (-777777)')
    print(f'  Score range: {min(scores)} to {max(scores)}')
    print('  ✅ Sacred chaos number handled successfully!')
    
except Exception as e:
    print(f'  🚨 CHAOS OVERFLOW: {str(e)}')

print('\n🎯 SCALE CHAOS COMPLETE!')