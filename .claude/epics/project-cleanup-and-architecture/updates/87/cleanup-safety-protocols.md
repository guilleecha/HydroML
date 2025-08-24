# Project Cleanup Safety Protocols and Testing Framework

**Issue #87 - Safety and Testing Protocols**  
**Purpose:** Ensure safe, reversible cleanup operations with comprehensive testing

## 1. Pre-Cleanup Safety Checklist

### Environment Validation
- [ ] **Development environment** fully functional
- [ ] **Docker services** running (db, redis, mlflow, web, worker)
- [ ] **All tests passing** baseline established
- [ ] **Git status clean** - no uncommitted changes
- [ ] **Branch created** from main for cleanup work
- [ ] **Backup created** of current state

### Baseline Testing
```bash
# Run comprehensive test suite
docker-compose exec web python -m pytest

# Manual UI regression testing
- [ ] Dashboard loads correctly
- [ ] Data Studio functionality works
- [ ] Experiment workflow functional
- [ ] All main navigation works
- [ ] Dark/light theme switching
- [ ] User authentication flows

# Performance baseline
- [ ] Page load times documented
- [ ] Console errors documented  
- [ ] Network requests baseline
```

## 2. Cleanup Phase Safety Protocols

### Phase 1: Low Risk Operations
**Target:** staticfiles directory, obvious duplicates

#### Pre-Phase Checklist:
- [ ] Current git commit saved
- [ ] Backup of files to be removed
- [ ] Test suite passes
- [ ] Docker containers healthy

#### Safety Commands:
```bash
# Create backup before changes
mkdir -p backups/phase1-$(date +%Y%m%d_%H%M%S)
cp -r staticfiles/ backups/phase1-$(date +%Y%m%d_%H%M%S)/

# Git safety
git checkout -b cleanup-phase1-staticfiles
git add . && git commit -m "Issue #87: Baseline before Phase 1 cleanup"

# Rollback command (if needed)
git checkout main
git branch -D cleanup-phase1-staticfiles
```

#### Post-Phase Verification:
```bash
# Regenerate staticfiles
docker-compose exec web python manage.py collectstatic --noinput

# Test suite
docker-compose exec web python -m pytest

# Manual verification
- [ ] All pages load without 404s
- [ ] CSS styling intact
- [ ] JavaScript functionality works
- [ ] No browser console errors
```

### Phase 2: Medium Risk Operations  
**Target:** Potentially unused files, Wave components

#### Pre-Phase Checklist:
- [ ] Phase 1 successfully completed
- [ ] Staging environment available
- [ ] Test suite 100% passing
- [ ] UI regression test plan ready

#### Safety Commands:
```bash
# Create phase 2 branch
git checkout -b cleanup-phase2-unused-files

# Backup strategy - individual file tracking
echo "# Files removed in Phase 2" > phase2-removed-files.log

# Before removing each file:
echo "$(date): Removing $FILE_PATH" >> phase2-removed-files.log
cp $FILE_PATH backups/phase2-individual/
```

#### Individual File Removal Protocol:
For each potentially unused file:
1. **Document**: Add to removal log
2. **Backup**: Copy to backup directory  
3. **Remove**: Delete from repository
4. **Test**: Run automated tests
5. **Verify**: Manual UI check
6. **Commit**: Single file commit for easy rollback

```bash
# Per-file safety protocol
remove_file_safely() {
    local file_path=$1
    echo "$(date): Removing $file_path" >> phase2-removed-files.log
    cp "$file_path" "backups/phase2-individual/$(basename $file_path)"
    rm "$file_path"
    git add . && git commit -m "Issue #87: Remove unused file $file_path"
    
    # Test immediately
    docker-compose exec web python -m pytest tests/unit/ -x
    if [ $? -ne 0 ]; then
        echo "TESTS FAILED - Rolling back $file_path"
        git revert HEAD --no-edit
        return 1
    fi
}
```

### Phase 3: High Risk Operations
**Target:** Template hierarchy, base components

#### Pre-Phase Requirements:
- [ ] Phases 1-2 completed successfully
- [ ] Full staging environment deployed
- [ ] Complete backup of templates/
- [ ] Extended test suite including E2E tests
- [ ] Team review of changes

#### Maximum Safety Protocol:
```bash
# Full environment backup
docker-compose exec web python manage.py dumpdata > backup-full-db.json
tar -czf backup-templates-$(date +%Y%m%d_%H%M%S).tar.gz */templates/

# Feature branch with protection
git checkout -b cleanup-phase3-templates-REVIEW-REQUIRED

# Require manual approval for each change
echo "Phase 3 requires manual review and approval for each file change"
```

## 3. Automated Rollback Procedures

### Quick Rollback Script
```bash
#!/bin/bash
# rollback_cleanup.sh

PHASE=$1
BACKUP_DIR="backups/phase${PHASE}-$(date +%Y%m%d_%H%M%S)"

case $PHASE in
    1)
        echo "Rolling back Phase 1: staticfiles cleanup"
        git checkout main
        git branch -D cleanup-phase1-staticfiles
        ;;
    2)
        echo "Rolling back Phase 2: unused files cleanup"
        # Restore files from backup
        cp -r backups/phase2-individual/* ./
        git checkout main
        git branch -D cleanup-phase2-unused-files
        ;;
    3)
        echo "Rolling back Phase 3: template changes"
        tar -xzf backup-templates-*.tar.gz
        docker-compose exec web python manage.py loaddata backup-full-db.json
        git checkout main
        git branch -D cleanup-phase3-templates-REVIEW-REQUIRED
        ;;
    *)
        echo "Usage: rollback_cleanup.sh [1|2|3]"
        ;;
esac

# Verify rollback
docker-compose down && docker-compose up --build
docker-compose exec web python -m pytest
```

