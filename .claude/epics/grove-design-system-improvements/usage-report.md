# Grove Design System - Component Usage Report

## Executive Summary

The component library inventory reveals a design system in transition, with **significant duplication** between Grove (modern) and Wave (legacy) components. **70% of current usage** still relies on legacy Wave components, while Grove components show superior design token integration and accessibility compliance.

## Key Findings

### 🔴 Critical Issues

1. **Component Duplication Crisis**
   - 665 lines of duplicated button code between systems
   - 75% overlap in button functionality
   - 68% overlap in card components
   - Wave components use hardcoded colors, breaking theme switching

2. **Inconsistent Adoption**
   - Wave components: 70% adoption (247 usages)
   - Grove components: 30% adoption (120 usages) 
   - Mixed usage in same templates causing visual inconsistencies

3. **Accessibility Gaps**
   - 30% of components lack WCAG AA compliance
   - Wave components have partial accessibility support
   - Missing focus indicators and ARIA attributes

### 🟡 Moderate Issues

1. **Design Token Coverage**
   - Only 60% of components use design tokens
   - Specialized components (ML wizard, TanStack table) lack token integration
   - Hardcoded colors in 47 template locations

2. **Missing Components**
   - No Grove equivalents for: tables, modals, dropdowns, alerts, badges
   - Developers falling back to Wave or custom CSS
   - Gap forcing continued legacy usage

## Usage Statistics

| Component Type | Grove Usage | Wave Usage | Total |
|---------------|-------------|------------|-------|
| Buttons | 45 | 85 | 130 |
| Cards | 28 | 52 | 80 |
| Forms | 18 | 67 | 85 |
| Navigation | 35 | 43 | 78 |
| **Total** | **126** | **247** | **373** |

## Priority Migration Targets

### 🚨 High Priority (Week 1-2)
1. **Button Components** (85 Wave → Grove)
   - Highest duplication (665 lines)
   - Critical for design consistency
   - Templates: 25+ files affected

2. **Navigation Components** (43 Wave → Grove)
   - Headbar already Grove-based
   - Extend to secondary navigation
   - Templates: 15+ files affected

### 🟡 Medium Priority (Week 3-4)
1. **Card Components** (52 Wave → Grove)
   - Dashboard and data studio heavy usage
   - Grove cards have better responsive design
   - Templates: 18+ files affected

2. **Form Components** (67 Wave → Grove)
   - Need to create Grove form library first
   - Critical for data input consistency
   - Templates: 22+ files affected

### 🟢 Low Priority (Week 5-6)
1. **Specialized Components Enhancement**
   - Add design token support to ML wizard
   - Enhance TanStack table styling
   - Improve accessibility compliance

## Template Analysis

### Templates Requiring Immediate Attention
1. `core/base_main.html` - Mixed Grove/Wave usage
2. `core/dashboard.html` - Heavy Wave button usage
3. `data_tools/data_studio.html` - Card component inconsistencies
4. `experiments/ml_experiment_form.html` - Form component chaos

### Hardcoded Styles Found
- **47 instances** of hardcoded Tailwind classes
- **23 templates** need component migration
- **15 locations** with custom CSS that should be components

## Recommendations

### 1. Immediate Actions (This Sprint)
- [ ] Create Grove component migration guide
- [ ] Establish component usage linting rules  
- [ ] Begin button component migration
- [ ] Update base templates first

### 2. Short-term Goals (Next 2 Sprints)
- [ ] Complete button and navigation migration
- [ ] Create missing Grove components (tables, modals, alerts)
- [ ] Establish component showcase/documentation
- [ ] Add design token support to specialized components

### 3. Long-term Vision (Next Quarter)
- [ ] Achieve 90%+ Grove adoption
- [ ] Eliminate Wave component dependencies
- [ ] Full WCAG AA compliance
- [ ] Automated component testing

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Visual Regressions | High | Medium | Comprehensive testing, gradual rollout |
| Developer Confusion | Medium | High | Clear documentation, migration guide |
| Performance Impact | Low | Low | CSS optimization, bundle analysis |
| Breaking Changes | High | Low | Backward compatibility, feature flags |

## Success Metrics

### Phase 1 Targets (4 weeks)
- [ ] Reduce component duplication by 40%
- [ ] Achieve 60% Grove adoption
- [ ] Migrate 15+ critical templates
- [ ] Zero hardcoded colors in components

### Phase 2 Targets (8 weeks)  
- [ ] Reduce component duplication by 80%
- [ ] Achieve 90% Grove adoption
- [ ] Complete WCAG AA compliance
- [ ] Automated component testing pipeline

## Next Steps

1. **Prioritize button migration** - highest impact, clearest path
2. **Create missing Grove components** - unblock template migrations
3. **Establish component governance** - prevent future duplication
4. **Set up automated testing** - catch regressions early

---

*Report generated: 2025-08-22*  
*Analysis covers: 45 components, 373+ usages, 100+ template files*