#!/usr/bin/env python3
"""
Lightweight cycle management using comm.json for coordination.
Integrates with existing message system.
"""

import json
import os
import subprocess
from datetime import datetime
from typing import Optional, Dict

class CycleComm:
    """Simple cycle management via comm.json messages."""
    
    def __init__(self, agent: str):
        self.agent = agent
        self.comm_file = "comm.json"
        self.cycle_state_file = f".cycle_{agent}.json"
    
    def start_cycle(self, task: str) -> bool:
        """Start a cycle - broadcasts to team via comm.json."""
        # Check if already have active cycle
        if os.path.exists(self.cycle_state_file):
            print("❌ Already have active cycle. Close it first!")
            return False
        
        # Create cycle state
        cycle_id = f"{self.agent}-{datetime.now().strftime('%H%M')}"
        cycle = {
            "id": cycle_id,
            "task": task,
            "started": datetime.now().isoformat(),
            "work_done": [],
            "issues": []
        }
        
        # Save local state
        with open(self.cycle_state_file, 'w') as f:
            json.dump(cycle, f, indent=2)
        
        # Broadcast to team
        msg = f"🔄 CYCLE START [{cycle_id}]: {task}"
        subprocess.run([
            "python3", "send_message.py", "guide", msg, "--from", self.agent
        ])
        
        print(f"✅ Started cycle: {task}")
        return True
    
    def track(self, what: str):
        """Track work in current cycle."""
        if not os.path.exists(self.cycle_state_file):
            print("⚠️  No active cycle")
            return
        
        with open(self.cycle_state_file, 'r') as f:
            cycle = json.load(f)
        
        cycle["work_done"].append({
            "time": datetime.now().strftime("%H:%M"),
            "what": what
        })
        
        with open(self.cycle_state_file, 'w') as f:
            json.dump(cycle, f, indent=2)
    
    def add_issue(self, issue: str):
        """Add issue found in cycle."""
        if not os.path.exists(self.cycle_state_file):
            return
        
        with open(self.cycle_state_file, 'r') as f:
            cycle = json.load(f)
        
        cycle["issues"].append(issue)
        
        with open(self.cycle_state_file, 'w') as f:
            json.dump(cycle, f, indent=2)
        
        # Notify team immediately
        msg = f"🐛 ISSUE: {issue}"
        subprocess.run([
            "python3", "send_message.py", "guide", msg, "--from", self.agent
        ])
    
    def close_cycle(self) -> bool:
        """Close cycle - commit if git repo exists, otherwise save locally."""
        if not os.path.exists(self.cycle_state_file):
            print("⚠️  No active cycle to close")
            return False
        
        with open(self.cycle_state_file, 'r') as f:
            cycle = json.load(f)
        
        # Create work summary
        work_summary = f"{len(cycle['work_done'])} items"
        issues_summary = f"{len(cycle['issues'])} issues" if cycle['issues'] else ""
        
        # Check if git repo exists and is functional
        git_available = self._check_git_repo()
        
        if git_available:
            # Git operations with proper error handling
            try:
                commit_msg = f"{self.agent}: {cycle['task']}\n\n"
                commit_msg += f"Cycle: {cycle['id']}\n"
                commit_msg += f"Work: {work_summary}\n"
                if issues_summary:
                    commit_msg += f"Issues: {issues_summary}\n"
                
                # Add and commit with error checking
                add_result = subprocess.run(["git", "add", "-A"], 
                                          capture_output=True, text=True)
                if add_result.returncode != 0:
                    print(f"⚠️  Git add failed: {add_result.stderr}")
                    git_available = False
                else:
                    commit_result = subprocess.run(["git", "commit", "-m", commit_msg], 
                                                 capture_output=True, text=True)
                    if commit_result.returncode != 0:
                        print(f"⚠️  Git commit failed: {commit_result.stderr}")
                        # Continue anyway - might be no changes to commit
                
            except Exception as e:
                print(f"⚠️  Git operations failed: {e}")
                git_available = False
        
        if not git_available:
            # Save cycle to local archive instead
            self._archive_cycle_locally(cycle)
        
        # Notify team
        commit_status = "committed" if git_available else "archived locally"
        msg = f"✅ CYCLE DONE [{cycle['id']}]: {work_summary}, {commit_status}"
        if cycle['issues']:
            msg += f", found {len(cycle['issues'])} issues"
        
        subprocess.run([
            "python3", "send_message.py", "guide", msg, "--from", self.agent
        ])
        
        # Clean up
        os.remove(self.cycle_state_file)
        
        print(f"✅ Cycle closed and {commit_status}")
        return True
    
    def _check_git_repo(self) -> bool:
        """Check if current directory is a functional git repository."""
        try:
            result = subprocess.run(["git", "status"], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False
    
    def _archive_cycle_locally(self, cycle):
        """Archive cycle data locally when git is not available."""
        try:
            # Create cycles directory if it doesn't exist
            cycles_dir = "cycles"
            os.makedirs(cycles_dir, exist_ok=True)
            
            # Save cycle with timestamp
            cycle_file = os.path.join(cycles_dir, f"{cycle['id']}.json")
            cycle["closed_at"] = datetime.now().isoformat()
            cycle["git_available"] = False
            
            with open(cycle_file, 'w') as f:
                json.dump(cycle, f, indent=2)
            
            print(f"📁 Cycle archived locally: {cycle_file}")
            
        except Exception as e:
            print(f"⚠️  Failed to archive cycle locally: {e}")
    
    def check_messages(self) -> list:
        """Check for messages to this agent."""
        try:
            with open(self.comm_file, 'r') as f:
                data = json.load(f)
            
            messages = [
                m for m in data.get('messages', [])
                if m['to'] == self.agent and not m['ack']
            ]
            
            return messages
        except:
            return []
    
    def morning_check(self):
        """Quick morning check - messages and status."""
        print(f"\n☀️ Good morning, {self.agent.upper()}!")
        print("=" * 40)
        
        # Check messages
        messages = self.check_messages()
        if messages:
            print(f"📬 You have {len(messages)} messages:")
            for msg in messages[:3]:
                print(f"  • From {msg['from']}: {msg['body'][:60]}...")
        else:
            print("📬 No new messages")
        
        # Check if have incomplete cycle
        if os.path.exists(self.cycle_state_file):
            with open(self.cycle_state_file, 'r') as f:
                cycle = json.load(f)
            print(f"\n⚠️  Incomplete cycle: {cycle['task']}")
            print("   Close it first: python3 cycle_comm.py --close")
        
        print("=" * 40)
        print("\nReady to start? python3 cycle_comm.py --start 'Your task'")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 cycle_comm.py [agent] --morning|--start|--track|--issue|--close")
        sys.exit(1)
    
    agent = sys.argv[1]
    cycle = CycleComm(agent)
    
    if "--morning" in sys.argv:
        cycle.morning_check()
    
    elif "--start" in sys.argv and len(sys.argv) > 3:
        task = " ".join(sys.argv[3:])
        cycle.start_cycle(task)
    
    elif "--track" in sys.argv and len(sys.argv) > 3:
        what = " ".join(sys.argv[3:])
        cycle.track(what)
    
    elif "--issue" in sys.argv and len(sys.argv) > 3:
        issue = " ".join(sys.argv[3:])
        cycle.add_issue(issue)
    
    elif "--close" in sys.argv:
        cycle.close_cycle()
    
    else:
        cycle.morning_check()