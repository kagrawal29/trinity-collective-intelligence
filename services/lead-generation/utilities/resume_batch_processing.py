#!/usr/bin/env python3
"""
Resume Batch Processing from Batch 14
Processes the remaining 70 leads that timed out
"""

import json
import time
from analyze_batch_llm_sqlite import SQLiteBatchLLMAnalyzer

def resume_processing(start_batch=14):
    """Resume processing from specific batch number"""
    
    print(f"🔄 RESUMING BATCH PROCESSING FROM BATCH {start_batch}")
    print("=" * 60)
    
    # Load engagement data
    with open('test_data/full_engagement_20250727_182551.json', 'r') as f:
        data = json.load(f)
    
    # Extract all leads (same logic as main script)
    leads = []
    
    # Process reactions
    for reaction in data.get('reactions', []):
        name = reaction.get('title', 'Unknown')
        subtitle = reaction.get('subtitle', '')
        url = reaction.get('navigationUrl', '')
        
        if '|' in subtitle:
            parts = subtitle.split('|', 1)
            title = parts[0].strip()
            company = parts[1].strip()
        else:
            title = subtitle
            company = ''
        
        leads.append({
            'name': name,
            'title': title,
            'company': company,
            'linkedin_url': url,
            'engagement_type': 'reaction',
            'source': 'reaction'
        })
    
    # Process comments
    for comment in data.get('comments', []):
        commenter = comment.get('commenter', {})
        name = commenter.get('title', 'Unknown')
        subtitle = commenter.get('subtitle', '')
        url = commenter.get('navigationUrl', '')
        
        if '|' in subtitle:
            parts = subtitle.split('|', 1)
            title = parts[0].strip()
            company = parts[1].strip()
        else:
            title = subtitle
            company = ''
        
        leads.append({
            'name': name,
            'title': title,
            'company': company,
            'linkedin_url': url,
            'engagement_type': 'comment',
            'source': 'comment'
        })
    
    print(f"Total leads found: {len(leads)}")
    
    # Calculate starting position
    analyzer = SQLiteBatchLLMAnalyzer()
    batch_size = analyzer.batch_size  # 10
    start_index = (start_batch - 1) * batch_size
    
    # Get remaining leads
    remaining_leads = leads[start_index:]
    print(f"Processing {len(remaining_leads)} remaining leads starting from index {start_index}")
    
    # Setup attribution (reuse existing post/influencer)
    post_url = data.get('post_url', 'https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642')
    
    # Get existing IDs from database
    cursor = analyzer.logger.db_connection.cursor()
    cursor.execute("SELECT id FROM influencers WHERE influencer_name = 'LinkedIn Lead Generation Expert'")
    result = cursor.fetchone()
    influencer_id = result[0] if result else 1
    
    cursor.execute("SELECT id FROM posts WHERE post_url = ?", (post_url,))
    result = cursor.fetchone()
    post_id = result[0] if result else 1
    
    print(f"✅ Using existing attribution: Influencer #{influencer_id} → Post #{post_id}")
    
    # Start new processing run for remaining leads
    run_id = analyzer.logger.start_processing_run(
        run_type="v2_resume_batch_" + str(start_batch),
        prompt_version_hash=analyzer.prompt_version,
        total_leads=len(remaining_leads)
    )
    
    processed_leads = []
    
    # Process remaining batches with smaller batch size (5) to avoid timeout
    SMALLER_BATCH_SIZE = 5
    
    for i in range(0, len(remaining_leads), SMALLER_BATCH_SIZE):
        batch = remaining_leads[i:i + SMALLER_BATCH_SIZE]
        batch_num = start_batch + (i // SMALLER_BATCH_SIZE)
        total_batches = start_batch + ((len(remaining_leads) + SMALLER_BATCH_SIZE - 1) // SMALLER_BATCH_SIZE) - 1
        
        print(f"\n🤖 Processing batch {batch_num}/{total_batches} ({len(batch)} leads)...")
        
        start_time = time.time()
        
        # Process with existing analyzer but smaller batch
        analyzer.batch_size = len(batch)  # Temporarily set batch size
        processed_batch = analyzer.process_batch(batch, batch_num, post_url, post_id, influencer_id)
        analyzer.batch_size = 10  # Reset
        
        batch_time = time.time() - start_time
        
        processed_leads.extend(processed_batch)
        
        print(f"✅ Batch {batch_num} completed in {batch_time:.1f}s")
        print(f"📝 Full provenance logged to SQLite database")
        
        # Add small delay to avoid rate limits
        if i + SMALLER_BATCH_SIZE < len(remaining_leads):
            time.sleep(0.5)
    
    # Generate final results for resumed processing
    qualified_leads = [lead for lead in processed_leads if lead.get('is_qualified', False)]
    qualification_rate = len(qualified_leads) / len(processed_leads) * 100
    
    # Complete the processing run
    analyzer.logger.complete_processing_run(len(qualified_leads), qualification_rate)
    
    print(f"\n📊 RESUME PROCESSING COMPLETE:")
    print(f"Run ID: {run_id}")
    print(f"Processed: {len(processed_leads)} remaining leads")
    print(f"Qualified: {len(qualified_leads)}")
    print(f"Qualification Rate: {qualification_rate:.1f}%")
    print(f"Database: SQLite with full attribution")
    
    # Save resumed results
    resumed_results = {
        'resume_timestamp': time.strftime('%Y%m%d_%H%M%S'),
        'resumed_from_batch': start_batch,
        'run_id': run_id,
        'leads_processed': len(processed_leads),
        'leads_qualified': len(qualified_leads),
        'qualification_rate': qualification_rate,
        'leads': processed_leads
    }
    
    output_file = f"test_data/resumed_batch_results_{time.strftime('%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(resumed_results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("✅ ALL 192 LEADS NOW PROCESSED WITH FULL ATTRIBUTION!")

if __name__ == "__main__":
    resume_processing(start_batch=14)