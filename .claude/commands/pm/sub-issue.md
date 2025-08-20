---
allowed-tools: Bash, Read, Write, LS
---

# Sub-Issue Management

Manage GitHub sub-issues using gh-sub-issue extension.

## Usage
```
/pm:sub-issue <command> <args>
```

## Available Commands

### List Sub-Issues
```bash
/pm:sub-issue list <epic-number>
```

View hierarchy and progress:
```bash
# Basic listing
gh sub-issue list $EPIC_NUMBER

# Show all states (including closed)
gh sub-issue list $EPIC_NUMBER --state all

# JSON output for scripting
gh sub-issue list $EPIC_NUMBER --json
```

### Add Existing Issue as Sub-Issue
```bash
/pm:sub-issue add <epic-number> <task-number>
```

Link an existing issue to an epic:
```bash
gh sub-issue add $EPIC_NUMBER $TASK_NUMBER
```

### Remove Sub-Issue Link
```bash
/pm:sub-issue remove <epic-number> <task-number>
```

Unlink (doesn't delete the issue):
```bash
gh sub-issue remove $EPIC_NUMBER $TASK_NUMBER
```

### Create New Sub-Issue
```bash
/pm:sub-issue create <epic-number> "<title>" [description]
```

Create and automatically link:
```bash
gh sub-issue create \
  --parent $EPIC_NUMBER \
  --title "$TITLE" \
  --body "$DESCRIPTION" \
  --label "task,epic:$EPIC_NAME"
```

## Epic Progress Commands

### Show Epic Progress
```bash
/pm:sub-issue progress <epic-number>
```

Display detailed progress:
```bash
# Get epic info
epic_info=$(gh issue view $EPIC_NUMBER --json title,state -q '{title: .title, state: .state}')

# Get sub-issues stats  
sub_issues=$(gh sub-issue list $EPIC_NUMBER --json)
total=$(echo "$sub_issues" | jq length)
closed=$(echo "$sub_issues" | jq '[.[] | select(.state == "closed")] | length')
progress=$((closed * 100 / total))

echo "Epic #$EPIC_NUMBER Progress: $progress% ($closed/$total tasks completed)"
```

### Bulk Operations
```bash
/pm:sub-issue bulk-add <epic-number> <task1> <task2> <task3>...
```

Add multiple sub-issues at once:
```bash
for task_num in $TASK_NUMBERS; do
  gh sub-issue add $EPIC_NUMBER $task_num
  echo "✅ Added #$task_num as sub-issue"
done
```

## Integration Examples

### Convert Existing Epic Structure
If you have EPICs with manually created tasks, convert to sub-issues:

```bash
# Data Studio Epic (#7) with tasks #8-#13
/pm:sub-issue bulk-add 7 8 9 10 11 12 13

# Wave Theme Epic (#14) with tasks #15-#22  
/pm:sub-issue bulk-add 14 15 16 17 18 19 20 21 22
```

### Check Epic Health
```bash
# Show progress for all active epics
for epic in $(gh issue list --label epic --state open --json number -q '.[].number'); do
  /pm:sub-issue progress $epic
done
```

## Error Handling

If gh-sub-issue is not installed:
```bash
if ! gh extension list | grep -q "yahsan2/gh-sub-issue"; then
  echo "❌ gh-sub-issue extension not found"
  echo "💡 Install with: gh extension install yahsan2/gh-sub-issue"
  exit 1
fi
```

Common issues:
- **Issue not found**: Verify issue numbers exist
- **Permission denied**: Check repository access
- **Already linked**: Use `remove` first, then `add`
- **Cross-repo linking**: Use `--repo owner/repo` flag

## Output Format

Standard output shows hierarchy:
```
Parent: #7 - [EPIC] Data Studio Enhancements
SUB-ISSUES (6 total, 6 open)
─────────────────────────────────────────
🔵 #8  Enhanced Pagination System [open]
🔵 #9  Advanced Filter Interface [open]  
🔵 #10 Active State Navigation [open]
🔵 #11 Session Management Enhancement [open]
🔵 #12 Backend API Support [open]
🔵 #13 Comprehensive Testing [open]
```

## Integration with CCMP

This command integrates with:
- `/pm:epic-sync` - Auto-creates sub-issues during sync
- `/pm:epic-status` - Shows progress via sub-issue status  
- `/pm:issue-start` - Works with sub-issues seamlessly

The CCMP system will automatically use gh-sub-issue when available, falling back to manual references when not installed.