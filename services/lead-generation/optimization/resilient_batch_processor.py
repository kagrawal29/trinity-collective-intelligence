#!/usr/bin/env python3
"""
Resilient Batch Processor with Auto-Recovery
Implements Guide's architecture for timeout-proof processing
"""

import json
import os
import time
import signal
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import contextmanager
from analyze_batch_llm_sqlite import SQLiteBatchLLMAnalyzer

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds):
    """Context manager for timeout handling"""
    def signal_handler(signum, frame):
        raise TimeoutException("Operation timed out!")
    
    # Set the signal handler and alarm
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)  # Disable alarm

class ResilientBatchProcessor:
    """Resilient processor with automatic checkpoint recovery"""
    
    def __init__(self, checkpoint_file="processing_checkpoint.json"):
        self.checkpoint_file = checkpoint_file
        self.analyzer = SQLiteBatchLLMAnalyzer()
        self.adaptive_batch_size = 10  # Start with default
        self.batch_timeout = 30  # seconds per batch
        self.max_retries = 3
        
    def save_checkpoint(self, batch_num: int, processed_count: int, 
                       run_id: str, post_id: int, influencer_id: int):
        """Save processing state after each successful batch"""
        checkpoint = {
            "last_completed_batch": batch_num,
            "total_processed": processed_count,
            "timestamp": datetime.now().isoformat(),
            "run_id": run_id,
            "post_id": post_id,
            "influencer_id": influencer_id,
            "adaptive_batch_size": self.adaptive_batch_size
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        print(f"💾 Checkpoint saved: Batch {batch_num} completed")
    
    def load_checkpoint(self) -> Optional[Dict]:
        """Load last checkpoint if exists"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            print(f"🔄 Checkpoint found: Resuming from batch {checkpoint['last_completed_batch'] + 1}")
            return checkpoint
        return None
    
    def adapt_batch_size(self, processing_time: float):
        """Dynamically adjust batch size based on performance"""
        if processing_time > 25:  # Taking too long
            self.adaptive_batch_size = max(3, self.adaptive_batch_size - 2)
            print(f"⚡ Reducing batch size to {self.adaptive_batch_size} for faster processing")
        elif processing_time < 10 and self.adaptive_batch_size < 10:
            self.adaptive_batch_size = min(10, self.adaptive_batch_size + 1)
            print(f"⚡ Increasing batch size to {self.adaptive_batch_size}")
    
    def process_with_timeout_recovery(self, batch: List[Dict], batch_num: int, 
                                    post_url: str, post_id: int, influencer_id: int):
        """Process batch with timeout protection and retry logic"""
        retries = 0
        
        while retries < self.max_retries:
            try:
                with timeout(self.batch_timeout):
                    start_time = time.time()
                    
                    # Process the batch
                    processed = self.analyzer.process_batch(
                        batch, batch_num, post_url, post_id, influencer_id
                    )
                    
                    processing_time = time.time() - start_time
                    self.adapt_batch_size(processing_time)
                    
                    return processed
                    
            except TimeoutException:
                retries += 1
                print(f"⏱️ Batch {batch_num} timed out (attempt {retries}/{self.max_retries})")
                
                if retries < self.max_retries:
                    # Reduce batch size for retry
                    self.adaptive_batch_size = max(3, self.adaptive_batch_size // 2)
                    print(f"🔄 Retrying with smaller batch size: {self.adaptive_batch_size}")
                    time.sleep(2)  # Brief pause before retry
                else:
                    print(f"❌ Batch {batch_num} failed after {self.max_retries} attempts")
                    raise
            
            except Exception as e:
                print(f"❌ Error in batch {batch_num}: {e}")
                raise
    
    def process_leads_resilient(self, leads: List[Dict], post_url: str, 
                               post_id: int = None, influencer_id: int = None):
        """Main processing function with full resilience"""
        
        # Check for existing checkpoint
        checkpoint = self.load_checkpoint()
        
        if checkpoint:
            # Resume from checkpoint
            start_batch = checkpoint['last_completed_batch'] + 1
            start_index = checkpoint['total_processed']
            run_id = checkpoint['run_id']
            post_id = post_id or checkpoint['post_id']
            influencer_id = influencer_id or checkpoint['influencer_id']
            self.adaptive_batch_size = checkpoint.get('adaptive_batch_size', 10)
            
            # Skip already processed leads
            remaining_leads = leads[start_index:]
            print(f"📊 Resuming: {len(remaining_leads)} leads remaining")
            
        else:
            # Fresh start
            start_batch = 1
            remaining_leads = leads
            
            # Register post and influencer if not provided
            if not influencer_id:
                influencer_id = self.analyzer.logger.register_influencer(
                    influencer_name="LinkedIn Lead Generation Expert",
                    profile_url="https://www.linkedin.com/in/example-influencer",
                    industry="B2B Sales & Marketing",
                    tier="macro"
                )
            
            if not post_id:
                post_id = self.analyzer.logger.register_post(
                    post_url=post_url,
                    total_reactions=143,
                    total_comments=52,
                    influencer_id=influencer_id
                )
            
            # Start new run
            run_id = self.analyzer.logger.start_processing_run(
                run_type="resilient_processing",
                prompt_version_hash=self.analyzer.prompt_version,
                total_leads=len(leads)
            )
        
        # Process with resilience
        processed_leads = []
        batch_num = start_batch
        
        while remaining_leads:
            # Get next batch with adaptive size
            batch = remaining_leads[:self.adaptive_batch_size]
            remaining_leads = remaining_leads[self.adaptive_batch_size:]
            
            print(f"\n🤖 Processing batch {batch_num} ({len(batch)} leads)...")
            
            try:
                # Process with timeout protection
                processed_batch = self.process_with_timeout_recovery(
                    batch, batch_num, post_url, post_id, influencer_id
                )
                
                processed_leads.extend(processed_batch)
                
                # Save checkpoint after successful batch
                total_processed = len(leads) - len(remaining_leads)
                self.save_checkpoint(batch_num, total_processed, run_id, post_id, influencer_id)
                
                print(f"✅ Batch {batch_num} completed successfully")
                
            except Exception as e:
                print(f"🛑 Fatal error in batch {batch_num}: {e}")
                print(f"💡 Run this script again to resume from batch {batch_num}")
                break
            
            batch_num += 1
            
            # Brief pause between batches to avoid rate limits
            if remaining_leads:
                time.sleep(0.5)
        
        # Complete the run if all processed
        if not remaining_leads:
            qualified_leads = [l for l in processed_leads if l.get('is_qualified', False)]
            qualification_rate = len(qualified_leads) / len(processed_leads) * 100
            
            self.analyzer.logger.complete_processing_run(len(qualified_leads), qualification_rate)
            
            print(f"\n🎉 PROCESSING COMPLETE!")
            print(f"Total Processed: {len(processed_leads)}")
            print(f"Qualified: {len(qualified_leads)} ({qualification_rate:.1f}%)")
            
            # Clean up checkpoint
            if os.path.exists(self.checkpoint_file):
                os.remove(self.checkpoint_file)
                print("🧹 Checkpoint cleaned up")
        
        return processed_leads


def main():
    """Run resilient processing with auto-recovery"""
    
    print("🛡️ RESILIENT BATCH PROCESSOR")
    print("Features: Auto-recovery, adaptive sizing, timeout protection")
    print("=" * 60)
    
    # Load engagement data
    with open('test_data/full_engagement_20250727_182551.json', 'r') as f:
        data = json.load(f)
    
    # Extract leads (same as original)
    leads = []
    
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
    
    print(f"Found {len(leads)} total leads to process")
    
    # Process with full resilience
    processor = ResilientBatchProcessor()
    post_url = data.get('post_url', 'https://www.linkedin.com/feed/update/urn:li:activity:7353758072894320642')
    
    processor.process_leads_resilient(leads, post_url)


if __name__ == "__main__":
    main()