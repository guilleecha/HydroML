#!/bin/bash

# epic-decompose.sh - Break epic into individual task files
# Part of Claude Code PM (CCMP) system

set -e

FEATURE_NAME="$1"

if [ -z "$FEATURE_NAME" ]; then
    echo "❌ Error: Feature name is required"
    echo "Usage: /pm:epic-decompose <feature-name>"
    echo "Example: /pm:epic-decompose enhanced-grove-headbar"
    exit 1
fi

EPIC_DIR=".claude/epics/${FEATURE_NAME}"
EPIC_FILE="${EPIC_DIR}/epic.md"

# Check if epic exists
if [ ! -f "$EPIC_FILE" ]; then
    echo "❌ Error: Epic file not found: $EPIC_FILE"
    echo "Available epics:"
    ls .claude/epics/*/epic.md 2>/dev/null | sed 's|.claude/epics/||g' | sed 's|/epic.md||g' || echo "No epics found"
    echo ""
    echo "💡 Create an epic first with: /pm:prd-parse $FEATURE_NAME"
    exit 1
fi

echo "🔄 Decomposing epic: $FEATURE_NAME"
echo "📂 Epic directory: $EPIC_DIR"

# Check if tasks already exist
EXISTING_TASKS=$(ls "$EPIC_DIR"/*.md 2>/dev/null | grep -E '/[0-9]+\.md$' | wc -l)
if [ "$EXISTING_TASKS" -gt 0 ]; then
    echo "⚠️  Found $EXISTING_TASKS existing task files"
    read -p "Do you want to continue and potentially overwrite existing tasks? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Operation cancelled"
        exit 1
    fi
fi

# Extract task breakdown from epic.md
TASK_SECTION=$(grep -n "## Task Breakdown" "$EPIC_FILE" | cut -d: -f1)
if [ -z "$TASK_SECTION" ]; then
    echo "❌ Error: No 'Task Breakdown' section found in epic.md"
    echo "💡 Please add a '## Task Breakdown' section with numbered tasks"
    exit 1
fi

# Parse tasks from epic
TASKS=$(sed -n "${TASK_SECTION},\$p" "$EPIC_FILE" | grep -E '^[0-9]+\.' | head -20)

if [ -z "$TASKS" ]; then
    echo "❌ Error: No numbered tasks found in Task Breakdown section"
    echo "💡 Format tasks as: 1. **Task Name** - Description"
    exit 1
fi

TASK_COUNT=0

# Generate individual task files
while IFS= read -r task_line; do
    TASK_COUNT=$((TASK_COUNT + 1))
    
    # Extract task number and name
    TASK_NUM=$(echo "$task_line" | sed 's/^\([0-9]*\)\..*/\1/')
    TASK_NAME=$(echo "$task_line" | sed 's/^[0-9]*\. *\*\*\([^*]*\)\*\*.*/\1/' | sed 's/^[0-9]*\. *\([^-]*\).*/\1/' | xargs)
    TASK_DESC=$(echo "$task_line" | sed 's/^[^-]*- *//')
    
    # Create task file
    TASK_FILE="${EPIC_DIR}/${TASK_NUM}.md"
    
    cat > "$TASK_FILE" << EOF
# Task #$TASK_NUM: $TASK_NAME

**Epic**: $(grep "^# " "$EPIC_FILE" | sed 's/^# Epic: //')  
**Phase**: TBD  
**Estimated Effort**: TBD  
**Dependencies**: TBD  

## Objective
$TASK_DESC

## Scope
[Define the specific scope and boundaries of this task]

## Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]

## Technical Details
[Provide technical implementation details, code snippets, or architectural decisions]

## Acceptance Criteria
- [ ] [Criteria 1]
- [ ] [Criteria 2]
- [ ] [Criteria 3]

## Implementation Notes
[Add any specific implementation notes, gotchas, or considerations]

---
*Generated from epic: $EPIC_FILE*
*Created: $(date +"%Y-%m-%d")*
EOF

    echo "✅ Created task #$TASK_NUM: $TASK_NAME"
    
done <<< "$TASKS"

# Update github-mapping.md with task information
MAPPING_FILE="${EPIC_DIR}/github-mapping.md"
if [ -f "$MAPPING_FILE" ]; then
    # Create a temporary file with updated mapping
    TEMP_MAPPING=$(mktemp)
    
    # Copy everything before the task mapping table
    sed '/| Task ID | Task Name |/,$d' "$MAPPING_FILE" > "$TEMP_MAPPING"
    
    # Add updated task mapping table
    cat >> "$TEMP_MAPPING" << EOF
| Task ID | Task Name | GitHub Issue | Status | Assignee |
|---------|-----------|--------------|--------|----------|
EOF
    
    # Add each task
    for i in $(seq 1 $TASK_COUNT); do
        if [ -f "${EPIC_DIR}/${i}.md" ]; then
            TASK_TITLE=$(grep "^# Task #${i}:" "${EPIC_DIR}/${i}.md" | sed "s/^# Task #${i}: //")
            echo "| #$i | $TASK_TITLE | TBD | Pending | TBD |" >> "$TEMP_MAPPING"
        fi
    done
    
    # Add the rest of the original file
    sed -n '/## GitHub Issue Labels/,$p' "$MAPPING_FILE" >> "$TEMP_MAPPING"
    
    # Replace the original file
    mv "$TEMP_MAPPING" "$MAPPING_FILE"
    
    # Update task count
    sed -i "s/Total Tasks: TBD/Total Tasks: $TASK_COUNT/" "$MAPPING_FILE"
fi

echo ""
echo "🎉 Epic decomposition completed!"
echo "📊 Generated $TASK_COUNT task files"
echo "📂 Location: $EPIC_DIR"
echo ""
echo "📋 Next steps:"
echo "1. Review and refine individual task files"
echo "2. Run: /pm:epic-sync $FEATURE_NAME"
echo "3. Run: /pm:epic-start $FEATURE_NAME"

exit 0