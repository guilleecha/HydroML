# HydroML Application - Comprehensive QA Test Plan

## 📋 Test Plan Overview

This document provides a detailed test plan to verify the functionality of all major forms and UI components in the HydroML application. The test plan is designed to ensure comprehensive coverage of user interactions, form validations, and UI/UX functionality.

---

## 🔧 Prerequisites

### Environment Setup

**⚠️ CRITICAL FIRST STEP: Start the Development Environment**

Before executing any test cases, the entire Docker environment must be started:

**Action:**
```bash
docker-compose up -d
```

**Expected Result:**
- All services (web, db, redis, mlflow, worker) are running successfully
- Web application is accessible at `http://localhost:8000`
- MLflow server is accessible at `http://localhost:5000`
- No container errors in `docker-compose ps` output

**Verification:**
1. Run `docker-compose ps` to confirm all 5 containers are in "Up" status
2. Access `http://localhost:8000` and verify the application loads
3. Check that you can see the HydroML login/dashboard page

---

## 🧪 Test Cases

### Test Suite A: "New Project" Form

**Test Case A.1: Valid Project Creation**

**Objective:** Verify that users can successfully create a new project with valid data

**Prerequisites:**
- User must be logged in to the application
- Access to the dashboard or projects page

**Test Steps:**
1. Navigate to the main dashboard (`http://localhost:8000`)
2. Locate and click the "Nuevo Proyecto" or "Create Project" button
3. Fill in the project form with the following valid data:
   - **Project Name:** "Test Project QA 2025"
   - **Description:** "This is a test project for QA validation purposes"
4. Click "Save" or "Crear" button

**Expected Results:**
- ✅ Form accepts the valid input
- ✅ Project is created successfully
- ✅ User is redirected to the project detail page
- ✅ Success message is displayed
- ✅ New project appears in the projects list

**Test Case A.2: Invalid Project Creation (Blank Name)**

**Test Steps:**
1. Navigate to the project creation form
2. Leave the **Project Name** field blank
3. Fill in **Description:** "Test description"
4. Attempt to submit the form

**Expected Results:**
- ❌ Form submission is prevented
- ❌ Validation error message appears for the name field
- ❌ Form remains open with error indicators
- ❌ No project is created in the database

---

### Test Suite B: "Upload DataSource" Slide-Over Panel

**Test Case B.1: Valid File Upload**

**Objective:** Verify that users can successfully upload a data file to a project

**Prerequisites:**
- A project must exist and be accessible
- Test CSV file available (create a simple CSV with headers: name,age,salary)

**Test Steps:**
1. Navigate to a project detail page
2. Locate and click the "Subir Datos" or "Upload Data" button
3. Verify the slide-over panel opens from the right side
4. Click the file selector or drag-and-drop area
5. Select a valid CSV file (e.g., `test_data.csv`)
6. Optionally fill in a custom name for the datasource
7. Click "Upload" or "Subir" button

**Expected Results:**
- ✅ Slide-over panel opens smoothly
- ✅ File selection interface works properly
- ✅ Valid file is accepted
- ✅ Upload progress indicator appears
- ✅ Success message is displayed
- ✅ Panel closes automatically after successful upload
- ✅ New datasource appears in the project's data sources list
- ✅ Datasource shows "processing" status initially

**Test Case B.2: Invalid Upload (No File Selected)**

**Test Steps:**
1. Open the "Subir Datos" slide-over panel
2. Leave the file input empty
3. Attempt to submit the form

**Expected Results:**
- ❌ Form validation prevents submission
- ❌ Error message indicates file is required
- ❌ Panel remains open with error state
- ❌ No datasource is created

---

### Test Suite C: "New Experiment" Slide-Over Panel (HIGH PRIORITY)

**Test Case C.1: Panel Opening Functionality**

**Objective:** Verify the experiment creation panel opens correctly

**Prerequisites:**
- Project with at least one datasource exists

**Test Steps:**
1. Navigate to a project detail page
2. Locate and click the "Nuevo Experimento ML" or "New ML Experiment" button
3. Observe the slide-over panel behavior

**Expected Results:**
- ✅ Slide-over panel opens from the right side
- ✅ Panel contains all necessary form fields
- ✅ Form loads without JavaScript errors
- ✅ All UI elements are properly styled and visible

**Test Case C.2: Dynamic Fields - DataSource Selection**

**Objective:** Verify that selecting a datasource populates related fields

**Test Steps:**
1. Open the "Nuevo Experimento ML" panel
2. Locate the "DataSource" dropdown field
3. Select an available datasource from the dropdown
4. Observe the target column selector and feature selectors

**Expected Results:**
- ✅ DataSource dropdown contains project's datasources
- ✅ After selecting a datasource, target column dropdown is populated with column names
- ✅ Feature selection area shows available columns
- ✅ Dynamic loading works without page refresh

