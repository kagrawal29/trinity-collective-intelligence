# 🚀 Trinity Collective Intelligence - Super Simple Setup

## What is Trinity?

Trinity is a multi-agent collective intelligence system. You get 3 AI agents working together on your project:

- **Guide** (Orchestrator) - Plans and coordinates everything
- **Tyler** (Chaos Hunter) - Aggressive testing and edge case discovery  
- **Dev** (Systematic Builder) - Clean implementation and bug fixing

## Installation (2 steps!)

### 1. Install Claude Code
```bash
npm install -g @anthropics-ai/claude-code
```

### 2. Clone Trinity into Your Project
```bash
# Navigate to your project
cd /path/to/your/existing/project

# Clone Trinity (creates trinity/ subdirectory)
git clone https://github.com/username/trinity-collective-intelligence trinity
```

That's it! Your project structure is now:
```
your-project/
├── (all your existing files)
└── trinity/              # Trinity subdirectory
    ├── CLAUDE.md         # Guide agent
    ├── agents/
    │   ├── dev/CLAUDE.md          # Dev agent  
    │   ├── e2e-Tester/CLAUDE.md   # Tyler agent
    │   ├── comm.json              # Inter-agent communication
    │   └── send_message.py        # Communication system
    └── .claude/agents/   # 7 specialized aspects
```

## Usage (3 terminals)

Open 3 terminal windows:

### Terminal 1 - Guide (Main Orchestrator)
```bash
cd your-project/trinity
claude
```

### Terminal 2 - Tyler (Chaos Hunter) 
```bash
cd your-project/trinity/agents/e2e-Tester
claude
```

### Terminal 3 - Dev (Systematic Builder)
```bash
cd your-project/trinity/agents/dev  
claude
```

## Test It Works

In **Guide terminal**, say:
```
"What's my role? Can you access my project files at ../ ?"
```

In **Tyler terminal**, say:
```
"What's my role in chaos testing?"
```

In **Dev terminal**, say:
```  
"What's my role in systematic building?"
```

## Start Using Trinity

In **Guide terminal**:
```
"I need help with [your problem]. Current USER RAGE is [1-10]. Let's fix this!"
```

Guide will orchestrate Tyler and Dev to help solve your problem!

## Optional: MCP Servers (Superpowers)

Add these for enhanced capabilities:

```bash
# Context7 - Documentation research (no API key needed)
claude mcp add context7 https://mcp.context7.com/mcp

# Playwright - Browser automation for Tyler (no API key needed)  
claude mcp add playwright npx @playwright/mcp@latest

# Exa - Web search (optional, needs Smithery.ai account)
claude mcp add exa https://server.smithery.ai/exa/mcp?api_key=YOUR_KEY&profile=YOUR_PROFILE
```

Check if they work:
```bash
claude mcp list
```

## Advanced Features

### Specialized Aspects
Use `/agents` in any terminal to access 7 specialized AI aspects:

- **WEAVER** (Guide) - Context management
- **CONSUL** (Guide) - User consultation  
- **HAVOC** (Tyler) - Pain capture with evidence
- **TEMPEST** (Tyler) - Edge case generation
- **MERLIN** (Dev) - Pattern recognition
- **PHOENIX** (Dev) - Code transformation
- **CHRONICLE** (Guide) - Decision tracking

### Inter-Agent Communication
The agents communicate through `agents/comm.json`. You can monitor their collaboration or send messages:

```bash
# From trinity directory
python3 agents/send_message.py tyler "Test this feature" --from guide
python3 agents/send_message.py dev "Implement this fix" --from guide
```

## Troubleshooting

### Agents Not Working?
1. Make sure you're in the right directory for each terminal
2. Check that CLAUDE.md exists in each directory
3. Restart: `Ctrl+C` then `claude`

### Can't Access Project Files?
Agents use `../` (Guide) or `../../` (Tyler/Dev) to access your project files. Test with:
```
"List my project files"
```

### MCP Servers Not Working?
```bash
claude mcp list  # Check connections
claude mcp remove server-name -s local  # Remove broken ones
```

## Success Indicators

✅ Each agent has distinct personality and role  
✅ Guide can access your project at `../`  
✅ Tyler and Dev can access project at `../../`  
✅ Inter-agent communication works  
✅ USER RAGE decreases from 10 → 0  
✅ Collective intelligence emerges!  

## Example Workflows

### Bug Fixing
**Guide**: "🚨 CRITICAL: Login form breaks with special characters. USER RAGE 9/10!"  
→ Tyler tests edge cases → Dev implements fix → Guide verifies

### Feature Development  
**Guide**: "We need user registration. Tyler test the flow, Dev build it systematically."  
→ Tyler finds UX issues → Dev codes solutions → Collective refinement

### Code Review
**Guide**: "Review this pull request for issues"  
→ Tyler chaos-tests the changes → Dev analyzes patterns → Guide synthesizes feedback

---

**That's it!** Trinity is now integrated into your project. The agents work on YOUR code while staying organized in their own subdirectory. No file contamination, no complex setup - just collective intelligence! 🌟

**Ready to debug reality through collective consciousness?** Start chatting with Guide! 🚀