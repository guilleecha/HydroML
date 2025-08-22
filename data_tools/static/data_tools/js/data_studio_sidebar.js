/**
 * Data Studio Sidebar - Main Controller
 * Orchestrates UI and API interactions for the Data Studio sidebar
 */

class DataStudioSidebar {
    constructor() {
        this.datasourceId = window.datasourceId || null;
        this.gridManager = window.gridManager || null;
        this.sessionActive = false;
        
        // Initialize API client
        this.api = new DataStudioAPI(this.datasourceId);
        
        this.init();
    }

    init() {
        this.initDropdowns();
        this.updateStats();
        this.bindEvents();
        this.updateSessionStatus();
        
        // Update stats and session status periodically
        setInterval(() => {
            this.updateStats();
            this.updateSessionStatus();
        }, 3000);
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
    }

    updateStats() {
        if (this.gridManager && this.gridManager.gridApi) {
            const api = this.gridManager.gridApi;
            const rowCount = api.getDisplayedRowCount();
            const columnCount = api.getColumnDefs()?.length || 0;
            
            const rowElement = document.getElementById('sidebar-row-count');
            const columnElement = document.getElementById('sidebar-column-count');
            
            if (rowElement) rowElement.textContent = rowCount.toLocaleString();
            if (columnElement) columnElement.textContent = columnCount.toLocaleString();
        }
    }

    async updateSessionStatus() {
        const data = await this.api.checkSessionStatus();
        this.updateSessionUI(data.session_exists || false, data);
    }

    updateSessionUI(sessionExists, sessionData = {}) {
        const dot = document.getElementById('session-status-dot');
        const label = document.getElementById('session-status-label');
        const stopBtn = document.getElementById('stop-session-btn');
        
        this.sessionActive = sessionExists;
        
        if (sessionExists) {
            if (dot) dot.className = 'w-2 h-2 rounded-full bg-green-500';
            if (label) label.textContent = 'Session Active';
            if (stopBtn) {
                stopBtn.classList.remove('hidden');
                stopBtn.style.display = 'inline-block';
            }
        } else {
            if (dot) dot.className = 'w-2 h-2 rounded-full bg-gray-400';
            if (label) label.textContent = 'No session';
            if (stopBtn) {
                stopBtn.classList.add('hidden');
                stopBtn.style.display = 'none';
            }
        }
    }

    // === SESSION MANAGEMENT ===
    
    async initializeSession() {
        try {
            DataStudioUIUtils.showNotification('Initializing session...', 'info');
            
            const data = await this.api.initializeSession();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Session initialized successfully', 'success');
                this.refreshGrid();
            } else {
                DataStudioUIUtils.showNotification(`Failed to initialize: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Session error: ${error.message}`, 'error');
        }
    }

    async stopSession() {
        if (!this.datasourceId || !this.sessionActive) return;

        try {
            const data = await this.api.stopSession();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Session stopped', 'success');
                this.updateSessionUI(false);
            } else {
                DataStudioUIUtils.showNotification(`Failed to stop session: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Error stopping session: ${error.message}`, 'error');
        }
    }

