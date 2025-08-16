# HydroML - Comprehensive End-to-End Test Plan

**Version:** 1.0  
**Date:** August 16, 2025  
**Author:** Senior QA Engineer  
**Project:** HydroML Machine Learning Platform  

---

## Table of Contents

1. [Prerequisites & Setup](#prerequisites--setup)
2. [Test Suite A: User & Project Management](#test-suite-a-user--project-management)
3. [Test Suite B: Data Ingestion & Preparation (Data Studio)](#test-suite-b-data-ingestion--preparation-data-studio)
4. [Test Suite C: End-to-End Single ML Experiment](#test-suite-c-end-to-end-single-ml-experiment)
5. [Test Suite D: End-to-End Experiment Suite (Optuna)](#test-suite-d-end-to-end-experiment-suite-optuna)
6. [Test Suite E: Collaborative Features](#test-suite-e-collaborative-features)
7. [Test Suite F: General UI/UX](#test-suite-f-general-uiux)
8. [Test Environment Cleanup](#test-environment-cleanup)

---

## Prerequisites & Setup

### Environment Setup and Data Preparation

**Objective:** Establish a clean, consistent testing environment with high-quality sample data.

#### Setup Step 1: Start the Environment
**Action:** Execute the following command to start all services:
```bash
docker-compose up -d
```
**Expected Result:** 
- All Docker containers (web, db, redis, celery, mlflow) start successfully
- Services are accessible on their configured ports
- No error messages in the logs

#### Setup Step 2: Clean the Database
**Action:** Execute the database cleanup command:
```bash
docker-compose exec web python manage.py cleandb --confirm
```
**Expected Result:**
- All existing Projects, DataSources, MLExperiments, and ExperimentSuites are deleted
- User accounts remain intact (superuser preserved)
- Confirmation message shows counts of deleted objects
- Database is in a clean state

#### Setup Step 3: Seed with Sample Data
**Action:** Execute the database seeding command:
```bash
docker-compose exec web python manage.py seeddb
```
**Expected Result:**
- 4 diverse projects are created successfully:
  1. **"Análisis de Ventas de Supermercado"** with 2 related datasets:
     - `ventas.parquet` (sales transactions with product_id)
     - `productos.parquet` (product catalog with product_id)
  2. **"Estudio Clínico Fármaco X"** with clinical trial data
  3. **"Análisis Macroeconómico LATAM"** with economic indicators
  4. **"Predicción Energía Renovable"** with weather and energy data
- All datasets are saved as .parquet files in the media directory
- Corresponding DataSource objects are created in the database
- No errors during data generation or file creation

#### Setup Verification
**Action:** Access the HydroML dashboard at `http://localhost:8000`
**Expected Result:**
- Login page loads successfully
- After login, dashboard shows 4 sample projects
- Each project displays correct number of datasources
- All projects are accessible and properly formatted

---

## Test Suite A: User & Project Management

### Test Case A.1: User Login and Logout
**Action 1:** Navigate to `http://localhost:8000`  
**Expected Result:** Login page displays with username/password fields

**Action 2:** Enter valid superuser credentials and click "Login"  
**Expected Result:** 
- Successful authentication
- Redirect to main dashboard/workspace
- User menu displays logged-in username

**Action 3:** Click on user menu and select "Logout"  
**Expected Result:**
- User is logged out successfully
- Redirect to login page
- No access to protected pages without re-authentication

### Test Case A.2: Create a New Project from Dashboard
**Action 1:** From the main dashboard, click "Crear Nuevo Proyecto" or similar button  
**Expected Result:** Project creation form appears (slide-over panel or new page)

**Action 2:** Fill in project details:
- Name: "Test Project QA"
- Description: "Project created during QA testing"  
**Expected Result:** Form accepts input, no validation errors

**Action 3:** Submit the form  
**Expected Result:**
- Project is created successfully
- Redirect to project detail page
- Success message confirms creation
- Project appears in the dashboard project list

### Test Case A.3: Dashboard Statistics and Recent Activity
**Action 1:** Navigate to the main dashboard  
**Expected Result:**
- Dashboard loads without errors
- Statistics section shows correct counts:
  - Total Projects: 5 (4 seeded + 1 created in A.2)
  - Recent activity log displays latest actions
  - Quick access cards for main features are visible

**Action 2:** Verify project cards display  
**Expected Result:**
- All 5 projects are visible as cards
- Each card shows project name, description, creation date
- DataSource counts are accurate for each project
- Click actions (view, edit) are functional

---

## Test Suite B: Data Ingestion & Preparation (Data Studio)

### Test Case B.1: Upload a New DataSource
**Action 1:** Navigate to any project (e.g., "Test Project QA")  
**Expected Result:** Project detail page loads with datasources section

**Action 2:** Click "Add DataSource" or upload button  
**Expected Result:** DataSource upload slide-over panel opens

**Action 3:** Upload a CSV file:
- Name: "Test Upload Dataset"
- Description: "CSV uploaded during QA testing"
- File: Any valid CSV file with numerical data  
**Expected Result:**
- File uploads successfully
- Processing status updates appear
- DataSource is converted to .parquet format
- New DataSource appears in project with "READY" status

### Test Case B.2: Data Quality Report Generation
**Action 1:** Navigate to a project with existing datasources (e.g., "Análisis de Ventas de Supermercado")  
**Expected Result:** Project shows datasources list

**Action 2:** Click on a DataSource to view details  
**Expected Result:** DataSource detail page loads

**Action 3:** Locate and access the Data Quality Report  
**Expected Result:**
- Quality report link/button is visible and clickable
- Report shows data profiling information:
  - Column types and statistics
  - Missing value counts
  - Distribution summaries
  - Data quality scores

### Test Case B.3: Data Studio AG Grid Functionality
**Action 1:** From a DataSource detail page, click "Open in Data Studio"  
**Expected Result:** Data Studio interface loads

**Action 2:** Verify AG Grid data loading  
**Expected Result:**
- AG Grid component displays the data correctly
- Column headers match the dataset schema
- Data pagination works (if dataset is large)
- Sorting and filtering controls are functional
- Row selection works properly

### Test Case B.4: Interactive Charts (Plotly)
**Action 1:** In the Data Studio, locate the chart/visualization section  
**Expected Result:** Chart controls and visualization area are visible

**Action 2:** Select a numerical column for visualization  
**Expected Result:**
- Dropdown/selector shows available numerical columns
- Column selection updates the visualization
- Plotly chart renders correctly (histogram, box plot, etc.)

**Action 3:** Try different chart types or configurations  
**Expected Result:**
- Chart updates dynamically based on selections
- Interactive features (zoom, hover, pan) work properly
- Chart is responsive and well-formatted

### Test Case B.5: Data Fusion Feature
**Action 1:** Navigate to the "Análisis de Ventas de Supermercado" project  
**Expected Result:** Project detail page shows the two related datasets:
- "ventas.parquet" (sales transactions)
- "productos.parquet" (product catalog)

**Action 2:** Access the "Data Fusion" tool/page  
**Expected Result:** Data Fusion interface loads with datasource selection options

**Action 3:** Configure the fusion:
- DataSource A: Select "ventas.parquet"
- DataSource B: Select "productos.parquet"  
**Expected Result:** Both datasources load successfully, column lists are populated

**Action 4:** Set up the join configuration:
- Select `producto_id` as the common column (join key) for the merge
- Configure join type (inner, left, right, outer)  
**Expected Result:**
- Join key dropdown shows matching columns from both datasets
- `producto_id` is available in both datasource column lists
- Join configuration is accepted

**Action 5:** Execute the fusion  
**Expected Result:**
- Fusion process starts without errors
- Progress indicators show the operation status
- A new "Fused" DataSource is created with status "READY"

**Action 6:** Verify the fused dataset  
**Expected Result:**
- Opening the new fused DataSource in Data Studio shows:
  - Combined columns from both original files
  - Data includes: `fecha`, `cantidad`, `precio_unitario` from sales
  - Data includes: `nombre_producto`, `categoria`, `marca` from products
  - Join was executed correctly with `producto_id` as the key
  - Row count matches expected join results

---

## Test Suite C: End-to-End Single ML Experiment

### Test Case C.1: Create MLExperiment with Time Series Cross-Validation
**Action 1:** Navigate to a project with suitable time series data (e.g., "Predicción Energía Renovable")  
**Expected Result:** Project detail page loads with available datasources

**Action 2:** Click "Create New Experiment" or similar button  
**Expected Result:** ML Experiment creation form loads

**Action 3:** Configure the experiment:
- Name: "Energy Generation Prediction Test"
- DataSource: Select "generacion_energia_renovable.parquet"
- Target Column: Select "generacion_total_renovable_mwh"
- Model: Choose "RandomForestRegressor"
- Validation Strategy: Select "Time Series Cross-Validation"
- Configure hyperparameters (n_estimators, max_depth)  
**Expected Result:**
- Form accepts all configurations
- Target column dropdown shows numerical columns
- Validation strategy option is available
- Hyperparameter fields appear based on model selection

**Action 4:** Submit the experiment configuration  
**Expected Result:**
- Experiment is created with "DRAFT" status
- Redirect to experiment detail page
- Configuration summary is displayed correctly

### Test Case C.2: Run the Experiment
**Action 1:** From the experiment detail page, click "Run Experiment"  
**Expected Result:**
- Experiment status changes to "RUNNING"
- Progress indicators or messages appear
- Celery task is triggered successfully

**Action 2:** Monitor execution progress  
**Expected Result:**
- Status updates reflect the current phase:
  - Data loading and preprocessing
  - Model training with time series CV
  - Evaluation and metrics calculation
- No error messages during execution

**Action 3:** Wait for completion  
**Expected Result:**
- Experiment status changes to "COMPLETED"
- Execution time is recorded
- Success message confirms completion

### Test Case C.3: Verify Results Display
**Action 1:** Review the experiment results section  
**Expected Result:**
- Metrics are displayed clearly:
  - R² Score, RMSE, MAE
  - Cross-validation scores
  - Train vs. validation performance

**Action 2:** Check visualization outputs  
**Expected Result:**
- Prediction vs. actual scatter plot is generated
- Residuals plot shows model performance
- Feature importance chart displays key variables
- Time series plots show predictions over time

**Action 3:** Verify SHAP plot generation  
**Expected Result:**
- SHAP feature importance plot is created
- Interactive SHAP visualizations load properly
- Plots provide interpretable insights into model decisions

### Test Case C.4: MLflow Integration Verification
**Action 1:** Locate the MLflow link in the experiment results  
**Expected Result:** MLflow tracking URL is visible and properly formatted

**Action 2:** Click the MLflow link  
**Expected Result:**
- MLflow UI opens in a new tab/window
- Experiment run is visible in the MLflow interface
- Parameters, metrics, and artifacts are logged correctly

**Action 3:** Verify artifact storage  
**Expected Result:**
- Trained model files are stored in MLflow
- Plots and charts are saved as artifacts
- All experiment metadata is properly tracked

---

## Test Suite D: End-to-End Experiment Suite (Optuna)

### Test Case D.1: Create Hyperparameter Optimization Suite
**Action 1:** Navigate to a project and access Experiment Suites section  
**Expected Result:** Suite management interface loads

**Action 2:** Click "Create New Suite" or similar button  
**Expected Result:** ExperimentSuite creation form appears

**Action 3:** Configure the suite:
- Name: "Hyperparameter Optimization Test Suite"
- Study Type: Select "Hyperparameter Optimization"
- Base DataSource: Choose a suitable dataset
- Target Column: Select numerical target
- Models to test: Choose multiple algorithms
- Optimization metric: Select "r2_score"
- Number of trials: Set to 20  
**Expected Result:**
- Form accepts all configurations
- Search space parameters are configured
- Optimization settings are properly set

### Test Case D.2: Run the Suite
**Action 1:** Submit the suite configuration  
**Expected Result:**
- Suite is created with "DRAFT" status
- Redirect to suite detail page

**Action 2:** Click "Run Suite" to start optimization  
**Expected Result:**
- Suite status changes to "RUNNING"
- Optuna study initialization confirms
- Progress tracking begins

**Action 3:** Monitor suite execution  
**Expected Result:**
- Trial progress updates are visible
- Individual experiments are created automatically
- Real-time optimization metrics are displayed

### Test Case D.3: Verify Child Experiments Creation
**Action 1:** Check the associated experiments list  
**Expected Result:**
- Multiple child experiments are created (up to 20 based on trial count)
- Each experiment has unique hyperparameter combinations
- Experiment statuses progress from "DRAFT" to "RUNNING" to "COMPLETED"

**Action 2:** Inspect individual child experiments  
**Expected Result:**
- Each child experiment has complete results
- Hyperparameters differ between experiments
- Performance metrics are properly recorded

### Test Case D.4: Suite Results Dashboard
**Action 1:** Navigate to the Suite Detail Page after completion  
**Expected Result:**
- Suite status shows "COMPLETED"
- Overall optimization results are displayed

**Action 2:** Review optimization visualization  
**Expected Result:**
- Optuna visualization components load:
  - Optimization history plot
  - Parameter importance chart
  - Parallel coordinate plot
  - Parameter relationships visualization

**Action 3:** Verify best trial identification  
**Expected Result:**
- Best performing trial is highlighted
- Best hyperparameters are clearly displayed
- Performance improvement over baseline is shown

---

## Test Suite E: Collaborative Features

### Test Case E.1: Publish an Experiment
**Action 1:** Navigate to a completed experiment with good results  
**Expected Result:** Experiment detail page shows "COMPLETED" status

**Action 2:** Locate and click "Publish Experiment" button  
**Expected Result:**
- Publish confirmation dialog appears
- Option to add publication notes/description

**Action 3:** Confirm publication  
**Expected Result:**
- Experiment `is_public` status changes to True
- `published_at` timestamp is recorded
- Success message confirms publication
- Experiment becomes visible to other users

### Test Case E.2: Public Experiments Gallery
**Action 1:** Navigate to "Experimentos Públicos" or "Public Experiments" section  
**Expected Result:** Public experiments gallery page loads

**Action 2:** Verify published experiment visibility  
**Expected Result:**
- Recently published experiment appears in the gallery
- Experiment card shows:
  - Name, description, and model type
  - Performance metrics summary
  - Publication date and author
  - View/Fork action buttons

**Action 3:** Browse and filter public experiments  
**Expected Result:**
- Gallery supports filtering by model type, performance, date
- Search functionality works for experiment names
- Pagination works for large numbers of public experiments

### Test Case E.3: Fork a Public Experiment
**Action 1:** From the public experiments gallery, select an experiment  
**Expected Result:** Public experiment detail view loads (read-only)

**Action 2:** Click "Fork Experiment" button  
**Expected Result:**
- Fork confirmation dialog appears
- Option to select target project for the fork

**Action 3:** Configure and confirm the fork:
- Target Project: Select an existing project or create new
- New Name: "Forked: [Original Name]"  
**Expected Result:**
- Fork process starts successfully
- Progress indicators show copy operation

**Action 4:** Verify the forked experiment  
**Expected Result:**
- New experiment is created in the target project
- All configuration is copied from original
- Status is set to "DRAFT" (ready for modification)
- `forked_from` relationship is established
- User can now modify and re-run the forked experiment

---

## Test Suite F: General UI/UX

### Test Case F.1: Dark/Light Mode Switcher
**Action 1:** Locate the theme switcher in the UI (usually in header/navbar)  
**Expected Result:** Theme toggle button/switch is visible

**Action 2:** Click to switch from current theme to alternate  
**Expected Result:**
- Theme changes immediately without page reload
- All UI elements adapt to new color scheme
- Text contrast remains readable
- Charts and visualizations update theme appropriately

**Action 3:** Switch back to original theme  
**Expected Result:**
- Theme preference is maintained
- All components return to original appearance
- No broken styling or layout issues

### Test Case F.2: Collapsible Sidebar Navigation
**Action 1:** Locate the sidebar navigation menu  
**Expected Result:** Sidebar is visible with navigation items

**Action 2:** Test hover interactions  
**Expected Result:**
- Hovering over collapsed sidebar shows tooltips/labels
- Hover states provide visual feedback
- Navigation items are clearly identifiable

**Action 3:** Test pin/unpin functionality  
**Expected Result:**
- Pin button allows locking sidebar in expanded state
- Unpin allows auto-collapse behavior
- User preference is maintained across page navigation

### Test Case F.3: Breadcrumb Navigation
**Action 1:** Navigate deep into the application hierarchy:
- Dashboard → Project → DataSource → Data Studio  
**Expected Result:** Breadcrumb trail updates at each level

**Action 2:** Verify breadcrumb functionality  
**Expected Result:**
- Each breadcrumb level is clickable
- Clicking navigates to the appropriate parent level
- Current page is highlighted in breadcrumb
- Breadcrumb accurately reflects navigation path

**Action 3:** Test breadcrumb from experiment flows:
- Dashboard → Project → Experiment → Results  
**Expected Result:**
- Experiment-specific breadcrumbs work correctly
- Suite → Individual Experiment navigation is clear
- Context is maintained throughout navigation

---

## Test Environment Cleanup

### Post-Testing Cleanup
After completing all test suites, optionally clean the test environment:

**Action:** Execute cleanup command:
```bash
docker-compose exec web python manage.py cleandb --confirm
```
**Expected Result:** All test data is removed, system returns to clean state

**Action:** Stop services:
```bash
docker-compose down
```
**Expected Result:** All containers are stopped and removed

---

## Test Execution Notes

### Critical Success Criteria
- All user authentication flows work correctly
- Data upload, processing, and fusion operate without errors  
- ML experiments execute successfully with proper result visualization
- Optuna integration creates and optimizes multiple experiments
- Collaborative features (publish/fork) maintain data integrity
- UI/UX elements are responsive and function across browsers

### Known Dependencies
- Docker environment must be running and healthy
- Sufficient disk space for datasets and model artifacts
- Network connectivity for MLflow integration
- Modern browser with JavaScript enabled

### Reporting
Document any failures with:
- Exact steps to reproduce
- Expected vs. actual results
- Browser and environment details
- Screenshots of any UI issues
- Console errors or log output

---

**End of Test Plan**
