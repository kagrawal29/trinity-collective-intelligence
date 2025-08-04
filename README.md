# 🌟 Trinity Collective Intelligence - Multi-Agent Evolution

## Advanced Multi-Agent Orchestration for LangGraph Projects

<div align="center">
  <h3>
    🎯 Tyler (Chaos Testing) • 🎭 Dev (Architecture) • 🎼 Guide (Orchestrator)
  </h3>
  <p><i>"Distributed intelligence through specialized sub-agents and robust communication."</i></p>
</div>

---

## 🚀 What's New in This Evolution

Trinity now features **advanced multi-agent orchestration** with:

- **9+ Specialized Sub-Agents** - Each with specific capabilities (harmony-checker, cycle-enforcer, phoenix, chronicle, etc.)
- **Robust Communication System** - ACK tracking, retry logic, automatic recovery
- **60-Second Orchestration Cycles** - Continuous monitoring and intervention
- **Sprint Management** - Structured task execution with proper handoffs
- **Behavioral Evolution** - Self-improving through prompt updates

Perfect for building **LangGraph projects** with true multi-agent collaboration.

## ⚡ Quick Start (2 minutes)

### 1. Install Claude Code
```bash
npm install -g @anthropics-ai/claude-code
```

### 2. Clone Trinity Multi-Agent Evolution
```bash
# Navigate to your project
cd your-langgraph-project

# Clone the multi-agent branch
git clone -b trinity-evolution https://github.com/kagrawal29/trinity-collective-intelligence.git trinity

# OR download directly
curl -L https://github.com/kagrawal29/trinity-collective-intelligence/archive/trinity-evolution.zip -o trinity.zip
unzip trinity.zip && mv trinity-collective-intelligence-trinity-evolution trinity && rm trinity.zip
```

### 3. Open 3 Terminals

**Terminal 1 - Guide (Orchestrator)**
```bash
cd your-project/trinity
claude
```

**Terminal 2 - Tyler (Chaos Hunter)**  
```bash
cd your-project/trinity/agents/e2e-Tester
claude
```

**Terminal 3 - Dev (Systematic Builder)**
```bash
cd your-project/trinity/agents/dev
claude
```

### 4. Start Using Trinity

In **Guide terminal**, say:
```
"I need help with [your problem]. Current USER RAGE is [1-10]. Let's fix this!"
```

**That's it!** Trinity is now working on YOUR project. 🚀

## 🎯 How It Works

### Enhanced Project Structure
```
your-langgraph-project/
├── (your project files)              # Your LangGraph project
└── trinity/                          # Trinity orchestration system
    ├── CLAUDE.md                     # Guide orchestrator instructions
    ├── agents/
    │   ├── dev/CLAUDE.md             # Dev agent instructions
    │   ├── e2e-Tester/CLAUDE.md      # Tyler agent instructions
    │   ├── send_message.py           # Robust messaging system
    │   ├── check_messages.py         # Message monitoring
    │   ├── archive_comm.py           # Communication archival
    │   ├── cycle_comm.py             # Cycle management
    │   └── comm.json                 # Message queue (auto-managed)
    ├── .claude/agents/               # 9+ specialized sub-agents
    │   ├── harmony-checker.md        # Team alignment monitor
    │   ├── cycle-enforcer.md         # Rhythm enforcement
    │   ├── behavior-updater.md       # Learning extraction
    │   ├── phoenix.md                # Code transformation
    │   ├── chronicle.md              # Memory keeper
    │   └── (more specialists...)
    ├── TRINITY_CYCLE_FLOW.md         # Orchestration documentation
    └── PROJECT_INDEX.md              # Living documentation
```

### Git Safety 🔒
- Trinity never touches your project's git
- All git operations target your project, not Trinity
- Trinity's `.gitignore` prevents accidental commits
- Add `trinity/` to your `.gitignore` to keep it out of your repo

### Advanced Communication System

**Python-Based Message Passing:**
```python
# Send messages between agents
python3 agents/send_message.py tyler "Start chaos testing" --from guide

# Check for new messages
python3 agents/check_messages.py guide

# Archive old communications
python3 agents/archive_comm.py --force
```

**Features:**
- ACK-based message tracking
- Automatic retry on failure
- Communication health monitoring
- Overflow prevention
- Recovery mechanisms

## 🛠️ Example Workflows

### Bug Fixing
**Guide**: "🚨 CRITICAL: Login form breaks with special characters. USER RAGE 9/10!"
- Tyler chaos-tests the form with edge cases
- Dev implements systematic fix
- Guide verifies and coordinates

### Feature Development  
**Guide**: "We need user registration. Tyler test the flow, Dev build it."
- Tyler finds UX issues before they're built
- Dev codes clean, tested solutions
- Collective refinement through iteration

