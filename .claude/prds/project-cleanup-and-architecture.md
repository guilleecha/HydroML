---
name: project-cleanup-and-architecture
description: Comprehensive project cleanup, file organization, and base template architecture modernization
status: backlog
created: 2025-08-24T17:27:05Z
---

# PRD: Project Cleanup and Architecture Modernization

## Executive Summary

HydroML requires comprehensive project cleanup and architectural modernization to reduce complexity, improve maintainability, and establish a clean foundation for future development. Analysis reveals 30-40% reduction potential in file complexity through removal of unused files, legacy component cleanup, and base template restructuring.

**Value Proposition**: Cleaner codebase, faster development cycles, improved maintainability, and professional project structure aligned with Grove Design System principles.

## Problem Statement

### Current Issues
1. **Static File Bloat**: 40,000+ unnecessary files in staticfiles directory from development artifacts
2. **Legacy Component Debt**: Incomplete Wave → Grove migration leaving redundant code
3. **Template Complexity**: base_main.html has 440 lines with inline styles and complex nesting
4. **Demo File Scatter**: Development artifacts spread throughout production code
5. **Context Documentation Redundancy**: 25+ context files with overlapping information

### Why This Matters Now
- Recent rendering issues traced to architectural complexity
- Grove Design System adoption requires clean component hierarchy
- Upcoming major epics (Data Studio, Session System) need solid foundation
- Development velocity decreased due to code navigation complexity
- Deployment bloat affects performance and security

## User Stories

### Primary Personas

#### 1. HydroML Developers
**Current Pain Points**:
- "I can't find where components are defined - files are scattered everywhere"
- "Base template is too complex to modify safely"
- "Deployment takes forever due to massive staticfiles directory"

**Desired Experience**:
- "I can quickly locate and modify any component"
- "Template changes are straightforward and well-structured"
- "Fast, clean deployments with optimized file structure"

#### 2. System Administrators
**Current Pain Points**:
- "Deployment packages are bloated with 40,000+ unnecessary files"
- "Can't determine which files are actually used in production"

**Desired Experience**:
- "Clean, minimal deployment packages"
- "Clear understanding of production vs development files"

#### 3. New Team Members
**Current Pain Points**:
- "Project structure is confusing - too many similar files"
- "Hard to understand which components are active vs legacy"

**Desired Experience**:
- "Clear, logical project organization"
- "Obvious component hierarchy and relationships"

## Requirements

### Functional Requirements

#### 1. Static File Optimization
- **FR1.1**: Remove all Node.js development artifacts from staticfiles
- **FR1.2**: Eliminate duplicate CSS/JS files across directories  
- **FR1.3**: Consolidate unused demo and testing files
- **FR1.4**: Maintain all active production functionality

#### 2. Component System Cleanup
- **FR2.1**: Complete Wave → Grove component migration analysis
- **FR2.2**: Remove confirmed unused Wave components
- **FR2.3**: Consolidate Grove component CSS loading order
- **FR2.4**: Preserve all active UI functionality

#### 3. Template Architecture Modernization
- **FR3.1**: Restructure base_main.html into modular partials
- **FR3.2**: Extract inline CSS to dedicated files
- **FR3.3**: Optimize Alpine.js and script loading order
- **FR3.4**: Create reusable panel and component patterns
- **FR3.5**: Maintain all current template functionality

#### 4. Documentation Consolidation
- **FR4.1**: Merge redundant context documentation files
- **FR4.2**: Archive obsolete implementation summaries
- **FR4.3**: Create comprehensive architecture documentation
- **FR4.4**: Update file organization guidelines

