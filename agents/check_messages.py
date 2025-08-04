#!/usr/bin/env python3
"""
Check messages for a specific agent and display unacknowledged ones.
Used in continuous loops to prevent agents from going idle.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def check_messages(agent_name):
    """Check and display messages for the specified agent."""
    comm_file = Path(__file__).parent / "comm.json"
    
    if not comm_file.exists():
        print(f"❌ No comm.json found. Run archive_comm.py first.")
        return 0
    
    with open(comm_file, 'r') as f:
        data = json.load(f)
    
    # Find unacknowledged messages for this agent
    messages = [m for m in data['messages'] 
                if m['to'] == agent_name and not m.get('ack', False)]
    
    if not messages:
        print(f"📭 No new messages for {agent_name}")
        return 0
    
    print(f"📬 {len(messages)} new messages for {agent_name}:")
    print("-" * 50)
    
    for msg in messages:
        # Format timestamp
        ts = datetime.fromtimestamp(msg['ts']).strftime("%H:%M:%S")
        from_agent = msg['from'].upper()
        body = msg['body'][:200] + "..." if len(msg['body']) > 200 else msg['body']
        
        print(f"[{ts}] FROM {from_agent}:")
        print(f"  {body}")
        print()
    
    print("-" * 50)
    print(f"💡 To acknowledge: python3 ../send_message.py {agent_name} '' --from {agent_name} --ack")
    
    return len(messages)

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 check_messages.py <agent_name>")
        print("Example: python3 check_messages.py tyler")
        sys.exit(1)
    
    agent_name = sys.argv[1].lower()
    if agent_name not in ['tyler', 'dev', 'guide']:
        print(f"❌ Unknown agent: {agent_name}")
        print("Valid agents: tyler, dev, guide")
        sys.exit(1)
    
    count = check_messages(agent_name)
    sys.exit(0 if count == 0 else count)

if __name__ == "__main__":
    main()