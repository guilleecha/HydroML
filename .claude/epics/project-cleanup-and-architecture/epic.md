---
name: project-cleanup-and-architecture
status: backlog
created: 2025-08-24T17:30:18Z
progress: 0%
prd: .claude/prds/project-cleanup-and-architecture.md
github: https://github.com/guilleecha/HydroML/issues/86
---

# Epic: Project Cleanup and Architecture Modernization

## Overview

Comprehensive modernization of HydroML project structure through systematic cleanup, component consolidation, and template architecture restructuring. This epic focuses on reducing file complexity by 30-40%, optimizing the Grove Design System integration, and establishing maintainable development patterns.

**Technical Focus**: File system optimization, template modularization, component system cleanup, and architectural documentation improvement.

## Architecture Decisions

### 1. Template Architecture Pattern
- **Decision**: Modular template inheritance with dedicated partials
- **Rationale**: Enables component-level testing, improves maintainability, supports Grove Design System
- **Pattern**: Base layout → Specialized templates → Reusable partials

### 2. CSS Loading Strategy  
- **Decision**: Grove components load before Tailwind CSS
- **Rationale**: Prevents cascade conflicts, maintains design system integrity
- **Implementation**: Dedicated CSS loading partial with proper order

### 3. Component System Hierarchy
- **Decision**: Grove Design System as primary, specialized components as extensions
- **Rationale**: Consistent with current architecture evolution, supports future scalability
- **Migration**: Complete Wave → Grove transition analysis and cleanup

### 4. Static File Management
- **Decision**: Aggressive cleanup with verification-based approach
- **Rationale**: Removes deployment bloat, improves security, simplifies maintenance
- **Safety**: Usage verification before deletion, comprehensive backup strategy

### 5. Documentation Architecture
- **Decision**: Single-source-of-truth for each architectural domain
- **Rationale**: Reduces redundancy, improves discoverability, easier maintenance
- **Structure**: Domain-specific documentation with cross-references

## Technical Approach

### Frontend Components

#### Template System Modernization
- **Base Template**: Simplified base_main.html extending modular base_grove.html
- **Partial Components**: Dedicated files for head, navigation, scripts, panels
- **Reusable Patterns**: Generic panel system for upload/experiment modals
- **Critical CSS**: Inline critical styles for FOUC prevention

#### Component System Cleanup
- **Grove Components**: Verify and consolidate all grove-*.css files
- **Legacy Migration**: Complete Wave component usage analysis
- **CSS Optimization**: Proper loading order, reduced conflicts
- **JavaScript Integration**: Optimized Alpine.js initialization

#### Asset Organization
- **Static Files**: Remove Node.js artifacts, consolidate duplicates
- **Demo Cleanup**: Consolidate development artifacts
- **Image Assets**: Verify usage and optimize organization

### Backend Services

#### No Backend Changes Required
- **Database**: No model or migration modifications
- **APIs**: Preserve all existing endpoint functionality  
- **Authentication**: Maintain current security implementation
- **Session Management**: No interference with Issues #81-85

#### File System Services
- **Static File Collection**: Optimize Django collectstatic process
- **Template Loading**: Verify template inheritance performance
- **Asset Serving**: Maintain current static file serving

### Infrastructure

#### Development Environment
- **CCMP Worktrees**: Parallel development in isolated branches
- **Testing Integration**: Playwright validation for all changes
- **Docker Environment**: Maintain containerized development

#### Deployment Optimization  
- **Package Size**: 60%+ reduction through file cleanup
- **Build Process**: Optimized static file collection
- **Security**: Remove development artifacts from production

#### Monitoring and Validation
- **Regression Testing**: Comprehensive Playwright coverage
- **Performance Monitoring**: Template rendering and load times
- **Functionality Verification**: All current features preserved

## Implementation Strategy

### Development Phases

#### Phase 1: Foundation and Analysis (2 days)
- Complete file usage analysis with verification
- Document current component relationships and dependencies
- Create detailed cleanup and migration recommendations
- Establish testing protocols and safety measures

