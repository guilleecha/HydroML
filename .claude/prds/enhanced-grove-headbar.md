# PRD: Enhanced Grove Headbar

**Status**: Draft  
**Priority**: High  
**Estimated Effort**: 2-3 weeks  
**Target Release**: Next Sprint  

## 🎯 Vision & Goals

### Problem Statement
The current Grove headbar component lacks the sophisticated two-row design and breadcrumb navigation system that matches the existing dashboard at `http://localhost:8000/dashboard/`. Users need consistent navigation patterns with special character-based breadcrumbs and proper workspace context awareness.

### Success Criteria
- [ ] **User Impact**: Intuitive navigation with consistent breadcrumb system using special characters (@, #, etc.)
- [ ] **Business Impact**: Improved user experience and reduced navigation confusion across HydroML
- [ ] **Technical Impact**: Modular two-row headbar architecture that can be reused across all pages

## 👥 User Stories

### Primary User Journey
**As a** HydroML user  
**I want** a consistent two-row headbar with contextual breadcrumbs  
**So that** I can quickly understand my current location and navigate efficiently between workspaces, data sources, and experiments

### Secondary Use Cases
- [ ] **Use Case 1**: Developer wants to identify current workspace context via @username breadcrumb
- [ ] **Use Case 2**: User wants to navigate between Workspace, Data Sources, and Experiments with visual counts
- [ ] **Use Case 3**: User wants search functionality and action buttons always accessible

## 🔧 Technical Requirements

### Core Functionality
1. **Two-Row Layout**: First row (celeste/gray background) with logo + breadcrumbs, second row (white background) with navigation tabs
2. **Special Character Breadcrumbs**: @username, #experiments, [TBD]database, [TBD]workspace navigation system
3. **Dynamic Tab Counts**: Show real-time counts for Workspace, Data Sources, and Experiments

### Integration Points
- [ ] **Database**: Query counts for workspaces, data sources, experiments
- [ ] **API**: Real-time updates for navigation counts via Django context
- [ ] **Frontend**: Alpine.js integration with existing WaveHeadbar component
- [ ] **External Services**: None required

### Performance Requirements
- **Response Time**: <200ms for navigation state changes
- **Scalability**: Support for 1000+ entities per category without UI lag
- **Reliability**: 99.9% uptime for navigation functionality

## 🎨 User Experience

### Interface Requirements
- [ ] **First Row (Breadcrumb Row)**: Celeste/gray background with grove_icon (not logo) and contextual breadcrumbs
- [ ] **Second Row (Navigation Row)**: White background with main navigation tabs, search bar, and action buttons
- [ ] **Mobile Responsive**: Collapsible design for mobile devices with hamburger menu

### User Flow
1. **Visual Context**: User sees @username breadcrumb indicating current workspace context
2. **Navigation Discovery**: User sees tab counts (Workspace: 5, Data Sources: 12, Experiments: 8) 
3. **Quick Actions**: User accesses search bar and + button for new actions on the right side

### Design Specifications
- **Row 1 Background**: `bg-gray-100 dark:bg-gray-900` (existing in base_github_style.html)
- **Row 2 Background**: `bg-white dark:bg-gray-900` (existing in base_github_style.html)
- **Grove Icon**: `grove_icon.svg` at w-12 h-12 (already implemented correctly)
- **Tab Counters**: `bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs px-2 py-1 rounded-full` (existing style)
- **Special Characters**: @ for username (✅ implemented), # for experiments, & for database, ~ for workspace

### Current Implementation Reference
- **File**: `core/templates/core/base_github_style.html` (lines 148-354)
- **Status**: Two-row design already exists and working
- **Missing**: Integration with WaveHeadbar component for grove_demo.html

## 🚀 Implementation Strategy

### Phase 1: Analysis & Integration
- [ ] **Extract Template Structure**: Copy two-row design from base_github_style.html (lines 148-354)
- [ ] **Adapt for WaveHeadbar**: Integrate HTML structure with existing WaveHeadbar.js component
- [ ] **Context Data Integration**: Connect Django view context variables for real-time counts

### Phase 2: Component Enhancement  
- [ ] **Special Character Breadcrumbs**: Extend @ username to include #experiments, &database, ~workspace
- [ ] **Universal Search System**: Implement character-prefixed search (@users, ~workspaces, #experiments, &databases)
- [ ] **Dynamic Count System**: Implement backend queries for workspace/datasource/experiment counts
- [ ] **Alpine.js Data Binding**: Update WaveHeadbar.createAlpineData() for two-row architecture

### Phase 3: Grove Demo Integration
- [ ] **Update grove_demo.html**: Replace current headbar with enhanced two-row version
- [ ] **CSS Optimization**: Ensure grove-headbar.css supports the two-row layout
- [ ] **Testing & Validation**: Verify functionality matches base_github_style.html behavior

## 📊 Success Metrics

### Key Performance Indicators
- **Navigation Efficiency**: <3 clicks to reach any main section (Dashboard, Workspace, Data Sources, Experiments)
- **Visual Consistency**: 100% design token compliance with existing dashboard headbar
- **User Comprehension**: Users understand current context within 2 seconds of page load

### Monitoring
- [ ] **Analytics Setup**: Track navigation click patterns and breadcrumb usage
- [ ] **Error Tracking**: Monitor console errors and JavaScript performance via Sentry
- [ ] **Performance Monitoring**: Measure component render times and DOM updates

## 🔍 Risk Assessment

### Technical Risks
- **Alpine.js Compatibility**: [Impact: Medium] - Ensure existing WaveHeadbar integration doesn't break with two-row design
- **CSS Layout Complexity**: [Impact: Low] - Two-row responsive design may require complex CSS Grid/Flexbox
- **Count Query Performance**: [Impact: Medium] - Real-time count queries could impact page load times

### Business Risks
- **User Confusion**: [Impact: Low] - New special character system (@, #) may need user education
- **Design Inconsistency**: [Impact: Medium] - Must match existing dashboard design exactly

## 📅 Timeline

### Dependencies
- [ ] **Grove Icon Asset**: Need grove_icon file (not full logo)
- [ ] **Dashboard Color Analysis**: Extract exact celeste/gray color values from existing dashboard
- [ ] **Count Query Implementation**: Backend support for workspace/datasource/experiment counts

### Estimated Timeline
- **Phase 1**: 3-4 days (Foundation + Design Analysis)
- **Phase 2**: 5-7 days (Core Features + Backend Integration)  
- **Phase 3**: 3-4 days (Polish + Testing)
- **Total**: 2-3 weeks

## 📋 Acceptance Criteria

### Functional Requirements
- [ ] **Two-Row Layout**: First row with celeste/gray background, second row with white background
- [ ] **Breadcrumb Navigation**: @username, #experiments, [TBD]database, [TBD]workspace special characters work correctly
- [ ] **Dynamic Counts**: Tab counters update in real-time reflecting actual data counts
- [ ] **Search & Actions**: Search bar and + button positioned on the right side and fully functional

### Non-Functional Requirements
- [ ] **Performance**: Page load time increase <100ms, navigation state changes <200ms
- [ ] **Security**: No exposure of sensitive user data in breadcrumb URLs or navigation
- [ ] **Accessibility**: WCAG 2.1 AA compliance, keyboard navigation support
- [ ] **Compatibility**: Works in Chrome, Firefox, Safari, Edge (latest 2 versions)

## 💡 Special Character System Design

### Proposed Character Mapping
- `@` **Username/Profile**: Represents the current user context (@guillermo, @admin)
- `#` **Experiments**: Represents ML experiments and research (#experiment-001, #model-training)
- `&` **Database**: Represents database connections and data sources (&postgres-prod, &mysql-dev)  
- `~` **Workspace**: Represents project workspaces and environments (~hydroml-workspace, ~ml-research)

### Universal Search Integration
**Search Syntax Examples:**
- `@guer` → Search users: @guillermo, @guest_user
- `~hydro` → Search workspaces: ~hydroml-workspace, ~hydro-analytics
- `#train` → Search experiments: #model-training, #training-v2
- `&post` → Search databases: &postgres-prod, &postgresql-dev
- `analytics` → Global search (no prefix = search all types)

### Implementation Notes
- Characters should be clickable and provide context switching
- Search bar supports both prefixed and global search modes
- Real-time suggestions dropdown with grouped results by type
- Maintain URL-safe encoding for routing and sharing
- Consider accessibility and screen reader compatibility
- Special characters should be visually distinct but not overwhelming

---

**Created**: 2025-01-21  
**Last Updated**: 2025-01-21  
**Status**: Ready for Epic Decomposition  
**Next Step**: Run `/pm:prd-parse enhanced-grove-headbar` to convert to Epic plan
