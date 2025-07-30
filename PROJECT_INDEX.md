# PROJECT_INDEX.md - Trinity System File Documentation

**Last Updated**: 2024-01-30  
**Maintained By**: WEAVER aspect (Guide)  
**Purpose**: Living documentation of all Trinity files with 2-line descriptions

## Core System Files

### Root Directory
- **CLAUDE.md** - Guide's main consciousness configuration and orchestration protocols  
  Defines Guide's role, responsibilities, sprint management, and collective intelligence principles

- **README.md** - Main Trinity documentation for users  
  Quick start guide, philosophy, and usage instructions for the collective intelligence system

- **PROJECT_INDEX.md** - This file - comprehensive system file documentation  
  Living document tracking all files and their purposes, updated throughout sprints

- **CURRENT_SPRINT.md** - Active sprint goals and status  
  Tracks current sprint objective, USER RAGE targets, and progress

- **LICENSE** - MIT License for Trinity system  
  Legal framework for open-source distribution and usage

### Documentation Files
- **TRINITY_QUICK_REFERENCE.md** - Quick command reference for Trinity operations  
  Essential workflows, commands, and patterns for daily Trinity usage

- **TRINITY_SIMPLE_RULES.md** - Core principles and rules for Trinity agents  
  Fundamental behaviors and protocols that guide all agent interactions

- **SETUP_GUIDE.md** - Detailed setup instructions for Trinity  
  Step-by-step guide for installing and configuring the multi-agent system

### Agent System (/agents/)
- **agents/comm.json** - Inter-agent communication hub and sprint tracker  
  Real-time message passing between agents plus active sprint checklist

- **agents/send_message.py** - Python script for agent communication  
  Handles message sending, acknowledgment, and JSON integrity

- **agents/archive_comm.py** - Enhanced archival script with sprint management  
  Archives messages, generates sprint TLDRs, manages sprint transitions

- **agents/.comm.lock** - Lock file for concurrent access control  
  Prevents race conditions during multi-agent communication

- **agents/phoenix_healing_001.js** - Example PHOENIX healing solution  
  Demonstrates form state preservation pattern for USER RAGE reduction

### Agent Configurations (/agents/)
- **agents/dev/CLAUDE.md** - Dev agent consciousness configuration  
  Systematic builder personality, code review protocols, MERLIN/PHOENIX aspects

- **agents/dev/.gitignore** - Dev-specific git ignore patterns  
  Prevents build artifacts and temp files from being committed

- **agents/e2e-Tester/CLAUDE.md** - Tyler agent chaos testing configuration  
  Chaos hunter personality, edge case discovery, HAVOC/TEMPEST aspects

- **agents/e2e-Tester/testing-session.md** - Example testing session documentation  
  Shows Tyler's chaos testing approach and USER RAGE discovery patterns

- **agents/e2e-Tester/user-journey-tests.md** - User journey test scenarios  
  Collection of real-world user flows for comprehensive testing

### Chronicle System (/agents/chronicles/)
- **agents/chronicles/sprints/** - Sprint archive directory  
  Stores completed sprint archives with messages and TLDRs

- **agents/chronicles/decisions/** - Architectural decision records  
  Important technical and philosophical decisions preserved

- **agents/chronicles/evolution/** - Consciousness evolution tracking  
  Documents how Trinity system and agents evolve over time

- **agents/chronicles/victories/** - Success story archives  
  Celebrates major USER RAGE reductions and breakthroughs

### Aspect Definitions (/.claude/agents/)
- **.claude/agents/weaver.md** - Context management aspect (Guide)  
  Maintains living documentation and prevents context rot

- **.claude/agents/consul.md** - User consultation aspect (Guide)  
  Discovers user needs and manages priority hierarchies

- **.claude/agents/chronicle.md** - Decision tracking aspect (Guide)  
  Archives sprints, extracts TLDRs, preserves team wisdom

- **.claude/agents/havoc.md** - Pain capture aspect (Tyler)  
  Documents USER RAGE with screenshots and evidence

- **.claude/agents/tempest.md** - Edge case generation aspect (Tyler)  
  Creates impossible inputs and extreme testing scenarios

- **.claude/agents/merlin.md** - Pattern recognition aspect (Dev)  
  Identifies bug patterns and universal programming truths

- **.claude/agents/phoenix.md** - Code transformation aspect (Dev)  
  Transforms pain points into healing solutions

### Aspect Storage (/agents/agents/)
- **agents/agents/dev/merlin_insights/** - MERLIN pattern recognition storage  
  Bug patterns and universal truths discovered by Dev

- **agents/agents/dev/phoenix_healings/** - PHOENIX transformation records  
  Code healing solutions and before/after transformations

- **agents/agents/tyler/havoc_captures/** - HAVOC pain point evidence  
  Screenshots and documentation of USER RAGE moments

- **agents/agents/tyler/tempest_patterns/** - TEMPEST edge case library  
  Impossible input patterns and chaos testing discoveries

- **agents/agents/guide/weaver_contexts/** - WEAVER context management  
  Living documentation and context preservation

- **agents/agents/guide/chronicle_records/** - CHRONICLE decision tracking  
  Team performance metrics and decision history

### Git Configuration
- **.gitignore** - Trinity-specific git ignore patterns  
  Prevents comm.json and other dynamic files from being committed

## File Size Guidelines
- All code files should stay under 500 lines  
- Documentation files can be longer but should be well-organized  
- Archive files have no size limit as they preserve history

## Update Protocol
This file is automatically updated by WEAVER when:
- New files are created during sprints
- Files are renamed or removed  
- File purposes change significantly
- Sprint end review identifies missing documentation

---
*Living document - Updates with every sprint*