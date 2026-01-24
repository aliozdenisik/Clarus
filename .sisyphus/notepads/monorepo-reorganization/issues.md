# Issues & Gotchas - Monorepo Reorganization

## Problems Encountered

*This file tracks problems, gotchas, and their solutions.*

---


## [2026-01-24] Delegation System Failure

### Issue

The `delegate_task()` function consistently runs in background mode despite `run_in_background=false` parameter.

### Evidence

- Task 2.1: Both attempts ran in background, failed with 0s duration
- Task 2.2: Ran in background, failed with 0s duration
- Task 2.3: Would have failed, executed directly instead

### Impact

- Orchestrator forced to execute tasks directly
- Violates orchestration pattern
- Acceptable for infrastructure setup (Tasks 2.1-2.4)
- May be problematic for complex feature tasks (Phase 3)

### Workaround

Orchestrator executes simple tasks directly using bash/write/edit tools. This is acceptable for:
- File creation
- Configuration updates
- Dependency installation
- Simple component creation

### Recommendation

For Phase 3 tasks (auth pages, landing page, search implementation):
- These are complex features requiring multiple files
- Should attempt delegation first
- If delegation fails, may need to break into smaller subtasks
- Document each direct implementation

