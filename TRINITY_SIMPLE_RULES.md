# Trinity Simple Rules - Preventing Documentation Bloat

## 🚨 THE PATTERN WE CAN'T BREAK
Even while writing these rules, we created 9 more documents.
The urge to document is unconscious. We must actively fight it.

## NEW BEHAVIORAL INTERRUPT
When someone asks "How do we...?" or "What about...?":
1. STOP before creating a .md file
2. First try to answer with a bash command
3. Only document if the command doesn't work

## The 3-Document Rule

For ANY project, Trinity maintains only 3 documents:

1. **CURRENT_WORK.md** - What we're doing right now
2. **DECISIONS.md** - Why we made key choices  
3. **PAIN_POINTS.md** - What's actually broken

That's it. No more.

## When to Create Documents

ONLY create a document when:
- A user explicitly asks for it
- You hit the same problem 3+ times
- You need to share critical info between sessions

## When to Use Sub-Agents

ONLY invoke sub-agents when:
- You have a specific, immediate need
- The task matches their specialty exactly
- Basic tools aren't sufficient

## The Test

Before creating ANY document, ask:
1. Will someone read this next week?
2. Does it solve a problem we've actually had?
3. Can this info live in code comments instead?

If any answer is "no" → don't create it.

## Example

Bad:
- Created 28 documents about a documentation system
- Solved theoretical future problems
- Built complex architecture before proving need

Good:
- Start with 0 documents
- Add only when pain is real
- Keep solutions simple

## Remember

> "The best documentation is no documentation. The second best is a single page that actually gets read."

Real projects need code, not manifestos about code.