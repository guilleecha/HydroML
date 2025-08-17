# QA Testing Quick Start Guide

## 🚀 Quick Environment Check

Before starting the QA test plan, perform these quick manual checks:

### 1. Container Status Check
```bash
docker-compose ps
```
**Expected:** All 5 containers (web, db, redis, mlflow, worker) should show "Up" status

### 2. Web Application Check
- Open browser and navigate to: `http://localhost:8000`
- **Expected:** HydroML application loads without errors

### 3. MLflow Server Check  
- Open browser and navigate to: `http://localhost:5000`
- **Expected:** MLflow UI loads showing experiments dashboard

### 4. Test Data Availability
- **File:** `test_data.csv` should exist in the project root
- **Content:** Contains sample data for upload testing

---

## 🎯 Priority Test Execution Order

Execute the test cases in this recommended order:

### Phase 1: Critical Functionality (Must Pass)
1. **Test Case A.1** - Valid Project Creation
2. **Test Case B.1** - Valid File Upload  
3. **Test Case C.1** - Experiment Panel Opening
4. **Test Case C.4** - Valid Experiment Submission

### Phase 2: Validation Testing (Should Pass)
1. **Test Case A.2** - Invalid Project Creation
2. **Test Case B.2** - Invalid File Upload
3. **Test Case C.5** - Invalid Experiment Submission
4. **Test Case D.2** - Invalid Profile Update

### Phase 3: Dynamic Features (Important)
1. **Test Case C.2** - DataSource Selection Dynamic Fields
2. **Test Case C.3** - Hyperparameter Preset Loading
3. **Test Case D.1** - Profile Update

### Phase 4: UI/UX Features (Nice-to-Have)
1. **Test Case E.1** - Dark/Light Mode Toggling
2. **Test Case E.2** - Sidebar Functionality
3. **Test Case E.3** - Breadcrumb Navigation

---

## 📝 Test Credentials

For testing purposes, you can either:

1. **Create a new test user:**
   - Navigate to the signup page
   - Create account: `qa_tester@hydroml.com`
   - Password: `TestPass123!`

2. **Use existing superuser (if available):**
   - Check if admin credentials are set up
   - Access via Django admin if needed

---

## 🔧 Common Issues & Solutions

### Issue: Containers not starting
**Solution:**
```bash
docker-compose down
docker-compose up -d
# Wait 2-3 minutes for full startup
```

### Issue: Web app shows 500 error
**Solution:**
```bash
# Check database migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### Issue: MLflow not accessible
**Solution:**
- Check if port 5000 is free
- Restart MLflow container: `docker-compose restart mlflow`

---

## 📊 Test Result Documentation

Use this template for each test case:

```
Test Case: [ID - Name]
Date: [Current Date]
Tester: [Your Name]
Status: [PASS/FAIL/PARTIAL/BLOCKED]
Browser: [Chrome/Firefox/Safari + Version]
Notes: [Any observations or issues]
Screenshots: [If applicable]
```

---

## 🎯 Success Criteria

**Ready for Production if:**
- ✅ All Phase 1 tests PASS
- ✅ At least 80% of Phase 2 tests PASS  
- ✅ No critical JavaScript errors in browser console
- ✅ Theme switching works correctly
- ✅ All form validations work as expected

**Additional Requirements:**
- Responsive design works on mobile (test at 375px width)
- Page load times are reasonable (< 3 seconds)
- Error messages are user-friendly

---

**Happy Testing! 🧪**
