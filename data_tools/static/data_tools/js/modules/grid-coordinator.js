/**
 * GridCoordinator - Grid System Coordination
 * Responsabilidad única: Coordinar GridController, GridUIController y PaginationManager
 * 
 * Filosofía: Event-driven coordination, loose coupling between modules
 */

class GridCoordinator {
    constructor() {
        this.gridController = new GridController();
        this.gridUIController = new GridUIController();
        this.paginationManager = new PaginationManager(this.gridController);
        
        this.setupEventListeners();
        this.exposeGlobalMethods();
    }

    // === EVENT COORDINATION ===

    setupEventListeners() {
        // Grid Controller Events -> UI Updates
        this.gridController.addEventListener('grid-ready', (event) => {
            this.gridUIController.updateGridStatus('ready', 'Grid loaded');
        });

        this.gridController.addEventListener('grid-error', (event) => {
            this.gridUIController.showGridError(event.detail.error);
            this.gridUIController.updateGridStatus('error', event.detail.error);
        });

        this.gridController.addEventListener('grid-selection-changed', (event) => {
            this.gridUIController.updateSelectionInfo(event.detail.selectedCount);
        });

        this.gridController.addEventListener('grid-pagination-changed', (event) => {
            // Update pagination state
            this.paginationManager.updateState(event.detail);
            
            // Update UI displays
            this.gridUIController.updateRowCountDisplay(event.detail);
            this.gridUIController.updateAriaLabels(event.detail);
        });

        this.gridController.addEventListener('grid-first-data-rendered', (event) => {
            // Initialize other systems when grid is ready
            this.dispatchSystemEvent('grid-system-ready', {
                gridApi: event.detail.api
            });
        });

        // Pagination Manager Events -> Notifications
        this.paginationManager.addEventListener('pagination-jump-invalid', (event) => {
            this.gridUIController.showNotification(
                `Invalid page number. Please enter a number between 1 and ${this.paginationManager.totalPages}`, 
                'warning'
            );
        });

        this.paginationManager.addEventListener('pagination-navigate', (event) => {
            this.gridUIController.showNotification(
                `Navigated to page ${event.detail.page}`, 
                'info'
            );
        });

        // Session Events -> Grid Updates
        window.addEventListener('data-studio-grid-update', (event) => {
            const { dataPreview, columnInfo } = event.detail;
            this.gridController.updateData(dataPreview, columnInfo);
        });

        // Window resize -> responsive updates
        window.addEventListener('resize', () => {
            this.gridUIController.handleResponsiveChanges();
        });
    }

    // === GRID SYSTEM OPERATIONS ===

    async initialize() {
        try {
            this.gridUIController.showGridLoading();
            this.gridUIController.updateGridStatus('loading', 'Initializing grid...');
            
            const result = this.gridController.initializeGrid();
            
            if (result.success) {
                this.gridUIController.hideGridLoading();
                this.gridUIController.updateGridStatus('ready', 'Grid ready');
                return result;
            } else {
                this.gridUIController.showGridError(result.error);
                return result;
            }
        } catch (error) {
            console.error('Failed to initialize grid system:', error);
            this.gridUIController.showGridError(error.message);
            return { success: false, error: error.message };
        }
    }

    refreshGrid() {
        const success = this.gridController.refreshGrid();
        if (success) {
            this.gridUIController.showNotification('Grid refreshed', 'success');
        } else {
            this.gridUIController.showNotification('Failed to refresh grid', 'error');
        }
        return success;
    }

    updateData(dataPreview, columnInfo) {
        this.gridUIController.showGridLoading();
        
        const success = this.gridController.updateData(dataPreview, columnInfo);
        
        this.gridUIController.hideGridLoading();
        
        if (success) {
            this.gridUIController.showNotification('Data updated', 'success');
        } else {
            this.gridUIController.showNotification('Failed to update data', 'error');
        }
        
        return success;
    }

    // === GLOBAL METHOD EXPOSURE ===

    exposeGlobalMethods() {
        // Expose grid methods globally for backward compatibility
        window.dataStudioGrid = {
            // Core operations
            initialize: () => this.initialize(),
            refresh: () => this.refreshGrid(),
            updateData: (dataPreview, columnInfo) => this.updateData(dataPreview, columnInfo),
            
            // Pagination operations
            navigateToPage: (page) => this.paginationManager.navigateToPage(page),
            navigateToFirstPage: () => this.paginationManager.navigateToFirstPage(),
            navigateToLastPage: () => this.paginationManager.navigateToLastPage(),
            navigateToNextPage: () => this.paginationManager.navigateToNextPage(),
            navigateToPreviousPage: () => this.paginationManager.navigateToPreviousPage(),
            jumpToPageInput: () => this.paginationManager.jumpToPageInput(),
            changePageSize: (size) => this.paginationManager.changePageSize(size),
            
            // State accessors
            getSelectedRows: () => this.gridController.getSelectedRows(),
            getPaginationInfo: () => this.paginationManager.getPageInfo(),
            getGridApi: () => this.gridController.api,
            
            // State setters for Alpine.js binding
            setJumpToPage: (page) => this.paginationManager.setJumpToPage(page)
        };

        // Expose individual components for advanced usage
        window.gridController = this.gridController;
        window.gridUIController = this.gridUIController;
        window.paginationManager = this.paginationManager;
    }

    // === SYSTEM EVENT DISPATCH ===

    dispatchSystemEvent(eventName, detail = {}) {
        window.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    // === GETTERS ===

    getGridController() {
        return this.gridController;
    }

    getUIController() {
        return this.gridUIController;
    }

    getPaginationManager() {
        return this.paginationManager;
    }

    getGridApi() {
        return this.gridController.api;
    }

    // === CLEANUP ===

    destroy() {
        this.gridController.destroy();
        this.gridUIController.destroy();
        
        // Clean up global references
        delete window.dataStudioGrid;
        delete window.gridController;
        delete window.gridUIController;
        delete window.paginationManager;
    }
}

// Export for use in other modules
window.GridCoordinator = GridCoordinator;

export default GridCoordinator;