#### Phase 2: Static File System Cleanup (1 day)  
- Remove Node.js development artifacts from staticfiles
- Consolidate duplicate CSS/JS files across directories
- Clean demo and testing artifacts with usage verification
- Validate deployment build process still functions

#### Phase 3: Component System Modernization (3 days)
- Complete Wave → Grove migration usage analysis
- Remove verified unused legacy components
- Consolidate Grove component CSS loading order
- Optimize Alpine.js and JavaScript component integration
- Test all UI components and interactive functionality

#### Phase 4: Template Architecture Restructure (4 days)
- Create modular base template structure with partials
- Extract inline CSS and scripts to dedicated files  
- Implement reusable panel patterns for modals
- Restructure base_main.html with proper inheritance
- Comprehensive testing of all pages and functionality

#### Phase 5: Documentation and Standards (2 days)
- Consolidate redundant context documentation files
- Create comprehensive architecture documentation
- Update development standards and guidelines
- Team knowledge transfer and validation

### Risk Mitigation Strategies

#### Technical Risks
- **Worktree Development**: Complete isolation from main branch
- **Incremental Changes**: Small, testable modifications with validation
- **Rollback Capability**: Immediate revert for any problematic changes
- **Comprehensive Testing**: Playwright validation at each phase

#### Process Risks
- **CCMP Coordination**: Parallel agents for complex multi-file operations
- **Backup Strategy**: Git-based backup with multiple restore points
- **Team Coordination**: Clear communication of changes and impacts

### Testing Approach

#### Automated Testing
- **Playwright Tests**: Full UI regression testing suite
- **Template Validation**: Django template syntax and inheritance
- **Component Testing**: Alpine.js initialization and functionality
- **CSS Validation**: Proper loading order and cascade behavior

#### Manual Validation
- **Cross-browser Testing**: All major browsers and mobile devices
- **Functionality Verification**: All interactive features and workflows  
- **Performance Testing**: Page load times and rendering speed
- **User Experience**: Navigation, forms, and interactive components

## Task Breakdown Preview

High-level task categories that will be created:

- [ ] **Analysis and Documentation**: File usage analysis, component mapping, safety protocols
- [ ] **Static File Cleanup**: Remove Node.js artifacts, consolidate duplicates, verify builds
- [ ] **Legacy Component Migration**: Wave usage analysis, Grove consolidation, CSS optimization
- [ ] **Template Architecture**: Base template restructure, partial extraction, script optimization
- [ ] **Reusable Component Patterns**: Panel system, modal patterns, component standardization
- [ ] **CSS Loading Optimization**: Grove/Tailwind order, critical CSS extraction, FOUC prevention  
- [ ] **Alpine.js Integration**: Script loading order, component initialization, functionality testing
- [ ] **Epic and Issue Consolidation**: GitHub epic cleanup, duplicate issue resolution, numbering standards
- [ ] **Documentation Consolidation**: Context file merging, architecture documentation, standards  
- [ ] **Testing and Validation**: Playwright testing, regression validation, performance verification
- [ ] **Deployment Optimization**: Build process verification, package size validation, security cleanup

## Dependencies

### External Dependencies
- **GitHub CLI**: Issue management and sub-issue hierarchy
- **Docker Environment**: Testing environment for validation
- **Playwright**: Automated UI regression testing
- **Current Grove Design System**: Stable component implementations

### Internal Dependencies  
- **Architecture Approval**: Project stakeholder sign-off on changes
- **Testing Coordination**: Ensure no conflicts with other development
- **Deployment Documentation**: Update build and deployment processes
- **Team Knowledge Transfer**: Ensure all developers understand new structure

### Technical Dependencies
- **Alpine.js Compatibility**: Current version 3.x integration
- **Django Static Files**: collectstatic process functionality
- **Tailwind CSS Build**: Current build system compatibility
- **Theme Management**: Existing theme system preservation

