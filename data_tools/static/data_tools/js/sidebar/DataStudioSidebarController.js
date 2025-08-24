/**
 * Data Studio Sidebar Controller - Main orchestrator
 * Coordinates between different sidebar modules and manages initialization
 */

class DataStudioSidebarController {
    constructor() {
        this.datasourceId = window.datasourceId || null;
        this.gridManager = window.gridManager || null;
        this.sessionActive = false;
        
        // Initialize API client
        this.api = new DataStudioAPI(this.datasourceId);
        
        // Initialize sub-managers
        this.sessionManager = new SessionManager(this.api);
        this.columnOpsManager = new ColumnOperationsManager(this.api);
        this.dataAnalysisManager = new DataAnalysisManager(this.api);
        this.uiStateManager = new UIStateManager();
        this.integrationManager = new IntegrationManager();
        
        this.init();
    }

    init() {
        this.initDropdowns();
        this.bindEvents();
        this.updateStats();
        this.updateSessionStatus();
        
        // Set up periodic updates
        setInterval(() => {
            this.updateStats();
            this.updateSessionStatus();
        }, 3000);
        
        // Subscribe to session changes
        this.sessionManager.onSessionStateChange((active) => {
            this.sessionActive = active;
            this.updateGridManager();
        });
    }

    initDropdowns() {
        DataStudioUIUtils.initDropdowns(() => {
            DataStudioUIUtils.closeAllDropdowns();
        });
    }

    bindEvents() {
        // Listen for grid updates
        if (window.gridManager) {
            const originalOnGridReady = window.gridManager.onGridReady;
            window.gridManager.onGridReady = (params) => {
                if (originalOnGridReady) originalOnGridReady(params);
                this.gridManager = window.gridManager;
                this.updateStats();
            };
        }

        // Bind sidebar action buttons using event delegation
        document.addEventListener('click', (e) => {
            const actionButton = e.target.closest('[data-action]');
            if (!actionButton) return;

            const action = actionButton.dataset.action;
            this.handleAction(action);
        });
    }

    handleAction(action) {
        // Delegate actions to appropriate managers
        switch (action) {
            case 'quick-nan-cleanup':
                this.dataAnalysisManager.openNaNCleaningModal();
                break;
            case 'analyze-missing':
                this.dataAnalysisManager.runNaNAnalysis();
                break;
            default:
                console.warn('Unknown action:', action);
                break;
        }
    }

    updateStats() {
        this.uiStateManager.updateStats(this.gridManager);
    }

    async updateSessionStatus() {
        const data = await this.api.checkSessionStatus();
        this.sessionManager.updateSessionUI(data.session_exists || false, data);
        this.sessionActive = data.session_exists || false;
    }

    updateGridManager() {
        // Update all managers with grid reference
        this.columnOpsManager.setGridManager(this.gridManager);
        this.dataAnalysisManager.setGridManager(this.gridManager);
    }

    // Public API methods for external access
    initializeSession() { return this.sessionManager.initializeSession(); }
    stopSession() { return this.sessionManager.stopSession(); }
    undoOperation() { return this.sessionManager.undoOperation(); }
    redoOperation() { return this.sessionManager.redoOperation(); }
    saveSession() { return this.sessionManager.saveSession(); }

    // Data analysis operations
    showDatasetInfo() { return this.dataAnalysisManager.showDatasetInfo(this.sessionActive, this.gridManager); }
    showQuickStats() { return this.dataAnalysisManager.showQuickStats(this.sessionActive); }

    // Column operations
    renameColumn() { return this.columnOpsManager.renameColumn(this.sessionActive, this.gridManager); }
    changeColumnType() { return this.columnOpsManager.changeColumnType(this.sessionActive, this.gridManager); }
    fillMissingValues() { return this.columnOpsManager.fillMissingValues(this.sessionActive, this.gridManager); }
    deleteSelectedColumns() { return this.columnOpsManager.deleteSelectedColumns(this.sessionActive, this.gridManager); }

    // Integration operations
    openQuickChartsModal() { return this.integrationManager.openQuickChartsModal(this.sessionActive); }
    openSQLModal() { return this.integrationManager.openSQLModal(this.sessionActive); }
    toggleColumnPanel() { return this.integrationManager.toggleColumnPanel(this.gridManager); }
    exportData() { return this.integrationManager.exportData(); }

    // Placeholder functions for future implementation
    combineColumns() { DataStudioUIUtils.showPlaceholderFeature('Combine columns'); }
    createCalculatedColumn() { DataStudioUIUtils.showPlaceholderFeature('Calculated column'); }
    normalizeData() { DataStudioUIUtils.showPlaceholderFeature('Data normalization'); }
    openChartBuilderModal() { DataStudioUIUtils.showPlaceholderFeature('Chart builder'); }
    createDataProfile() { DataStudioUIUtils.showPlaceholderFeature('Data profile'); }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.dataStudioSidebar = new DataStudioSidebarController();
});

// Export for use in other modules
window.DataStudioSidebarController = DataStudioSidebarController;