#### 5. Epic and Issue Consolidation
- **FR5.1**: Analyze and consolidate duplicate/obsolete GitHub epics
- **FR5.2**: Merge redundant Celery integration issues (#54, #35, #55-60)
- **FR5.3**: Close completed/resolved issues marked with ✅
- **FR5.4**: Establish clear epic numbering and organization standards
- **FR5.5**: Archive obsolete feature requests and analysis tasks

#### 6. Project Structure Standards
- **FR6.1**: Establish clear directory organization patterns
- **FR6.2**: Create component location standards
- **FR6.3**: Document file naming conventions
- **FR6.4**: Implement automated cleanup verification

### Non-Functional Requirements

#### Performance
- **NFR1**: Reduce deployment package size by 60%+
- **NFR2**: Improve template parsing speed through modularization
- **NFR3**: Optimize CSS loading order for FOUC prevention
- **NFR4**: Maintain current page load performance

#### Maintainability
- **NFR5**: Enable individual template partial testing
- **NFR6**: Create self-documenting component hierarchy
- **NFR7**: Establish clear separation of concerns
- **NFR8**: Enable easy component location and modification

#### Security
- **NFR9**: Remove development artifacts from production builds
- **NFR10**: Eliminate unused code that could contain vulnerabilities
- **NFR11**: Maintain current security practices

#### Compatibility
- **NFR12**: Preserve all existing functionality
- **NFR13**: Maintain Alpine.js component initialization
- **NFR14**: Keep Grove Design System compatibility
- **NFR15**: Support current theme management system

## Success Criteria

### Measurable Outcomes
1. **File Reduction**: Reduce total project files by 30-40%
2. **Deployment Size**: Decrease deployment package by 60%+
3. **Template Complexity**: Reduce base_main.html from 440 to <150 lines
4. **Documentation Consolidation**: Reduce context files by 25%
5. **Developer Velocity**: 50% faster component location and modification

### Key Metrics and KPIs
- **Static File Count**: From 40,000+ to <5,000
- **CSS Loading Time**: Optimized Grove → Tailwind cascade
- **Template Modularity**: 8+ reusable partial components
- **Documentation Coverage**: Single authoritative architecture guide
- **Zero Regression**: All current functionality preserved

### Acceptance Criteria
- [ ] All pages render correctly with new template structure
- [ ] Alpine.js components initialize properly
- [ ] Grove Design System components work as expected  
- [ ] Theme switching functionality maintained
- [ ] Mobile responsive design preserved
- [ ] No JavaScript console errors
- [ ] Playwright tests pass completely
- [ ] Deployment builds successfully
- [ ] Performance metrics maintained or improved

## Constraints & Assumptions

### Technical Constraints
- **TC1**: Must maintain Grove Design System compatibility
- **TC2**: Cannot break existing Alpine.js components
- **TC3**: Must preserve current authentication and security
- **TC4**: Cannot modify core Django template inheritance
- **TC5**: Must maintain current database and session functionality

### Timeline Constraints
- **TC6**: Must complete before major Data Studio epic begins
- **TC7**: Cannot interfere with current development workflow
- **TC8**: Cleanup phases must be individually testable

### Resource Constraints  
- **TC9**: Single developer implementation with CCMP agents
- **TC10**: Must use existing tooling and infrastructure
- **TC11**: Limited testing environment for validation

### Assumptions
- **A1**: Current Grove components are stable and final
- **A2**: No major Alpine.js version changes during implementation
- **A3**: Existing Playwright tests adequately cover functionality
- **A4**: Session system refactoring (Issues #81-85) won't conflict

## Out of Scope

### Explicitly NOT Building
1. **New Features**: No new functionality, only cleanup and organization
2. **Design Changes**: No UI/UX modifications to existing components  
3. **Performance Optimization**: Beyond what cleanup naturally provides
4. **Database Changes**: No model or migration modifications
5. **Third-party Updates**: No library version upgrades
6. **Testing Infrastructure**: No new testing framework implementation
7. **Session System Modifications**: Wait for Issues #81-85 completion

### Future Considerations
- Advanced component testing framework
- Automated file usage analysis tools  
- Performance monitoring integration
- Advanced template optimization techniques

## Dependencies

### External Dependencies
- **D1**: GitHub CLI for issue management
- **D2**: Docker environment for testing changes
- **D3**: Playwright for UI regression testing
- **D4**: Current Grove Design System stability

### Internal Team Dependencies
- **D5**: Architecture approval from project stakeholders
- **D6**: Testing coordination to avoid conflicts
- **D7**: Deployment process documentation updates
- **D8**: Team coordination for worktree development

### Technical Dependencies
- **D9**: Current Alpine.js version compatibility
- **D10**: Django static file collection process
- **D11**: Tailwind CSS build system
- **D12**: Current theme management system

### Timing Dependencies
- **D13**: Complete before Data Studio epic implementation
- **D14**: Coordinate with session system refactoring timeline
- **D15**: Align with any planned infrastructure updates

## Implementation Phases

### Phase 1: Analysis and Documentation (1-2 days)
- Complete file usage analysis
- Document current component relationships  
- Create detailed cleanup recommendations
- Establish testing protocols

### Phase 2: Static File Cleanup (1 day)
- Remove Node.js artifacts from staticfiles
- Consolidate duplicate files
- Clean demo and testing artifacts
- Verify deployment still works

### Phase 3: Component System Modernization (2-3 days)
- Complete Wave → Grove migration analysis
- Remove unused legacy components
- Consolidate CSS loading order
- Test all UI components

### Phase 4: Template Architecture Restructure (3-4 days)
- Create modular base template structure
- Extract inline CSS and scripts
- Implement reusable panel patterns
- Comprehensive testing of all pages

### Phase 5: Documentation and Standards (1-2 days)
- Consolidate context documentation
- Create architecture guidelines
- Update development standards
- Team knowledge transfer

## Risk Assessment

### Low Risk (Execute with confidence)
- Static file cleanup in staticfiles directory
- Demo file removal and consolidation
- Context documentation merging
- CSS extraction to dedicated files

### Medium Risk (Requires careful testing)
- Wave component removal (need usage verification)
- Template partial extraction
- Script loading order changes
- Base template inheritance modification

### High Risk (Requires extensive validation)
- Complete base_main.html restructure
- Alpine.js initialization changes
- Core template hierarchy modifications

### Mitigation Strategies
- **Backup Strategy**: Git worktrees for safe parallel development
- **Testing Protocol**: Playwright validation at each phase
- **Rollback Plan**: Immediate revert capability for any changes
- **Incremental Approach**: Small, testable changes with validation
- **CCMP Coordination**: Parallel agents for complex multi-file operations

## Success Measurement

### Short-term Success (End of Implementation)
- All acceptance criteria met
- No functionality regression
- Improved developer experience metrics
- Clean deployment builds

### Medium-term Success (1 month)
- Faster development velocity
- Easier onboarding for new developers
- Reduced maintenance overhead
- Stable component system

### Long-term Success (3 months)
- Foundation for future epic implementations
- Sustainable development practices
- Professional codebase quality
- Improved system performance

---

**Ready for Epic Creation**: This PRD provides comprehensive requirements for CCMP epic decomposition into parallel implementation tasks.