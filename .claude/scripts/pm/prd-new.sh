#!/bin/bash
# CCMP - Create new Product Requirements Document

FEATURE_NAME="$1"

if [ -z "$FEATURE_NAME" ]; then
    echo "❌ Error: Feature name required"
    echo "Usage: prd-new.sh <feature-name>"
    exit 1
fi

PRD_DIR=".claude/prds"
PRD_FILE="$PRD_DIR/${FEATURE_NAME}.md"

# Create PRD directory if it doesn't exist
mkdir -p "$PRD_DIR"

# Check if PRD already exists
if [ -f "$PRD_FILE" ]; then
    echo "⚠️  PRD already exists: $PRD_FILE"
    echo "📝 Opening existing PRD..."
    cat "$PRD_FILE"
    exit 0
fi

# Create PRD template
cat > "$PRD_FILE" << 'EOF'
# PRD: Feature Name

**Status**: Draft  
**Priority**: Low  
**Estimated Effort**: TBD  
**Target Release**: Future  

## 🎯 Vision & Goals

### Problem Statement
[Describe the problem this feature solves]

### Success Criteria
- [ ] **User Impact**: 
- [ ] **Business Impact**: 
- [ ] **Technical Impact**: 

## 👥 User Stories

### Primary User Journey
**As a** [user type]  
**I want** [functionality]  
**So that** [benefit/outcome]

### Secondary Use Cases
- [ ] **Use Case 1**: 
- [ ] **Use Case 2**: 

## 🔧 Technical Requirements

### Core Functionality
1. **Component 1**: 
2. **Component 2**: 
3. **Component 3**: 

### Integration Points
- [ ] **Database**: 
- [ ] **API**: 
- [ ] **Frontend**: 
- [ ] **External Services**: 

### Performance Requirements
- **Response Time**: 
- **Scalability**: 
- **Reliability**: 

## 🎨 User Experience

### Interface Requirements
- [ ] **UI Component 1**: 
- [ ] **UI Component 2**: 
- [ ] **Mobile Responsive**: 

### User Flow
1. **Step 1**: 
2. **Step 2**: 
3. **Step 3**: 

## 🚀 Implementation Strategy

### Phase 1: Foundation
- [ ] **Task 1**: 
- [ ] **Task 2**: 

### Phase 2: Core Features
- [ ] **Task 1**: 
- [ ] **Task 2**: 

### Phase 3: Enhancement
- [ ] **Task 1**: 
- [ ] **Task 2**: 

## 📊 Success Metrics

### Key Performance Indicators
- **Metric 1**: 
- **Metric 2**: 
- **Metric 3**: 

### Monitoring
- [ ] **Analytics Setup**: 
- [ ] **Error Tracking**: 
- [ ] **Performance Monitoring**: 

## 🔍 Risk Assessment

### Technical Risks
- **Risk 1**: [Impact: High/Medium/Low] - [Mitigation strategy]
- **Risk 2**: [Impact: High/Medium/Low] - [Mitigation strategy]

### Business Risks
- **Risk 1**: [Impact: High/Medium/Low] - [Mitigation strategy]

## 📅 Timeline

### Dependencies
- [ ] **Dependency 1**: 
- [ ] **Dependency 2**: 

### Estimated Timeline
- **Phase 1**: X weeks
- **Phase 2**: X weeks  
- **Phase 3**: X weeks
- **Total**: X weeks

## 📋 Acceptance Criteria

### Functional Requirements
- [ ] **Requirement 1**: 
- [ ] **Requirement 2**: 
- [ ] **Requirement 3**: 

### Non-Functional Requirements
- [ ] **Performance**: 
- [ ] **Security**: 
- [ ] **Accessibility**: 
- [ ] **Compatibility**: 

---

**Created**: $(date)  
**Last Updated**: $(date)  
**Status**: Ready for Epic Decomposition
EOF

# Replace placeholder with actual feature name
sed -i "s/Feature Name/${FEATURE_NAME}/g" "$PRD_FILE"

echo "✅ PRD created: $PRD_FILE"
echo "📝 Edit the PRD to add your requirements, then run:"
echo "   prd-parse.sh $FEATURE_NAME"