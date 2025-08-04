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

def archive_sprint(sprint_end=False, force_archive=False):
    """Archive messages with enhanced strategies for long-running systems."""
    # Read current comm.json with error handling
    try:
        with open('comm.json', 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Error reading comm.json: {e}")
        return False
    
    all_messages = data.get('messages', [])
    active_sprint = data.get('active_sprint', None)
    
    # ENHANCED ARCHIVAL TRIGGERS
    file_size_mb = os.path.getsize('comm.json') / (1024 * 1024)
    message_count = len(all_messages)
    
    # Auto-archive triggers for long-running systems
    should_auto_archive = (
        force_archive or 
        file_size_mb > 1.0 or  # File larger than 1MB
        message_count > 150 or  # More than 150 messages
        (message_count > 50 and not active_sprint)  # Many messages but no active sprint
    )
    
    if should_auto_archive and not sprint_end:
        print(f"📦 AUTO-ARCHIVE triggered: {message_count} messages, {file_size_mb:.2f}MB")
        _perform_regular_archive(data, all_messages)
        return True
    
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
        # Regular archiving
        _perform_regular_archive(data, all_messages)

def _perform_regular_archive(data, all_messages):
    """Enhanced regular archiving with smart retention."""
    total_count = len(all_messages)
    print(f"Total messages found: {total_count}")
    
    # Smart retention based on message age and activity
    if total_count <= 20:
        print("No need to archive - 20 or fewer messages")
        return
    
    current_time = datetime.now().timestamp()
    
    # Keep messages from last 24 hours + last 20 messages minimum
    recent_messages = []
    older_messages = []
    
    for msg in all_messages:
        msg_age_hours = (current_time - msg['ts']) / 3600
        if msg_age_hours < 24 or len(recent_messages) < 20:
            recent_messages.append(msg)
        else:
            older_messages.append(msg)
    
    # Ensure we keep at least 20 messages
    if len(recent_messages) < 20:
        needed = 20 - len(recent_messages)
        if older_messages:
            recent_messages.extend(older_messages[-needed:])
            older_messages = older_messages[:-needed]
    
    if not older_messages:
        print("✅ All messages are recent or within minimum retention")
        return
    
    # Enhanced archive structure
    archive_path = 'comm_archive.json'
    if os.path.exists(archive_path):
        try:
            with open(archive_path, 'r') as f:
                archive_data = json.load(f)
        except json.JSONDecodeError:
            print("⚠️  Archive corrupted, creating new one")
            archive_data = {"archived_messages": [], "archive_sessions": []}
    else:
        archive_data = {"archived_messages": [], "archive_sessions": []}
    
    # Create archive session with more metadata
    archive_session = {
        "archived_at": datetime.now().isoformat(),
        "message_count": len(older_messages),
        "retention_strategy": "24h_recent_plus_20_minimum",
        "first_message_ts": older_messages[0]['ts'] if older_messages else None,
        "last_message_ts": older_messages[-1]['ts'] if older_messages else None,
        "agents_involved": list(set(msg.get('from', 'unknown') for msg in older_messages)),
        "file_size_before_mb": os.path.getsize('comm.json') / (1024 * 1024)
    }
    
    # Add to archive
    archive_data['archived_messages'].extend(older_messages)
    archive_data['archive_sessions'].append(archive_session)
    
    # Keep archive manageable (max 10,000 archived messages)
    if len(archive_data['archived_messages']) > 10000:
        archive_data['archived_messages'] = archive_data['archived_messages'][-10000:]
        print("⚠️  Archive trimmed to last 10,000 messages")
    
    # Save archive with error handling
    try:
        with open(archive_path, 'w') as f:
            json.dump(archive_data, f, indent=2)
    except Exception as e:
        print(f"❌ Archive save failed: {e}")
        return
    
    # Update comm.json
    data['messages'] = sorted(recent_messages, key=lambda x: x['ts'])
    data['metadata']['last_archived'] = datetime.now().isoformat()
    data['metadata']['archive_stats'] = {
        "archived_count": len(older_messages),
        "retained_count": len(recent_messages),
        "archive_sessions_total": len(archive_data['archive_sessions'])
    }
    
    try:
        with open('comm.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ comm.json update failed: {e}")
        return
    
    print(f"✅ Archived {len(older_messages)} messages")
    print(f"📋 Kept {len(recent_messages)} recent messages")
    print(f"📦 Archive contains {len(archive_data['archived_messages'])} total messages")

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

def check_system_health():
    """Check communication system health and recommend actions."""
    try:
        with open('comm.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ comm.json health check failed: {e}")
        return
    
    messages = data.get('messages', [])
    file_size_mb = os.path.getsize('comm.json') / (1024 * 1024)
    
    print(f"🔍 SYSTEM HEALTH CHECK:")
    print(f"   Messages: {len(messages)}")
    print(f"   File size: {file_size_mb:.2f}MB")
    print(f"   Active sprint: {data.get('active_sprint', {}).get('id', 'None')}")
    
    # Health recommendations
    if file_size_mb > 0.5:
        print(f"⚠️  RECOMMENDATION: File size large, consider archiving")
    if len(messages) > 100:
        print(f"⚠️  RECOMMENDATION: Many messages, consider archiving")
    
    # Check for patterns that might indicate issues
    recent_messages = [m for m in messages if (datetime.now().timestamp() - m['ts']) < 3600]
    if len(recent_messages) > 50:
        print(f"⚠️  HIGH ACTIVITY: {len(recent_messages)} messages in last hour")
    
    print("✅ Health check complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trinity sprint and message archiving')
    parser.add_argument('--sprint-end', action='store_true', help='Archive current sprint and prepare for new one')
    parser.add_argument('--start-sprint', nargs=3, metavar=('GOAL', 'RAGE_START', 'RAGE_TARGET'),
                       help='Start new sprint with goal and USER RAGE metrics')
    parser.add_argument('--force', action='store_true', help='Force archive regardless of size/count')
    parser.add_argument('--health', action='store_true', help='Check communication system health')
    
    args = parser.parse_args()
    
    if args.health:
        check_system_health()
    elif args.start_sprint:
        goal, rage_start, rage_target = args.start_sprint
        start_new_sprint(goal, int(rage_start), int(rage_target))
    elif args.sprint_end:
        archive_sprint(sprint_end=True)
    else:
        archive_sprint(force_archive=args.force)