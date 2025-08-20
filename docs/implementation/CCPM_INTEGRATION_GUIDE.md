# Claude Code PM (CCMP) Integration Guide for HydroML

## Overview
This guide documents the integration of the Claude Code PM system into HydroML, enabling spec-driven development with parallel AI agents for accelerated feature delivery.

## What is CCPM?
Claude Code PM is an AI-augmented development workflow that provides:
- **Spec-driven development** with full traceability
- **Parallel AI agent execution** for 3x faster development
- **GitHub Issues integration** for seamless project management  
- **89% reduction in context switching**
- **75% reduction in bug rates**

## Integration Benefits for HydroML

### Development Acceleration
- **Parallel Execution**: Multiple AI agents work simultaneously on different aspects of a feature
- **Django Specialization**: Dedicated agent for Django models, views, and API development
- **Frontend Focus**: Specialized agent for Alpine.js, Tailwind CSS, and AG Grid components
- **ML Integration**: Expert agent for MLflow experiments and data pipeline optimization

### Quality Assurance
- **Comprehensive Testing**: Dedicated test agent ensures >80% coverage across all components
- **Code Standards**: Enforces HydroML's CLAUDE.md guidelines automatically
- **Security Validation**: Validates environment variable usage and security practices
- **Performance Optimization**: Database query optimization and frontend responsiveness

## Implementation Architecture

### Directory Structure
```
hydroML/
├── .claude/                     # CCPM integration directory
│   ├── CLAUDE.md               # HydroML-specific instructions
│   ├── README.md               # CCPM system documentation
│   ├── agents/                 # Specialized AI agents
│   │   ├── django-specialist.md
│   │   ├── frontend-specialist.md
│   │   ├── ml-specialist.md
│   │   ├── data-specialist.md
│   │   └── test-specialist.md
│   ├── commands/pm/            # Project management commands
│   │   ├── prd-new.md
│   │   ├── epic-decompose.md
│   │   └── issue-start.md
│   ├── context/                # Project context for agents
│   │   ├── hydroml_architecture.md
│   │   ├── django_apps.md
│   │   └── development_setup.md
│   ├── prds/                   # Product Requirements Documents
│   ├── epics/                  # Epic workspace (gitignored)
│   └── scripts/                # Utility scripts
└── [existing HydroML structure]
```

### Agent Specialization

#### Django Specialist Agent
- **Focus**: Django models, views, API endpoints, migrations
- **Expertise**: UUID primary keys, modular structure, service layer patterns
- **Output**: Concise Django component implementations

#### Frontend Specialist Agent  
- **Focus**: Alpine.js components, Tailwind CSS layouts, AG Grid integration
- **Expertise**: Reactive components, responsive design, data visualization
- **Output**: Modern frontend implementations with mobile support

#### ML Specialist Agent
- **Focus**: MLflow integration, experiment tracking, hyperparameter optimization
- **Expertise**: Model validation pipelines, Optuna studies, data quality assessment
- **Output**: Optimized ML workflows and experiment configurations

#### Data Specialist Agent
- **Focus**: Data processing pipelines, quality assessment, transformation workflows
- **Expertise**: Multi-format support, session management, Great Expectations integration
- **Output**: Robust data processing implementations

#### Test Specialist Agent
- **Focus**: Comprehensive testing across Django, frontend, and ML components
- **Expertise**: Unit tests, integration tests, E2E testing with Playwright
- **Output**: >80% test coverage with reliable validation

## Workflow Integration

### 1. Spec-Driven Development Process
```bash
# 1. Brainstorm feature requirements
/pm:prd-new user_authentication_enhancement

# 2. Convert PRD to implementation plan
/pm:prd-parse user_authentication_enhancement

# 3. Decompose into parallelizable tasks
/pm:epic-decompose user_authentication_enhancement

# 4. Sync to GitHub Issues  
/pm:epic-sync user_authentication_enhancement

# 5. Launch parallel agent development
/pm:issue-start 42
```

### 2. Parallel Execution Example
When implementing a new Data Export feature:

**Agent Distribution:**
- **django-specialist**: Creates export models, API endpoints, serializers
- **frontend-specialist**: Builds export UI components, form handling, progress indicators
- **data-specialist**: Implements export pipeline, format conversion, quality validation
- **test-specialist**: Creates unit tests, integration tests, E2E export workflows
- **ml-specialist**: Adds experiment result export, MLflow integration

**Coordination**: All agents work simultaneously in isolated Git worktrees, with progress updates posted to GitHub Issues.

### 3. GitHub Issues Integration
- **Epic Planning**: Issues created with proper labels and dependencies
- **Progress Tracking**: Real-time updates from each agent
- **Human-AI Collaboration**: Seamless handoffs through issue comments
- **Quality Gates**: Automated validation before issue closure

## HydroML-Specific Customizations

### Technology Stack Awareness
All agents understand HydroML's specific stack:
- **Django 5.2.4** with modular app structure
- **PostgreSQL 14** with UUID primary keys
- **Alpine.js + Tailwind CSS** for reactive frontend
- **MLflow 2.22.1** for experiment tracking
- **Docker Compose** for development environment

