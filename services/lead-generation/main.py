#!/usr/bin/env python3
"""
Lead Qualification System - Main Entry Point

Usage:
    python main.py process leads.csv --limit 10
    python main.py process leads.csv --resume
    python main.py export leads.csv --qualified-only
    python main.py reanalyze leads.csv
    python main.py stats leads.csv
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pipeline.orchestrator import LeadQualificationPipeline
from database.manager import DatabaseManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description='Lead Qualification System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process first 10 leads:
    python main.py process leads.csv --limit 10
    
  Resume processing:
    python main.py process leads.csv --resume
    
  Export qualified leads only:
    python main.py export leads.csv --qualified-only
    
  Re-analyze with updated criteria:
    python main.py reanalyze leads.csv
    
  View statistics:
    python main.py stats leads.csv
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process leads from CSV')
    process_parser.add_argument('input_file', help='Input CSV file')
    process_parser.add_argument('--limit', type=int, help='Limit number of leads to process')
    process_parser.add_argument('--no-resume', action='store_true', help='Start from beginning')
    process_parser.add_argument('--output', help='Output CSV file path')
    process_parser.add_argument('--delay', type=float, default=2.0, help='Delay between API calls (default: 2.0s)')
    process_parser.add_argument('--db', default='lead_qualification.db', help='Database file')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export results')
    export_parser.add_argument('input_file', help='Original input CSV file')
    export_parser.add_argument('--output', help='Output CSV file path')
    export_parser.add_argument('--qualified-only', action='store_true', help='Export only qualified leads')
    export_parser.add_argument('--db', default='lead_qualification.db', help='Database file')
    
    # Reanalyze command
    reanalyze_parser = subparsers.add_parser('reanalyze', help='Re-analyze all leads')
    reanalyze_parser.add_argument('input_file', help='Original input CSV file')
    reanalyze_parser.add_argument('--db', default='lead_qualification.db', help='Database file')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='View statistics')
    stats_parser.add_argument('input_file', help='Original input CSV file', nargs='?')
    stats_parser.add_argument('--db', default='lead_qualification.db', help='Database file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize pipeline
    pipeline = LeadQualificationPipeline(db_path=args.db)
    
    # Execute command
    if args.command == 'process':
        # Set custom rate limit delay if provided
        if hasattr(args, 'delay'):
            pipeline.rate_limit_delay = args.delay
        
        summary = pipeline.process_csv_file(
            args.input_file,
            limit=args.limit,
            resume=not args.no_resume,
            output_file=args.output
        )
        
    elif args.command == 'export':
        output_path = pipeline.csv_processor.export_results(
            args.input_file,
            args.output,
            qualified_only=args.qualified_only
        )
        print(f"\n✅ Exported to: {output_path}")
        
    elif args.command == 'reanalyze':
        pipeline.reanalyze_all(args.input_file)
        # Export updated results
        output_path = pipeline.csv_processor.export_results(args.input_file)
        print(f"\n✅ Updated results exported to: {output_path}")
        
    elif args.command == 'stats':
        db = DatabaseManager(args.db)
        
        if args.input_file:
            # Stats for specific file
            stats = db.get_statistics(args.input_file)
            report = pipeline.csv_processor.create_summary_report(args.input_file)
            
            print(f"\n📊 Statistics for {args.input_file}")
            print("="*50)
            print(f"Total leads: {stats['total_leads']}")
            print(f"Processed: {stats['processed']}")
            print(f"Qualified: {stats['qualified']}")
            print(f"Qualification rate: {report['summary']['qualification_rate']:.1f}%")
            
            # Disqualification breakdown
            if report['disqualification_breakdown']:
                print("\n❌ Disqualification reasons:")
                for reason, count in report['disqualification_breakdown'].items():
                    print(f"  - {reason}: {count}")
            
            # Top leads
            if report['top_qualified_leads']:
                print("\n🌟 Top qualified leads:")
                for lead in report['top_qualified_leads'][:5]:
                    print(f"  - {lead['name']} (Score: {lead['score']})")
        else:
            # Overall stats
            stats = db.get_statistics()
            print(f"\n📊 Overall Database Statistics")
            print("="*50)
            print(f"Total leads: {stats['total_leads']}")
            print(f"Processed: {stats['processed']}")
            print(f"Qualified: {stats['qualified']}")
            
            # List all source files
            with db.get_connection() as conn:
                files = conn.execute("""
                    SELECT DISTINCT source_file, COUNT(*) as count
                    FROM leads
                    GROUP BY source_file
                """).fetchall()
                
                if files:
                    print("\n📁 Source files:")
                    for file in files:
                        print(f"  - {file['source_file']}: {file['count']} leads")


if __name__ == '__main__':
    main()