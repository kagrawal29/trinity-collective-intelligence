# Sprint Management System - Implementation Plan

## Implementation Order & Dependencies

### Phase 1: Core Infrastructure
1. **Update comm.json structure**
   - Add active_sprint object
   - Ensure backward compatibility
   - Guide will be only one updating checklist

2. **Create sprint archive directory**
   ```
   agents/chronicles/sprints/
   ```

3. **Update archive_comm.py**
   - Add --sprint-end flag
   - Extract TLDR generation
   - Create sprint handoff

### Phase 2: Aspect Updates (Critical for Natural Behavior)

4. **Update CHRONICLE aspect** (.claude/agents/chronicle.md)
   - Add sprint archival commands
   - TLDR extraction logic
   - Sprint handoff protocol

5. **Update WEAVER aspect** (.claude/agents/weaver.md)
   - PROJECT_INDEX.md maintenance
   - File tracking during sprint
   - End-of-sprint completeness check

### Phase 3: Agent Behavior Updates

6. **Update Guide's CLAUDE.md**
   - Sprint start/end protocols
   - Checklist management (only Guide updates)
   - Natural triggers for using CHRONICLE/WEAVER
   - Example: "When Tyler says 'ready for chaos', mark discovery complete"

7. **Update Dev's CLAUDE.md**
   - End-of-sprint code review protocol
   - Refactoring triggers (files >500 lines)
   - Natural integration: "Before celebrating sprint completion, review code quality"

8. **Update Tyler's CLAUDE.md**
   - End-of-sprint chaos validation
   - USER RAGE final assessment
   - Natural trigger: "When Guide says 'sprint ending', do final chaos sweep"

### Phase 4: Documentation

9. **Create PROJECT_INDEX.md**
   - Initial file listing
   - 2-line descriptions
   - Living document header

10. **Update TRINITY_QUICK_REFERENCE.md**
    - Add sprint workflow
    - Quick commands for sprint management

## Key Integration Points

### Natural Workflow Triggers:
- **Sprint Start**: When Guide says "New sprint for [goal]"
- **Update Checklist**: When team members report completion
- **Update PROJECT_INDEX**: When files are created/modified
- **Sprint End**: When USER RAGE target achieved
- **Code Review**: Natural part of "sprint completion"

### Embedded Behaviors (Not Separate Tasks):
```
Instead of: "Remember to update PROJECT_INDEX"
Embed as: "When creating a file, WEAVER automatically documents it"

Instead of: "Do code review at sprint end"  
Embed as: "Before celebrating victory, Dev ensures code quality"

Instead of: "Archive the sprint"
Embed as: "When USER RAGE target achieved, CHRONICLE preserves our wisdom"
```

## Success Criteria

The system works when:
1. ✅ Agents naturally follow sprint protocols without reminders
2. ✅ PROJECT_INDEX stays current without manual updates
3. ✅ Code reviews happen as part of completion flow
4. ✅ Sprint knowledge transfers seamlessly
5. ✅ No additional complexity for users

## Critical Success Factor

**Make it invisible**: The best system is one that happens naturally. Agents should do these things because it's part of their character, not because there's a checklist.

Example: 
- Guide celebrates victories by archiving wisdom (CHRONICLE)
- Dev's perfectionism includes code review before declaring "done"
- Tyler's chaos includes final validation sweep
- WEAVER documents as naturally as breathing

This way, the system maintains itself through the agents' natural behaviors.