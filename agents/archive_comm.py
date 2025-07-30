#!/usr/bin/env python3
"""
Enhanced archive script for Trinity sprint management.
Handles both regular archiving and sprint-end archiving with TLDR generation.
"""

import json
from datetime import datetime
import os
import argparse

def generate_sprint_tldr(messages, sprint_data):
    """Generate TLDR from sprint messages focusing on key learnings."""
    # Key patterns to extract
    breakthroughs = []
    user_rage_reductions = []
    key_discoveries = []
    
    for msg in messages:
        body = msg.get('body', '').lower()
        
        # Find USER RAGE reductions
        if 'user rage' in body and '→' in body:
            user_rage_reductions.append(msg['body'])
        
        # Find breakthroughs
        if any(word in body for word in ['breakthrough', 'solved', 'fixed', 'perfect']):
            breakthroughs.append(msg['body'][:100] + '...' if len(msg['body']) > 100 else msg['body'])
        
        # Find key discoveries
        if any(word in body for word in ['discovered', 'found', 'pattern', 'revelation']):
            key_discoveries.append(msg['body'][:100] + '...' if len(msg['body']) > 100 else msg['body'])
    
    # Create TLDR
    tldr_parts = []
    
    if sprint_data:
        rage_start = sprint_data.get('user_rage_start', '?')
        rage_end = sprint_data.get('user_rage_target', '?')
        tldr_parts.append(f"Sprint Goal: {sprint_data.get('goal', 'Unknown')}")
        tldr_parts.append(f"USER RAGE: {rage_start} → {rage_end}")
    
    if breakthroughs:
        tldr_parts.append(f"Key Breakthrough: {breakthroughs[-1]}")
    
    if key_discoveries:
        tldr_parts.append(f"Discovery: {key_discoveries[-1]}")
    
    return " | ".join(tldr_parts) if tldr_parts else "Sprint completed successfully."

def archive_sprint(sprint_end=False):
    """Archive messages with optional sprint-end functionality."""
    # Read current comm.json
    with open('comm.json', 'r') as f:
        data = json.load(f)
    
    all_messages = data.get('messages', [])
    active_sprint = data.get('active_sprint', None)
    
    if sprint_end and active_sprint:
        # Sprint-end archiving
        sprint_id = active_sprint.get('id', f'sprint-{datetime.now().strftime("%Y%m%d-%H%M%S")}')
        
        # Generate TLDR
        tldr = generate_sprint_tldr(all_messages, active_sprint)
        
        # Create sprint archive
        sprint_archive = {
            "sprint_id": sprint_id,
            "archived_at": datetime.now().isoformat(),
            "sprint_data": active_sprint,
            "message_count": len(all_messages),
            "messages": all_messages,
            "tldr": tldr,
            "metadata": {
                "start_ts": all_messages[0]['ts'] if all_messages else None,
                "end_ts": all_messages[-1]['ts'] if all_messages else None,
                "user_rage_achieved": active_sprint.get('user_rage_target', None)
            }
        }
        
        # Save sprint archive
        archive_path = f'chronicles/sprints/{sprint_id}.json'
        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
        
        with open(archive_path, 'w') as f:
            json.dump(sprint_archive, f, indent=2)
        
        print(f"✅ Sprint '{sprint_id}' archived successfully")
        print(f"📝 TLDR: {tldr}")
        
        # Reset comm.json for new sprint
        new_data = {
            "messages": [],
            "active_sprint": None,
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "previous_sprint": sprint_id,
                "tldr_from_previous": tldr
            }
        }
        
        with open('comm.json', 'w') as f:
            json.dump(new_data, f, indent=2)
        
        print("🔄 comm.json reset for new sprint")
        print(f"📋 TLDR passed to next sprint: {tldr}")
        
    else:
        # Regular archiving (keep last 10 messages)
        total_count = len(all_messages)
        print(f"Total messages found: {total_count}")
        
        if total_count <= 10:
            print("No need to archive - 10 or fewer messages")
            return
        
        # Split messages
        messages_to_archive = all_messages[:-10]
        messages_to_keep = all_messages[-10:]
        
        # Load or create archive
        archive_path = 'comm_archive.json'
        if os.path.exists(archive_path):
            with open(archive_path, 'r') as f:
                archive_data = json.load(f)
        else:
            archive_data = {
                "archived_messages": [],
                "archive_sessions": []
            }
        
        # Create archive session
        archive_session = {
            "archived_at": datetime.now().isoformat(),
            "message_count": len(messages_to_archive),
            "first_message_ts": messages_to_archive[0]['ts'],
            "last_message_ts": messages_to_archive[-1]['ts']
        }
        
        # Add to archive
        archive_data['archived_messages'].extend(messages_to_archive)
        archive_data['archive_sessions'].append(archive_session)
        
        # Save archive
        with open(archive_path, 'w') as f:
            json.dump(archive_data, f, indent=2)
        
        # Update comm.json
        data['messages'] = messages_to_keep
        data['metadata']['last_archived'] = datetime.now().isoformat()
        
        with open('comm.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Archived {len(messages_to_archive)} messages")
        print(f"📋 Kept last {len(messages_to_keep)} messages")

def start_new_sprint(goal, user_rage_start, user_rage_target):
    """Initialize a new sprint in comm.json."""
    with open('comm.json', 'r') as f:
        data = json.load(f)
    
    sprint_id = f'sprint-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
    
    data['active_sprint'] = {
        "id": sprint_id,
        "goal": goal,
        "user_rage_start": user_rage_start,
        "user_rage_target": user_rage_target,
        "started": datetime.now().isoformat(),
        "checklist": [
            {"id": "discovery", "task": "Tyler discovers all pain points", "status": "pending"},
            {"id": "implementation", "task": "Dev implements solutions", "status": "pending"},
            {"id": "testing", "task": "Tyler chaos tests everything", "status": "pending"},
            {"id": "code_review", "task": "Dev reviews code quality", "status": "pending"},
            {"id": "project_index", "task": "PROJECT_INDEX.md updated", "status": "pending"},
            {"id": "doc_review", "task": "Documentation reviewed", "status": "pending"},
            {"id": "user_rage_target", "task": "USER RAGE target achieved", "status": "pending"}
        ],
        "tldr_from_previous": data['metadata'].get('tldr_from_previous', '')
    }
    
    with open('comm.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"🚀 New sprint '{sprint_id}' started!")
    print(f"🎯 Goal: {goal}")
    print(f"😤 USER RAGE: {user_rage_start} → {user_rage_target}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trinity sprint and message archiving')
    parser.add_argument('--sprint-end', action='store_true', help='Archive current sprint and prepare for new one')
    parser.add_argument('--start-sprint', nargs=3, metavar=('GOAL', 'RAGE_START', 'RAGE_TARGET'),
                       help='Start new sprint with goal and USER RAGE metrics')
    
    args = parser.parse_args()
    
    if args.start_sprint:
        goal, rage_start, rage_target = args.start_sprint
        start_new_sprint(goal, int(rage_start), int(rage_target))
    elif args.sprint_end:
        archive_sprint(sprint_end=True)
    else:
        archive_sprint()