/**
 * DataSources List Page JavaScript
 * Handles AG Grid initialization for datasources listing
 * Part of HydroML Projects module
 */

class DataSourcesListPage {
    constructor() {
        this.gridComponent = null;
        this.datasources = [];
    }

    init(datasources) {
        this.datasources = datasources;
        this.initializeGrid();
        this.setupEventListeners();
    }

    initializeGrid() {
        // Check if DataSourceGrid component is available
        if (typeof DataSourceGrid === 'undefined') {
            console.error('DataSourceGrid component not loaded. Please ensure DataSourceGrid.js is included.');
            this.showGridError('DataSourceGrid component not available');
            return;
        }
        
        try {
            // Initialize the DataSourceGrid component
            this.gridComponent = new DataSourceGrid('datasourcesGrid', this.datasources);
            
            // Make grid globally available if needed
            window.datasourceGrid = this.gridComponent;
        } catch (error) {
            console.error('Error initializing DataSourceGrid:', error);
            this.showGridError('Failed to initialize data grid');
        }
    }
    
    showGridError(message) {
        const gridContainer = document.getElementById('datasourcesGrid');
        if (gridContainer) {
            gridContainer.innerHTML = `
                <div class="flex items-center justify-center h-32 text-gray-500 dark:text-gray-400">
                    <div class="text-center">
                        <p class="mb-2">${message}</p>
                        <button onclick="window.location.reload()" class="grove-btn grove-btn--secondary grove-btn--sm">
                            Refresh Page
                        </button>
                    </div>
                </div>
            `;
        }
    }

    setupEventListeners() {
        // Add any additional event listeners here
        // For example, refresh button, search functionality, etc.
    }

    // Public API methods
    refreshGrid() {
        if (this.gridComponent) {
            this.gridComponent.refresh();
        }
    }

    getSelectedRows() {
        return this.gridComponent ? this.gridComponent.getSelectedRows() : [];
    }

    updateDatasources(newDatasources) {
        this.datasources = newDatasources;
        if (this.gridComponent) {
            this.gridComponent.updateData(newDatasources);
        }
    }
}

// Auto-initialization when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if datasources data is available
    if (typeof window.datasourcesData !== 'undefined') {
        const pageController = new DataSourcesListPage();
        pageController.init(window.datasourcesData);
        
        // Make controller globally available
        window.dataSourcesListPage = pageController;
    } else {
        console.warn('DataSources List: No datasources data found');
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataSourcesListPage;
}

// Global registration
if (typeof window !== 'undefined') {
    window.DataSourcesListPage = DataSourcesListPage;
}