**Test Case C.3: Dynamic Fields - Hyperparameter Preset Loading**

**Objective:** Verify that selecting a hyperparameter preset fills form fields

**Prerequisites:**
- At least one hyperparameter preset exists for the user

**Test Steps:**
1. In the experiment form, locate the "Hyperparameter Preset" dropdown
2. Select an available preset
3. Observe the hyperparameter form fields

**Expected Results:**
- ✅ Preset dropdown shows available presets
- ✅ Selecting a preset automatically fills hyperparameter fields
- ✅ Fields are populated with correct values from the preset
- ✅ User can still manually modify the auto-filled values

**Test Case C.4: Valid Experiment Submission**

**Objective:** Verify that a complete, valid experiment can be created

**Test Steps:**
1. Open the experiment creation panel
2. Fill in all required fields:
   - **Experiment Name:** "QA Test Experiment"
   - **Description:** "Test experiment for QA validation"
   - **DataSource:** Select available datasource
   - **Target Column:** Select a numeric column
   - **Model Type:** Select "RandomForestRegressor"
   - **Features:** Select at least 2 feature columns
   - **Test Split:** 0.2
   - **Random State:** 42
3. Add tags (optional): "test", "qa"
4. Click "Create Experiment" button

**Expected Results:**
- ✅ All form validations pass
- ✅ Experiment is created successfully
- ✅ Success message appears
- ✅ Panel closes after successful creation
- ✅ User is redirected to experiment detail page or project page
- ✅ New experiment appears in experiments list

**Test Case C.5: Invalid Experiment Submission (Missing Required Field)**

**Objective:** Verify proper validation when required fields are missing

**Test Steps:**
1. Open the experiment creation panel
2. Fill in most fields but deliberately leave **Target Column** unselected
3. Attempt to submit the form

**Expected Results:**
- ❌ Form validation prevents submission
- ❌ Inline error message appears near the Target Column field
- ❌ Panel remains open to allow corrections
- ❌ No experiment is created
- ❌ Error styling is applied to invalid fields

---

### Test Suite D: "User Settings" Form

**Test Case D.1: Profile Update**

**Objective:** Verify that users can update their profile information

**Prerequisites:**
- User must be logged in

**Test Steps:**
1. Navigate to the user settings page (usually via user menu or `/settings/`)
2. Locate the "Profile" or "Perfil" section
3. Update the following fields:
   - **First Name:** "QA"
   - **Last Name:** "Tester"
   - **Email:** (keep existing or update to valid email)
4. Click "Save" or "Guardar" button

**Expected Results:**
- ✅ Form accepts the valid input
- ✅ Settings are saved successfully
- ✅ Success message appears ("Your profile has been updated successfully")
- ✅ Page reloads or updates to show new values
- ✅ Changes persist after page refresh

**Test Case D.2: Invalid Profile Update**

**Test Steps:**
1. Navigate to user settings
2. Update the **Email** field to an invalid format: "invalid-email"
3. Attempt to save the form

**Expected Results:**
- ❌ Form validation catches invalid email format
- ❌ Error message appears for email field
- ❌ Settings are not saved
- ❌ User remains on the settings page with error indicators

---

### Test Suite E: General UI/UX Verification

**Test Case E.1: Dark/Light Mode Toggling**

**Objective:** Verify that the theme switcher works correctly

**Test Steps:**
1. Locate the theme toggle button in the application header (sun/moon icon)
2. Note the current theme (observe background colors, text colors)
3. Click the theme toggle button
4. Observe the visual changes
5. Refresh the page (`F5` or `Ctrl+R`)
6. Verify the theme persists after refresh
7. Toggle the theme again to test bidirectional switching

**Expected Results:**
- ✅ Theme toggle button is visible in the header
- ✅ Clicking the button instantly changes the theme
- ✅ All UI elements switch between light and dark themes
- ✅ Icon changes between sun (light mode) and moon (dark mode)
- ✅ Theme choice persists after page reload
- ✅ Smooth visual transition occurs
- ✅ All text remains readable in both modes

**Test Case E.2: Sidebar Functionality**

**Objective:** Verify that the sidebar hover and pin functionality works

**Test Steps:**
1. **Desktop Test:** Ensure browser window is wide enough to show sidebar (>1024px)
2. **Hover Test:** Move mouse over the collapsed sidebar
3. Verify sidebar expands on hover
4. Move mouse away from sidebar
5. Verify sidebar collapses again
6. **Pin Test:** Hover over sidebar to expand it
7. Locate and click the "pin" icon (usually a bookmark/pin symbol)
8. Move mouse away from sidebar
9. Verify sidebar remains expanded
10. Click the pin icon again to unpin

