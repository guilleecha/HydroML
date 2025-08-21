#!/bin/bash

# epic-sync.sh - Push epic and tasks to GitHub Issues
# Part of Claude Code PM (CCMP) system

set -e

FEATURE_NAME="$1"

if [ -z "$FEATURE_NAME" ]; then
    echo "❌ Error: Feature name is required"
    echo "Usage: /pm:epic-sync <feature-name>"
    echo "Example: /pm:epic-sync enhanced-grove-headbar"
    exit 1
fi

EPIC_DIR=".claude/epics/${FEATURE_NAME}"
EPIC_FILE="${EPIC_DIR}/epic.md"
MAPPING_FILE="${EPIC_DIR}/github-mapping.md"

# Check if epic exists
if [ ! -f "$EPIC_FILE" ]; then
    echo "❌ Error: Epic file not found: $EPIC_FILE"
    echo "💡 Create an epic first with: /pm:prd-parse $FEATURE_NAME"
    exit 1
fi

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI (gh) is not installed"
    echo "💡 Install from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated with GitHub
if ! gh auth status &> /dev/null; then
    echo "❌ Error: Not authenticated with GitHub"
    echo "💡 Run: gh auth login"
    exit 1
fi

echo "🔄 Syncing epic to GitHub: $FEATURE_NAME"
echo "📂 Epic directory: $EPIC_DIR"

# Extract epic information
EPIC_TITLE=$(grep "^# Epic:" "$EPIC_FILE" | sed 's/^# Epic: //')
EPIC_PRIORITY="medium"  # Default priority

# Check if priority is specified in PRD
PRD_FILE=".claude/prds/${FEATURE_NAME}.md"
if [ -f "$PRD_FILE" ]; then
    EPIC_PRIORITY=$(grep -i "priority:" "$PRD_FILE" | head -1 | sed 's/.*Priority.*: *//' | tr '[:upper:]' '[:lower:]' || echo "medium")
fi

# Create epic issue body from epic.md
EPIC_BODY_FILE=$(mktemp)
cat > "$EPIC_BODY_FILE" << EOF
## Epic Overview
$(sed -n '/## Overview/,/## /p' "$EPIC_FILE" | head -n -1 | tail -n +2)

## Business Objectives
$(sed -n '/## Business Objectives/,/## /p' "$EPIC_FILE" | head -n -1 | tail -n +2)

## Task Breakdown
$(sed -n '/## Task Breakdown/,/## /p' "$EPIC_FILE" | head -n -1 | tail -n +2)

## Success Metrics
$(sed -n '/## Success Metrics/,/## /p' "$EPIC_FILE" | head -n -1 | tail -n +2)

