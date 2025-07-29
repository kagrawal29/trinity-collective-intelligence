#!/usr/bin/env python3
"""
Emergency Lead Storage Solution
Directly store the 151 qualified leads from the analysis
"""

import json
import sqlite3
from datetime import datetime

def store_qualified_leads():
    """Store qualified leads directly into database"""
    
    # Load the analysis results
    with open('test_data/realtime_analysis_20250728_075551.json', 'r') as f:
        data = json.load(f)
    
    # Connect to database
    conn = sqlite3.connect('trinity_logging.db')
    cursor = conn.cursor()
    
    # Create leads table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            name TEXT,
            job_title TEXT,
            company TEXT,
            profile_url TEXT,
            profile_urn TEXT,
            engagement_type TEXT,
            source_type TEXT,
            qualification_score INTEGER,
            qualification_status TEXT,
            comment_text TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id)
        )
    ''')
    
    # Get the post_id for our test post - extract from first lead
    if not data['leads']:
        print("❌ No leads found in data")
        return
        
    post_url = data['leads'][0]['post_url']
    cursor.execute('SELECT id FROM posts WHERE post_url = ?', (post_url,))
    result = cursor.fetchone()
    
    if not result:
        print(f"❌ Post not found in database: {post_url}")
        return
    
    post_id = result[0]
    print(f"✅ Found post ID: {post_id} for URL: {post_url}")
    
    # Store only qualified leads (with score >= 70)
    qualified_leads = [lead for lead in data['leads'] if lead.get('llm_score', 0) >= 70]
    print(f"📊 Found {len(qualified_leads)} qualified leads to store")
    stored_count = 0
    
    for lead in qualified_leads:
        try:
            cursor.execute('''
                INSERT INTO leads (
                    post_id, name, job_title, company, profile_url, profile_urn,
                    engagement_type, source_type, qualification_score, 
                    qualification_status, comment_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post_id,
                lead['name'],
                lead.get('title', ''),
                lead.get('company', ''),
                lead.get('linkedin_url', ''),
                lead.get('profile_urn', ''),
                lead.get('engagement_type', ''),
                lead.get('source', ''),
                lead.get('llm_score', 0),
                'QUALIFIED',
                lead.get('comment', '')
            ))
            stored_count += 1
            
        except Exception as e:
            print(f"❌ Failed to store {lead['name']}: {e}")
    
    conn.commit()
    
    # Verify storage
    cursor.execute('SELECT COUNT(*) FROM leads WHERE post_id = ?', (post_id,))
    total_leads = cursor.fetchone()[0]
    
    print(f"\n🎉 STORAGE COMPLETE!")
    print(f"✅ Stored {stored_count} qualified leads")
    print(f"📊 Total leads for post {post_id}: {total_leads}")
    
    # Show top 5 stored leads
    cursor.execute('''
        SELECT name, job_title, qualification_score 
        FROM leads 
        WHERE post_id = ? 
        ORDER BY qualification_score DESC 
        LIMIT 5
    ''', (post_id,))
    
    print("\n🏆 TOP 5 STORED LEADS:")
    for i, (name, title, score) in enumerate(cursor.fetchall(), 1):
        print(f"{i}. {name} - {title} (Score: {score})")
    
    conn.close()

if __name__ == "__main__":
    store_qualified_leads()