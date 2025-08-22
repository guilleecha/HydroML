/**
 * GridController - AG Grid Management
 * Responsabilidad única: Inicialización y control del grid AG Grid
 * 
 * Filosofía: Core grid logic only, no UI updates, no mixed concerns
 */

class GridController {
    constructor() {
        this.gridApi = null;
        this.gridInstance = null;
        this.isInitialized = false;
        this.eventTarget = new EventTarget();
    }

    // === CORE GRID OPERATIONS ===

    initializeGrid() {
        // Prevent double initialization
        if (this.isInitialized) {
            // Grid already initialized, skipping
            return { success: true, message: 'Already initialized' };
        }
        
        if (!window.gridRowData || !window.columnDefsData) {
            console.warn('Grid data not available:', {
                rowData: !!window.gridRowData,
                columnDefs: !!window.columnDefsData
            });
            return { success: false, error: 'Grid data not available' };
        }

        try {
            // Initializing AG Grid
            
            const columnDefs = this.buildColumnDefinitions();
            const gridOptions = this.buildGridOptions(columnDefs);
            
            const gridDiv = document.querySelector('#data-preview-grid');
            if (!gridDiv) {
                throw new Error('Grid container not found');
            }

            if (gridDiv.querySelector('.ag-root-wrapper')) {
                throw new Error('Grid container already has grid content');
            }

            // Creating AG Grid
            this.gridInstance = agGrid.createGrid(gridDiv, gridOptions);
            
            this.isInitialized = true;
            this.dispatchEvent('grid-initialized', { gridApi: this.gridApi });
            
            return { success: true, gridApi: this.gridApi };
            
        } catch (error) {
            console.error('Failed to initialize grid:', error);
            this.dispatchEvent('grid-error', { error: error.message });
            return { success: false, error: error.message };
        }
    }

    updateData(dataPreview, columnInfo) {
        if (!this.gridApi) {
            console.warn('Grid API not available for data update');
            return false;
        }

        try {
            if (columnInfo) {
                const columnDefs = this.buildColumnDefinitions(columnInfo);
                this.gridApi.setGridOption('columnDefs', columnDefs);
            }
            
            if (dataPreview) {
                this.gridApi.setGridOption('rowData', dataPreview);
            }
            
            this.dispatchEvent('grid-data-updated', { dataPreview, columnInfo });
            return true;
        } catch (error) {
            console.error('Failed to update grid data:', error);
            this.dispatchEvent('grid-error', { error: error.message });
            return false;
        }
    }

    refreshGrid() {
        if (!this.gridApi) return false;

        try {
            this.gridApi.refreshCells();
            this.gridApi.sizeColumnsToFit();
            this.dispatchEvent('grid-refreshed');
            return true;
        } catch (error) {
            console.error('Failed to refresh grid:', error);
            return false;
        }
    }

    getSelectedRows() {
        if (!this.gridApi) return [];
        
        try {
            return this.gridApi.getSelectedRows();
        } catch (error) {
            console.error('Failed to get selected rows:', error);
            return [];
        }
    }

    getDisplayedRowCount() {
        if (!this.gridApi) return 0;
        
        try {
            return this.gridApi.getDisplayedRowCount();
        } catch (error) {
            console.error('Failed to get displayed row count:', error);
            return 0;
        }
    }

    getCurrentPage() {
        if (!this.gridApi) return 0;
        
        try {
            return this.gridApi.paginationGetCurrentPage();
        } catch (error) {
            console.error('Failed to get current page:', error);
            return 0;
        }
    }

    getPageSize() {
        if (!this.gridApi) return 25;
        
        try {
            return this.gridApi.paginationGetPageSize();
        } catch (error) {
            console.error('Failed to get page size:', error);
            return 25;
        }
    }

    // === PAGINATION OPERATIONS ===

    navigateToPage(page) {
        if (!this.gridApi) return false;
        
        try {
            // AG Grid is 0-based, convert from 1-based
            this.gridApi.paginationGoToPage(page - 1);
            this.dispatchEvent('grid-page-changed', { page });
            return true;
        } catch (error) {
            console.error('Failed to navigate to page:', error);
            return false;
        }
    }

    changePageSize(newSize) {
        if (!this.gridApi) return false;
        
        try {
            const size = newSize === 'All' ? this.getDisplayedRowCount() : parseInt(newSize);
            this.gridApi.paginationSetPageSize(size);
            this.dispatchEvent('grid-page-size-changed', { pageSize: size });
            return true;
        } catch (error) {
            console.error('Failed to change page size:', error);
            return false;
        }
    }

