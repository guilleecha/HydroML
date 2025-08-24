/**
 * Data Analysis Manager - Handles data analysis and statistical operations
 * Manages dataset info, statistics, NaN analysis, and data profiling
 */

class DataAnalysisManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.gridManager = null;
    }

    setGridManager(gridManager) {
        this.gridManager = gridManager;
    }

    ensureActiveSession(sessionActive) {
        if (!sessionActive) {
            DataStudioUIUtils.showNotification('Please initialize a session first', 'warning');
            return false;
        }
        return true;
    }

    showDatasetInfo(sessionActive, gridManager) {
        if (!this.ensureActiveSession(sessionActive)) return;
        
        if (gridManager && gridManager.gridApi) {
            const api = gridManager.gridApi;
            const rowCount = api.getDisplayedRowCount();
            const columnCount = api.getColumnDefs()?.length || 0;
            
            const info = `Dataset Info:\nRows: ${rowCount.toLocaleString()}\nColumns: ${columnCount}`;
            DataStudioUIUtils.showNotification(info, 'info');
        } else {
            DataStudioUIUtils.showNotification('Grid data not available', 'warning');
        }
    }

    async showQuickStats(sessionActive) {
        if (!this.ensureActiveSession(sessionActive)) return;

        try {
            DataStudioUIUtils.showNotification('Loading column statistics...', 'info');
            
            const data = await this.api.getColumnStatistics();
            
            if (data.success) {
                this.displayColumnStatistics(data.column_statistics, data.dataset_statistics);
            } else {
                DataStudioUIUtils.showNotification(`Failed to get statistics: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Statistics error: ${error.message}`, 'error');
        }
    }

    displayColumnStatistics(columnStats, datasetStats) {
        console.log('Column Statistics:', columnStats);
        console.log('Dataset Statistics:', datasetStats);
        
        // Show a summary in notification
        const topNullColumns = Object.values(columnStats)
            .filter(col => col.null_percentage > 0)
            .sort((a, b) => b.null_percentage - a.null_percentage)
            .slice(0, 3);
            
        let message = `Statistics loaded for ${datasetStats.total_columns} columns:\n`;
        if (topNullColumns.length > 0) {
            message += `Top missing data:\n${topNullColumns.map(col => 
                `${col.name}: ${col.null_percentage.toFixed(1)}%`).join('\n')}`;
        } else {
            message += 'No missing data detected';
        }
        
        DataStudioUIUtils.showNotification(message, 'success');
    }

    async runNaNAnalysis() {
        if (!this.ensureActiveSession(true)) return;

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

    showNaNAnalysisResults(data) {
        console.log('NaN Analysis Results:', data);
        
        if (data.column_nullity && data.column_nullity.length > 0) {
            const topMissing = data.column_nullity.slice(0, 3);
            const message = `Analysis complete. Top missing data:\n${topMissing.map(col => 
                `${col.column}: ${col.null_percentage}%`).join('\n')}`;
            DataStudioUIUtils.showNotification(message, 'info');
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
        if (!this.ensureActiveSession(true)) {
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

    refreshGrid() {
        if (this.gridManager && this.gridManager.refreshData) {
            this.gridManager.refreshData();
        }
    }
}

// Export for use in other modules
window.DataAnalysisManager = DataAnalysisManager;