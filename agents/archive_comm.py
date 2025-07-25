#!/usr/bin/env python3
"""
Script to archive old messages from comm.json to comm_archive.json
Keeps only the last 10 messages in comm.json
"""

import json
from datetime import datetime
import os

def archive_messages():
    # Read current comm.json
    with open('comm.json', 'r') as f:
        data = json.load(f)
    
    # Get all messages
    all_messages = data['messages']
    total_count = len(all_messages)
    
    print(f"Total messages found: {total_count}")
    
    if total_count <= 10:
        print("No need to archive - 10 or fewer messages")
        return
    
    # Split messages
    messages_to_archive = all_messages[:-10]  # All but last 10
    messages_to_keep = all_messages[-10:]     # Last 10
    
    print(f"Messages to archive: {len(messages_to_archive)}")
    print(f"Messages to keep: {len(messages_to_keep)}")
    
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
        "last_message_ts": messages_to_archive[-1]['ts'],
        "total_messages_before": total_count,
        "messages_kept": len(messages_to_keep)
    }
    
    # Add to archive
    archive_data['archived_messages'].extend(messages_to_archive)
    archive_data['archive_sessions'].append(archive_session)
    
    # Save archive
    with open(archive_path, 'w') as f:
        json.dump(archive_data, f, indent=2)
    
    # Update comm.json with only last 10 messages
    data['messages'] = messages_to_keep
    data['metadata']['last_archived'] = datetime.now().isoformat()
    data['metadata']['total_archived'] = len(archive_data['archived_messages'])
    
    with open('comm.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Successfully archived {len(messages_to_archive)} messages")
    print(f"✅ Kept last {len(messages_to_keep)} messages in comm.json")
    print(f"✅ Total messages in archive: {len(archive_data['archived_messages'])}")

if __name__ == "__main__":
    archive_messages()