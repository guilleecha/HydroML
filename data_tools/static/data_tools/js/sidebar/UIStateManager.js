/**
 * UI State Manager - Handles UI state updates and notifications
 * Manages stats display, grid refreshing, and notification coordination
 */

class UIStateManager {
    constructor() {
        // UI state management
    }

    updateStats(gridManager) {
        if (gridManager && gridManager.gridApi) {
            const api = gridManager.gridApi;
            const rowCount = api.getDisplayedRowCount();
            const columnCount = api.getColumnDefs()?.length || 0;
            
            const rowElement = document.getElementById('sidebar-row-count');
            const columnElement = document.getElementById('sidebar-column-count');
            
            if (rowElement) rowElement.textContent = rowCount.toLocaleString();
            if (columnElement) columnElement.textContent = columnCount.toLocaleString();
        }
    }

    refreshGrid(gridManager) {
        if (gridManager && gridManager.refreshData) {
            gridManager.refreshData();
        }
    }

    showSuccess(message) {
        DataStudioUIUtils.showNotification(message, 'success');
    }

    showError(message) {
        DataStudioUIUtils.showNotification(message, 'error');
    }

    showWarning(message) {
        DataStudioUIUtils.showNotification(message, 'warning');
    }

    showInfo(message) {
        DataStudioUIUtils.showNotification(message, 'info');
    }
}

// Export for use in other modules
window.UIStateManager = UIStateManager;