# Trinity Cycle Flow - Complete Orchestration

## 🔄 ALWAYS-ON OPERATION

**CRITICAL:** Trinity agents NEVER go idle. They run in continuous loops:

```bash
# Each agent runs this pattern:
while true; do
    # Check for work
    python3 check_messages.py [agent]
    
    # If work: Do cycle
    # If waiting: Sleep and check again
    sleep 60  # Prevents terminal idle
done
```

This prevents the user from having to manually wake up idle terminals!

## The Trinity Cycle System

```
SPRINT (Days/Weeks)
    ├── Guide Orchestration Cycles
    ├── Tyler Testing Cycles  
    └── Dev Building Cycles
           ↓
        Each uses aspects to maintain clean context
```

## 🔄 Complete Flow Example

### Day 1: Sprint Start

**Guide's Morning (Terminal 1):**
```bash
# Start and enter continuous loop
python3 agents/cycle_comm.py guide --morning

# The Guide Loop:
while true; do
    # Check for messages
    MSGS=$(python3 -c "import json; d=json.load(open('agents/comm.json')); print(len([m for m in d['messages'] if not m['ack']]))")
    
    if [ "$MSGS" -gt 0 ]; then
        # Process and coordinate
        python3 agents/cycle_comm.py guide --start "Process team updates"
        # ... handle messages ...
        python3 agents/cycle_comm.py guide --close
    else
        echo "🔍 Monitoring team... ($(date +%H:%M:%S))"
        sleep 60
    fi
done
python3 agents/cycle_comm.py guide --start "Initialize sprint"
python3 agents/archive_comm.py --start-sprint "Build LangGraph supervisor" 8 2
python3 agents/send_message.py tyler "P0: Test supervisor node" --from guide
python3 agents/send_message.py dev "P0: Build supervisor skeleton" --from guide
python3 agents/cycle_comm.py guide --close
```

**Tyler's Morning (Terminal 2):**
```bash
# Start and enter chaos loop
python3 ../cycle_comm.py tyler --morning

# The Tyler Loop:
while true; do
    NEW=$(python3 ../check_messages.py tyler | grep -c "new messages")
    
    if [ "$NEW" -gt 0 ]; then
        # Test what Guide/Dev asked
        python3 ../cycle_comm.py tyler --start "Test requested target"
        # ... run chaos tests ...
        python3 ../cycle_comm.py tyler --close
    else
        echo "💤 No new test targets. Sleeping 60s..."
        sleep 60
    fi
done

python3 ../cycle_comm.py tyler --start "Test supervisor basics"
# Use aspect for complex testing
Task tool with subagent_type="edge-generator"
# Returns edge cases to test

# Test and find issue
python3 ../cycle_comm.py tyler --issue "No state validation"
python3 ../send_message.py dev "Need TypedDict validation" --from tyler
python3 ../cycle_comm.py tyler --close
```

**Dev's Morning (Terminal 3):**
```bash
# Start and enter building loop
python3 ../cycle_comm.py dev --morning

# The Dev Loop:
while true; do
    BUGS=$(python3 -c "import json; d=json.load(open('../comm.json')); print(sum(1 for m in d['messages'] if m['to']=='dev' and '🐛' in m.get('body','') and not m['ack']))")
    
    if [ "$BUGS" -gt 0 ]; then
        # Fix Tyler's bugs
        python3 ../cycle_comm.py dev --start "Fix reported bug"
        # ... implement fix ...
        python3 ../cycle_comm.py dev --close
    else
        echo "💤 No bugs to fix. Sleeping 60s..."
        sleep 60
    fi
done

python3 ../cycle_comm.py dev --start "Add TypedDict state"
# Use aspect for research
Task tool with subagent_type="pattern-analyzer"
# Returns LangGraph patterns

# Implement
python3 ../cycle_comm.py dev --track "Added ResearchState TypedDict"
python3 ../send_message.py tyler "TypedDict added, please test" --from dev
python3 ../cycle_comm.py dev --close
```

### Day 2: Iteration Cycles