    async undoOperation() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('No active session', 'warning');
            return;
        }

        try {
            const data = await this.api.undoOperation();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Operation undone', 'success');
                this.refreshGrid();
            } else {
                DataStudioUIUtils.showNotification(`Undo failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Undo error: ${error.message}`, 'error');
        }
    }

    async redoOperation() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('No active session', 'warning');
            return;
        }

        try {
            const data = await this.api.redoOperation();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Operation redone', 'success');
                this.refreshGrid();
            } else {
                DataStudioUIUtils.showNotification(`Redo failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Redo error: ${error.message}`, 'error');
        }
    }

    async saveSession() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('No active session to save', 'warning');
            return;
        }

        try {
            DataStudioUIUtils.showNotification('Saving dataset...', 'info');
            
            const data = await this.api.saveSession();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Dataset saved successfully', 'success');
            } else {
                DataStudioUIUtils.showNotification(`Save failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Save error: ${error.message}`, 'error');
        }
    }

    // === NaN CLEANING ===
    
    async runNaNAnalysis() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('Please initialize a session first', 'warning');
            return;
        }

        try {
            DataStudioUIUtils.showNotification('Running NaN analysis...', 'info');
            
            const data = await this.api.runNaNAnalysis();
            
            if (data.success) {
                this.showNaNAnalysisResults(data);
                DataStudioUIUtils.showNotification('NaN analysis completed', 'success');
            } else {
                DataStudioUIUtils.showNotification(`Analysis failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Analysis error: ${error.message}`, 'error');
        }
    }

    async openNaNCleaningModal() {
        const modal = DataStudioUIUtils.createModal('nanCleaningModal', 'nan-cleaning-modal');
        DataStudioUIUtils.openModal(modal);
    }

    closeNaNCleaningModal() {
        DataStudioUIUtils.closeModal('nan-cleaning-modal');
    }

    async performNaNCleaning() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('Please initialize a session first', 'warning');
            this.closeNaNCleaningModal();
            return;
        }

        try {
            const removeRows = document.getElementById('remove-nan-rows').checked;
            const removeColumns = document.getElementById('remove-nan-columns').checked;
            
            this.closeNaNCleaningModal();
            DataStudioUIUtils.showNotification('Cleaning NaN values...', 'info');
            
            const data = await this.api.performNaNCleaning(removeRows, removeColumns);
            
            if (data.success) {
                DataStudioUIUtils.showNotification('NaN cleaning completed', 'success');
                this.refreshGrid();
            } else {
                DataStudioUIUtils.showNotification(`Cleaning failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Cleaning error: ${error.message}`, 'error');
        }
    }

    // === COLUMN OPERATIONS ===
    
    async deleteSelectedColumns() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('Please initialize a session first', 'warning');
            return;
        }

        if (!this.gridManager || !this.gridManager.gridApi) {
            DataStudioUIUtils.showNotification('Grid not available', 'error');
            return;
        }

        const selectedColumns = this.gridManager.getSelectedColumns();
        if (!selectedColumns || selectedColumns.length === 0) {
            DataStudioUIUtils.showNotification('No columns selected', 'warning');
            return;
        }

        if (!confirm(`Delete ${selectedColumns.length} selected column(s)?`)) {
            return;
        }

        try {
            DataStudioUIUtils.showNotification('Deleting columns...', 'info');
            
            const data = await this.api.deleteColumns(selectedColumns);
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Columns deleted successfully', 'success');
                this.refreshGrid();
            } else {
                DataStudioUIUtils.showNotification(`Delete failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Delete error: ${error.message}`, 'error');
        }
    }

    // === INTEGRATIONS ===
    
    async openQuickChartsModal() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('Please initialize a session first', 'warning');
            return;
        }

        if (window.openVisualizationModal) {
            window.openVisualizationModal();
        } else {
            DataStudioUIUtils.showNotification('Chart functionality will be implemented', 'info');
        }
    }

    async openSQLModal() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('Please initialize a session first', 'warning');
            return;
        }

        if (window.openSQLQueryModal) {
            window.openSQLQueryModal();
        } else {
            DataStudioUIUtils.showNotification('SQL functionality will be implemented', 'info');
        }
    }

    toggleColumnPanel() {
        if (this.gridManager && this.gridManager.toggleColumnPanel) {
            this.gridManager.toggleColumnPanel();
            DataStudioUIUtils.showNotification('Column panel toggled', 'info');
        } else {
            DataStudioUIUtils.showNotification('Column panel not available', 'warning');
        }
    }

    // === UTILITY FUNCTIONS ===
    
    refreshGrid() {
        if (this.gridManager && this.gridManager.refreshData) {
            this.gridManager.refreshData();
        }
    }

    showNaNAnalysisResults(data) {
        console.log('NaN Analysis Results:', data);
        
        if (data.column_nullity && data.column_nullity.length > 0) {
            const topMissing = data.column_nullity.slice(0, 3);
            const message = `Analysis complete. Top missing data:\n${topMissing.map(col => 
                `${col.column}: ${col.null_percentage}%`).join('\n')}`;
            DataStudioUIUtils.showNotification(message, 'info');
        }
    }

    // === PLACEHOLDER FUNCTIONS (Using shared utility) ===
    
    showDatasetInfo() {
        DataStudioUIUtils.showPlaceholderFeature('Dataset info');
    }

    showQuickStats() {
        DataStudioUIUtils.showPlaceholderFeature('Quick stats');
    }

    renameColumn() {
        DataStudioUIUtils.showPlaceholderFeature('Column rename');
    }

    changeColumnType() {
        DataStudioUIUtils.showPlaceholderFeature('Column type change');
    }

    fillMissingValues() {
        DataStudioUIUtils.showPlaceholderFeature('Fill missing values');
    }

    combineColumns() {
        DataStudioUIUtils.showPlaceholderFeature('Combine columns');
    }

    createCalculatedColumn() {
        DataStudioUIUtils.showPlaceholderFeature('Calculated column');
    }

    normalizeData() {
        DataStudioUIUtils.showPlaceholderFeature('Data normalization');
    }

    openChartBuilderModal() {
        DataStudioUIUtils.showPlaceholderFeature('Chart builder');
    }

    createDataProfile() {
        DataStudioUIUtils.showPlaceholderFeature('Data profile');
    }

    exportData() {
        // Open the export wizard modal
        if (window.exportWizard) {
            window.exportWizard.open();
        } else {
            console.warn('Export wizard not available');
            DataStudioUIUtils.showPlaceholderFeature('Export data');
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.dataStudioSidebar = new DataStudioSidebar();
});

// Export for use in other modules
window.DataStudioSidebar = DataStudioSidebar;