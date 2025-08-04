#!/usr/bin/env python3
"""
Communication Recovery Utility - Emergency recovery and data integrity tools
Handles corruption, provides backup/restore, and emergency communication modes
"""

import json
import os
import shutil
import time
from datetime import datetime
import argparse
from typing import Dict, List, Any, Optional, Tuple

class CommRecovery:
    """Emergency recovery and data integrity tools for Trinity communication."""
    
    def __init__(self):
        self.comm_file = "comm.json"
        self.backup_dir = "comm_backups"
        self.emergency_file = "comm_emergency.json"
        
    def create_backup(self, label: str = None) -> str:
        """Create timestamped backup of current comm.json."""
        os.makedirs(self.backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"comm_{timestamp}"
        if label:
            backup_name += f"_{label}"
        backup_name += ".json"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            if os.path.exists(self.comm_file):
                shutil.copy2(self.comm_file, backup_path)
                print(f"✅ Backup created: {backup_path}")
                return backup_path
            else:
                print("❌ No comm.json to backup")
                return None
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
            
    def validate_json_integrity(self, filepath: str = None) -> Tuple[bool, List[str]]:
        """Validate JSON structure and data integrity."""
        filepath = filepath or self.comm_file
        issues = []
        
        if not os.path.exists(filepath):
            return False, ["File does not exist"]
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"JSON decode error: {e}"]
        except Exception as e:
            return False, [f"File read error: {e}"]
            
        # Structure validation
        if not isinstance(data, dict):
            issues.append("Root must be a dictionary")
            
        if 'messages' not in data:
            issues.append("Missing 'messages' key")
        elif not isinstance(data['messages'], list):
            issues.append("'messages' must be a list")
        else:
            # Validate message structure
            for i, msg in enumerate(data['messages']):
                if not isinstance(msg, dict):
                    issues.append(f"Message {i} is not a dictionary")
                    continue
                    
                required_keys = {'id', 'from', 'to', 'body', 'ack', 'ts'}
                missing_keys = required_keys - set(msg.keys())
                if missing_keys:
                    issues.append(f"Message {i} missing keys: {missing_keys}")
                    
                # Data type validation
                if 'ts' in msg and not isinstance(msg['ts'], (int, float)):
                    issues.append(f"Message {i} timestamp invalid type")
                    
                if 'ack' in msg and not isinstance(msg['ack'], bool):
                    issues.append(f"Message {i} ack field invalid type")
                    
        # Metadata validation
        if 'metadata' in data and not isinstance(data['metadata'], dict):
            issues.append("'metadata' must be a dictionary")
            
        # Sprint validation
        if 'active_sprint' in data and data['active_sprint'] is not None:
            if not isinstance(data['active_sprint'], dict):
                issues.append("'active_sprint' must be a dictionary or null")
                
        return len(issues) == 0, issues
        
    def repair_json(self, filepath: str = None, backup_first: bool = True) -> bool:
        """Attempt to repair corrupted JSON file."""
        filepath = filepath or self.comm_file
        
        if backup_first:
            self.create_backup("pre_repair")
            
        print(f"🔧 Attempting to repair {filepath}")
        
        # First, try to validate
        is_valid, issues = self.validate_json_integrity(filepath)
        if is_valid:
            print("✅ File is already valid")
            return True
            
        print(f"Found {len(issues)} issues:")
        for issue in issues[:5]:  # Show first 5 issues
            print(f"  - {issue}")
            
        try:
            # Try to read with relaxed JSON parsing
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Common repair attempts
            repaired_content = content
            
            # Fix common JSON issues
            repaired_content = repaired_content.replace('\\n', '\\\\n')  # Escape newlines
            repaired_content = repaired_content.replace('\t', '\\t')    # Escape tabs
            
            # Try to parse repaired content
            try:
                data = json.loads(repaired_content)
            except json.JSONDecodeError:
                print("❌ Could not repair JSON structure")
                return False
                
            # Structural repairs
            if not isinstance(data, dict):
                data = {"messages": [], "metadata": {"repaired": True}}
                
            if 'messages' not in data:
                data['messages'] = []
            elif not isinstance(data['messages'], list):
                data['messages'] = []
                
            # Clean up messages
            valid_messages = []
            for msg in data.get('messages', []):
                if isinstance(msg, dict) and all(key in msg for key in ['id', 'from', 'to', 'body']):
                    # Ensure required fields
                    if 'ack' not in msg:
                        msg['ack'] = False
                    if 'ts' not in msg:
                        msg['ts'] = time.time()
                    valid_messages.append(msg)
                    
            data['messages'] = valid_messages
            
            # Ensure metadata
            if 'metadata' not in data or not isinstance(data['metadata'], dict):
                data['metadata'] = {}
                
            data['metadata']['repaired_at'] = datetime.now().isoformat()
            data['metadata']['repair_issues_found'] = len(issues)
            
            # Write repaired file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
                
            print(f"✅ Repaired file with {len(valid_messages)} valid messages")
            return True
            
        except Exception as e:
            print(f"❌ Repair failed: {e}")
            return False
            
    def emergency_reset(self, preserve_sprint: bool = True) -> bool:
        """Emergency reset to minimal working state."""
        print("🚨 Performing emergency reset")
        
        # Backup current state
        backup_path = self.create_backup("emergency_reset")
        
        # Try to preserve important data
        preserved_data = {}
        if preserve_sprint and os.path.exists(self.comm_file):
            try:
                with open(self.comm_file, 'r') as f:
                    current_data = json.load(f)
                    if 'active_sprint' in current_data:
                        preserved_data['active_sprint'] = current_data['active_sprint']
                    if 'metadata' in current_data:
                        preserved_data['previous_metadata'] = current_data['metadata']
            except:
                pass
                
        # Create minimal working structure
        emergency_data = {
            "messages": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "emergency_reset",
                "emergency_reset_at": datetime.now().isoformat(),
                "backup_location": backup_path
            }
        }
        
        # Add preserved data
        emergency_data.update(preserved_data)
        
        try:
            with open(self.comm_file, 'w') as f:
                json.dump(emergency_data, f, indent=2)
                
            print("✅ Emergency reset completed")
            print(f"📁 Previous data backed up to: {backup_path}")
            
            # Also create emergency communication file
            with open(self.emergency_file, 'w') as f:
                json.dump({
                    "status": "emergency_reset_active",
                    "timestamp": datetime.now().isoformat(),
                    "backup_location": backup_path,
                    "instructions": "Communication system was reset due to corruption. Previous data is backed up."
                }, f, indent=2)
                
            return True
            
        except Exception as e:
            print(f"❌ Emergency reset failed: {e}")
            return False
            
    def restore_from_backup(self, backup_name: str = None) -> bool:
        """Restore from a specific backup or latest backup."""
        if not os.path.exists(self.backup_dir):
            print("❌ No backups directory found")
            return False
            
        backups = [f for f in os.listdir(self.backup_dir) if f.endswith('.json')]
        if not backups:
            print("❌ No backups found")
            return False
            
        if backup_name:
            backup_path = os.path.join(self.backup_dir, backup_name)
            if not os.path.exists(backup_path):
                print(f"❌ Backup {backup_name} not found")
                return False
        else:
            # Use latest backup
            backups.sort(reverse=True)
            backup_path = os.path.join(self.backup_dir, backups[0])
            print(f"Using latest backup: {backups[0]}")
            
        # Validate backup before restoring
        is_valid, issues = self.validate_json_integrity(backup_path)
        if not is_valid:
            print(f"❌ Backup is corrupted: {issues}")
            return False
            
        try:
            # Create current backup before restore
            self.create_backup("pre_restore")
            
            # Restore
            shutil.copy2(backup_path, self.comm_file)
            print(f"✅ Restored from {backup_path}")
            
            # Clean up emergency file if it exists
            if os.path.exists(self.emergency_file):
                os.remove(self.emergency_file)
                
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
            
    def list_backups(self):
        """List available backups with details."""
        if not os.path.exists(self.backup_dir):
            print("No backups directory found")
            return
            
        backups = [f for f in os.listdir(self.backup_dir) if f.endswith('.json')]
        if not backups:
            print("No backups found")
            return
            
        print("📁 Available backups:")
        backups.sort(reverse=True)
        
        for backup in backups[:10]:  # Show last 10 backups
            backup_path = os.path.join(self.backup_dir, backup)
            try:
                stat = os.stat(backup_path)
                size_kb = stat.st_size / 1024
                mtime = datetime.fromtimestamp(stat.st_mtime)
                
                # Quick validation
                is_valid, _ = self.validate_json_integrity(backup_path)
                status = "✅" if is_valid else "❌"
                
                print(f"  {status} {backup} ({size_kb:.1f}KB, {mtime.strftime('%Y-%m-%d %H:%M')})")
                
            except Exception as e:
                print(f"  ❓ {backup} (error reading: {e})")
                
    def system_diagnosis(self) -> Dict[str, Any]:
        """Comprehensive system diagnosis."""
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "comm_file_status": {},
            "backup_status": {},
            "system_files": {},
            "recommendations": []
        }
        
        # Comm file analysis
        if os.path.exists(self.comm_file):
            is_valid, issues = self.validate_json_integrity()
            stat = os.stat(self.comm_file)
            
            diagnosis["comm_file_status"] = {
                "exists": True,
                "valid": is_valid,
                "issues": issues,
                "size_kb": round(stat.st_size / 1024, 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
            if not is_valid:
                diagnosis["recommendations"].append("Repair or restore comm.json")
        else:
            diagnosis["comm_file_status"] = {"exists": False}
            diagnosis["recommendations"].append("Emergency reset needed - no comm.json")
            
        # Backup analysis
        if os.path.exists(self.backup_dir):
            backups = [f for f in os.listdir(self.backup_dir) if f.endswith('.json')]
            valid_backups = 0
            
            for backup in backups:
                backup_path = os.path.join(self.backup_dir, backup)
                is_valid, _ = self.validate_json_integrity(backup_path)
                if is_valid:
                    valid_backups += 1
                    
            diagnosis["backup_status"] = {
                "backup_dir_exists": True,
                "total_backups": len(backups),
                "valid_backups": valid_backups,
                "latest_backup": backups[0] if backups else None
            }
            
            if valid_backups == 0 and len(backups) > 0:
                diagnosis["recommendations"].append("All backups corrupted - investigate")
        else:
            diagnosis["backup_status"] = {"backup_dir_exists": False}
            diagnosis["recommendations"].append("Create backup system")
            
        # System files check
        system_files = {
            "lock_file": os.path.exists(".comm.lock"),
            "corruption_signal": os.path.exists(".json_corrupted"),
            "emergency_file": os.path.exists(self.emergency_file),
            "archive_file": os.path.exists("comm_archive.json")
        }
        
        diagnosis["system_files"] = system_files
        
        if system_files["corruption_signal"]:
            diagnosis["recommendations"].append("Clear corruption signal after investigation")
        if system_files["lock_file"]:
            diagnosis["recommendations"].append("Check for stale lock file")
            
        return diagnosis

def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(description='Trinity Communication Recovery Tools')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup of current comm.json')
    parser.add_argument('--label', type=str,
                       help='Label for backup file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate JSON integrity')
    parser.add_argument('--repair', action='store_true',
                       help='Attempt to repair corrupted JSON')
    parser.add_argument('--emergency-reset', action='store_true',
                       help='Emergency reset to minimal working state')
    parser.add_argument('--restore', type=str, nargs='?', const='latest',
                       help='Restore from backup (specify name or use latest)')
    parser.add_argument('--list-backups', action='store_true',
                       help='List available backups')
    parser.add_argument('--diagnose', action='store_true',
                       help='Run comprehensive system diagnosis')
    parser.add_argument('--file', type=str,
                       help='Specific file to operate on (default: comm.json)')
    
    args = parser.parse_args()
    recovery = CommRecovery()
    
    if args.file:
        recovery.comm_file = args.file
        
    if args.backup:
        recovery.create_backup(args.label)
        
    elif args.validate:
        is_valid, issues = recovery.validate_json_integrity()
        if is_valid:
            print("✅ JSON is valid")
        else:
            print(f"❌ JSON validation failed:")
            for issue in issues:
                print(f"  - {issue}")
                
    elif args.repair:
        recovery.repair_json()
        
    elif args.emergency_reset:
        recovery.emergency_reset()
        
    elif args.restore:
        if args.restore == 'latest':
            recovery.restore_from_backup()
        else:
            recovery.restore_from_backup(args.restore)
            
    elif args.list_backups:
        recovery.list_backups()
        
    elif args.diagnose:
        diagnosis = recovery.system_diagnosis()
        print("🔍 SYSTEM DIAGNOSIS")
        print("=" * 40)
        
        # Comm file status
        comm_status = diagnosis["comm_file_status"]
        if comm_status.get("exists"):
            status_icon = "✅" if comm_status.get("valid") else "❌"
            print(f"{status_icon} comm.json: {comm_status.get('size_kb')}KB")
            if not comm_status.get("valid"):
                print(f"   Issues: {len(comm_status.get('issues', []))}")
        else:
            print("❌ comm.json: Missing")
            
        # Backup status
        backup_status = diagnosis["backup_status"]
        if backup_status.get("backup_dir_exists"):
            print(f"📁 Backups: {backup_status.get('valid_backups')}/{backup_status.get('total_backups')} valid")
        else:
            print("📁 Backups: No backup directory")
            
        # Recommendations
        recommendations = diagnosis["recommendations"]
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"  - {rec}")
        else:
            print("\n✅ No immediate actions needed")
            
    else:
        # Default: quick status
        is_valid, issues = recovery.validate_json_integrity()
        if is_valid:
            print("✅ Communication system is healthy")
        else:
            print(f"❌ Issues detected: {len(issues)}")
            print("Run --diagnose for detailed analysis")

if __name__ == "__main__":
    main()