#!/bin/bash

# prd-parse.sh - Convert PRD to implementation epic
# Part of Claude Code PM (CCMP) system

set -e

FEATURE_NAME="$1"

if [ -z "$FEATURE_NAME" ]; then
    echo "❌ Error: Feature name is required"
    echo "Usage: /pm:prd-parse <feature-name>"
    echo "Example: /pm:prd-parse enhanced-grove-headbar"
    exit 1
fi

PRD_FILE=".claude/prds/${FEATURE_NAME}.md"
EPIC_DIR=".claude/epics/${FEATURE_NAME}"
EPIC_FILE="${EPIC_DIR}/epic.md"

# Check if PRD exists
if [ ! -f "$PRD_FILE" ]; then
    echo "❌ Error: PRD file not found: $PRD_FILE"
    echo "Available PRDs:"
    ls .claude/prds/*.md 2>/dev/null | sed 's|.claude/prds/||g' | sed 's|.md||g' || echo "No PRDs found"
    exit 1
fi

# Create epic directory
mkdir -p "$EPIC_DIR"

echo "🔄 Parsing PRD: $FEATURE_NAME"
echo "📂 Creating epic directory: $EPIC_DIR"

# Check if epic already exists
if [ -f "$EPIC_FILE" ]; then
    echo "⚠️  Epic already exists: $EPIC_FILE"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Operation cancelled"
        exit 1
    fi
fi

# Extract key information from PRD
PRD_TITLE=$(grep "^# " "$PRD_FILE" | head -1 | sed 's/^# //')
PRD_PRIORITY=$(grep -i "priority:" "$PRD_FILE" | head -1 | sed 's/.*Priority.*: *//' || echo "Medium")
PRD_EFFORT=$(grep -i "estimated effort:" "$PRD_FILE" | head -1 | sed 's/.*Estimated Effort.*: *//' || echo "TBD")

# Generate epic.md
cat > "$EPIC_FILE" << EOF
# Epic: $PRD_TITLE

## Overview
Epic automatically generated from PRD: $FEATURE_NAME
This epic implements the requirements specified in the Product Requirements Document.

## Business Objectives
[Extracted from PRD - requires manual review and refinement]

## Epic Scope
Based on the $FEATURE_NAME PRD, this epic addresses the key requirements and user stories defined in the original document.

## Technical Architecture
[To be defined based on PRD technical requirements]

## Success Metrics
[Extracted from PRD success criteria]

## Timeline
- **Total Duration**: $PRD_EFFORT
- **Priority**: $PRD_PRIORITY
- **Status**: Ready for decomposition

## Task Breakdown
[Tasks will be generated during epic decomposition]

## Dependencies
[To be identified from PRD requirements]

## Risk Mitigation
[Based on PRD risk assessment]

## Definition of Done
- All tasks completed and tested
- PRD requirements fully implemented
- Success metrics achieved
- Quality standards met

---
*Generated from PRD: $PRD_FILE*
*Created: $(date +"%Y-%m-%d")*
EOF

# Create github-mapping.md
cat > "${EPIC_DIR}/github-mapping.md" << EOF
# $PRD_TITLE - GitHub Issues Mapping

## Epic Information
- **Epic Name**: $PRD_TITLE
- **Created**: $(date +"%Y-%m-%d")
- **Status**: Ready for Decomposition
- **Total Tasks**: TBD

## Task to GitHub Issue Mapping

| Task ID | Task Name | GitHub Issue | Status | Assignee |
|---------|-----------|--------------|--------|----------|
| TBD | Tasks will be populated during decomposition | TBD | Pending | TBD |

## GitHub Issue Labels
- \`epic:$FEATURE_NAME\`
- \`priority:$(echo $PRD_PRIORITY | tr '[:upper:]' '[:lower:]')\`
- \`type:enhancement\`

## Sync Commands
\`\`\`bash
# Decompose epic into tasks
/pm:epic-decompose $FEATURE_NAME

# Sync to GitHub Issues
/pm:epic-sync $FEATURE_NAME

# Start parallel execution
/pm:epic-start $FEATURE_NAME
\`\`\`

## Notes
- This mapping will be updated during epic decomposition
- Issue numbers will be populated after GitHub sync
EOF

echo "✅ Epic created successfully!"
echo "📄 Epic file: $EPIC_FILE"
echo "🔗 GitHub mapping: ${EPIC_DIR}/github-mapping.md"
echo ""
echo "📋 Next steps:"
echo "1. Review and refine the generated epic"
echo "2. Run: /pm:epic-decompose $FEATURE_NAME"
echo "3. Run: /pm:epic-sync $FEATURE_NAME"

exit 0