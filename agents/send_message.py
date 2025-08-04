#!/usr/bin/env python3
"""
Send messages between Tyler, Guide, Dev, and E2E agents via comm.json
Usage: python3 send_message.py <to_agent> "Your message here" [--from <from_agent>]
Examples:
  python3 send_message.py dev "Run tests on Investors page"
  python3 send_message.py guide "Tests completed" --from dev
"""
import json
import uuid
import time
import sys
import fcntl
import os
import tempfile
import subprocess
from datetime import datetime
import argparse

def validate_json_structure(data):
    """Ensure comm.json has correct structure"""
    if not isinstance(data, dict):
        return False, "Root must be a dictionary"
    if 'messages' not in data:
        return False, "Missing 'messages' key"
    if not isinstance(data['messages'], list):
        return False, "'messages' must be a list"
    
    # Validate each message structure
    for i, msg in enumerate(data['messages']):
        if not isinstance(msg, dict):
            return False, f"Message {i} is not a dictionary"
        required_keys = {'id', 'from', 'to', 'body', 'ack', 'ts'}
        missing_keys = required_keys - set(msg.keys())
        if missing_keys:
            return False, f"Message {i} missing keys: {missing_keys}"
    
    return True, "Valid"

def signal_corruption_to_guide(error_details):
    """Create a signal file for GUIDE to handle JSON recovery"""
    signal_file = os.path.join(os.path.dirname(__file__), ".json_corrupted")
    recovery_info = {
        "timestamp": datetime.now().isoformat(),
        "error": str(error_details),
        "handler": "guide",
        "action_needed": "Reset comm.json and recover from archive if possible"
    }
    
    try:
        with open(signal_file, 'w') as f:
            json.dump(recovery_info, f, indent=2)
        print(f"⚠️  JSON corruption detected. Signaled GUIDE for recovery.")
    except:
        print(f"❌ Critical: Could not create recovery signal!")

def atomic_json_write(filepath, data):
    """Write JSON atomically using temp file and rename"""
    # Validate structure before writing
    is_valid, error_msg = validate_json_structure(data)
    if not is_valid:
        raise ValueError(f"Invalid JSON structure: {error_msg}")
    
    # Create temp file in same directory for atomic rename
    dir_name = os.path.dirname(filepath) or '.'
    temp_fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix='.tmp_comm_')
    
    try:
        # Write to temp file
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')  # Add newline at end of file
        
        # Atomic rename (replaces original)
        os.replace(temp_path, filepath)
        return True
    except Exception as e:
        # Clean up temp file if something went wrong
        try:
            os.unlink(temp_path)
        except:
            pass
        raise e

def check_message_constraints(from_agent, message, data):
    """Check message constraints: rate limits, size, content validation"""
    import time
    current_time = time.time()
    
    # 1. MESSAGE SIZE LIMITS (prevent bloat)
    MAX_MESSAGE_SIZE = 8192  # 8KB per message
    if len(message.encode('utf-8')) > MAX_MESSAGE_SIZE:
        return False, f"Message too large: {len(message.encode('utf-8'))} bytes (max {MAX_MESSAGE_SIZE})"
    
    # 2. RATE LIMITING
    recent_messages = [msg for msg in data.get("messages", []) 
                      if msg["from"] == from_agent and (current_time - msg["ts"]) < 300]  # 5 minutes
    
    if len(recent_messages) > 20:  # More than 20 messages in 5 minutes
        return False, f"Rate limit exceeded: {len(recent_messages)} messages in 5 minutes"
    
    # 3. DUPLICATE DETECTION
    if len(recent_messages) >= 3:
        last_three = recent_messages[-3:]
        if all(msg["body"] == last_three[0]["body"] for msg in last_three):
            return False, "Duplicate message loop detected"
    
    # 4. CONTENT VALIDATION (prevent malicious payloads)
    if message.count('{') > 10 or message.count('[') > 10:
        return False, "Message contains excessive JSON-like structure"
    
    # 5. UNICODE VALIDATION
    try:
        message.encode('utf-8').decode('utf-8')
    except UnicodeError:
        return False, "Message contains invalid Unicode"
    
    return True, "OK"

