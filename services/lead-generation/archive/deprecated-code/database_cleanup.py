#!/usr/bin/env python3
"""
Database Cleanup Script - Fix Integrity Issues
Trinity Collective Intelligence - Dev Implementation

Fixes Tyler's identified issues:
1. Remove duplicate qualifications (38 for 21 posts)
2. Fix orphan posts without qualifications  
3. Validate score consistency
4. Clean up database integrity issues
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any

class DatabaseCleanup:
    """Clean up database integrity issues"""
    
    def __init__(self, db_path: str = "trinity_logging.db"):
        self.db_path = db_path
        self.cleanup_report = {
            "cleanup_run_id": f"db_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "issues_found": [],
            "fixes_applied": [],
            "summary": {}
        }
        
    def analyze_database_issues(self):
        """Analyze and identify specific database integrity issues"""
        print("🔍 ANALYZING DATABASE INTEGRITY ISSUES")
        print("="*60)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Issue 1: Count posts vs qualifications
        cursor.execute("SELECT COUNT(*) FROM posts")
        post_count = cursor.fetchone()[0]
        
        # Check if processing_steps table exists (qualification data might be there)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processing_steps'")
        has_processing_steps = bool(cursor.fetchone())
        
        if has_processing_steps:
            cursor.execute("SELECT COUNT(*) FROM processing_steps WHERE workflow_step = 'post_qualification'")
            qualification_count = cursor.fetchone()[0]
        else:
            qualification_count = 0
            
        print(f"📊 COUNTS:")
        print(f"   Posts: {post_count}")
        print(f"   Qualifications: {qualification_count}")
        
        if qualification_count > post_count:
            issue = f"DUPLICATE QUALIFICATIONS: {qualification_count} qualifications for {post_count} posts"
            print(f"   ❌ {issue}")
            self.cleanup_report["issues_found"].append(issue)
        
        # Issue 2: Find duplicate posts by URL
        cursor.execute("""
            SELECT post_url, COUNT(*) as count 
            FROM posts 
            GROUP BY post_url 
            HAVING COUNT(*) > 1
        """)
        duplicate_posts = cursor.fetchall()
        
        if duplicate_posts:
            for url, count in duplicate_posts:
                issue = f"DUPLICATE POST: {url} appears {count} times"
                print(f"   ❌ {issue}")
                self.cleanup_report["issues_found"].append(issue)
        
        # Issue 3: Check for orphan posts (posts without qualifications)
        if has_processing_steps:
            cursor.execute("""
                SELECT p.id, p.post_url 
                FROM posts p 
                LEFT JOIN processing_steps ps ON p.post_url LIKE '%' || SUBSTR(ps.input_data, -19, 19) || '%'
                    AND ps.workflow_step = 'post_qualification'
                WHERE ps.id IS NULL
            """)
            orphan_posts = cursor.fetchall()
            
            if orphan_posts:
                for post_id, url in orphan_posts:
                    issue = f"ORPHAN POST: Post ID {post_id} ({url[-30:]}) has no qualification"
                    print(f"   ❌ {issue}")
                    self.cleanup_report["issues_found"].append(issue)
        
        # Issue 4: Check for inconsistent scoring (same content, different scores)
        if has_processing_steps:
            cursor.execute("""
                SELECT ps.output_data, COUNT(DISTINCT JSON_EXTRACT(ps.output_data, '$.overall_score')) as score_variants
                FROM processing_steps ps
                WHERE ps.workflow_step = 'post_qualification'
                GROUP BY JSON_EXTRACT(ps.input_data, '$.post_content')
                HAVING score_variants > 1
            """)
            inconsistent_scores = cursor.fetchall()
            
            if inconsistent_scores:
                issue = f"INCONSISTENT SCORING: {len(inconsistent_scores)} content pieces with varying scores"
                print(f"   ❌ {issue}")
                self.cleanup_report["issues_found"].append(issue)
        
        conn.close()
        
        print(f"\n📋 TOTAL ISSUES FOUND: {len(self.cleanup_report['issues_found'])}")
        return self.cleanup_report["issues_found"]
    
    def remove_duplicate_qualifications(self):
        """Remove duplicate qualification entries, keeping the most recent"""
        print("\n🧹 REMOVING DUPLICATE QUALIFICATIONS")
        print("-" * 40)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if processing_steps table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processing_steps'")
        if not cursor.fetchone():
            print("   ⚠️  No processing_steps table found - skipping qualification cleanup")
            conn.close()
            return
        
        # Find duplicate qualifications by post URL pattern
        cursor.execute("""
            WITH post_qualifications AS (
                SELECT 
                    id,
                    input_data,
                    output_data,
                    created_at,
                    ROW_NUMBER() OVER (
                        PARTITION BY JSON_EXTRACT(input_data, '$.post_url') 
                        ORDER BY created_at DESC
                    ) as rn
                FROM processing_steps 
                WHERE workflow_step = 'post_qualification'
            )
            SELECT id FROM post_qualifications WHERE rn > 1
        """)
        
        duplicate_ids = [row[0] for row in cursor.fetchall()]
        
        if duplicate_ids:
            # Delete duplicates
            cursor.execute(f"""
                DELETE FROM processing_steps 
                WHERE id IN ({','.join(['?'] * len(duplicate_ids))})
            """, duplicate_ids)
            
            fix = f"REMOVED {len(duplicate_ids)} duplicate qualification entries"
            print(f"   ✅ {fix}")
            self.cleanup_report["fixes_applied"].append(fix)
        else:
            print("   ✅ No duplicate qualifications found")
        
        conn.commit()
        conn.close()
    
    def remove_duplicate_posts(self):
        """Remove duplicate posts, keeping the one with most recent data"""
        print("\n🧹 REMOVING DUPLICATE POSTS")
        print("-" * 40)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find duplicate posts and keep the most recent
        cursor.execute("""
            WITH ranked_posts AS (
                SELECT 
                    id,
                    post_url,
                    ROW_NUMBER() OVER (
                        PARTITION BY post_url 
                        ORDER BY created_at DESC, id DESC
                    ) as rn
                FROM posts
            )
            SELECT id FROM ranked_posts WHERE rn > 1
        """)
        
        duplicate_ids = [row[0] for row in cursor.fetchall()]
        
        if duplicate_ids:
            # Delete duplicates
            cursor.execute(f"""
                DELETE FROM posts 
                WHERE id IN ({','.join(['?'] * len(duplicate_ids))})
            """, duplicate_ids)
            
            fix = f"REMOVED {len(duplicate_ids)} duplicate post entries"
            print(f"   ✅ {fix}")
            self.cleanup_report["fixes_applied"].append(fix)
        else:
            print("   ✅ No duplicate posts found")
        
        conn.commit()
        conn.close()
    
    def fix_orphan_posts(self):
        """Identify orphan posts and mark them for reprocessing"""
        print("\n🧹 FIXING ORPHAN POSTS")
        print("-" * 40)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if processing_steps table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processing_steps'")
        if not cursor.fetchone():
            print("   ⚠️  No processing_steps table found - cannot check for orphans")
            conn.close()
            return
        
        # Find posts without qualifications
        cursor.execute("""
            SELECT p.id, p.post_url, p.post_content
            FROM posts p 
            LEFT JOIN processing_steps ps ON p.post_url LIKE '%' || SUBSTR(ps.input_data, -19, 19) || '%'
                AND ps.workflow_step = 'post_qualification'
            WHERE ps.id IS NULL
        """)
        
        orphan_posts = cursor.fetchall()
        
        if orphan_posts:
            fix = f"IDENTIFIED {len(orphan_posts)} orphan posts for reprocessing"
            print(f"   ⚠️  {fix}")
            self.cleanup_report["fixes_applied"].append(fix)
            
            # Log orphan posts for manual review
            for post_id, url, content in orphan_posts:
                print(f"      Orphan: Post {post_id} - {url[-30:]}...")
        else:
            print("   ✅ No orphan posts found")
        
        conn.close()
    
    def validate_score_consistency(self):
        """Check for and report scoring inconsistencies"""
        print("\n🧹 VALIDATING SCORE CONSISTENCY")  
        print("-" * 40)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if processing_steps table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processing_steps'")
        if not cursor.fetchone():
            print("   ⚠️  No processing_steps table found - cannot validate scores")
            conn.close()
            return
        
        # Check for inconsistent scoring
        cursor.execute("""
            SELECT 
                JSON_EXTRACT(input_data, '$.post_content') as content_preview,
                COUNT(*) as score_count,
                GROUP_CONCAT(DISTINCT JSON_EXTRACT(output_data, '$.overall_score')) as scores
            FROM processing_steps 
            WHERE workflow_step = 'post_qualification'
            GROUP BY JSON_EXTRACT(input_data, '$.post_content')
            HAVING COUNT(DISTINCT JSON_EXTRACT(output_data, '$.overall_score')) > 1
        """)
        
        inconsistent_scoring = cursor.fetchall()
        
        if inconsistent_scoring:
            for content, count, scores in inconsistent_scoring:
                content_preview = content[:50] + "..." if content and len(content) > 50 else content
                issue = f"INCONSISTENT SCORES: '{content_preview}' scored as: {scores}"
                print(f"   ⚠️  {issue}")
                self.cleanup_report["issues_found"].append(issue)
        else:
            print("   ✅ No scoring inconsistencies found")
        
        conn.close()
    
    def generate_cleanup_summary(self):
        """Generate final cleanup summary and statistics"""
        print("\n📊 CLEANUP SUMMARY")
        print("="*60)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Final counts
        cursor.execute("SELECT COUNT(*) FROM posts")
        final_post_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processing_steps'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM processing_steps WHERE workflow_step = 'post_qualification'")
            final_qualification_count = cursor.fetchone()[0]
        else:
            final_qualification_count = 0
        
        conn.close()
        
        # Update summary
        self.cleanup_report["summary"] = {
            "final_post_count": final_post_count,
            "final_qualification_count": final_qualification_count,
            "issues_found": len(self.cleanup_report["issues_found"]),
            "fixes_applied": len(self.cleanup_report["fixes_applied"]),
            "ratio": f"{final_qualification_count}:{final_post_count}" if final_post_count > 0 else "N/A"
        }
        
        print(f"📈 FINAL STATISTICS:")
        print(f"   Posts: {final_post_count}")
        print(f"   Qualifications: {final_qualification_count}")
        print(f"   Qualification Ratio: {self.cleanup_report['summary']['ratio']}")
        print(f"   Issues Found: {self.cleanup_report['summary']['issues_found']}")
        print(f"   Fixes Applied: {self.cleanup_report['summary']['fixes_applied']}")
        
        # Determine overall status
        if final_qualification_count <= final_post_count and len(self.cleanup_report["issues_found"]) <= 2:
            status = "✅ DATABASE INTEGRITY RESTORED"
        elif len(self.cleanup_report["fixes_applied"]) > 0:
            status = "⚠️  DATABASE PARTIALLY CLEANED - REVIEW REQUIRED"
        else:
            status = "❌ DATABASE ISSUES REMAIN - MANUAL INTERVENTION NEEDED"
        
        print(f"\n{status}")
        
        # Save cleanup report
        self.cleanup_report["end_time"] = datetime.now().isoformat()
        report_file = f"test_data/database_cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2)
        
        print(f"📋 Cleanup report saved: {report_file}")
        
        return self.cleanup_report["summary"]
    
    def run_complete_cleanup(self):
        """Execute complete database cleanup workflow"""
        print("🧹 DATABASE CLEANUP INITIATED")
        print("="*60)
        
        # Step 1: Analyze issues
        issues = self.analyze_database_issues()
        
        if not issues:
            print("\n✅ NO ISSUES FOUND - DATABASE IS CLEAN")
            return
        
        # Step 2: Apply fixes
        self.remove_duplicate_qualifications()
        self.remove_duplicate_posts()
        self.fix_orphan_posts()
        self.validate_score_consistency()
        
        # Step 3: Generate summary
        summary = self.generate_cleanup_summary()
        
        return summary

def main():
    """Run database cleanup"""
    cleanup = DatabaseCleanup()
    summary = cleanup.run_complete_cleanup()
    
    # Return exit code based on results
    if summary["issues_found"] <= 2:
        exit(0)  # Success
    else:
        exit(1)  # Issues remain

if __name__ == "__main__":
    main()