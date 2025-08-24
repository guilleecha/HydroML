/**
 * Column Operations Manager - Handles column transformation operations
 * Manages column renaming, type changes, missing value filling, and column deletion
 */

class ColumnOperationsManager {
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

    ensureGridAvailable() {
        if (!this.gridManager || !this.gridManager.gridApi) {
            DataStudioUIUtils.showNotification('Grid not available', 'error');
            return false;
        }
        return true;
    }

    async renameColumn(sessionActive, gridManager) {
        if (!this.ensureActiveSession(sessionActive) || !this.ensureGridAvailable()) return;

        const selectedColumns = this.gridManager.getSelectedColumns();
        if (!selectedColumns || selectedColumns.length === 0) {
            DataStudioUIUtils.showNotification('Please select a column first', 'warning');
            return;
        }

        if (selectedColumns.length > 1) {
            DataStudioUIUtils.showNotification('Please select only one column to rename', 'warning');
            return;
        }

        const oldName = selectedColumns[0];
        const newName = prompt(`Enter new name for column "${oldName}":`, oldName);
        
        if (!newName || newName === oldName) return;

        await this.executeColumnOperation('Renaming column', async () => {
            return await this.api.renameColumn(oldName, newName);
        });
    }

    async changeColumnType(sessionActive, gridManager) {
        if (!this.ensureActiveSession(sessionActive) || !this.ensureGridAvailable()) return;

        const selectedColumns = this.gridManager.getSelectedColumns();
        if (!selectedColumns || selectedColumns.length === 0) {
            DataStudioUIUtils.showNotification('Please select a column first', 'warning');
            return;
        }

        if (selectedColumns.length > 1) {
            DataStudioUIUtils.showNotification('Please select only one column to change type', 'warning');
            return;
        }

        const columnName = selectedColumns[0];
        const typeOptions = ['int', 'float', 'string', 'datetime', 'boolean', 'category'];
        const newType = prompt(`Enter new data type for column "${columnName}".\nOptions: ${typeOptions.join(', ')}`);
        
        if (!newType || !typeOptions.includes(newType.toLowerCase())) {
            DataStudioUIUtils.showNotification('Invalid data type selected', 'warning');
            return;
        }

        await this.executeColumnOperation('Changing column type', async () => {
            return await this.api.changeColumnType(columnName, newType.toLowerCase());
        });
    }

    async fillMissingValues(sessionActive, gridManager) {
        if (!this.ensureActiveSession(sessionActive) || !this.ensureGridAvailable()) return;

        const selectedColumns = this.gridManager.getSelectedColumns();
        if (!selectedColumns || selectedColumns.length === 0) {
            DataStudioUIUtils.showNotification('Please select columns to fill missing values', 'warning');
            return;
        }

        const strategyOptions = ['mean', 'median', 'mode', 'forward_fill', 'backward_fill', 'constant'];
        const strategy = prompt(`Select filling strategy for ${selectedColumns.length} column(s).\nOptions: ${strategyOptions.join(', ')}`);
        
        if (!strategy || !strategyOptions.includes(strategy.toLowerCase())) {
            DataStudioUIUtils.showNotification('Invalid strategy selected', 'warning');
            return;
        }

        let fillValue = null;
        if (strategy.toLowerCase() === 'constant') {
            fillValue = prompt('Enter the constant value to use for filling:');
            if (fillValue === null) return;
        }

        await this.executeColumnOperation('Filling missing values', async () => {
            return await this.api.fillMissingValues(selectedColumns, strategy.toLowerCase(), fillValue);
        });
    }

    async deleteSelectedColumns(sessionActive, gridManager) {
        if (!this.ensureActiveSession(sessionActive) || !this.ensureGridAvailable()) return;

        const selectedColumns = this.gridManager.getSelectedColumns();
        if (!selectedColumns || selectedColumns.length === 0) {
            DataStudioUIUtils.showNotification('No columns selected', 'warning');
            return;
        }

        if (!confirm(`Delete ${selectedColumns.length} selected column(s)?`)) return;

        await this.executeColumnOperation('Deleting columns', async () => {
            return await this.api.deleteColumns(selectedColumns);
        });
    }

    async executeColumnOperation(operationName, apiCall) {
        try {
            DataStudioUIUtils.showNotification(`${operationName}...`, 'info');
            
            const data = await apiCall();
            
            if (data.success) {
                DataStudioUIUtils.showNotification(data.message || `${operationName} completed`, 'success');
                this.refreshGrid();
            } else {
                DataStudioUIUtils.showNotification(`${operationName} failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`${operationName} error: ${error.message}`, 'error');
        }
    }

    refreshGrid() {
        if (this.gridManager && this.gridManager.refreshData) {
            this.gridManager.refreshData();
        }
    }
}

// Export for use in other modules
window.ColumnOperationsManager = ColumnOperationsManager;