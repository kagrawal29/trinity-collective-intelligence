# PROJECT INDEX - Trinity Multi-Agent Evolution

**Last Updated**: 2025-08-04  
**Purpose**: Comprehensive documentation of Trinity's multi-agent orchestration system

## Overview
Advanced multi-agent orchestration system for LangGraph projects featuring:
- **3 Main Agents**: Guide (Orchestrator), Tyler (Chaos Testing), Dev (Architecture)
- **9+ Sub-Agents**: Specialized capabilities via Task tool invocation
- **Python Communication**: ACK-based messaging with retry logic
- **60-Second Cycles**: Continuous orchestration and monitoring
- **Sprint Management**: Structured task execution with handoffs

## Core System Architecture

### Main Agents
1. **Guide** (Strategic Orchestrator)
   - Location: `/trinity/CLAUDE.md`
   - Role: Orchestration, sprint management, team coordination
   - Sub-agents: harmony-checker, cycle-enforcer, behavior-updater, git-keeper, sprint-conductor, consul, chronicle

2. **Tyler** (Chaos Testing Expert)
   - Location: `/trinity/agents/e2e-Tester/CLAUDE.md`
   - Role: Edge case discovery, failure analysis, stress testing
   - Sub-agents: edge-generator, failure-capturer, test-documenter

3. **Dev** (Architecture Specialist)
   - Location: `/trinity/agents/dev/CLAUDE.md`
   - Role: Pattern analysis, node building, code transformation
   - Sub-agents: pattern-analyzer, node-builder, phoenix

### Communication Infrastructure

**Python Scripts** (`/trinity/agents/`):
- **send_message.py** - Robust message sending with ACK tracking and retry logic
- **check_messages.py** - Monitor unread/unacked messages
- **archive_comm.py** - Archive old communications with sprint TLDRs
- **cycle_comm.py** - Manage orchestration cycles
- **comm_monitor.py** - Real-time health monitoring
- **comm_recovery.py** - Automatic recovery from failures
- **comm.json** - Message queue (auto-managed)

**Protocol Features**:
- ACK-based tracking prevents message loops
- Retry logic with exponential backoff
- Automatic overflow management
- Recovery from communication failures
- Clean archival system

### Sub-Agent System (`/trinity/.claude/agents/`)

**Guide's Orchestration Sub-Agents**:
- **harmony-checker.md** - Monitor team alignment, detect stuck loops
- **cycle-enforcer.md** - Ensure all agents follow operational rhythms
- **behavior-updater.md** - Extract learnings and update prompts
- **git-keeper.md** - Version control and persistence
- **sprint-conductor.md** - Manage sprint lifecycle
- **consul.md** - User consultation and priority discovery
- **chronicle.md** - Memory keeper and decision recording
- **weaver.md** - Context management

**Tyler's Testing Sub-Agents** (`/trinity/agents/e2e-Tester/.claude/agents/`):
- **edge-generator.md** - Create chaos testing scenarios
- **failure-capturer.md** - Document and analyze failures
- **test-documenter.md** - Track testing patterns

**Dev's Architecture Sub-Agents** (`/trinity/agents/dev/.claude/agents/`):
- **pattern-analyzer.md** - Research and analyze code patterns
- **node-builder.md** - Construct architectural nodes
- **phoenix.md** - Transform pain into healing code

### Sub-Agent Invocation Pattern
```bash
Task tool subagent_type="general-purpose" 
prompt="Act as [agent-name]. Read /trinity/.claude/agents/[agent-name].md. [specific task]"
```

## Orchestration Cycle (60 seconds)

```bash
while true; do
    # 1. CHECK PHASE - harmony-checker monitors alignment
    python3 agents/check_messages.py guide
    Task tool subagent="harmony-checker"
    
    # 2. ASSESS PHASE - cycle-enforcer verifies rhythms
    Task tool subagent="cycle-enforcer"
    
    # 3. GUIDE PHASE - Direct intervention if needed
    if [issues detected]; then
        python3 agents/send_message.py tyler/dev "[guidance]"
    fi
    
    # 4. ARCHIVE PHASE - Clean communication queue (every 3 cycles)
    python3 agents/archive_comm.py
    
    # 5. LEARN PHASE - Extract patterns (every 5 cycles)
    Task tool subagent="behavior-updater"
    
    # 6. SAVE PHASE - Git commit (every 10 cycles)
    Task tool subagent="git-keeper"
    
    sleep 60
done
```

## Key Documentation Files

- **CLAUDE.md** - Behavioral instructions for each agent
- **README.md** - User-facing documentation and setup guide
- **TRINITY_CYCLE_FLOW.md** - Detailed orchestration documentation
- **SPRINT_HISTORY.md** - Sprint tracking and progress
- **CONTRIBUTION_SUMMARY.md** - Summary of Trinity evolution features
- **LICENSE** - MIT License for open-source distribution

## Integration with LangGraph Projects

### Perfect For:
- **State Machine Development**: Tyler tests state transitions
- **Agent Graph Construction**: Dev builds node architecture
- **Workflow Orchestration**: Guide manages overall flow
- **Edge Case Discovery**: Tyler's chaos testing finds issues early
- **Pattern Analysis**: Dev identifies reusable patterns

### Setup for Your LangGraph Project:
1. Clone Trinity into your project directory
2. Open 3 terminals for Guide, Tyler, and Dev
3. Start orchestration cycle
4. Trinity will coordinate work on your LangGraph components

### Benefits:
- Automatic state validation through chaos testing
- Systematic node construction with architectural patterns
- Continuous integration testing of agent interactions
- Sprint-based feature development
- Self-improving through behavioral updates

## Success Metrics

✅ **Teams report sub-agent activity** - "Using pattern-analyzer for research"  
✅ **Clean message handoffs** - No stuck loops or repetition  
✅ **Sprint progress visible** - Clear task completion  
✅ **Behavioral improvements** - Prompts evolve over time  
✅ **Communication health GREEN** - harmony-checker reports healthy  
✅ **All cycles synchronized** - cycle-enforcer confirms rhythm  

## Technical Innovations

### Behavioral Evolution
- Long-term changes through CLAUDE.md prompt updates
- Learning extraction via behavior-updater
- No code changes needed for behavioral shifts

### Communication Protocol
```json
{
    "id": "unique_id",
    "from": "sender",
    "to": "recipient",
    "body": "message content",
    "ack": false,
    "ts": 1234567890.123,
    "processed_ids": ["previous_message_ids"]
}
```

### Sprint Management
- Open → Active → Close lifecycle
- Task discipline with sprint goals
- Proper handoffs between teams
- Archival with TLDRs

## Future Enhancements
- Enhanced LangGraph state management
- Vector storage for memory system
- Cross-team sub-agent collaboration
- Automated sprint planning
- Performance metrics dashboard

---
*Living document - Trinity Multi-Agent Evolution v2.0*