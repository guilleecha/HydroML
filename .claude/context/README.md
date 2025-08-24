# HydroML Context Documentation

This directory contains comprehensive context documentation for the HydroML project, providing essential information about system architecture, design patterns, and development workflows.

**Documentation Status**: ✅ **CONSOLIDATED** - August 2025 major reorganization  
**Total Files**: 11 active documents (reduced from 27 through consolidation)  
**Coverage**: Complete system architecture, design system, and development workflows

## 📁 Active Documentation Structure

### 🏗️ System Architecture
- **`system-architecture-overview.md`** - Complete system architecture documentation
  - Technology stack and infrastructure
  - Django application structure and patterns
  - Database architecture and optimization
  - Security and performance considerations
  - Future roadmap and scalability planning

### 🎨 Design System
- **`grove-design-system-guide.md`** - Complete Grove Design System documentation
  - Component library and usage patterns
  - Design tokens and theming system
  - Migration guides from Wave to Grove
  - Development guidelines and best practices
  - Visual testing results and browser compatibility

### 🔧 Data Tools & Session Management
- **`data-tools-architecture.md`** - Data manipulation and session management
  - Session-based workflow architecture
  - Modular frontend JavaScript structure
  - TanStack Table integration
  - API endpoints and backend services
  - Performance optimization and caching

### 🔧 Configuration & Integration
- **`mcp-configuration.md`** - MCP server configuration and integration
- **`ccmp-workflow.md`** - CCMP (Claude Code PM) workflow documentation
- **`sentry-integration-summary.md`** - Error monitoring and observability

### 📋 Project Management
- **`current-status.md`** - Current project status and active development
- **`design-specifications.md`** - UI/UX design specifications and standards
- **`branding-evolution.md`** - Brand identity and visual evolution
- **`autonomous-execution-plan.md`** - Autonomous development planning

## 📚 Archive Structure

### Consolidated Documentation
The following files have been consolidated into comprehensive guides:

#### Grove Design System (7 files → 1)
- ✅ `grove-design-system-implementation-summary.md` → `grove-design-system-guide.md`
- ✅ `grove-card-component-reference.md` → `grove-design-system-guide.md`
- ✅ `wave-to-grove-migration-guide.md` → `grove-design-system-guide.md`
- ✅ `rendering-issue-resolution-summary.md` → `grove-design-system-guide.md`
- ✅ `tabler-icons-troubleshooting-guide.md` → `grove-design-system-guide.md`
- ✅ `blank-page-rendering-fix.md` → `grove-design-system-guide.md`
- ✅ `theme-demo-implementation-summary.md` → `grove-design-system-guide.md`

#### System Architecture (4 files → 1)
- ✅ `hydroml-architecture.md` → `system-architecture-overview.md`
- ✅ `hydroml-system-architecture.md` → `system-architecture-overview.md`
- ✅ `base-template-reorganization-plan.md` → `system-architecture-overview.md`
- ✅ `breadcrumb-fixes-and-tanstack-implementation.md` → `system-architecture-overview.md`

#### Data Tools Architecture (4 files → 1)
- ✅ `session-system-architecture.md` → `data-tools-architecture.md`
- ✅ `data-studio-frontend-fix-summary.md` → `data-tools-architecture.md`
- ✅ `data-studio-refactoring-summary.md` → `data-tools-architecture.md`
- ✅ `tanstack-table-implementation-solution.md` → `data-tools-architecture.md`

### Archived Files
Historical documentation preserved in `archive/` directory:

#### `/archive/project-analysis/`
- `github-epic-consolidation-analysis.md` - GitHub epic analysis (completed)
- `project-cleanup-analysis.md` - Project cleanup analysis (completed)
- `issues-obsolescence-analysis.md` - Issue obsolescence tracking (superseded)
- `code-refactoring-summary.md` - Code refactoring summary (completed)

#### `/archive/implementation-summaries/`
- Implementation summaries consolidated into active guides

#### `/archive/troubleshooting-guides/`
- Issue-specific troubleshooting guides (resolved issues)

#### `/archive/migration-guides/`
- Migration documentation (completed transitions)

#### `/archive/technical-summaries/`
- Technical implementation summaries (completed features)

## 🚀 Context Usage Guide

### For New Developers
1. **Start with**: `system-architecture-overview.md` for overall understanding
2. **UI Development**: Read `grove-design-system-guide.md` for design patterns
3. **Data Tools**: Review `data-tools-architecture.md` for data manipulation features
4. **Setup**: Check `mcp-configuration.md` and `ccmp-workflow.md` for development setup

### For AI Agents
1. **System Understanding**: Load `system-architecture-overview.md` for complete context
2. **Design Consistency**: Reference `grove-design-system-guide.md` for UI work
3. **Data Features**: Use `data-tools-architecture.md` for data-related tasks
4. **Current State**: Check `current-status.md` for active development priorities

### For Architecture Changes
1. **Impact Assessment**: Review all three main architecture documents
2. **Design System Changes**: Update `grove-design-system-guide.md`
3. **Infrastructure Changes**: Update `system-architecture-overview.md`
4. **Data Layer Changes**: Update `data-tools-architecture.md`

## 📊 Documentation Metrics

### Consolidation Results
- **Files Reduced**: 27 → 11 (59% reduction)
- **Total Documentation**: ~200KB preserved and organized
- **Duplication Eliminated**: 100% - no conflicting information
- **Coverage Maintained**: Complete system documentation preserved
- **Accessibility Improved**: Clear navigation and cross-references

### Quality Standards
- ✅ **Comprehensive**: All system aspects documented
- ✅ **Current**: All documentation reflects latest implementation
- ✅ **Cross-Referenced**: Clear links between related concepts
- ✅ **Searchable**: Well-structured headings and content organization
- ✅ **Maintainable**: Clear ownership and update procedures

## 🔄 Maintenance Guidelines

### Update Frequency
- **System Architecture**: Update after major architectural changes
- **Grove Design System**: Update when adding new components or patterns
- **Data Tools**: Update when session management or data processing changes
- **Configuration**: Update when integrations or tools change

### Review Schedule
- **Quarterly Review**: Validate all documentation is current
- **Post-Epic Review**: Update relevant documentation after major feature completion
- **Annual Archive**: Move completed implementation summaries to archive

### Content Standards
- **Code Examples**: Include working code examples where applicable
- **Visual Evidence**: Screenshots for UI components and layouts
- **Cross-References**: Link related concepts between documents
- **Version History**: Track significant changes and updates

## 🔧 Integration Points

### Development Workflow
- **CCMP System**: Documented in `ccmp-workflow.md`
- **Grove Components**: Usage patterns in `grove-design-system-guide.md`
- **Data Sessions**: Architecture in `data-tools-architecture.md`
- **Error Monitoring**: Sentry integration details in `sentry-integration-summary.md`

### External References
- **GitHub Issues**: References preserved in archived analysis documents
- **Design Files**: UI specifications in `design-specifications.md`
- **Deployment**: Infrastructure details in `system-architecture-overview.md`
- **Testing**: Testing strategies throughout architecture documents

---

**Last Updated**: August 2025  
**Next Review**: November 2025  
**Maintained By**: HydroML Development Team  
**Documentation Standard**: CLAUDE.md compliant