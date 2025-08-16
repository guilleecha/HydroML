# Test Case Document: End-to-End MLflow Integration

## Test Case Information

**Test Case ID:** TC_E2E_001  
**Title:** End-to-End MLflow Integration with HydroML Experiment Pipeline  
**Test Type:** Integration Test  
**Priority:** High  
**Created Date:** August 15, 2025  
**Version:** 1.0  

## Test Objective

Verify that the complete ML experiment workflow integrates correctly with MLflow tracking, ensuring dual persistence (Django database + MLflow) and proper visualization of results in both HydroML and MLflow UIs.

## Prerequisites

### Environment Setup
- [ ] Docker and docker-compose installed and running
- [ ] HydroML development environment accessible at `http://localhost:8000`
- [ ] MLflow tracking server accessible at `http://localhost:5000`
- [ ] All containerized services running via `docker-compose up`

### Data Prerequisites
- [ ] At least one Project exists in the system
- [ ] At least one DataSource is available for the project
- [ ] DataSource contains valid data with numeric columns suitable for ML training
- [ ] User has appropriate permissions to create and run experiments

### Service Verification
- [ ] Django web server responding (port 8000)
- [ ] Celery worker connected and processing tasks
- [ ] PostgreSQL database accessible
- [ ] Redis message broker operational
- [ ] MLflow tracking server initialized

## Test Steps

| Step # | Action | Expected Result |
|--------|--------|-----------------|
| **1** | Navigate to `http://localhost:8000` in web browser | HydroML homepage loads successfully without errors |
| **2** | Login with valid credentials (if authentication required) | User successfully authenticated and redirected to dashboard |
| **3** | Navigate to Projects section and select an existing project | Project detail page displays with available DataSources and Experiments sections |
| **4** | Click "Create New Experiment" or navigate to experiment creation page | Experiment creation form loads with all required fields visible |
| **5** | Fill out experiment form with following data:<br/>- **Name:** "E2E Test Experiment [timestamp]"<br/>- **Input DataSource:** Select available datasource<br/>- **Target Column:** Select numeric column from datasource<br/>- **Model Name:** "RandomForestRegressor"<br/>- **Test Size:** 0.2<br/>- **Random State:** 42 | Form accepts all inputs without validation errors |
| **6** | Click "Save" or "Create Experiment" button | Experiment created successfully, redirected to experiment detail page with status "DRAFT" |
| **7** | Verify experiment detail page displays correctly | Page shows:<br/>- Experiment metadata (name, model, parameters)<br/>- Status: "DRAFT"<br/>- "Run Experiment" button is visible and enabled<br/>- No results section yet |
| **8** | Click "Run Experiment" button | Button becomes disabled, page shows status change to "RUNNING", success message displayed |
| **9** | Monitor experiment status by refreshing page every 30 seconds | Status progresses through: RUNNING → FINISHED (or remains RUNNING until completion) |
| **10** | Open new browser tab and navigate to `http://localhost:5000` | MLflow UI loads successfully |
| **11** | In MLflow UI, verify new experiment run appears | New run visible in experiments list with:<br/>- Status: "RUNNING" or "FINISHED"<br/>- Start time matching HydroML experiment<br/>- Parameters section populated |
| **12** | Click on the MLflow run to view details | Run detail page shows:<br/>- **Parameters:** model_name, test_size, random_state<br/>- **Metrics:** Being populated during training<br/>- **Tags:** experiment_id, project_id |
| **13** | Return to HydroML experiment detail page and wait for completion | Final status shows "FINISHED" within reasonable time (< 5 minutes for small dataset) |
| **14** | Verify HydroML results section displays | Results section shows:<br/>- **Performance Metrics:** MSE, MAE, R² with numeric values<br/>- **Interactive Chart:** Scatter plot of actual vs predicted values<br/>- **MLflow Integration:** Run ID displayed with clickable link |
| **15** | Click MLflow Run ID link in HydroML | Opens MLflow run detail page in new tab/window |
| **16** | In MLflow run detail, verify final state | Run shows:<br/>- **Status:** "FINISHED"<br/>- **Metrics:** mse, mae, r2_score with values matching HydroML<br/>- **Artifacts:** "model" artifact present and downloadable<br/>- **Duration:** Reasonable execution time logged |
| **17** | Download model artifact from MLflow | Model file downloads successfully (pickle format) |
| **18** | Verify data consistency between systems | Compare metrics values between HydroML and MLflow - they should match exactly |
| **19** | Create second experiment with different parameters | Verify MLflow creates separate run and both systems maintain independent tracking |
| **20** | Test error handling by creating experiment with invalid target column | System gracefully handles error, shows appropriate message, MLflow run marked as failed |

## Expected Final State

### HydroML System
- Experiment status: `FINISHED`
- Results section populated with metrics and visualization
- MLflow run ID displayed and functional
- Database contains complete experiment record

### MLflow System
- Run status: `FINISHED`
- All parameters logged correctly
- All metrics logged with matching values
- Model artifact stored and accessible
- Run linked to HydroML experiment via tags

## Pass/Fail Criteria

### Pass Criteria
- [ ] All test steps execute without critical errors
- [ ] Experiment completes successfully in both systems
- [ ] Metrics values match between HydroML and MLflow
- [ ] MLflow run ID correctly links systems
- [ ] Model artifact is stored and accessible
- [ ] UI displays are functional and user-friendly

### Fail Criteria
- [ ] Experiment fails to start or complete
- [ ] Critical errors in either UI
- [ ] Metrics mismatch between systems
- [ ] MLflow integration not working
- [ ] Data corruption or loss
- [ ] Performance degradation beyond acceptable limits

## Test Data Cleanup

After test completion:
1. Delete test experiment from HydroML UI
2. Archive or delete MLflow runs if needed
3. Verify no orphaned data remains
4. Reset system to clean state for subsequent tests

## Notes and Observations

**Performance Benchmarks:**
- Experiment creation: < 5 seconds
- Pipeline execution: < 5 minutes (dataset dependent)
- UI responsiveness: < 2 seconds for page loads

**Known Limitations:**
- Test assumes stable network connectivity
- Performance may vary based on dataset size
- MLflow UI refresh may be needed to see latest updates

## Acceptance Criteria Verification

This test case verifies the following acceptance criteria:
- ✅ Complete ML experiment workflow functions end-to-end
- ✅ MLflow integration tracks all experiment data
- ✅ Dual persistence (Django + MLflow) works correctly
- ✅ UI provides clear status and results visualization
- ✅ System handles both success and error scenarios
- ✅ Data consistency maintained between systems