def send_message_with_lock(to_agent, message, from_agent="user"):
    """Send message with file locking and rate limiting to prevent race conditions and loops"""
    comm_file = os.path.join(os.path.dirname(__file__), "comm.json")
    lock_file = os.path.join(os.path.dirname(__file__), ".comm.lock")
    max_retries = 5
    retry_delay = 0.5
    
    # Validate agent names
    valid_agents = ["tyler", "guide", "dev", "e2e"]
    if to_agent not in valid_agents:
        print(f"Error: 'to' agent must be one of: {', '.join(valid_agents)}")
        return False
    if from_agent not in valid_agents + ["user"]:
        print(f"Error: 'from' agent must be one of: {', '.join(valid_agents + ['user'])}")
        return False
    
    for attempt in range(max_retries):
        try:
            # Use a separate lock file to avoid issues with JSON reading
            with open(lock_file, 'w') as lock_f:
                # Acquire exclusive lock
                fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
                
                # Read current data
                try:
                    with open(comm_file, 'r') as f:
                        content = f.read()
                        if not content.strip():
                            # Empty file, initialize
                            data = {"messages": [], "metadata": {"last_updated": datetime.now().isoformat()}}
                        else:
                            data = json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    signal_corruption_to_guide(e)
                    # Initialize with empty structure
                    data = {"messages": [], "metadata": {"last_updated": datetime.now().isoformat()}}
                except FileNotFoundError:
                    # File doesn't exist, create it
                    data = {"messages": [], "metadata": {"last_updated": datetime.now().isoformat()}}
                
                # Validate loaded data
                is_valid, error_msg = validate_json_structure(data)
                if not is_valid:
                    print(f"❌ Invalid JSON structure: {error_msg}")
                    signal_corruption_to_guide(error_msg)
                    # Reset to valid structure
                    data = {"messages": [], "metadata": {"last_updated": datetime.now().isoformat()}}
                
                # Check message constraints (rate, size, content)
                constraints_ok, constraint_msg = check_message_constraints(from_agent, message, data)
                if not constraints_ok:
                    print(f"❌ Message blocked: {constraint_msg}")
                    # Signal to Guide for intervention
                    signal_corruption_to_guide(f"Message constraint violation by {from_agent}: {constraint_msg}")
                    return False
                
                # Check file size and auto-archive if needed
                message_count = len(data.get("messages", []))
                if message_count > 200:  # More aggressive archiving
                    print(f"⚠️  Message count high: {message_count}, triggering auto-archive")
                    try:
                        # Trigger auto-archival before adding new message
                        subprocess.run(["python3", "archive_comm.py"], 
                                     cwd=os.path.dirname(__file__), 
                                     capture_output=True, check=True)
                        # Reload data after archival
                        with open(comm_file, 'r') as f:
                            data = json.loads(f.read())
                        print(f"✅ Auto-archived, new count: {len(data.get('messages', []))}")
                    except Exception as e:
                        print(f"❌ Auto-archive failed: {e}")
                        signal_corruption_to_guide(f"Auto-archive failure: {e}")
                        return False
                elif message_count > 500:  # Hard limit
                    print(f"❌ Message hard limit exceeded: {message_count} messages")
                    signal_corruption_to_guide(f"Message overflow: {message_count} messages")
                    return False
                
                # Add new message
                new_message = {
                    "id": str(uuid.uuid4()),
                    "from": from_agent,
                    "to": to_agent,
                    "body": message,
                    "ack": False,
                    "ts": time.time()
                }
                data["messages"].append(new_message)
                
                # Update metadata
                if "metadata" not in data:
                    data["metadata"] = {}
                data["metadata"]["last_updated"] = datetime.now().isoformat()
                
                # Write atomically
                atomic_json_write(comm_file, data)
                
                # Release lock (happens automatically when file closes)
                print(f"✅ Sent message from {from_agent.upper()} to {to_agent.upper()}: {message[:50]}...")
                return True
                
        except BlockingIOError:
            # Lock is held by another process, retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                print(f"❌ Failed to acquire lock after {max_retries} attempts")
                return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            signal_corruption_to_guide(e)
            return False
    
    return False

def acknowledge_messages(agent_name):
    """Mark all messages to a specific agent as acknowledged"""
    comm_file = os.path.join(os.path.dirname(__file__), "comm.json")
    lock_file = os.path.join(os.path.dirname(__file__), ".comm.lock")
    
    try:
        with open(lock_file, 'w') as lock_f:
            fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
            
            with open(comm_file, 'r') as f:
                data = json.loads(f.read())
            
            # Acknowledge messages
            ack_count = 0
            for msg in data.get("messages", []):
                if msg["to"] == agent_name and not msg["ack"]:
                    msg["ack"] = True
                    ack_count += 1
            
            if ack_count > 0:
                atomic_json_write(comm_file, data)
                print(f"✅ Acknowledged {ack_count} messages for {agent_name.upper()}")
            
            return True
    except Exception as e:
        print(f"❌ Error acknowledging messages: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send messages between agents')
    parser.add_argument('to_agent', help='Target agent (tyler, guide, dev, e2e)')
    parser.add_argument('message', help='Message to send')
    parser.add_argument('--from', dest='from_agent', default='user', 
                        help='Sender agent (default: user)')
    parser.add_argument('--ack', action='store_true', 
                        help='Acknowledge all messages for the sender')
    
    args = parser.parse_args()
    
    # If acknowledging messages
    if args.ack and args.from_agent != 'user':
        acknowledge_messages(args.from_agent)
    
    # Send the message
    success = send_message_with_lock(args.to_agent.lower(), args.message, args.from_agent.lower())
    if not success:
        sys.exit(1)