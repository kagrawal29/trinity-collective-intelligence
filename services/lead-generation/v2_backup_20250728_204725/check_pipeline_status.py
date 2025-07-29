#!/usr/bin/env python3
"""
Pipeline Status Checker - Monitor V2 Lead Generation Progress
"""

import sqlite3
import json
import os
import glob
from datetime import datetime

def check_status():
    print("🔍 V2 LEAD GENERATION PIPELINE STATUS")
    print("=" * 60)
    
    # Check database
    try:
        conn = sqlite3.connect('trinity_logging.db')
        cursor = conn.cursor()
        
        # Lead count
        cursor.execute("SELECT COUNT(*) FROM leads")
        total_leads = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM leads WHERE created_at > datetime('now', '-1 hour')")
        recent_leads = cursor.fetchone()[0]
        
        print(f"📊 DATABASE STATUS:")
        print(f"   Total Leads: {total_leads}")
        print(f"   Added in Last Hour: {recent_leads}")
        
        # Post qualifications
        cursor.execute("SELECT COUNT(*) FROM posts")
        total_posts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM post_qualifications")
        total_quals = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM post_qualifications WHERE qualification_status = 'QUALIFIED'")
        qualified_posts = cursor.fetchone()[0]
        
        print(f"\n📝 POST QUALIFICATION:")
        print(f"   Total Posts: {total_posts}")
        print(f"   Total Qualifications: {total_quals}")
        print(f"   Qualified Posts: {qualified_posts}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Database Error: {e}")
    
    # Check engagement files
    print(f"\n📁 ENGAGEMENT FILES:")
    engagement_files = sorted(glob.glob("test_data/engagement_*.json"), key=os.path.getmtime, reverse=True)
    
    for i, file in enumerate(engagement_files[:5]):
        size = os.path.getsize(file) / 1024  # KB
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        filename = os.path.basename(file)
        
        # Count leads in file
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                reactions = len(data.get('reactions', []))
                comments = len(data.get('comments', []))
                total = reactions + comments
                print(f"   {i+1}. {filename} ({size:.1f}KB)")
                print(f"      Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"      Leads: {total} ({reactions} reactions, {comments} comments)")
        except:
            print(f"   {i+1}. {filename} ({size:.1f}KB) - Error reading")
    
    # Check for analysis results
    print(f"\n🎯 ANALYSIS RESULTS:")
    
    # Batch LLM results
    batch_results = sorted(glob.glob("test_data/batch_llm_results_*.json"), key=os.path.getmtime, reverse=True)
    if batch_results:
        latest_batch = batch_results[0]
        with open(latest_batch, 'r') as f:
            data = json.load(f)
            print(f"   Latest Batch Analysis: {os.path.basename(latest_batch)}")
            print(f"   Total Analyzed: {data.get('total_leads', 0)}")
            print(f"   Qualified: {data.get('qualified_leads', 0)} ({data.get('qualification_rate', 0):.1f}%)")
    
    # Realtime analysis results
    realtime_results = sorted(glob.glob("test_data/realtime_analysis_*.json"), key=os.path.getmtime, reverse=True)
    if realtime_results:
        print(f"\n   ✅ Realtime Analysis Found: {len(realtime_results)} files")
        latest = realtime_results[0]
        with open(latest, 'r') as f:
            data = json.load(f)
            print(f"   Latest: {os.path.basename(latest)}")
            print(f"   Stored in DB: {data.get('stored_in_database', 0)} leads")
    else:
        print(f"   ⏳ No realtime analysis results yet")
    
    # Check for running processes
    print(f"\n🔄 PROCESS CHECK:")
    
    # Check for zombie processes
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        processes = result.stdout.split('\n')
        
        python_processes = [p for p in processes if 'python' in p and ('end_to_end' in p or 'analyze' in p)]
        
        if python_processes:
            print(f"   ⚠️  Found {len(python_processes)} relevant Python processes:")
            for proc in python_processes[:3]:
                parts = proc.split()
                if len(parts) > 10:
                    pid = parts[1]
                    cpu = parts[2]
                    mem = parts[3]
                    cmd = ' '.join(parts[10:])[:50] + '...'
                    print(f"      PID {pid}: CPU {cpu}%, MEM {mem}% - {cmd}")
        else:
            print(f"   ✅ No hanging processes detected")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("💡 NEXT STEPS:")
    
    if total_leads <= 3:
        print("   1. Run: python3 analyze_engagement_realtime.py")
        print("   2. This will process the 246-lead engagement file")
        print("   3. Qualified leads will be stored in database immediately")
    else:
        print("   ✅ Leads are being processed and stored!")
        print("   Monitor progress with: python3 check_pipeline_status.py")

if __name__ == "__main__":
    check_status()