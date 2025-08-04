#!/usr/bin/env python3
"""
Communication System Monitor - Advanced monitoring and self-healing capabilities
Detects communication issues, corruption patterns, and provides automated recovery
"""

import json
import os
import time
from datetime import datetime, timedelta
import subprocess
import argparse
from typing import Dict, List, Any, Optional

class CommMonitor:
    """Advanced communication monitoring and self-healing system."""
    
    def __init__(self):
        self.comm_file = "comm.json"
        self.archive_file = "comm_archive.json"
        self.health_log = "comm_health.log"
        self.corruption_signals = ".json_corrupted"
        
    def analyze_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health analysis."""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "issues": [],
            "recommendations": [],
            "metrics": {}
        }
        
        try:
            # File existence and readability
            if not os.path.exists(self.comm_file):
                health_report["issues"].append("comm.json missing")
                health_report["overall_status"] = "critical"
                return health_report
                
            # JSON validity
            try:
                with open(self.comm_file, 'r') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                health_report["issues"].append(f"JSON corruption: {e}")
                health_report["overall_status"] = "critical"
                return health_report
                
            # Basic metrics
            messages = data.get('messages', [])
            file_size_mb = os.path.getsize(self.comm_file) / (1024 * 1024)
            
            health_report["metrics"] = {
                "message_count": len(messages),
                "file_size_mb": round(file_size_mb, 3),
                "active_sprint": data.get('active_sprint', {}).get('id', None),
                "last_updated": data.get('metadata', {}).get('last_updated', None)
            }
            
            # Size analysis
            if file_size_mb > 2.0:
                health_report["issues"].append(f"Large file size: {file_size_mb:.2f}MB")
                health_report["recommendations"].append("Force archive to reduce size")
                health_report["overall_status"] = "warning"
                
            if len(messages) > 200:
                health_report["issues"].append(f"High message count: {len(messages)}")
                health_report["recommendations"].append("Archive old messages")
                if health_report["overall_status"] == "healthy":
                    health_report["overall_status"] = "warning"
                    
            # Activity analysis
            current_time = time.time()
            recent_messages = [m for m in messages if (current_time - m.get('ts', 0)) < 3600]
            
            if len(recent_messages) > 100:
                health_report["issues"].append(f"High recent activity: {len(recent_messages)} messages/hour")
                health_report["recommendations"].append("Check for message loops or chaos testing")
                
            # Agent activity patterns
            agent_activity = {}
            for msg in recent_messages:
                agent = msg.get('from', 'unknown')
                agent_activity[agent] = agent_activity.get(agent, 0) + 1
                
            for agent, count in agent_activity.items():
                if count > 20:  # More than 20 messages per hour from one agent
                    health_report["issues"].append(f"High activity from {agent}: {count} messages/hour")
                    
            # Duplicate detection
            bodies = [m.get('body', '') for m in messages[-20:]]  # Check last 20 messages
            duplicates = len(bodies) - len(set(bodies))
            if duplicates > 3:
                health_report["issues"].append(f"Duplicate messages detected: {duplicates} in recent messages")
                health_report["recommendations"].append("Check for messaging loops")
                
            # Lock file issues
            if os.path.exists(".comm.lock"):
                lock_age = time.time() - os.path.getmtime(".comm.lock")
                if lock_age > 300:  # Lock older than 5 minutes
                    health_report["issues"].append(f"Stale lock file: {lock_age:.0f} seconds old")
                    health_report["recommendations"].append("Remove stale lock file")
                    
            # Corruption signals
            if os.path.exists(self.corruption_signals):
                health_report["issues"].append("Corruption signal file exists")
                health_report["recommendations"].append("Investigate corruption and clean signal file")
                health_report["overall_status"] = "warning"
                
        except Exception as e:
            health_report["issues"].append(f"Health analysis failed: {e}")
            health_report["overall_status"] = "error"
            
        return health_report
        
    def auto_heal(self) -> bool:
        """Attempt automatic healing of detected issues."""
        health = self.analyze_system_health()
        
        if health["overall_status"] == "healthy":
            return True
            
        healed_issues = []
        
        # Remove stale lock files
        if os.path.exists(".comm.lock"):
            lock_age = time.time() - os.path.getmtime(".comm.lock")
            if lock_age > 300:
                try:
                    os.remove(".comm.lock")
                    healed_issues.append("Removed stale lock file")
                except Exception as e:
                    print(f"Failed to remove stale lock: {e}")
                    
        # Auto-archive if file is too large
        metrics = health.get("metrics", {})
        if (metrics.get("file_size_mb", 0) > 1.0 or 
            metrics.get("message_count", 0) > 150):
            try:
                result = subprocess.run(
                    ["python3", "archive_comm.py", "--force"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode == 0:
                    healed_issues.append("Auto-archived large message file")
                else:
                    print(f"Auto-archive failed: {result.stderr}")
            except Exception as e:
                print(f"Auto-archive error: {e}")
                
        # Clean corruption signals after investigation
        if os.path.exists(self.corruption_signals):
            try:
                with open(self.corruption_signals, 'r') as f:
                    signal_data = json.load(f)
                    
                # Log the corruption for analysis
                self.log_health_event("corruption_signal", signal_data)
                
                # Remove signal file
                os.remove(self.corruption_signals)
                healed_issues.append("Cleaned corruption signal file")
            except Exception as e:
                print(f"Failed to clean corruption signal: {e}")
                
        if healed_issues:
            self.log_health_event("auto_heal", {"actions": healed_issues})
            print(f"✅ Auto-healed: {', '.join(healed_issues)}")
            return True
            
        return False
        
    def log_health_event(self, event_type: str, data: Any):
        """Log health events for analysis."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "data": data
            }
            
            # Append to health log
            with open(self.health_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            print(f"Failed to log health event: {e}")
            
    def continuous_monitor(self, interval: int = 60, max_iterations: int = None):
        """Run continuous monitoring with specified interval."""
        print(f"🔍 Starting continuous monitoring (interval: {interval}s)")
        
        iteration = 0
        while True:
            if max_iterations and iteration >= max_iterations:
                break
                
            try:
                health = self.analyze_system_health()
                status_emoji = {
                    "healthy": "✅",
                    "warning": "⚠️",
                    "critical": "❌",
                    "error": "💥"
                }.get(health["overall_status"], "❓")
                
                print(f"{status_emoji} [{datetime.now().strftime('%H:%M:%S')}] "
                      f"Status: {health['overall_status']} | "
                      f"Messages: {health['metrics'].get('message_count', 0)} | "
                      f"Size: {health['metrics'].get('file_size_mb', 0):.2f}MB")
                
                if health["issues"]:
                    print(f"   Issues: {', '.join(health['issues'][:3])}")
                    
                # Attempt auto-healing if issues detected
                if health["overall_status"] != "healthy":
                    if self.auto_heal():
                        print("   🔧 Auto-healing attempted")
                        
                # Log periodic health status
                if iteration % 10 == 0:  # Every 10 iterations
                    self.log_health_event("periodic_check", health)
                    
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"💥 Monitor error: {e}")
                
            time.sleep(interval)
            iteration += 1
            
    def generate_report(self) -> str:
        """Generate comprehensive health report."""
        health = self.analyze_system_health()
        
        report = f"""
🔍 TRINITY COMMUNICATION SYSTEM HEALTH REPORT
Generated: {health['timestamp']}
Overall Status: {health['overall_status'].upper()}

📊 METRICS:
- Messages: {health['metrics'].get('message_count', 0)}
- File Size: {health['metrics'].get('file_size_mb', 0):.3f}MB
- Active Sprint: {health['metrics'].get('active_sprint', 'None')}
- Last Updated: {health['metrics'].get('last_updated', 'Unknown')}

"""
        
        if health["issues"]:
            report += "⚠️ ISSUES DETECTED:\n"
            for issue in health["issues"]:
                report += f"- {issue}\n"
            report += "\n"
            
        if health["recommendations"]:
            report += "💡 RECOMMENDATIONS:\n"
            for rec in health["recommendations"]:
                report += f"- {rec}\n"
            report += "\n"
            
        # Add historical data if available
        if os.path.exists(self.health_log):
            try:
                with open(self.health_log, 'r') as f:
                    lines = f.readlines()[-10:]  # Last 10 events
                    
                if lines:
                    report += "📈 RECENT HEALTH EVENTS:\n"
                    for line in lines:
                        try:
                            event = json.loads(line.strip())
                            report += f"- {event['timestamp'][:19]}: {event['event_type']}\n"
                        except:
                            continue
                            
            except Exception:
                pass
                
        return report

