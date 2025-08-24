/**
 * TanStackTableCoordinator - Coordination layer for TanStack Table integration
 * Responsabilidad única: Coordinar TanStackTableController con el ecosistema Data Studio
 * 
 * Filosofía: Event-driven coordination, seamless migration from AG Grid
 */

class TanStackTableCoordinator {
    constructor(config = {}) {
        this.config = {
            containerId: 'data-preview-grid',
            enableSearch: true,
            enablePagination: true,
            pageSize: 25,
            ...config
        };
        
        // Core components
        this.tableController = null;
        this.isInitialized = false;
        
        // Data state
        this.currentData = [];
        this.currentColumns = [];
        
        // Session integration
        this.sessionCoordinator = null;
        this.filterCoordinator = null;
        
        // Setup event coordination
        this.setupEventListeners();
        
        // Auto-initialize if data is available
        this.initialize();
    }

    // === INITIALIZATION ===

    async initialize(retryCount = 0, maxRetries = 10) {
        try {
            // Check if container exists
            const container = document.getElementById(this.config.containerId);
            if (!container) {
                if (retryCount >= maxRetries) {
                    throw new Error(`Container '${this.config.containerId}' not found after ${maxRetries} retries`);
                }
                console.warn(`TanStack Table container '${this.config.containerId}' not found, retrying... (${retryCount + 1}/${maxRetries})`);
                // Try again after DOM is ready
                setTimeout(() => this.initialize(retryCount + 1, maxRetries), 100);
                return false;
            }

            // Initialize TanStack Table Controller
            this.tableController = new TanStackTableController(this.config.containerId, {
                enableSorting: true,
                enableFiltering: this.config.enableSearch,
                enablePagination: this.config.enablePagination,
                pageSize: this.config.pageSize
            });

            // Setup table event listeners
            this.setupTableEventListeners();

            // Load initial data if available
            await this.loadInitialData();
            
            this.isInitialized = true;
            
            this.dispatchSystemEvent('tanstack-table-system-ready', {
                config: this.config,
                rowCount: this.currentData.length,
                columnCount: this.currentColumns.length
            });
            
            return true;

        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleGridError(error, {
                    operation: 'tanstack_table_coordinator_initialization'
                });
            } else {
                console.error('TanStack Table Coordinator initialization failed:', error);
            }
            return false;
        }
    }

    async loadInitialData() {
        // Load data from window globals (same as AG Grid was doing)
        if (window.gridRowData && window.columnDefsData) {
            await this.setGridData(window.gridRowData);
            await this.setColumnDefinitions(window.columnDefsData);
            
            // Update UI indicators
            this.updateGridMetrics();
        }
    }

    // === DATA MANAGEMENT ===

    async setGridData(data) {
        try {
            this.currentData = Array.isArray(data) ? data : [];
            
            if (this.tableController) {
                this.tableController.setData(this.currentData);
            }
            
            this.dispatchSystemEvent('tanstack-table-data-updated', {
                rowCount: this.currentData.length,
                data: this.currentData
            });
            
            return true;
        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleGridError(error, {
                    operation: 'set_grid_data',
                    dataLength: data?.length
                });
            }
            return false;
        }
    }

    async setColumnDefinitions(columnDefs) {
        try {
            this.currentColumns = Array.isArray(columnDefs) ? columnDefs : [];
            
            if (this.tableController) {
                this.tableController.setColumns(this.currentColumns);
            }
            
            this.dispatchSystemEvent('tanstack-table-columns-updated', {
                columnCount: this.currentColumns.length,
                columns: this.currentColumns
            });
            
            return true;
        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleGridError(error, {
                    operation: 'set_column_definitions',
                    columnCount: columnDefs?.length
                });
            }
            return false;
        }
    }

    // === INTEGRATION WITH EXISTING SYSTEMS ===

    integrateWithSessionCoordinator(sessionCoordinator) {
        this.sessionCoordinator = sessionCoordinator;
        
        // Listen to session events
        sessionCoordinator.addEventListener('session-data-updated', (event) => {
            this.handleSessionDataUpdate(event.detail);
        });
        
        sessionCoordinator.addEventListener('session-refreshed', () => {
            this.refreshGrid();
        });
    }

    integrateWithFilterCoordinator(filterCoordinator) {
        this.filterCoordinator = filterCoordinator;
        
        // Listen to filter events
        filterCoordinator.addEventListener('filters-applied', (event) => {
            this.handleFiltersApplied(event.detail);
        });
        
        filterCoordinator.addEventListener('filters-cleared', () => {
            this.clearFilters();
        });
    }

    // === EVENT HANDLING ===

    setupEventListeners() {
        // Listen to global system events
        window.addEventListener('data-studio-session-data-loaded', (event) => {
            this.handleSessionDataLoaded(event.detail);
        });

        window.addEventListener('data-studio-refresh-request', () => {
            this.refreshGrid();
        });

        // Compatibility layer for AG Grid events
        window.addEventListener('ag-grid-data-update', (event) => {
            // Convert AG Grid event to TanStack format
            this.setGridData(event.detail.data);
        });
    }

    setupTableEventListeners() {
        if (!this.tableController) return;

        this.tableController.addEventListener('table-rendered', (event) => {
            this.updateGridMetrics();
            this.dispatchSystemEvent('grid-rendered', event.detail);
        });

        this.tableController.addEventListener('data-updated', (event) => {
            this.updateGridMetrics();
            this.dispatchSystemEvent('grid-data-changed', event.detail);
        });

        this.tableController.addEventListener('sorting-changed', (event) => {
            this.dispatchSystemEvent('grid-sorting-changed', event.detail);
        });

        // Forward table events to maintain compatibility
        this.tableController.addEventListener('table-resized', (event) => {
            this.dispatchSystemEvent('grid-resized', event.detail);
        });
    }

    // === DATA PROCESSING ===

    handleSessionDataLoaded(detail) {
        if (detail.gridData && detail.columnDefs) {
            this.setGridData(detail.gridData);
            this.setColumnDefinitions(detail.columnDefs);
        }
    }

    handleSessionDataUpdate(detail) {
        if (detail.data) {
            this.setGridData(detail.data);
        }
    }

    handleFiltersApplied(detail) {
        // TanStack Table handles filtering internally via globalFilter
        // This could be extended to support more complex filter integration
        if (detail.searchTerm) {
            this.setGlobalFilter(detail.searchTerm);
        }
    }

    // === GRID OPERATIONS ===

    refreshGrid() {
        if (this.tableController) {
            this.tableController.updateTable();
            this.updateGridMetrics();
        }
    }

    setGlobalFilter(searchTerm) {
        if (this.tableController) {
            this.tableController.globalFilter = searchTerm;
            this.tableController.updateTable();
        }
    }

    clearFilters() {
        if (this.tableController) {
            this.tableController.globalFilter = '';
            this.tableController.updateTable();
        }
    }

    // === UI UPDATES ===

    updateGridMetrics() {
        if (!this.tableController) return;

        const totalRows = this.tableController.getTotalRowCount();
        const filteredRows = this.tableController.getFilteredRowCount();
        
        // Update grid row count display
        const gridRowCountEl = document.getElementById('grid-row-count');
        if (gridRowCountEl) {
            gridRowCountEl.textContent = totalRows.toLocaleString();
        }

        // Update displayed rows info
        const displayedRowsEl = document.getElementById('displayed-rows');
        if (displayedRowsEl) {
            displayedRowsEl.textContent = this.tableController.pagination.pageSize;
        }

        // Update grid selection info
        const gridSelectionEl = document.getElementById('grid-selection-info');
        if (gridSelectionEl) {
            const selectedRows = this.tableController.getSelectedRows();
            gridSelectionEl.textContent = selectedRows.length > 0 
                ? `${selectedRows.length} selected` 
                : 'No selection';
        }

        // Dispatch metrics update event
        this.dispatchSystemEvent('grid-metrics-updated', {
            totalRows,
            filteredRows,
            pageSize: this.tableController.pagination.pageSize,
            currentPage: this.tableController.pagination.pageIndex + 1
        });
    }

    // === BACKWARD COMPATIBILITY ===

    // Methods to maintain compatibility with existing AG Grid integrations
    getApi() {
        // Return compatibility layer that mimics AG Grid API
        return {
            setRowData: (data) => this.setGridData(data),
            setColumnDefs: (defs) => this.setColumnDefinitions(defs),
            refreshCells: () => this.refreshGrid(),
            sizeColumnsToFit: () => {
                // TanStack Table handles sizing automatically
                console.log('sizeColumnsToFit: Auto-handled by TanStack Table');
            },
            getFilterModel: () => ({
                globalFilter: this.tableController?.globalFilter || ''
            }),
            setFilterModel: (model) => {
                if (model?.globalFilter) {
                    this.setGlobalFilter(model.globalFilter);
                }
            },
            exportDataAsCsv: () => this.tableController?.exportData('csv'),
            getSelectedRows: () => this.tableController?.getSelectedRows() || [],
            // Add more AG Grid API methods as needed
        };
    }

    // === EXPORT FUNCTIONALITY ===

    exportData(format = 'csv') {
        if (!this.tableController) return '';
        return this.tableController.exportData(format);
    }

    // === PUBLIC API ===

    getData() {
        return this.currentData;
    }

    getColumns() {
        return this.currentColumns;
    }

    getRowCount() {
        return this.tableController?.getTotalRowCount() || 0;
    }

    getFilteredRowCount() {
        return this.tableController?.getFilteredRowCount() || 0;
    }

    isReady() {
        return this.isInitialized && this.tableController !== null;
    }

    // === GLOBAL METHOD EXPOSURE ===

    exposeGlobalMethods() {
        // Expose methods globally for backward compatibility
        window.tanStackTableCoordinator = {
            setData: (data) => this.setGridData(data),
            setColumns: (columns) => this.setColumnDefinitions(columns),
            refresh: () => this.refreshGrid(),
            export: (format) => this.exportData(format),
            getApi: () => this.getApi(),
            isReady: () => this.isReady(),
            
            // Direct access to controller
            getController: () => this.tableController,
            getCoordinator: () => this
        };
    }

    // === SYSTEM EVENT DISPATCH ===

    dispatchSystemEvent(eventName, detail = {}) {
        window.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    // === CLEANUP ===

    destroy() {
        if (this.tableController) {
            this.tableController.destroy();
            this.tableController = null;
        }
        
        this.isInitialized = false;
        
        // Clean up global references
        delete window.tanStackTableCoordinator;
        
        this.dispatchSystemEvent('tanstack-table-system-destroyed');
    }
}

// Export for use in other modules
window.TanStackTableCoordinator = TanStackTableCoordinator;