## 4. Testing Framework for Each Phase

### Automated Test Categories

#### Unit Tests
```bash
# Core functionality tests
docker-compose exec web python -m pytest tests/unit/ -v

# Specific areas to focus:
- Static file loading tests
- Template rendering tests  
- Component integration tests
- Asset pipeline tests
```

#### Integration Tests
```bash
# Full workflow testing
docker-compose exec web python -m pytest tests/integration/ -v

# Key scenarios:
- User authentication flows
- Data Studio complete workflow
- Experiment creation and execution
- Project management operations
```

#### UI Regression Tests
```bash
# Manual testing checklist
- [ ] Dashboard loads with all cards
- [ ] Navigation menu functional
- [ ] Data Studio table renders
- [ ] Experiment wizard works
- [ ] Settings pages accessible
- [ ] File upload functionality
- [ ] Export/download features
```

### Performance Monitoring
```bash
# Page load time monitoring
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/"

# Browser console error detection
# Use browser dev tools to check for:
- 404 errors for missing assets
- JavaScript errors
- CSS parsing errors
- Network request failures
```

## 5. Verification Scripts

### File Reference Verification
```python
# verify_file_references.py
def verify_no_broken_references():
    """Scan all templates and code for references to removed files"""
    broken_refs = []
    # Implementation from file_usage_analysis.py
    return broken_refs

def verify_critical_assets_exist():
    """Ensure critical assets are still present"""
    critical_files = [
        'css/output.css',
        'core/img/logos/grove_icon.svg', 
        'js/alpine/hydro-ml-app.js'
    ]
    # Verification logic
    return all_exist
```

### Template Inheritance Verification
```python
# verify_templates.py  
def verify_template_inheritance():
    """Ensure all templates can still be rendered"""
    # Test template resolution
    # Check for circular dependencies
    # Verify all extends/includes resolve
    return success

def verify_css_loading():
    """Ensure all CSS files load correctly"""
    # Parse all templates for CSS references
    # Check files exist
    # Verify no circular imports
    return success
```

## 6. Monitoring and Alerting

### Post-Cleanup Monitoring (48 hours)
- [ ] **Error rate monitoring** via Sentry
- [ ] **Page load performance** tracking
- [ ] **User experience** feedback collection
- [ ] **Browser console errors** detection
- [ ] **404 requests** for removed files

### Alert Thresholds
- Error rate > 5% increase: Immediate rollback
- Page load time > 20% increase: Investigation required
- 404 requests for removed files: Immediate fix required
- JavaScript errors > baseline: Review and fix

## 7. Team Communication Protocol

### Before Each Phase
1. **Team notification** of planned cleanup
2. **Downtime warning** if applicable
3. **Rollback contact** assignment
4. **Testing assignment** distribution

### During Cleanup
1. **Status updates** every 30 minutes
2. **Issue escalation** path clear
3. **Rollback decision** authority assigned

### After Each Phase
1. **Success confirmation** to team
2. **Issue summary** if any occurred
3. **Next phase scheduling** coordination

## 8. Success Criteria and Exit Conditions

### Phase Completion Criteria
- [ ] All automated tests pass
- [ ] Manual UI regression tests pass
- [ ] No browser console errors
- [ ] Performance within acceptable range
- [ ] Team approval received

### Emergency Exit Conditions
- Test suite failure rate > 10%
- Critical functionality broken
- Performance degradation > 25%
- Production user impact detected

### Success Metrics Tracking
```bash
# Before and after comparison
echo "Phase completion metrics:" > cleanup-metrics.log
echo "Files removed: $REMOVED_COUNT" >> cleanup-metrics.log  
echo "Size reduction: $SIZE_REDUCTION" >> cleanup-metrics.log
echo "Test pass rate: $TEST_PASS_RATE" >> cleanup-metrics.log
echo "Performance impact: $PERF_IMPACT" >> cleanup-metrics.log
```

## 9. Implementation Commands

### Setup Safety Environment
```bash
# Initial setup
cd ../epic-project-cleanup-and-architecture
mkdir -p backups/phase{1,2,3}-individual
mkdir -p logs

# Safety scripts
chmod +x rollback_cleanup.sh
chmod +x verify_cleanup.sh

# Git hooks for safety
echo "#!/bin/bash" > .git/hooks/pre-commit  
echo "python verify_file_references.py" >> .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Daily Safety Check
```bash
#!/bin/bash
# daily_cleanup_check.sh
echo "$(date): Daily cleanup safety check" >> logs/daily-check.log

# Verify environment health
docker-compose exec web python -m pytest tests/unit/ -x --tb=short
echo "Tests status: $?" >> logs/daily-check.log

# Check for broken references
python verify_file_references.py >> logs/daily-check.log

# Performance check
curl -w "Load time: %{time_total}s\n" -o /dev/null -s http://localhost:8000/ >> logs/daily-check.log
```

---

**Protocol Version:** 1.0  
**Last Updated:** 2025-08-24  
**Review Required:** Before Phase 3 implementation  
**Contact:** Development Team Lead for emergency rollback authority