**Expected Results:**
- ✅ Sidebar starts in collapsed state (narrow strip on left)
- ✅ Hovering expands sidebar to full width
- ✅ Moving mouse away collapses sidebar
- ✅ Pin icon is visible when sidebar is expanded
- ✅ Clicking pin keeps sidebar expanded permanently
- ✅ Pinned state persists when mouse moves away
- ✅ Unpinning returns to hover behavior
- ✅ Smooth animations during expand/collapse

**Test Case E.3: Breadcrumb Navigation**

**Objective:** Verify that breadcrumb navigation accurately reflects the current page location

**Test Steps:**
1. Navigate to the main dashboard
2. Click on a project to view project details
3. Observe the breadcrumb trail in the header
4. From the project page, navigate to an experiment detail page
5. Observe the updated breadcrumb trail
6. Click on an intermediate breadcrumb link (e.g., the project name)
7. Verify navigation works correctly

**Expected Results:**
- ✅ Breadcrumbs appear in the header area
- ✅ Initial page shows appropriate breadcrumb
- ✅ Navigating to project shows: "Projects > [Project Name]"
- ✅ Navigating to experiment shows: "Projects > [Project Name] > [Experiment Name]"
- ✅ Each breadcrumb level is clickable (except the current page)
- ✅ Clicking breadcrumb links navigates to the correct page
- ✅ Current page is highlighted/styled differently
- ✅ Breadcrumbs accurately reflect the navigation hierarchy

---

## 🎯 Test Execution Guidelines

### Testing Environment Requirements

1. **Browser Compatibility:**
   - Primary: Chrome/Chromium (latest)
   - Secondary: Firefox (latest)
   - Tertiary: Safari (if on macOS)

2. **Screen Resolution Testing:**
   - Desktop: 1920x1080 (primary)
   - Tablet: 768x1024
   - Mobile: 390x844 (iPhone 12 Pro size)

3. **Network Conditions:**
   - Test on normal network speeds
   - Test with slower connections to verify loading states

### Critical Success Criteria

For the test plan to be considered successful, the following must pass:

**🔴 Critical (Must Pass):**
- All form submissions with valid data succeed
- All form validations catch invalid data appropriately
- No JavaScript console errors during normal operation
- User authentication and session management works

**🟡 Important (Should Pass):**
- UI transitions and animations work smoothly
- Theme switching persists across sessions
- Sidebar functionality works as expected
- Breadcrumb navigation is accurate

**🟢 Nice-to-Have:**
- Loading indicators appear during data processing
- Error messages are user-friendly and informative
- Responsive design works on all screen sizes

### Defect Reporting

When issues are found, report them with:

1. **Test Case Reference:** (e.g., "Test Case C.3")
2. **Browser/OS:** (e.g., "Chrome 120 on Windows 11")
3. **Steps to Reproduce:** Clear, numbered steps
4. **Expected vs. Actual Result:** What should happen vs. what actually happened
5. **Screenshots/Video:** Visual evidence when applicable
6. **Console Errors:** Any JavaScript errors from browser dev tools

### Test Data Requirements

**For Datasource Upload Testing:**
Create a test CSV file named `test_data.csv`:
```csv
name,age,salary,department,years_experience
John Doe,25,50000,Engineering,3
Jane Smith,30,65000,Marketing,5
Bob Johnson,35,75000,Engineering,8
Alice Brown,28,55000,Sales,4
```

**For Experiment Testing:**
- Ensure numeric columns for target selection (age, salary, years_experience)
- Ensure categorical columns for features (department)
- Mixed data types to test form validation

---

## 📊 Test Results Summary Template

Use this template to document test execution results:

| Test Case | Status | Notes | Reporter | Date |
|-----------|--------|--------|----------|------|
| A.1 - Valid Project Creation | ✅ PASS | | | |
| A.2 - Invalid Project Creation | ✅ PASS | | | |
| B.1 - Valid File Upload | ✅ PASS | | | |
| B.2 - Invalid Upload | ✅ PASS | | | |
| C.1 - Panel Opening | ✅ PASS | | | |
| C.2 - DataSource Selection | ✅ PASS | | | |
| C.3 - Preset Loading | ✅ PASS | | | |
| C.4 - Valid Experiment | ✅ PASS | | | |
| C.5 - Invalid Experiment | ✅ PASS | | | |
| D.1 - Profile Update | ✅ PASS | | | |
| D.2 - Invalid Profile | ✅ PASS | | | |
| E.1 - Theme Toggling | ✅ PASS | | | |
| E.2 - Sidebar Functionality | ✅ PASS | | | |
| E.3 - Breadcrumb Navigation | ✅ PASS | | | |

**Legend:**
- ✅ PASS: Test completed successfully
- ❌ FAIL: Test failed, defect identified
- ⚠️ PARTIAL: Test partially passed with minor issues
- 🔄 BLOCKED: Test cannot be completed due to environment issues

---

**End of Test Plan**

*This test plan should be executed in its entirety before any major release or deployment. All critical test cases must pass before the application can be considered production-ready.*
