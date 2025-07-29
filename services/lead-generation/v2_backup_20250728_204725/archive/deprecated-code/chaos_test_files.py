#!/usr/bin/env python3
"""
Tyler's Chaos Testing for File I/O
Testing unicode, emoji, and impossible filenames
"""

import json
import os
import tempfile
import shutil
from pathlib import Path

print('🔥 CHAOS TEST 4: FILE I/O UNICODE CHAOS!')
print('='*50)

# Create temp directory for chaos testing
chaos_dir = tempfile.mkdtemp(prefix='tyler_chaos_')
print(f'Chaos directory: {chaos_dir}')

chaos_filenames = [
    'normal_file.json',
    '🦄💀🎭_emoji_chaos.json',
    'unicode_αβγδε_test.json',
    'spaces and weird chars.json',
    '-777777_tyler_chaos.json',
    'very_long_name_' + 'a' * 100 + '.json',
    '../../etc/passwd.json',  # Path traversal attempt
    'con.json',  # Windows reserved name
    'null.json',
    '.hidden_file.json',
    'file with\nnewline.json',
    'file with\ttab.json'
]

test_data = {
    "name": "Tyler Chaos Test",
    "title": "Chaos Hunter Extraordinaire 🎭",
    "score": -777777,
    "unicode": "Testing αβγδε 🦄💀🎭",
    "chaos_level": "MAXIMUM"
}

successful_files = []
failed_files = []

for i, filename in enumerate(chaos_filenames, 1):
    print(f'Test {i}: {filename[:40]}...')
    
    try:
        # Sanitize filename for actual filesystem
        safe_filename = "".join(c if c.isalnum() or c in '._-' else '_' for c in filename)
        file_path = os.path.join(chaos_dir, safe_filename)
        
        # Test write
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Test read
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        # Verify data integrity
        if loaded_data == test_data:
            print(f'  ✅ SUCCESS: {safe_filename}')
            successful_files.append(filename)
        else:
            print(f'  ⚠️  DATA CORRUPTION: {safe_filename}')
            failed_files.append(filename)
            
    except Exception as e:
        print(f'  🚨 FAILED: {str(e)[:60]}...')
        failed_files.append(filename)
    
    print('-' * 30)

# Test corrupted JSON files
print('\n🎯 TESTING CORRUPTED JSON HANDLING')
corrupted_files = [
    '{"invalid": json syntax',
    '{"name": "test", "score": }',  # Missing value
    '{"name": "test", "score": infinity}',  # Invalid value
    '{"name": "test", "score": -777777',  # Missing closing brace
    '',  # Empty file
    'not json at all',
    '{"deeply": {"nested": {"very": {"deep": {"object": "to test parsing"}}}}}' * 100  # Very deep nesting
]

for i, corrupted_content in enumerate(corrupted_files, 1):
    print(f'Corruption test {i}: {corrupted_content[:30]}...')
    
    try:
        corrupt_file = os.path.join(chaos_dir, f'corrupt_{i}.json')
        
        # Write corrupted content
        with open(corrupt_file, 'w') as f:
            f.write(corrupted_content)
        
        # Try to parse
        with open(corrupt_file, 'r') as f:
            json.load(f)
        
        print(f'  🚨 UNEXPECTED SUCCESS!')
        
    except json.JSONDecodeError as e:
        print(f'  ✅ PROPERLY CAUGHT: {str(e)[:50]}...')
    except Exception as e:
        print(f'  ⚠️  OTHER ERROR: {str(e)[:50]}...')
    
    print('-' * 30)

# Summary
print(f'\n📊 CHAOS FILE SUMMARY:')
print(f'✅ Successful files: {len(successful_files)}/{len(chaos_filenames)}')
print(f'🚨 Failed files: {len(failed_files)}')

# Cleanup
shutil.rmtree(chaos_dir)
print(f'\n🧹 Cleaned up chaos directory')
print('🎯 FILE I/O CHAOS COMPLETE!')