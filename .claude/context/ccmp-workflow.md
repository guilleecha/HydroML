# CCMP Workflow and Commands

## 🚀 CCMP SYSTEM OVERVIEW
**HydroML uses the official Claude Code PM (CCMP) system from automazeio for spec-driven development with parallel AI agents.**

### Available CCMP Commands
```bash
/pm:prd-new <feature-name>      # Create Product Requirements Document
/pm:prd-parse <feature-name>    # Convert PRD to Epic implementation plan
/pm:epic-decompose <feature>    # Break epic into parallel tasks
/pm:epic-sync <feature>         # Sync tasks to GitHub Issues (requires gh CLI)
/pm:issue-start <issue-number>  # Launch parallel specialist agents
/pm:sub-issue <command> <args>  # Manage sub-issue hierarchies (requires gh-sub-issue)
```

### CCMP Workflow
1. **Brainstorm** → PRD creation
2. **Document** → Epic specification  
3. **Plan** → Task decomposition
4. **Sync** → GitHub Issues integration with hierarchical sub-issues
5. **Execute** → Parallel agent implementation

### 📊 Sub-Issue Management (gh-sub-issue)
**Extension installed**: `yahsan2/gh-sub-issue v0.3.0`

Create hierarchical task structures with automatic parent-child relationships:
```bash
# List epic progress
gh sub-issue list 7    # Data Studio Enhancements (6 tasks)
gh sub-issue list 14   # Wave Theme Integration (8 tasks)

# Manual sub-issue management
gh sub-issue add <epic-number> <task-number>     # Link existing issue
gh sub-issue create --parent <epic> --title "Task Name"  # Create new
gh sub-issue remove <epic-number> <task-number>  # Unlink
```

**Current Epic Structure:**
- **Epic #7**: Data Studio Enhancements → Sub-issues #8-#13 (6 tasks)
- **Epic #14**: Wave Theme Integration → Sub-issues #15-#22 (8 tasks)
- **Epic #23**: Project Cleanup → Automated cleanup system
- **Epic #39**: Enhanced Grove Headbar → Sub-issues #40-#48 (9 tasks)

## Command Execution

All CCMP commands are executed via instructions in `.claude/commands/pm/` directory.
Each command has detailed documentation with:
- Preflight checklists
- Step-by-step instructions  
- Error handling
- Quality validation
- Post-completion actions

## Integration with GitHub

CCMP integrates directly with GitHub via:
- **gh CLI**: Standard GitHub operations
- **gh-sub-issue extension**: Hierarchical issue management
- **GitHub Official MCP**: Advanced repository operations
- **GitHub Labels**: Automatic epic and task classification