    // === PRIVATE METHODS ===

    buildColumnDefinitions(customColumnDefs = null) {
        const columnDefs = customColumnDefs || window.columnDefsData;
        
        // Add row number column as first column
        return [
            {
                headerName: '#',
                field: 'rowNumber',
                width: 60,
                pinned: 'left',
                cellStyle: { 
                    fontWeight: 'bold', 
                    backgroundColor: '#f8fafc',
                    color: '#64748b',
                    textAlign: 'center'
                },
                valueGetter: (params) => params.node.rowIndex + 1,
                suppressMenu: true,
                sortable: false,
                filter: false,
                resizable: false
            },
            ...columnDefs
        ];
    }

    buildGridOptions(columnDefs) {
        return {
            columnDefs: columnDefs,
            rowData: window.gridRowData,
            
            // Column configuration for optimal width usage
            defaultColDef: {
                resizable: true,
                sortable: true,
                filter: true,
                floatingFilter: true,
                minWidth: 100,
                maxWidth: 300,
                flex: 1,
                cellStyle: {
                    'white-space': 'nowrap',
                    'overflow': 'hidden',
                    'text-overflow': 'ellipsis'
                }
            },
            
            // Grid behavior configuration
            rowSelection: 'multiple',
            pagination: true,
            paginationPageSize: 25,
            paginationPageSizeSelector: [10, 25, 50, 100, 'All'],
            suppressRowClickSelection: false,
            enableCellTextSelection: true,
            animateRows: true,
            suppressHorizontalScroll: false,
            
            // Grid sizing configuration
            suppressAutoSize: false,
            skipHeaderOnAutoSize: false,
            
            // Event handlers
            onGridReady: (params) => {
                // Grid ready
                
                // FIXED: Store only the API reference, not the grid instance
                this.gridApi = params.api;
                
                // Size columns to fit container width
                params.api.sizeColumnsToFit();
                
                // Set up resize listener with cleanup
                this.setupResizeListener();
                
                this.dispatchEvent('grid-ready', { 
                    api: params.api,
                    columnApi: params.columnApi 
                });
            },
            
            onSelectionChanged: (event) => {
                const selectedRows = event.api.getSelectedRows().length;
                this.dispatchEvent('grid-selection-changed', { 
                    selectedCount: selectedRows,
                    selectedRows: event.api.getSelectedRows()
                });
            },
            
            onFirstDataRendered: (params) => {
                // First data rendered
                params.api.sizeColumnsToFit();
                this.dispatchEvent('grid-first-data-rendered', { api: params.api });
            },
            
            onPaginationChanged: (params) => {
                const paginationInfo = {
                    currentPage: params.api.paginationGetCurrentPage() + 1, // Convert to 1-based
                    totalPages: params.api.paginationGetTotalPages(),
                    pageSize: params.api.paginationGetPageSize(),
                    totalRows: params.api.getDisplayedRowCount()
                };
                this.dispatchEvent('grid-pagination-changed', paginationInfo);
            },
            
            onGridSizeChanged: (params) => {
                // Grid size changed
                params.api.sizeColumnsToFit();
                this.dispatchEvent('grid-size-changed');
            }
        };
    }

    setupResizeListener() {
        // Set up resize listener with proper cleanup
        const handleResize = () => {
            setTimeout(() => {
                if (this.gridApi) {
                    this.gridApi.sizeColumnsToFit();
                }
            }, 100);
        };
        
        window.addEventListener('resize', handleResize);
        
        // Store reference for cleanup
        this.resizeHandler = handleResize;
    }

    // === EVENT SYSTEM ===

    dispatchEvent(eventName, detail = {}) {
        this.eventTarget.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    addEventListener(eventName, handler) {
        this.eventTarget.addEventListener(eventName, handler);
    }

    removeEventListener(eventName, handler) {
        this.eventTarget.removeEventListener(eventName, handler);
    }

    // === CLEANUP ===

    destroy() {
        if (this.resizeHandler) {
            window.removeEventListener('resize', this.resizeHandler);
        }
        
        if (this.gridInstance && this.gridInstance.destroy) {
            this.gridInstance.destroy();
        }
        
        this.gridApi = null;
        this.gridInstance = null;
        this.isInitialized = false;
        
        this.dispatchEvent('grid-destroyed');
    }

    // === GETTERS ===

    get api() {
        return this.gridApi;
    }

    get initialized() {
        return this.isInitialized;
    }
}

// Export for use in other modules
window.GridController = GridController;

export default GridController;