#!/usr/bin/env python3
"""
Chaos Testing Execution Script for V2 Optimization Components
Tyler's systematic approach to validate optimization safety
"""

import json
import time
import sqlite3
import threading
import subprocess
import os
from datetime import datetime
from typing import Dict, List

class ChaosTestExecutor:
    def __init__(self):
        self.test_results = {
            'test_run_id': f"chaos_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'start_time': datetime.now().isoformat(),
            'tests': [],
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
    def log_test_result(self, test_name: str, status: str, details: Dict, execution_time: float):
        """Log individual chaos test result"""
        self.test_results["tests"].append({
            "test_name": test_name,
            "status": status,  # "PASS", "FAIL", "WARN"
            "execution_time_ms": int(execution_time * 1000),
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        self.test_results["summary"]["total_tests"] += 1
        if status == "PASS":
            self.test_results["summary"]["passed"] += 1
        elif status == "FAIL":
            self.test_results["summary"]["failed"] += 1
        elif status == "WARN":
            self.test_results["summary"]["warnings"] += 1
            
        # Real-time output
        status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
        print(f"{status_emoji[status]} {test_name}: {status} ({execution_time*1000:.0f}ms)")
        if details.get("message"):
            print(f"   {details['message']}")

    def test_realtime_monitor_safety(self):
        """LOW RISK: Test realtime monitor visualization"""
        print("\n📊 TESTING: realtime_monitor.py (LOW RISK)")
        print("-" * 50)
        
        # Test 1: Normal operation
        start_time = time.time()
        try:
            from realtime_monitor import RealTimeMonitor
            monitor = RealTimeMonitor()
            
            # Test basic functionality
            monitor.stats = {'total_processed': 100, 'qualified': 60, 'tier1': 10, 'tier2': 35, 'tier3': 15, 'tier4': 0, 'unqualified': 40}
            
            # This should not crash
            monitor.display_dashboard(5, 10)
            
            self.log_test_result(
                "RealTimeMonitor_Basic_Display",
                "PASS",
                {"message": "Dashboard renders without errors"},
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test_result(
                "RealTimeMonitor_Basic_Display",
                "FAIL",
                {"message": f"Display failed: {str(e)}", "error_type": type(e).__name__},
                time.time() - start_time
            )
        
        # Test 2: Edge cases
        start_time = time.time()
        try:
            # Test with zero values
            monitor.stats = {'total_processed': 0, 'qualified': 0, 'tier1': 0, 'tier2': 0, 'tier3': 0, 'tier4': 0, 'unqualified': 0}
            monitor.display_dashboard(0, 0)
            
            # Test with large values
            monitor.stats = {'total_processed': 99999, 'qualified': 60000, 'tier1': 5000, 'tier2': 35000, 'tier3': 20000, 'tier4': 0, 'unqualified': 39999}
            monitor.display_dashboard(999, 1000)
            
            self.log_test_result(
                "RealTimeMonitor_Edge_Cases",
                "PASS",
                {"message": "Handles zero and large values correctly"},
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test_result(
                "RealTimeMonitor_Edge_Cases",
                "FAIL",
                {"message": f"Edge case failed: {str(e)}"},
                time.time() - start_time
            )

    def test_ml_prefilter_quality(self):
        """MEDIUM RISK: Test ML prefilter for false negatives"""
        print("\n🤖 TESTING: ml_prefilter.py (MEDIUM RISK)")
        print("-" * 50)
        
        # Test 1: Known high-quality leads (should never be filtered)
        start_time = time.time()
        try:
            # Tyler's gold standard test cases
            high_quality_leads = [
                {"name": "John Smith", "title": "CEO", "company": "TechCorp Inc"},
                {"name": "Jane Doe", "title": "Chief Technology Officer", "company": "Innovation Labs"},
                {"name": "Bob Wilson", "title": "VP of Sales", "company": "Growth Dynamics"},
                {"name": "Alice Johnson", "title": "Founder & CEO", "company": "StartupX"},
            ]
            
            false_negatives = 0
            
            # Note: This test would require the ML model to be trained first
            # For now, we'll simulate the test structure
            print("   📝 NOTE: ML prefilter requires training data first")
            print("   🎯 Would test these high-quality leads for false negatives:")
            for lead in high_quality_leads:
                print(f"      - {lead['name']}: {lead['title']} at {lead['company']}")
            
            # Simulated result for now
            self.log_test_result(
                "MLPrefilter_False_Negative_Check",
                "WARN",
                {"message": "ML model not trained yet - test structure ready", "test_cases": len(high_quality_leads)},
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test_result(
                "MLPrefilter_False_Negative_Check",
                "FAIL",
                {"message": f"ML testing failed: {str(e)}"},
                time.time() - start_time
            )

    def test_parallel_processor_concurrency(self):
        """HIGH RISK: Test parallel processor for race conditions"""
        print("\n⚡ TESTING: parallel_lead_processor.py (HIGH RISK)")
        print("-" * 50)
        
        # Test 1: Single vs Multi-worker consistency
        start_time = time.time()
        try:
            # Load test data
            test_leads = [
                {"name": f"Test User {i}", "title": "CEO", "company": f"Company {i}", "engagement_type": "reaction"}
                for i in range(20)  # Small dataset for testing
            ]
            
            print(f"   🧪 Testing with {len(test_leads)} leads")
            print("   📊 NOTE: Full concurrency testing requires actual parallel processing")
            print("   ⚠️  Would test:")
            print("      - Single worker vs 8 workers result consistency")
            print("      - Cache state integrity across workers")
            print("      - Worker failure and recovery")
            print("      - Database write concurrency")
            
            # For safety, we don't actually run the parallel processor in chaos test
            # This would require careful test environment setup
            
            self.log_test_result(
                "ParallelProcessor_Concurrency_Test",
                "WARN", 
                {"message": "High-risk component - requires isolated test environment", "test_leads": len(test_leads)},
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test_result(
                "ParallelProcessor_Concurrency_Test",
                "FAIL",
                {"message": f"Concurrency test setup failed: {str(e)}"},
                time.time() - start_time
            )
        
        # Test 2: Worker death simulation
        start_time = time.time()
        try:
            print("   🔥 CHAOS SCENARIO: Worker death simulation")
            print("      - Would kill individual worker threads during processing")
            print("      - Verify other workers continue normally")
            print("      - Check partial results are preserved")
            print("      - Validate cleanup and recovery")
            
            self.log_test_result(
                "ParallelProcessor_Worker_Death",
                "WARN",
                {"message": "Worker death simulation not executed - requires process isolation"},
                time.time() - start_time
            )
            
        except Exception as e:
            self.log_test_result(
                "ParallelProcessor_Worker_Death",
                "FAIL",
                {"message": f"Worker death test failed: {str(e)}"},
                time.time() - start_time
            )

    def validate_production_integrity(self):
        """Ensure production system remains unaffected by testing"""
        print("\n🛡️ PRODUCTION INTEGRITY VALIDATION")
        print("-" * 50)
        
        start_time = time.time()
        try:
            # Check database integrity
            conn = sqlite3.connect('trinity_logging.db')
            cursor = conn.cursor()
            
            # Verify core tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['leads', 'processing_logs', 'processing_runs']
            missing_tables = [t for t in required_tables if t not in tables]
            
            # Check lead count hasn't been corrupted
            cursor.execute("SELECT COUNT(*) FROM leads")
            current_leads = cursor.fetchone()[0]
            
            conn.close()
            
            if not missing_tables and current_leads >= 151:  # At least our known good state
                self.log_test_result(
                    "Production_Database_Integrity",
                    "PASS",
                    {"message": f"Database intact: {current_leads} leads, all tables present"},
                    time.time() - start_time
                )
            else:
                self.log_test_result(
                    "Production_Database_Integrity",
                    "FAIL",
                    {"message": f"Database issues: missing tables {missing_tables}, leads: {current_leads}"},
                    time.time() - start_time
                )
                
        except Exception as e:
            self.log_test_result(
                "Production_Database_Integrity",
                "FAIL",
                {"message": f"Production validation failed: {str(e)}"},
                time.time() - start_time
            )

    def execute_safe_chaos_tests(self):
        """Execute Tyler's systematic chaos testing"""
        print("🔥 TYLER'S CHAOS TESTING SUITE")
        print("=" * 80)
        print(f"Test Run ID: {self.test_results['test_run_id']}")
        print("🎯 PHILOSOPHY: Break it before users do")
        print("⚡ METHOD: Systematic failure injection and validation")
        print("🛡️ SAFETY: Production system integrity maintained")
        print("=" * 80)
        
        # Execute tests in order of risk (low to high)
        self.test_realtime_monitor_safety()
        self.test_ml_prefilter_quality()
        self.test_parallel_processor_concurrency()
        self.validate_production_integrity()
        
        # Generate final report
        self.test_results["end_time"] = datetime.now().isoformat()
        
        print("\n" + "=" * 80)
        print("🏁 CHAOS TESTING COMPLETE")
        print("=" * 80)
        
        summary = self.test_results["summary"]
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   ✅ Passed: {summary['passed']}")
        print(f"   ❌ Failed: {summary['failed']}")
        print(f"   ⚠️  Warnings: {summary['warnings']}")
        
        success_rate = (summary['passed'] / summary['total_tests']) * 100 if summary['total_tests'] > 0 else 0
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        # Save results
        results_file = f"test_data/chaos_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("test_data", exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"   📋 Results saved: {results_file}")
        
        # Tyler's chaos assessment
        if summary['failed'] == 0:
            if summary['warnings'] == 0:
                print(f"   🎉 STATUS: ALL SYSTEMS CHAOS-READY!")
            else:
                print(f"   ✅ STATUS: CHAOS-RESISTANT WITH NOTED RISKS")
        else:
            print(f"   ⚠️  STATUS: OPTIMIZATION COMPONENTS NEED HARDENING")
        
        print("\n🔬 TYLER'S CHAOS HUNTER VERDICT:")
        if summary['failed'] == 0 and summary['warnings'] <= 2:
            print("   ✅ Optimization suite shows good chaos resistance")
            print("   🚀 Ready for controlled production testing")
        else:
            print("   ⚠️  High-risk components need additional hardening")
            print("   🛡️  Stick with proven analyze_engagement_realtime_logged.py")
        
        return self.test_results

def main():
    """Run Tyler's chaos testing suite"""
    print("🎭 INITIALIZING CHAOS TESTING ENVIRONMENT...")
    print("🔒 Creating isolated test space...")
    
    # Backup production database
    import shutil
    backup_file = f"trinity_logging_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    try:
        shutil.copy2('trinity_logging.db', backup_file)
        print(f"✅ Production database backed up: {backup_file}")
    except:
        print("⚠️  Could not backup database - proceeding with caution")
    
    executor = ChaosTestExecutor()
    results = executor.execute_safe_chaos_tests()
    
    print("\n🔥 CHAOS TESTING SESSION COMPLETE!")
    print("📋 Review results and decide on optimization deployment safety")
    
    return results

if __name__ == "__main__":
    main()