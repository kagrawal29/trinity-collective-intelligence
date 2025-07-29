#!/usr/bin/env python3
"""
SQLite Database Viewer for Trinity Lead Generation System
Easy way to explore stored leads and processing logs
"""

import sqlite3
import json
from datetime import datetime

def view_database(db_path="trinity_logging.db"):
    """View and analyze the SQLite database contents"""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🗄️  TRINITY LEAD GENERATION DATABASE")
    print("=" * 60)
    
    # 1. Processing Runs Summary
    print("\n📊 PROCESSING RUNS:")
    cursor.execute("""
        SELECT run_id, run_type, total_leads, total_qualified, 
               qualification_rate, status, started_at
        FROM processing_runs 
        ORDER BY started_at DESC
    """)
    
    runs = cursor.fetchall()
    for run in runs:
        print(f"Run: {run['run_id']}")
        print(f"  Type: {run['run_type']}")
        print(f"  Leads: {run['total_leads']} → {run['total_qualified']} qualified ({run['qualification_rate']:.1f}%)")
        print(f"  Status: {run['status']} at {run['started_at']}")
        print()
    
    # 2. Lead Qualification Results
    print("\n👥 QUALIFIED LEADS (Score ≥ 70):")
    cursor.execute("""
        SELECT lead_name, lead_title, lead_company, llm_score, 
               tier_classification, llm_reasoning, linkedin_url
        FROM lead_qualification_results 
        WHERE is_qualified = 1
        ORDER BY llm_score DESC
    """)
    
    qualified = cursor.fetchall()
    for i, lead in enumerate(qualified, 1):
        print(f"{i}. {lead['lead_name']} (Score: {lead['llm_score']}/100)")
        print(f"   Title: {lead['lead_title']}")
        print(f"   Company: {lead['lead_company']}")
        print(f"   Tier: {lead['tier_classification']}")
        print(f"   Reasoning: {lead['llm_reasoning']}")
        print(f"   LinkedIn: {lead['linkedin_url']}")
        print()
    
    # 3. Score Distribution
    print("\n📈 SCORE DISTRIBUTION:")
    cursor.execute("""
        SELECT 
            tier_classification,
            COUNT(*) as count,
            AVG(llm_score) as avg_score,
            MIN(llm_score) as min_score,
            MAX(llm_score) as max_score
        FROM lead_qualification_results 
        GROUP BY tier_classification
        ORDER BY avg_score DESC
    """)
    
    tiers = cursor.fetchall()
    for tier in tiers:
        print(f"{tier['tier_classification']}: {tier['count']} leads")
        print(f"  Avg Score: {tier['avg_score']:.1f}")
        print(f"  Range: {tier['min_score']}-{tier['max_score']}")
        print()
    
    # 4. Processing Performance
    print("\n⚡ PROCESSING PERFORMANCE:")
    cursor.execute("""
        SELECT 
            workflow_step,
            COUNT(*) as executions,
            AVG(execution_time_ms) as avg_time,
            SUM(leads_processed) as total_leads,
            SUM(leads_qualified) as total_qualified
        FROM processing_logs 
        WHERE status = 'success'
        GROUP BY workflow_step
    """)
    
    performance = cursor.fetchall()
    for perf in performance:
        print(f"{perf['workflow_step']}: {perf['executions']} executions")
        print(f"  Avg Time: {perf['avg_time']:.0f}ms")
        print(f"  Processed: {perf['total_leads']} leads → {perf['total_qualified']} qualified")
        print()
    
    # 5. Latest Processing Details
    print("\n🔍 LATEST PROCESSING DETAILS:")
    cursor.execute("""
        SELECT * FROM processing_logs 
        ORDER BY created_at DESC 
        LIMIT 3
    """)
    
    logs = cursor.fetchall()
    for log in logs:
        print(f"Step: {log['workflow_step']} ({log['status']})")
        print(f"  Run ID: {log['run_id']}")
        print(f"  Time: {log['execution_time_ms']}ms")
        print(f"  Leads: {log['leads_processed']} → {log['leads_qualified']} qualified")
        print()
    
    conn.close()
    
    print("✅ Database exploration complete!")
    print(f"📊 Database size: {sqlite3.connect(db_path).execute('PRAGMA page_count').fetchone()[0] * 4096 / 1024:.1f} KB")

def export_qualified_leads(db_path="trinity_logging.db", output_file="qualified_leads.json"):
    """Export qualified leads to JSON file"""
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT lead_name, lead_title, lead_company, llm_score, 
               tier_classification, llm_reasoning, linkedin_url,
               engagement_type, batch_number, created_at
        FROM lead_qualification_results 
        WHERE is_qualified = 1
        ORDER BY llm_score DESC
    """)
    
    qualified = [dict(row) for row in cursor.fetchall()]
    
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "total_qualified": len(qualified),
        "leads": qualified
    }
    
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"✅ Exported {len(qualified)} qualified leads to {output_file}")
    conn.close()

if __name__ == "__main__":
    print("Choose an option:")
    print("1. View database summary")
    print("2. Export qualified leads to JSON")
    print("3. Both")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice in ["1", "3"]:
        view_database()
    
    if choice in ["2", "3"]:
        export_qualified_leads()