### Code Quality Standards
CCPM enforces HydroML's quality guidelines:
- Functions: maximum 50 lines
- Classes: maximum 100 lines
- Files: maximum 500 lines
- Test coverage: >80% required
- Environment variables only (no hardcoded secrets)

### Development Patterns
Agents follow established HydroML patterns:
- Service layer separation from Django requests
- Modular models/views in separate directories  
- Session-based data transformation workflows
- Comprehensive error handling with Sentry integration

## Getting Started

### 1. Initialize CCPM System
```bash
# Make script executable
chmod +x .claude/scripts/init.sh

# Run initialization  
./.claude/scripts/init.sh
```

### 2. Configure GitHub Integration
```bash
# Set up GitHub remote (if not already configured)
git remote add origin https://github.com/your-org/hydroML.git

# Configure GitHub CLI for Issues integration
gh auth login
```

### 3. Create First Feature with CCPM
```bash
# Example: Enhanced Data Quality Pipeline
/pm:prd-new data_quality_enhancement
/pm:prd-parse data_quality_enhancement  
/pm:epic-decompose data_quality_enhancement
/pm:epic-sync data_quality_enhancement
/pm:issue-start 45  # Use actual GitHub Issue number
```

## Advanced Features

### Git Worktree Management
CCPM creates isolated worktrees for parallel development:
```
.claude/worktrees/issue-45/
├── main/                    # Main development branch
├── agent-django/           # Django specialist workspace
├── agent-frontend/         # Frontend specialist workspace
├── agent-data/            # Data specialist workspace
└── agent-tests/           # Test specialist workspace
```

### Context Preservation
Each agent maintains awareness of:
- **Project Architecture**: HydroML's Django app structure
- **Existing Patterns**: Established code patterns and conventions
- **Dependencies**: Coordination with other parallel agents
- **Quality Standards**: CLAUDE.md guidelines and testing requirements

### Integration Testing
Automated validation ensures:
- **Code Quality**: Compliance with HydroML standards
- **Security**: Proper environment variable usage
- **Performance**: Optimized database queries and frontend responsiveness
- **Compatibility**: Cross-browser and mobile device support

## Monitoring and Optimization

### Performance Metrics
Track CCPM effectiveness through:
- **Development Speed**: Time from PRD to deployment
- **Bug Rates**: Issues found in production vs development
- **Test Coverage**: Automated coverage reporting
- **Code Quality**: Adherence to CLAUDE.md standards

### Continuous Improvement
- **Agent Optimization**: Refine agent specializations based on results
- **Pattern Recognition**: Update context files with new architectural decisions
- **Workflow Refinement**: Optimize command templates and processes
- **Integration Enhancement**: Improve GitHub Issues and CI/CD integration

## Best Practices

### Epic Planning
1. **Comprehensive PRDs**: Include user stories, technical requirements, and success criteria
2. **Technology Considerations**: Account for all HydroML stack components
3. **Parallel Planning**: Design for simultaneous agent execution
4. **Clear Acceptance Criteria**: Define measurable completion standards

### Agent Coordination
1. **Minimize Dependencies**: Reduce inter-agent coordination overhead
2. **Clear Interfaces**: Define explicit API contracts between components
3. **Context Management**: Maintain agent context firewalls
4. **Progress Transparency**: Regular GitHub Issues updates

### Quality Assurance
1. **Testing First**: Plan test strategies before implementation
2. **Security Review**: Validate security practices in every change
3. **Performance Focus**: Monitor and optimize system performance
4. **Documentation**: Keep implementation docs current

## Troubleshooting

### Common Issues
- **Agent Conflicts**: Resolved through Git worktree isolation
- **Context Overflow**: Agents return concise summaries only
- **Integration Failures**: Validated through automated testing
- **Performance Degradation**: Monitored through metrics and alerts

### Support Resources
- **Agent Definitions**: `.claude/agents/` directory
- **Command References**: `.claude/commands/pm/` templates
- **Context Files**: `.claude/context/` for project awareness
- **PRD Templates**: `.claude/prds/` for feature planning

## Future Enhancements

### Planned Improvements
1. **CI/CD Integration**: Automatic CCPM workflow triggers
2. **Enhanced Agents**: More specialized agents for specific domains
3. **Metrics Dashboard**: Real-time development analytics
4. **Template Expansion**: Additional PRD and task templates

### Customization Opportunities
1. **Domain Agents**: Specialized agents for hydrology-specific features
2. **Integration Agents**: Dedicated agents for external system integration
3. **Performance Agents**: Specialized optimization and monitoring agents
4. **Documentation Agents**: Automated documentation generation and updates

## Conclusion
The CCPM integration transforms HydroML development by enabling parallel AI agent execution with full spec-driven traceability. This system accelerates feature delivery while maintaining high quality standards and seamless GitHub integration.

Ready to experience 3x faster development with AI-powered parallel execution! 🚀