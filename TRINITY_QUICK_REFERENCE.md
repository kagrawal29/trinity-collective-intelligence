# Trinity Quick Reference - The Only Doc You Need

## Core Documents (Maximum 3)
- `/TRINITY_SIMPLE_RULES.md` - How to avoid bloat
- `/TRINITY_QUICK_REFERENCE.md` - This file
- `/CLAUDE.md` - Guide's prompt (Tyler & Dev have their own)

## Sub-Agents Location
All in `/.claude/agents/`:
- `weaver` - Context management
- `havoc` - Pain capture  
- `tempest` - Edge cases
- `merlin` - Pattern recognition
- `phoenix` - Healing engine
- `chronicle` - History keeper

## How to Use
```bash
# View available agents
/agents

# Use when needed (like grep/sed)
"Use havoc to capture this login bug"
"Use merlin to find the pattern"
```

## The 3-Document Rule
For ANY new project:
1. CURRENT_WORK.md - Active tasks
2. DECISIONS.md - Why choices (if asked 3+ times)  
3. PAIN_POINTS.md - Real problems with evidence

## Remember
- We created 28 documents about documentation (don't repeat this)
- Best documentation is no documentation
- Code comments > separate docs
- Only document what hurts 3+ times
- Cleanup doesn't happen - prevent creation instead