### Timing Dependencies
- **Session System Coordination**: Avoid conflicts with Issues #81-85
- **Data Studio Epic Preparation**: Complete before major Data Studio work begins
- **Current Development Workflow**: Minimize disruption to active development

## Success Criteria (Technical)

### Performance Benchmarks
- **File Count Reduction**: 30-40% decrease in total project files
- **Deployment Package**: 60%+ reduction in deployment size
- **Template Complexity**: base_main.html reduced from 440 to <150 lines
- **CSS Loading**: Optimized Grove → Tailwind cascade with no FOUC
- **Build Time**: Maintain or improve current build performance

### Quality Gates
- **Zero Regression**: All existing functionality preserved
- **Template Performance**: No degradation in template rendering speed
- **Component Functionality**: All Alpine.js components work correctly
- **UI Consistency**: Grove Design System components render properly
- **Cross-browser Compatibility**: All major browsers and devices supported

### Acceptance Criteria
- [ ] All pages render correctly with new template structure
- [ ] Navigation, modals, and interactive elements function properly
- [ ] Theme switching and user interface state preserved
- [ ] Mobile responsive design maintained across all screen sizes
- [ ] JavaScript console shows no errors during normal operation
- [ ] Playwright test suite passes completely with no regressions
- [ ] Docker deployment builds successfully with optimized size
- [ ] Development workflow remains efficient for team members

### Code Quality Standards
- **Template Modularity**: Clear separation of concerns with reusable partials
- **CSS Architecture**: Proper component hierarchy with minimal conflicts
- **Component Organization**: Logical file structure with easy navigation
- **Documentation Quality**: Comprehensive, accurate, and up-to-date guides

## Estimated Effort

### Overall Timeline: 8-10 development days

#### Breakdown by Phase:
- **Phase 1** (Analysis): 2 days - Complex analysis and documentation
- **Phase 2** (Static Cleanup): 1 day - Straightforward file operations  
- **Phase 3** (Components): 3 days - Component analysis and migration
- **Phase 4** (Templates): 4 days - Most complex, requires careful testing
- **Phase 5** (Documentation): 2 days - Consolidation and standards

#### Resource Requirements:
- **Primary Developer**: Full-time focus with CCMP agent assistance
- **Testing Environment**: Docker environment for validation
- **Review Process**: Code review for architectural changes
- **Coordination**: Team communication for workflow integration

#### Critical Path Items:
1. **Template Architecture Changes**: Highest complexity and risk
2. **Component Migration Analysis**: Requires thorough investigation  
3. **CSS Loading Order**: Critical for proper rendering
4. **Alpine.js Integration**: Must preserve all interactive functionality

#### Parallel Work Opportunities:
- **Static File Cleanup**: Can be done independently
- **Documentation Consolidation**: Parallel to technical implementation
- **Component Analysis**: Can run alongside template work
- **Testing Framework**: Prepare while implementation proceeds

## Tasks Created

- [ ] #87 - Project Analysis and Documentation (parallel: true)
- [ ] #88 - Static File System Cleanup (parallel: false)  
- [ ] #89 - Legacy Component Migration Analysis (parallel: true)
- [ ] #96 - Template Architecture Foundation (parallel: false)
- [ ] #97 - Base Template Restructure Implementation (parallel: false)
- [ ] #98 - Alpine.js Integration Optimization (parallel: false)
- [ ] #90 - CSS Loading Order Optimization (parallel: false)
- [ ] #91 - Epic and GitHub Issue Consolidation (parallel: true)
- [ ] #92 - Reusable Component Patterns (parallel: false)
- [ ] #93 - Context Documentation Consolidation (parallel: true)
- [ ] #94 - Testing and Validation Framework (parallel: false)
- [ ] #95 - Deployment Optimization and Final Validation (parallel: false)

**Total tasks**: 12
**Parallel tasks**: 4 (087, 089, 091, 093)
**Sequential tasks**: 8 (088, 090, 092, 094, 095, 096, 097, 098)
**Estimated total effort**: 32-40 hours (8-10 development days)
