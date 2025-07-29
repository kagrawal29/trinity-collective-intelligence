#!/usr/bin/env python3
"""
Cleanup Results Validator - Quick validation of database integrity post-cleanup
Trinity Collective Intelligence - Dev Support Tool

Validates Tyler's cleanup execution results
"""

import sqlite3
import json
from datetime import datetime

def validate_cleanup_results():
    """Quick validation of database state after cleanup"""
    print("🔍 VALIDATING CLEANUP RESULTS")
    print("="*50)
    
    try:
        conn = sqlite3.connect('trinity_logging.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"📋 Available Tables: {', '.join(tables)}")
        
        # Core validation metrics
        results = {"validation_time": datetime.now().isoformat()}
        
        # 1. Posts count
        if 'posts' in tables:
            cursor.execute("SELECT COUNT(*) FROM posts")
            posts_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM posts WHERE post_content IS NOT NULL AND post_content != ''")
            posts_with_content = cursor.fetchone()[0]
            
            results["posts"] = {
                "total": posts_count,
                "with_content": posts_with_content,
                "content_rate": f"{(posts_with_content/posts_count*100):.1f}%" if posts_count > 0 else "0%"
            }
            
            print(f"📊 POSTS: {posts_count} total, {posts_with_content} with content ({results['posts']['content_rate']})")
        
        # 2. Qualifications count (check multiple possible locations)
        qualification_sources = []
        
        # Check post_qualifications table
        if 'post_qualifications' in tables:
            cursor.execute("SELECT COUNT(*) FROM post_qualifications")
            pq_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT post_id) FROM post_qualifications")
            unique_post_quals = cursor.fetchone()[0]
            
            qualification_sources.append(f"post_qualifications: {pq_count} total, {unique_post_quals} unique posts")
            
            results["post_qualifications"] = {
                "total": pq_count,
                "unique_posts": unique_post_quals,
                "ratio": f"{pq_count}:{unique_post_quals}"
            }
        
        # Check processing_steps table
        if 'processing_steps' in tables:
            cursor.execute("SELECT COUNT(*) FROM processing_steps WHERE workflow_step = 'post_qualification'")
            ps_count = cursor.fetchone()[0]
            qualification_sources.append(f"processing_steps: {ps_count} qualification entries")
            
            results["processing_steps_qualifications"] = ps_count
        
        print(f"🎯 QUALIFICATIONS: {', '.join(qualification_sources)}")
        
        # 3. Integrity check
        integrity_status = "✅ GOOD"
        issues = []
        
        if 'posts' in tables and 'post_qualifications' in tables:
            # Check 1:1 ratio
            if results["posts"]["total"] != results["post_qualifications"]["unique_posts"]:
                integrity_status = "⚠️ MISMATCH"
                issues.append(f"Posts ({results['posts']['total']}) != Unique Qualifications ({results['post_qualifications']['unique_posts']})")
            
            # Check for duplicates
            if results["post_qualifications"]["total"] != results["post_qualifications"]["unique_posts"]:
                integrity_status = "❌ DUPLICATES"
                issues.append(f"Total qualifications ({results['post_qualifications']['total']}) > unique posts ({results['post_qualifications']['unique_posts']})")
        
        results["integrity"] = {
            "status": integrity_status,
            "issues": issues
        }
        
        print(f"🔒 INTEGRITY: {integrity_status}")
        for issue in issues:
            print(f"   ⚠️ {issue}")
        
        # 4. Sample data check
        if 'posts' in tables and results["posts"]["total"] > 0:
            cursor.execute("SELECT id, post_url, LENGTH(post_content) as content_length FROM posts LIMIT 3")
            sample_posts = cursor.fetchall()
            
            print(f"📄 SAMPLE POSTS:")
            for post_id, url, content_len in sample_posts:
                url_preview = url[-40:] if url else "N/A"
                print(f"   ID {post_id}: {url_preview} ({content_len} chars)")
        
        conn.close()
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if integrity_status == "✅ GOOD":
            print("   ✅ DATABASE CLEANUP SUCCESSFUL!")
            print("   ✅ Ready for engagement testing")
        elif integrity_status == "⚠️ MISMATCH":
            print("   ⚠️ Minor issues detected - review needed")
        else:
            print("   ❌ Significant issues remain - additional cleanup required")
        
        return results
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return {"error": str(e), "validation_time": datetime.now().isoformat()}

if __name__ == "__main__":
    validate_cleanup_results()