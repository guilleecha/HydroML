/**
 * Integration Manager - Handles external integrations and modal operations
 * Manages chart builder, SQL query modal, column panel, and export functionality
 */

class IntegrationManager {
    constructor() {
        // External integration management
    }

    async openQuickChartsModal(sessionActive) {
        if (!sessionActive) {
            DataStudioUIUtils.showNotification('Please initialize a session first', 'warning');
            return;
        }

        if (window.openVisualizationModal) {
            window.openVisualizationModal();
        } else {
            DataStudioUIUtils.showNotification('Chart functionality will be implemented', 'info');
        }
    }

    async openSQLModal(sessionActive) {
        if (!sessionActive) {
            DataStudioUIUtils.showNotification('Please initialize a session first', 'warning');
            return;
        }

        if (window.openSQLQueryModal) {
            window.openSQLQueryModal();
        } else {
            DataStudioUIUtils.showNotification('SQL functionality will be implemented', 'info');
        }
    }

    toggleColumnPanel(gridManager) {
        if (gridManager && gridManager.toggleColumnPanel) {
            gridManager.toggleColumnPanel();
            DataStudioUIUtils.showNotification('Column panel toggled', 'info');
        } else {
            DataStudioUIUtils.showNotification('Column panel not available', 'warning');
        }
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

// Export for use in other modules
window.IntegrationManager = IntegrationManager;