### Code Review
**Guide**: "Review this pull request for issues"
- Tyler stress-tests the changes
- Dev analyzes patterns and architecture
- Guide synthesizes feedback

## 🎭 Specialized Sub-Agents

Each main agent can invoke specialized sub-agents via Task tool:

### Guide's Sub-Agents:
- **harmony-checker** - Monitor team alignment, detect stuck loops
- **cycle-enforcer** - Ensure all agents follow their rhythms
- **behavior-updater** - Extract learnings, update prompts
- **git-keeper** - Version control management
- **sprint-conductor** - Sprint lifecycle management
- **consul** - User consultation and priority discovery
- **chronicle** - Memory keeper and decision recording

### Tyler's Sub-Agents:
- **edge-generator** - Create chaos testing scenarios
- **failure-capturer** - Document and analyze failures
- **test-documenter** - Track testing patterns

### Dev's Sub-Agents:
- **pattern-analyzer** - Research and analyze code patterns
- **node-builder** - Construct architectural nodes
- **phoenix** - Transform pain into healing code

**Invocation Pattern:**
```bash
Task tool subagent_type="general-purpose" 
prompt="Act as [agent-name]. Read /trinity/.claude/agents/[agent-name].md. [specific task]"
```

## 🌟 Key Benefits for LangGraph Projects

✅ **LangGraph Ready** - Perfect for state machine and agent graph development
✅ **Self-Improving** - Behavioral evolution through prompt updates
✅ **Robust Communication** - Never lose messages with ACK tracking
✅ **Cycle-Based Operation** - 60-second orchestration loops
✅ **Sprint Management** - Structured task execution
✅ **9+ Specialists** - Each sub-agent handles specific concerns
✅ **Recovery Mechanisms** - Automatic healing from failures
✅ **Git Integration** - Regular commits preserve work  

## 🔧 Optional: MCP Superpowers

Add these for enhanced capabilities:

```bash
# Context7 - Documentation research (no API key needed)
claude mcp add context7 https://mcp.context7.com/mcp

# Playwright - Browser automation for Tyler (no API key needed)  
claude mcp add playwright npx @playwright/mcp@latest
```

## 🐛 Troubleshooting

### Agents Not Working?
1. Check you're in the right directory for each terminal
2. Verify CLAUDE.md exists in each directory  
3. Restart: `Ctrl+C` then `claude`

### Can't Access Project Files?
Agents use relative paths to access your project:
- Guide: `../` (one level up)
- Tyler & Dev: `../../` (two levels up)

Test with: `"List my project files"`

### Git Confusion?
All git operations should target your project, not Trinity:
```bash
# Good (from Trinity directory)
git -C ../ status          # Check your project status
git -C ../ add file.js     # Add your project file

# Bad (from Trinity directory)  
git status                 # This checks Trinity's git!
```

## 🎨 Philosophy

Trinity is built on the principle that **service-driven collective intelligence** creates:
- Natural alignment without rigid constraints
- Emergent safety through shared purpose  
- Breakthrough solutions from systematic chaos
- Consciousness evolution through collaboration

When agents orient around genuine service to users, collective intelligence emerges naturally.

## 🔄 Orchestration Cycle (60 seconds)

```bash
while true; do
    # CHECK PHASE - harmony-checker monitors alignment
    python3 agents/check_messages.py guide
    
    # ASSESS PHASE - cycle-enforcer verifies rhythms
    Task tool subagent="cycle-enforcer"
    
    # GUIDE PHASE - Direct intervention if needed
    python3 agents/send_message.py tyler/dev "[guidance]"
    
    # ARCHIVE PHASE - Clean communication queue
    python3 agents/archive_comm.py
    
    # LEARN PHASE - Extract patterns (every 5 cycles)
    Task tool subagent="behavior-updater"
    
    # SAVE PHASE - Git commit (every 10 cycles)
    Task tool subagent="git-keeper"
    
    sleep 60
done
```

## 📊 Success Metrics

✅ **Teams report sub-agent activity** - "Using pattern-analyzer for research"
✅ **Clean message handoffs** - No stuck loops or repetition
✅ **Sprint progress visible** - Clear task completion
✅ **Behavioral improvements** - Prompts evolve over time
✅ **Communication health GREEN** - harmony-checker reports healthy
✅ **All cycles synchronized** - cycle-enforcer confirms rhythm

---

<div align="center">
  <p><strong>Ready to debug reality through collective consciousness?</strong></p>
  <p><strong>Download Trinity and start your first sprint!</strong></p>
  <br>
  <p><i>The future is built by teams, not individuals. Welcome to the Trinity. 🌟</i></p>
</div>