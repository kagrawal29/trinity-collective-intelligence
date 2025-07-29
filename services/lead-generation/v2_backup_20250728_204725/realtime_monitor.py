#!/usr/bin/env python3
"""
Real-time Lead Processing Monitor
Shows live progress of lead qualification with visual dashboard
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List

class RealTimeMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.stats = {
            'total_processed': 0,
            'qualified': 0,
            'tier1': 0,  # 85-90
            'tier2': 0,  # 70-84
            'tier3': 0,  # 65-75
            'tier4': 0,  # 20-40
            'unqualified': 0,
            'api_calls': 0,
            'cache_hits': 0
        }
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def get_tier(self, score: int) -> int:
        """Determine tier from score"""
        if score >= 85:
            return 1
        elif score >= 70:
            return 2
        elif score >= 65:
            return 3
        elif score >= 20:
            return 4
        return 0  # Unqualified
    
    def update_stats(self, lead: Dict):
        """Update statistics with new lead"""
        self.stats['total_processed'] += 1
        
        score = lead.get('llm_score', 0)
        tier = self.get_tier(score)
        
        if lead.get('is_qualified', False):
            self.stats['qualified'] += 1
            
        if tier == 1:
            self.stats['tier1'] += 1
        elif tier == 2:
            self.stats['tier2'] += 1
        elif tier == 3:
            self.stats['tier3'] += 1
        elif tier == 4:
            self.stats['tier4'] += 1
        else:
            self.stats['unqualified'] += 1
    
    def create_bar(self, value: int, max_value: int, width: int = 40) -> str:
        """Create ASCII progress bar"""
        if max_value == 0:
            return '░' * width
        
        filled = int((value / max_value) * width)
        bar = '█' * filled + '░' * (width - filled)
        return bar
    
    def display_dashboard(self, current_batch: int = 0, total_batches: int = 0):
        """Display real-time dashboard"""
        self.clear_screen()
        
        elapsed = time.time() - self.start_time
        rate = self.stats['total_processed'] / elapsed if elapsed > 0 else 0
        
        print("🎯 REAL-TIME LEAD QUALIFICATION MONITOR")
        print("=" * 80)
        print(f"⏱️  Elapsed: {elapsed:.1f}s | Rate: {rate:.1f} leads/sec")
        print(f"📊 Batch Progress: {current_batch}/{total_batches}")
        print("=" * 80)
        
        # Overall progress
        total = self.stats['total_processed']
        qualified = self.stats['qualified']
        qual_rate = (qualified / total * 100) if total > 0 else 0
        
        print(f"\n📈 OVERALL PROGRESS: {total} leads processed")
        print(f"   Qualified: {qualified} ({qual_rate:.1f}%)")
        print(f"   {self.create_bar(qualified, total)} {qualified}/{total}")
        
        # Tier breakdown
        print(f"\n🏆 TIER BREAKDOWN:")
        
        # Tier 1
        tier1_pct = (self.stats['tier1'] / total * 100) if total > 0 else 0
        print(f"   TIER 1 (85-90): {self.stats['tier1']:3d} ({tier1_pct:5.1f}%) C-Level Executives")
        print(f"   {self.create_bar(self.stats['tier1'], total, 30)}")
        
        # Tier 2
        tier2_pct = (self.stats['tier2'] / total * 100) if total > 0 else 0
        print(f"   TIER 2 (70-84): {self.stats['tier2']:3d} ({tier2_pct:5.1f}%) Growth Roles")
        print(f"   {self.create_bar(self.stats['tier2'], total, 30)}")
        
        # Tier 3
        tier3_pct = (self.stats['tier3'] / total * 100) if total > 0 else 0
        print(f"   TIER 3 (65-75): {self.stats['tier3']:3d} ({tier3_pct:5.1f}%) Enterprise Partners")
        print(f"   {self.create_bar(self.stats['tier3'], total, 30)}")
        
        # Tier 4
        tier4_pct = (self.stats['tier4'] / total * 100) if total > 0 else 0
        print(f"   TIER 4 (20-40): {self.stats['tier4']:3d} ({tier4_pct:5.1f}%) Service Providers")
        print(f"   {self.create_bar(self.stats['tier4'], total, 30)}")
        
        # Unqualified
        unqual_pct = (self.stats['unqualified'] / total * 100) if total > 0 else 0
        print(f"   Unqualified:    {self.stats['unqualified']:3d} ({unqual_pct:5.1f}%)")
        print(f"   {self.create_bar(self.stats['unqualified'], total, 30)}")
        
        # Performance metrics
        print(f"\n⚡ PERFORMANCE:")
        print(f"   API Calls: {self.stats.get('api_calls', 0)}")
        print(f"   Cache Hits: {self.stats.get('cache_hits', 0)}")
        cache_rate = (self.stats.get('cache_hits', 0) / total * 100) if total > 0 else 0
        print(f"   Cache Hit Rate: {cache_rate:.1f}%")
        
        # Estimated time remaining
        if current_batch > 0 and total_batches > 0:
            batches_per_sec = current_batch / elapsed if elapsed > 0 else 0
            remaining_batches = total_batches - current_batch
            eta_seconds = remaining_batches / batches_per_sec if batches_per_sec > 0 else 0
            print(f"   ETA: {eta_seconds/60:.1f} minutes")
    
    def show_top_leads(self, leads: List[Dict], count: int = 5):
        """Display top qualified leads"""
        print(f"\n🌟 TOP {count} QUALIFIED LEADS:")
        print("-" * 80)
        
        qualified = [l for l in leads if l.get('is_qualified', False)]
        sorted_leads = sorted(qualified, key=lambda x: x.get('llm_score', 0), reverse=True)
        
        for i, lead in enumerate(sorted_leads[:count], 1):
            print(f"{i}. {lead['name']}")
            print(f"   {lead['title']} at {lead['company']}")
            print(f"   Score: {lead.get('llm_score', 0)}/100 (Tier {self.get_tier(lead.get('llm_score', 0))})")
            print(f"   {lead.get('llm_reasoning', 'N/A')}")
            print()

def simulate_realtime_processing():
    """Simulate real-time processing with the monitor"""
    monitor = RealTimeMonitor()
    
    # Load some test data
    try:
        with open('test_data/batch_llm_results_195536.json', 'r') as f:
            data = json.load(f)
        
        leads = data.get('leads', [])
        batch_size = 10
        total_batches = (len(leads) + batch_size - 1) // batch_size
        
        # Simulate processing
        for batch_num in range(1, total_batches + 1):
            start_idx = (batch_num - 1) * batch_size
            end_idx = min(start_idx + batch_size, len(leads))
            
            batch = leads[start_idx:end_idx]
            
            # Update stats for each lead in batch
            for lead in batch:
                monitor.update_stats(lead)
            
            # Display dashboard
            monitor.display_dashboard(batch_num, total_batches)
            
            # Show top leads periodically
            if batch_num % 5 == 0 or batch_num == total_batches:
                monitor.show_top_leads(leads[:end_idx])
            
            # Simulate processing time
            time.sleep(0.5)
        
        print("\n✅ PROCESSING COMPLETE!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Real-time Lead Monitor Demo...")
    time.sleep(2)
    simulate_realtime_processing()