---
*This epic is managed by Claude Code PM (CCMP)*
*Epic Directory: \`$EPIC_DIR\`*
EOF

# Create the epic issue
echo "🎯 Creating epic issue: $EPIC_TITLE"
EPIC_ISSUE_URL=$(gh issue create \
    --title "Epic: $EPIC_TITLE" \
    --body-file "$EPIC_BODY_FILE" \
    --label "epic:$FEATURE_NAME" \
    --label "priority:$EPIC_PRIORITY" \
    --label "type:epic" \
    2>/dev/null || echo "")

rm "$EPIC_BODY_FILE"

if [ -z "$EPIC_ISSUE_URL" ]; then
    echo "❌ Error: Failed to create epic issue"
    exit 1
fi

EPIC_ISSUE_NUMBER=$(echo "$EPIC_ISSUE_URL" | sed 's|.*/||')
echo "✅ Epic issue created: #$EPIC_ISSUE_NUMBER"
echo "🔗 URL: $EPIC_ISSUE_URL"

# Count task files
TASK_FILES=($(ls "$EPIC_DIR"/[0-9]*.md 2>/dev/null | sort -V))
TASK_COUNT=${#TASK_FILES[@]}

if [ $TASK_COUNT -eq 0 ]; then
    echo "⚠️  No task files found. Run: /pm:epic-decompose $FEATURE_NAME"
    exit 0
fi

echo "📝 Creating $TASK_COUNT task issues..."

# Initialize arrays to store issue numbers and URLs
declare -a TASK_ISSUES=()
declare -a TASK_URLS=()

# Create individual task issues
for task_file in "${TASK_FILES[@]}"; do
    TASK_NUM=$(basename "$task_file" .md)
    TASK_TITLE=$(grep "^# Task #${TASK_NUM}:" "$task_file" | sed "s/^# Task #${TASK_NUM}: //")
    
    # Create task issue body
    TASK_BODY_FILE=$(mktemp)
    cat > "$TASK_BODY_FILE" << EOF
## Objective
$(sed -n '/## Objective/,/## /p' "$task_file" | head -n -1 | tail -n +2)

## Scope
$(sed -n '/## Scope/,/## /p' "$task_file" | head -n -1 | tail -n +2)

## Deliverables
$(sed -n '/## Deliverables/,/## /p' "$task_file" | head -n -1 | tail -n +2)

## Acceptance Criteria
$(sed -n '/## Acceptance Criteria/,/## /p' "$task_file" | head -n -1 | tail -n +2)

---
*Part of Epic: #$EPIC_ISSUE_NUMBER*
*Task File: \`$task_file\`*
*Managed by Claude Code PM (CCMP)*
EOF

    # Create the task issue
    TASK_ISSUE_URL=$(gh issue create \
        --title "Task #$TASK_NUM: $TASK_TITLE" \
        --body-file "$TASK_BODY_FILE" \
        --label "epic:$FEATURE_NAME" \
        --label "priority:$EPIC_PRIORITY" \
        --label "type:task" \
        --label "task:$TASK_NUM" \
        2>/dev/null || echo "")
    
    rm "$TASK_BODY_FILE"
    
    if [ -n "$TASK_ISSUE_URL" ]; then
        TASK_ISSUE_NUMBER=$(echo "$TASK_ISSUE_URL" | sed 's|.*/||')
        TASK_ISSUES+=("$TASK_ISSUE_NUMBER")
        TASK_URLS+=("$TASK_ISSUE_URL")
        echo "  ✅ Task #$TASK_NUM created: #$TASK_ISSUE_NUMBER"
        
        # Add task as sub-issue to epic (if gh-sub-issue extension is available)
        if command -v "gh sub-issue" &> /dev/null; then
            gh sub-issue add "$EPIC_ISSUE_NUMBER" "$TASK_ISSUE_NUMBER" 2>/dev/null || true
        fi
    else
        echo "  ❌ Failed to create task #$TASK_NUM"
    fi
done

# Update github-mapping.md with actual issue numbers
if [ -f "$MAPPING_FILE" ]; then
    echo "📋 Updating GitHub mapping file..."
    
    TEMP_MAPPING=$(mktemp)
    
    # Copy file header
    sed '/| Task ID | Task Name |/,$d' "$MAPPING_FILE" > "$TEMP_MAPPING"
    
    # Add updated table header
    cat >> "$TEMP_MAPPING" << EOF
| Task ID | Task Name | GitHub Issue | Status | Assignee |
|---------|-----------|--------------|--------|----------|
EOF
    
    # Add each task with actual issue numbers
    for i in "${!TASK_FILES[@]}"; do
        task_file="${TASK_FILES[$i]}"
        TASK_NUM=$(basename "$task_file" .md)
        TASK_TITLE=$(grep "^# Task #${TASK_NUM}:" "$task_file" | sed "s/^# Task #${TASK_NUM}: //")
        
        if [ $i -lt ${#TASK_ISSUES[@]} ]; then
            ISSUE_NUM="${TASK_ISSUES[$i]}"
            echo "| #$TASK_NUM | $TASK_TITLE | #$ISSUE_NUM | Open | TBD |" >> "$TEMP_MAPPING"
        else
            echo "| #$TASK_NUM | $TASK_TITLE | Failed | Error | TBD |" >> "$TEMP_MAPPING"
        fi
    done
    
    # Add epic information
    cat >> "$TEMP_MAPPING" << EOF

## Epic GitHub Issue
- **Epic Issue**: #$EPIC_ISSUE_NUMBER
- **Epic URL**: $EPIC_ISSUE_URL

## GitHub Issue Labels
- \`epic:$FEATURE_NAME\`
- \`priority:$EPIC_PRIORITY\`
- \`type:epic\`
- \`type:task\`

## Sync Status
- **Last Sync**: $(date +"%Y-%m-%d %H:%M:%S")
- **Epic Issue**: #$EPIC_ISSUE_NUMBER
- **Tasks Created**: ${#TASK_ISSUES[@]}/$TASK_COUNT
- **Sub-issue Support**: $(command -v "gh sub-issue" &> /dev/null && echo "✅ Available" || echo "❌ Install gh-sub-issue extension")

## Quick Commands
\`\`\`bash
# Start parallel execution
/pm:epic-start $FEATURE_NAME

# View epic status
/pm:epic-status $FEATURE_NAME

# View epic on GitHub
gh issue view $EPIC_ISSUE_NUMBER
\`\`\`
EOF
    
    # Replace the mapping file
    mv "$TEMP_MAPPING" "$MAPPING_FILE"
fi

echo ""
echo "🎉 Epic sync completed successfully!"
echo "📊 Summary:"
echo "  📋 Epic Issue: #$EPIC_ISSUE_NUMBER"
echo "  📝 Tasks Created: ${#TASK_ISSUES[@]}/$TASK_COUNT"
echo "  🔗 Epic URL: $EPIC_ISSUE_URL"

if [ ${#TASK_ISSUES[@]} -gt 0 ]; then
    echo ""
    echo "📝 Task Issues:"
    for i in "${!TASK_ISSUES[@]}"; do
        echo "  #${TASK_ISSUES[$i]}: ${TASK_URLS[$i]}"
    done
fi

echo ""
echo "📋 Next steps:"
echo "1. Run: /pm:epic-start $FEATURE_NAME"
echo "2. Monitor progress: /pm:epic-status $FEATURE_NAME"
echo "3. View on GitHub: gh issue view $EPIC_ISSUE_NUMBER"

exit 0