"""Main pipeline orchestrator for lead qualification"""

import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

from database.manager import DatabaseManager
from processors.profile_fetcher import ProfileFetcher
from processors.llm_analyzer import LLMAnalyzer
from processors.csv_processor import CSVProcessor


class LeadQualificationPipeline:
    """Orchestrates the complete lead qualification process"""
    
    def __init__(self, db_path: str = "lead_qualification.db"):
        # Initialize components
        self.db = DatabaseManager(db_path)
        self.fetcher = ProfileFetcher(self.db)
        self.analyzer = LLMAnalyzer(self.db)
        self.csv_processor = CSVProcessor(self.db)
        
        # Processing settings
        self.rate_limit_delay = 2.0  # seconds between API calls (increased to avoid rate limits)
        self.batch_save_interval = 10  # save progress every N leads
    
    def process_csv_file(self, csv_file: str, limit: Optional[int] = None, 
                        resume: bool = True, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Process leads from CSV file
        
        Args:
            csv_file: Input CSV file path
            limit: Maximum number of leads to process
            resume: Resume from last position
            output_file: Output CSV file path
            
        Returns:
            Processing summary
        """
        print("\n" + "="*60)
        print("🚀 LEAD QUALIFICATION PIPELINE")
        print("="*60)
        
        start_time = time.time()
        
        # Step 1: Import leads
        print("\n📥 Step 1: Importing leads...")
        imported = self.csv_processor.import_leads(csv_file, resume=resume)
        
        if imported == 0 and resume:
            print("  ℹ️  No new leads to import. Checking for pending leads...")
        
        # Step 2: Get pending leads
        pending_leads = self.db.get_pending_leads(csv_file, limit=limit)
        
        if not pending_leads:
            print("\n✅ All leads already processed!")
            return self._generate_summary(csv_file, start_time)
        
        print(f"\n📋 Found {len(pending_leads)} leads to process")
        
        # Step 3: Create processing batch
        batch_id = self.db.create_batch(csv_file, len(pending_leads))
        
        # Step 4: Process leads
        print("\n🔄 Step 2: Processing leads...")
        print("-" * 40)
        
        processed = 0
        qualified = 0
        errors = 0
        
        for i, lead_data in enumerate(pending_leads):
            lead_id = lead_data['id']
            linkedin_url = lead_data['linkedin_url']
            
            print(f"\n[{i+1}/{len(pending_leads)}] Processing: {linkedin_url}")
            
            try:
                # Update lead status
                self.db.update_lead_status(lead_id, 'processing')
                
                # Fetch profile
                profile = self.fetcher.fetch_profile(linkedin_url)
                
                if not profile:
                    # Check if it's a 404 or other error
                    error_msg = "Profile not found (404)" if "404" in str(self.fetcher._fetch_from_api(linkedin_url)) else "Failed to fetch profile"
                    raise Exception(error_msg)
                
                # Analyze qualification
                qualification = self.analyzer.analyze_profile(profile)
                
                # Update lead with results
                self.db.update_lead_status(lead_id, 'completed', profile_id=profile.id)
                
                processed += 1
                if qualification.is_qualified:
                    qualified += 1
                    print(f"  🎯 QUALIFIED! Score: {qualification.overall_score}/100")
                else:
                    print(f"  ❌ Not qualified: {qualification.disqualification_reason}")
                
                # Update batch progress
                if processed % self.batch_save_interval == 0:
                    self.db.update_batch_progress(batch_id, processed, qualified)
                    print(f"\n💾 Progress saved: {processed}/{len(pending_leads)} processed")
                
                # Rate limiting
                if i < len(pending_leads) - 1:
                    time.sleep(self.rate_limit_delay)
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
                self.db.update_lead_status(lead_id, 'error', error_message=str(e)[:200])
                errors += 1
        
        # Step 5: Complete batch
        self.db.update_batch_progress(batch_id, processed, qualified)
        self.db.complete_batch(batch_id)
        
        # Step 6: Export results
        print("\n📤 Step 3: Exporting results...")
        output_path = self.csv_processor.export_results(csv_file, output_file)
        
        # Step 7: Generate summary
        summary = self._generate_summary(csv_file, start_time)
        
        # Print summary
        self._print_summary(summary)
        
        return summary
    
    def _generate_summary(self, csv_file: str, start_time: float) -> Dict[str, Any]:
        """Generate processing summary"""
        stats = self.db.get_statistics(csv_file)
        report = self.csv_processor.create_summary_report(csv_file)
        fetcher_stats = self.fetcher.get_stats()
        
        summary = {
            'file': csv_file,
            'duration_seconds': int(time.time() - start_time),
            'statistics': stats,
            'report': report,
            'performance': {
                'api_requests': fetcher_stats['api_requests'],
                'cache_hits': fetcher_stats['cache_hits'],
                'cache_hit_rate': fetcher_stats['cache_hit_rate']
            }
        }
        
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print summary report"""
        print("\n" + "="*60)
        print("📊 PROCESSING COMPLETE")
        print("="*60)
        
        stats = summary['statistics']
        report = summary['report']['summary']
        perf = summary['performance']
        
        print(f"\n📈 Results:")
        print(f"  - Total leads: {stats['total_leads']}")
        print(f"  - Processed: {stats['processed']}")
        print(f"  - Qualified: {stats['qualified']} ({report['qualification_rate']:.1f}%)")
        print(f"  - Average score: {report['average_score']:.1f}/100")
        
        print(f"\n🎯 Breakdown:")
        print(f"  - Decision makers: {report['decision_makers']}")
        print(f"  - Competitors: {report['competitors']}")
        print(f"  - Influencers: {report['influencers']}")
        
        print(f"\n⚡ Performance:")
        print(f"  - Duration: {summary['duration_seconds']}s")
        print(f"  - API requests: {perf['api_requests']}")
        print(f"  - Cache hits: {perf['cache_hits']}")
        print(f"  - Cache hit rate: {perf['cache_hit_rate']:.1f}%")
        
        # Top qualified leads
        if summary['report']['top_qualified_leads']:
            print(f"\n🌟 Top Qualified Leads:")
            for lead in summary['report']['top_qualified_leads'][:5]:
                print(f"  - {lead['name']} ({lead['score']}/100)")
                print(f"    {lead['headline'][:60]}...")
        
        print("\n✅ Done!")
    
    def reanalyze_all(self, csv_file: str):
        """Force re-analysis of all leads with current criteria"""
        print("\n🔄 Re-analyzing all leads with updated criteria...")
        
        with self.db.get_connection() as conn:
            # Get all processed leads
            leads = conn.execute("""
                SELECT l.id, p.*
                FROM leads l
                JOIN profiles p ON l.profile_id = p.id
                WHERE l.source_file = ? AND l.processing_status = 'completed'
            """, (csv_file,)).fetchall()
        
        for lead in leads:
            profile = Profile(
                id=lead['id'],
                linkedin_url=lead['linkedin_url'],
                full_name=lead['full_name'],
                headline=lead['headline'],
                followers=lead['followers'],
                connections=lead['connections'],
                about=lead['about'],
                profile_data=json.loads(lead['profile_data']) if lead['profile_data'] else None
            )
            
            # Force re-analysis
            self.analyzer.analyze_profile(profile, force_reanalyze=True)
        
        print(f"✅ Re-analyzed {len(leads)} profiles")
    
    def export_qualified_only(self, csv_file: str, output_file: str = None):
        """Export only qualified leads"""
        return self.csv_processor.export_results(
            csv_file, 
            output_file or csv_file.replace('.csv', '_qualified_only.csv'),
            qualified_only=True
        )