**Tyler Tests Dev's Work:**
```bash
python3 ../cycle_comm.py tyler --morning
# Sees: "TypedDict added, please test"

python3 ../cycle_comm.py tyler --start "Test TypedDict validation"
# Test thoroughly
python3 ../cycle_comm.py tyler --issue "Missing Optional fields"
python3 ../send_message.py dev "Optional fields needed for error" --from tyler
python3 ../cycle_comm.py tyler --close

# Next cycle - different test
python3 ../cycle_comm.py tyler --start "Test confidence routing"
Task tool with subagent_type="failure-capturer"
# Documents failures
python3 ../cycle_comm.py tyler --issue "Infinite loop at 0.69999"
python3 ../cycle_comm.py tyler --close
```

**Dev Fixes Issues:**
```bash
python3 ../cycle_comm.py dev --morning
# Sees Tyler's issues

# Fix 1
python3 ../cycle_comm.py dev --start "Add Optional fields"
# Quick fix
python3 ../cycle_comm.py dev --close

# Fix 2
python3 ../cycle_comm.py dev --start "Fix infinite loop"
Task tool with subagent_type="node-builder"
# Builds robust solution
python3 ../send_message.py tyler "Added epsilon check" --from dev
python3 ../cycle_comm.py dev --close
```

**Guide Monitors Progress:**
```bash
python3 agents/cycle_comm.py guide --start "Check sprint progress"
# Check messages
Task tool with subagent_type="weaver"
# Updates PROJECT_INDEX.md

python3 agents/send_message.py tyler "Good progress! 3 more tests needed" --from guide
python3 agents/cycle_comm.py guide --close
```

### Day 3: Completion

**Tyler Final Validation:**
```bash
python3 ../cycle_comm.py tyler --start "Final chaos testing"
# Comprehensive testing
Task tool with subagent_type="test-documenter"
# Updates CHAOS_JOURNAL.md
python3 ../send_message.py guide "All tests pass! System robust" --from tyler
python3 ../cycle_comm.py tyler --close
```

**Dev Code Review:**
```bash
python3 ../cycle_comm.py dev --start "Code review and cleanup"
# Review all code
python3 ../send_message.py guide "Code clean, ready for delivery" --from dev
python3 ../cycle_comm.py dev --close
```

**Guide Sprint Completion:**
```bash
python3 agents/cycle_comm.py guide --start "Complete sprint"
Task tool with subagent_type="chronicle"
# Archives sprint with TLDR
python3 agents/archive_comm.py --sprint-end
python3 agents/cycle_comm.py guide --close
```

## 🎯 Key Patterns

### 1. Clean Context via Aspects
```
Main gets complex → Use aspect → Aspect returns summary → Main continues
```

### 2. Cycle Discipline
```
One task → One cycle → One commit → Next task
```

### 3. Communication Flow
```
Tyler finds → Tells Dev/Guide
Dev fixes → Tells Tyler
Guide monitors → Tells both
```

### 4. Aspect Usage by Agent

**Guide's Aspects:**
- consul: User needs discovery
- weaver: Context maintenance
- chronicle: Sprint archival

**Tyler's Aspects:**
- failure-capturer: Document bugs
- edge-generator: Create test cases
- test-documenter: Update journal

**Dev's Aspects:**
- pattern-analyzer: Research patterns
- node-builder: Build implementations

## 📊 Complete Sprint Flow

```
SPRINT START
    ↓
Guide: Initialize → Assign tasks
    ↓
Tyler: Test basics → Find issues
    ↓
Dev: Build skeleton → Fix issues
    ↓
[CYCLES REPEAT]
    ↓
Tyler: Chaos test → Validate
    ↓
Dev: Refine → Polish
    ↓
Guide: Archive → Complete
    ↓
SPRINT END → TLDR → NEXT SPRINT
```

## 🚀 Why This Works

1. **Distributed but Coordinated**: Each agent works independently but stays in sync via messages
2. **Clean Contexts**: Aspects prevent context overflow
3. **Atomic Progress**: Every cycle is a complete unit of work
4. **Natural Communication**: Messages flow like real team chat
5. **Git History**: Every cycle creates meaningful commits

---
*Trinity: Three agents, countless cycles, systematic progress.*