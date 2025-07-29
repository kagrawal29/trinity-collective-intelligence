"""CSV processor for lead data"""

import csv
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from database.models import Lead
from database.manager import DatabaseManager
from utils.linkedin_url_parser import extract_username_from_row


class CSVProcessor:
    """Handles CSV input/output operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def import_leads(self, csv_file: str, resume: bool = True) -> int:
        """
        Import leads from CSV file into database
        
        Args:
            csv_file: Path to CSV file
            resume: Skip already processed leads
            
        Returns:
            Number of leads imported
        """
        print(f"\n📥 Importing leads from {csv_file}")
        
        # Read CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        imported = 0
        skipped = 0
        
        for i, row in enumerate(rows):
            # Extract LinkedIn URL
            linkedin_url = self._extract_linkedin_url(row)
            
            if not linkedin_url:
                print(f"  ⚠️  Row {i+1}: No LinkedIn URL found, skipping")
                continue
            
            # Check if already exists
            if resume:
                existing = self.db.get_connection()
                with existing as conn:
                    exists = conn.execute(
                        "SELECT id FROM leads WHERE source_file = ? AND source_row_number = ?",
                        (csv_file, i)
                    ).fetchone()
                
                if exists:
                    skipped += 1
                    continue
            
            # Create lead record
            lead = Lead(
                source_file=csv_file,
                source_row_number=i,
                linkedin_url=linkedin_url,
                original_data=row,
                processing_status='pending'
            )
            
            self.db.save_lead(lead)
            imported += 1
            
            if imported % 100 == 0:
                print(f"  ✅ Imported {imported} leads...")
        
        print(f"\n📊 Import complete:")
        print(f"  - Total rows: {len(rows)}")
        print(f"  - Imported: {imported}")
        print(f"  - Skipped: {skipped}")
        
        return imported
    
    def export_results(self, source_file: str, output_file: str = None, 
                      qualified_only: bool = False) -> str:
        """
        Export results to CSV
        
        Args:
            source_file: Original source file
            output_file: Output file path (auto-generated if None)
            qualified_only: Export only qualified leads
            
        Returns:
            Path to output file
        """
        if not output_file:
            suffix = '_qualified' if qualified_only else '_processed'
            output_file = source_file.replace('.csv', f'{suffix}.csv')
        
        print(f"\n📤 Exporting results to {output_file}")
        
        # Get leads with qualifications
        with self.db.get_connection() as conn:
            query = """
                SELECT 
                    l.original_data,
                    l.processing_status,
                    l.error_message,
                    p.full_name,
                    p.headline,
                    p.followers,
                    p.connections,
                    q.decision_maker,
                    q.decision_maker_reason,
                    q.competitor,
                    q.competitor_reason,
                    q.influencer_score,
                    q.influencer_reason,
                    q.is_qualified,
                    q.qualification_summary,
                    q.disqualification_reason,
                    q.overall_score
                FROM leads l
                LEFT JOIN profiles p ON l.profile_id = p.id
                LEFT JOIN qualifications q ON p.id = q.profile_id
                WHERE l.source_file = ?
            """
            
            if qualified_only:
                query += " AND q.is_qualified = 1"
            
            query += " ORDER BY l.source_row_number"
            
            rows = conn.execute(query, (source_file,)).fetchall()
        
        # Prepare output data
        output_rows = []
        for row in rows:
            # Parse original data
            original = json.loads(row['original_data']) if row['original_data'] else {}
            
            # Add qualification data
            original.update({
                'processing_status': row['processing_status'],
                'error_message': row['error_message'] or '',
                'full_name': row['full_name'] or '',
                'headline': row['headline'] or '',
                'followers': row['followers'] or 0,
                'connections': row['connections'] or 0,
                'decision_maker': 'TRUE' if row['decision_maker'] else 'FALSE',
                'decision_maker_reason': row['decision_maker_reason'] or '',
                'competitor': 'TRUE' if row['competitor'] else 'FALSE',
                'competitor_reason': row['competitor_reason'] or '',
                'influencer_score': row['influencer_score'] or 0,
                'influencer_reason': row['influencer_reason'] or '',
                'qualified': 'TRUE' if row['is_qualified'] else 'FALSE',
                'qualification_summary': row['qualification_summary'] or '',
                'disqualification_reason': row['disqualification_reason'] or '',
                'overall_score': row['overall_score'] or 0
            })
            
            output_rows.append(original)
        
        # Write CSV
        if output_rows:
            fieldnames = list(output_rows[0].keys())
            
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(output_rows)
        
        print(f"  ✅ Exported {len(output_rows)} leads")
        return output_file
    
    def _extract_linkedin_url(self, row: Dict[str, str]) -> Optional[str]:
        """Extract LinkedIn URL from various possible fields"""
        # First try navigationUrl as requested
        nav_url = row.get('navigationUrl', '')
        if nav_url and 'linkedin.com/in/' in nav_url:
            return nav_url
        
        # Fallback to other fields
        return extract_username_from_row(row)
    
    def get_progress(self, source_file: str) -> Dict[str, Any]:
        """Get processing progress for a file"""
        stats = self.db.get_statistics(source_file)
        
        progress = {
            'total': stats['total_leads'],
            'processed': stats['processed'],
            'qualified': stats['qualified'],
            'pending': stats['total_leads'] - stats['processed'],
            'progress_percent': (stats['processed'] / stats['total_leads'] * 100) 
                              if stats['total_leads'] > 0 else 0
        }
        
        return progress
    
    def create_summary_report(self, source_file: str) -> Dict[str, Any]:
        """Create detailed summary report"""
        with self.db.get_connection() as conn:
            # Overall stats
            overall = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN q.is_qualified = 1 THEN 1 ELSE 0 END) as qualified,
                    SUM(CASE WHEN q.decision_maker = 1 THEN 1 ELSE 0 END) as decision_makers,
                    SUM(CASE WHEN q.competitor = 1 THEN 1 ELSE 0 END) as competitors,
                    SUM(CASE WHEN q.influencer_score >= 70 THEN 1 ELSE 0 END) as influencers,
                    AVG(q.overall_score) as avg_score
                FROM leads l
                LEFT JOIN qualifications q ON l.profile_id = q.profile_id
                WHERE l.source_file = ? AND l.processing_status = 'completed'
            """, (source_file,)).fetchone()
            
            # Top qualified leads
            top_leads = conn.execute("""
                SELECT p.full_name, p.headline, q.overall_score
                FROM leads l
                JOIN profiles p ON l.profile_id = p.id
                JOIN qualifications q ON p.id = q.profile_id
                WHERE l.source_file = ? AND q.is_qualified = 1
                ORDER BY q.overall_score DESC
                LIMIT 10
            """, (source_file,)).fetchall()
            
            # Disqualification reasons
            disqual_reasons = conn.execute("""
                SELECT 
                    CASE 
                        WHEN q.decision_maker = 0 THEN 'Not a decision maker'
                        WHEN q.competitor = 1 THEN 'Competitor'
                        WHEN q.influencer_score >= 70 THEN 'Influencer'
                    END as reason,
                    COUNT(*) as count
                FROM leads l
                JOIN qualifications q ON l.profile_id = q.profile_id
                WHERE l.source_file = ? AND q.is_qualified = 0
                GROUP BY reason
            """, (source_file,)).fetchall()
        
        report = {
            'summary': {
                'total_processed': overall['total'],
                'qualified': overall['qualified'],
                'qualification_rate': (overall['qualified'] / overall['total'] * 100) 
                                    if overall['total'] > 0 else 0,
                'decision_makers': overall['decision_makers'],
                'competitors': overall['competitors'],
                'influencers': overall['influencers'],
                'average_score': overall['avg_score'] or 0
            },
            'top_qualified_leads': [
                {
                    'name': lead['full_name'],
                    'headline': lead['headline'],
                    'score': lead['overall_score']
                }
                for lead in top_leads
            ],
            'disqualification_breakdown': {
                reason['reason']: reason['count']
                for reason in disqual_reasons if reason['reason']
            }
        }
        
        return report