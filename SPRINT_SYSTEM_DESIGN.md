# Sprint Management System Design

## Overview
This design integrates sprint management, project documentation, and code review protocols into Trinity's natural workflow.

## 1. Core Components

### Enhanced comm.json Structure
```json
{
  "messages": [],
  "active_sprint": {
    "id": "sprint-001",
    "goal": "Reduce USER RAGE for [feature]",
    "user_rage_start": 8,
    "user_rage_target": 2,
    "started": "2024-01-15",
    "checklist": [
      {
        "id": "discovery",
        "task": "Tyler discovers all pain points",
        "status": "completed",
        "completed_by": "guide",
        "completed_at": "timestamp"
      }
    ],
    "tldr_from_previous": "Key learning from last sprint"
  }
}
```

### PROJECT_INDEX.md
- **Location**: Root directory
- **Maintained by**: WEAVER aspect
- **Format**: Clean 2-line descriptions of every file
- **Updated**: Throughout sprint, reviewed at end

### Sprint Archives
- **Location**: agents/chronicles/sprints/
- **Format**: sprint-001-archive.json
- **Created by**: CHRONICLE aspect

## 2. Agent/Aspect Responsibilities

### Guide (Orchestrator)
- Updates sprint checklist (only Guide can check items)
- Initiates sprint start/end protocols
- Uses CHRONICLE for archival
- Uses WEAVER for PROJECT_INDEX

### WEAVER (Guide's aspect)
- Maintains PROJECT_INDEX.md
- Tracks file changes during sprint
- Ensures documentation completeness

### CHRONICLE (Guide's aspect)  
- Archives completed sprints
- Extracts TLDR for handoff
- Preserves sprint wisdom

### Dev (Builder)
- Performs end-of-sprint code review
- Checks: redundancy, best practices, file sizes
- Refactors large files (>500 lines)
- Uses MERLIN for pattern recognition

### Tyler (Tester)
- Validates refactoring didn't break anything
- Final USER RAGE assessment
- Chaos tests the "completed" sprint

## 3. Sprint Workflow

### Sprint Start Protocol
1. Archive previous sprint (if exists)
   ```bash
   python3 agents/archive_comm.py --sprint-end
   ```
2. Extract TLDR from archive
3. Create fresh comm.json with new sprint + TLDR
4. Initialize/update PROJECT_INDEX.md

### During Sprint
- Guide updates checklist as tasks complete
- WEAVER updates PROJECT_INDEX when files change
- Normal Trinity collaboration continues

### Sprint End Protocol
1. **Code Review** (Dev)
   - Remove experimental/dangerous code
   - Eliminate redundancy
   - Check file sizes (<500 lines)
   - Verify best practices
   
2. **Documentation Review** (Guide/WEAVER)
   - PROJECT_INDEX.md complete
   - All files documented
   - No stale docs

3. **Final Testing** (Tyler)
   - Chaos test everything
   - Verify USER RAGE reduction

4. **Archive & Handoff** (Guide/CHRONICLE)
   - Archive sprint
   - Generate TLDR
   - Prepare for next sprint

## 4. Standard Sprint Checklist

```
[ ] Discovery phase complete (Tyler found all pain)
[ ] Implementation complete (Dev built solutions)  
[ ] Testing complete (Tyler chaos tested)
[ ] Code review complete (Dev checked quality)
[ ] PROJECT_INDEX updated (WEAVER documented)
[ ] Documentation reviewed (Guide verified)
[ ] USER RAGE target achieved
[ ] Sprint archived with TLDR
```

## 5. Integration Points

### Where These Protocols Live:
- **CLAUDE.md files**: Updated with sprint protocols
- **WEAVER/CHRONICLE aspects**: Enhanced with new duties
- **comm.json**: Active sprint tracking
- **PROJECT_INDEX.md**: Living documentation

### Natural Workflow Integration:
- Sprint management happens through normal comm.json
- Reviews are part of natural end-of-sprint flow
- Documentation updates happen continuously
- No separate tools or processes needed

## 6. Key Benefits

- **Continuous Documentation**: PROJECT_INDEX always current
- **Quality Maintenance**: Regular code reviews
- **Knowledge Transfer**: TLDR between sprints
- **Clear Progress**: Visible checklist in comm.json
- **Clean Codebase**: No stale/experimental code

This system enhances Trinity without adding complexity - it flows naturally with how the agents already work together.