def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(description='Trinity Communication System Monitor')
    parser.add_argument('--monitor', action='store_true', 
                       help='Start continuous monitoring')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in seconds (default: 60)')
    parser.add_argument('--heal', action='store_true',
                       help='Attempt auto-healing of detected issues')
    parser.add_argument('--report', action='store_true',
                       help='Generate health report')
    parser.add_argument('--max-iterations', type=int,
                       help='Maximum monitoring iterations (for testing)')
    
    args = parser.parse_args()
    monitor = CommMonitor()
    
    if args.report:
        print(monitor.generate_report())
        
    elif args.heal:
        health = monitor.analyze_system_health()
        print(f"Current status: {health['overall_status']}")
        if monitor.auto_heal():
            print("✅ Auto-healing completed")
        else:
            print("ℹ️ No healing actions needed or possible")
            
    elif args.monitor:
        monitor.continuous_monitor(args.interval, args.max_iterations)
        
    else:
        # Default: show health status
        health = monitor.analyze_system_health()
        status_emoji = {
            "healthy": "✅",
            "warning": "⚠️", 
            "critical": "❌",
            "error": "💥"
        }.get(health["overall_status"], "❓")
        
        print(f"{status_emoji} System Status: {health['overall_status'].upper()}")
        print(f"Messages: {health['metrics'].get('message_count', 0)}")
        print(f"File Size: {health['metrics'].get('file_size_mb', 0):.3f}MB")
        
        if health["issues"]:
            print("\nIssues:")
            for issue in health["issues"]:
                print(f"  - {issue}")
                
        if health["recommendations"]:
            print("\nRecommendations:")
            for rec in health["recommendations"]:
                print(f"  - {rec}")

if __name__ == "__main__":
    main()