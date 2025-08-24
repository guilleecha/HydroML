/**
 * TanStack Table Component for HydroML
 * Simplified vanilla JavaScript implementation with proper CDN integration
 */

class HydroMLTanStackTable {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            pageSize: 25,
            enableSorting: true,
            enableFiltering: true,
            enablePagination: true,
            debugMode: true,
            ...options
        };
        
        this.table = null;
        this.data = [];
        this.columns = [];
        this.state = {
            columnPinning: {},
            pagination: { pageIndex: 0, pageSize: this.options.pageSize },
            globalFilter: '',
            sorting: [],
            columnSizing: {},
            columnVisibility: {},
            columnFilters: []
        };
        
        console.log('🚀 HydroMLTanStackTable inicializada:', { containerId, options: this.options });
    }

    /**
     * Initialize the table with data and columns
     */
    init(data, columns) {
        this.data = data || [];
        this.columns = columns || [];
        
        console.log('📊 Datos recibidos:', { 
            dataLength: this.data.length, 
            columnsLength: this.columns.length 
        });
        
        if (!this.data || this.data.length === 0) {
            console.warn('⚠️ No hay datos para mostrar en la tabla');
            this.renderEmpty();
            return;
        }

        this.createTable();
        this.setupEventListeners();
        this.render();
        
        console.log('✅ TanStack Table inicializada correctamente');
    }

    /**
     * Create TanStack Table instance
     */
    createTable() {
        // Wait for TanStack Table library to load
        if (typeof window.TableCore === 'undefined') {
            console.warn('⚠️ TanStack Table library not loaded yet, waiting for bootstrap...');
            // Listen for the ready event from bootstrap
            window.addEventListener('tanstack-table-ready', () => {
                if (window.TableCore) {
                    this.createTable();
                } else {
                    console.error('❌ TanStack Table bootstrap failed');
                    this.renderError(new Error('TanStack Table library not available'));
                }
            }, { once: true });
            return;
        }

        const { createTable, getCoreRowModel, getPaginationRowModel, getSortedRowModel, getFilteredRowModel } = window.TableCore;
        
        // Create column definitions
        const columnDefs = this.columns.map(columnName => ({
            id: columnName,
            accessorKey: columnName,
            header: columnName,
            cell: info => {
                const value = info.getValue();
                return value !== null && value !== undefined ? String(value).slice(0, 100) : '-';
            },
            enableSorting: this.options.enableSorting,
            enableColumnFilter: this.options.enableFiltering,
            // TanStack v8+ column sizing configuration
            size: 150,
            minSize: 50,
            maxSize: 300,
            enableResizing: false,
        }));

        console.log('📋 Columnas definidas:', columnDefs.length);

        // Create table instance
        try {
            this.table = createTable({
                data: this.data,
                columns: columnDefs,
                getCoreRowModel: getCoreRowModel(),
                getPaginationRowModel: getPaginationRowModel(),
                getSortedRowModel: getSortedRowModel(),
                getFilteredRowModel: getFilteredRowModel(),
                state: this.state,
                columnResizeMode: 'onChange',
                enableColumnResizing: false,
                debugAll: true,
                onStateChange: (updater) => {
                    const newState = typeof updater === 'function' ? updater(this.state) : updater;
                    this.state = { ...this.state, ...newState };
                    this.render();
                },
                onGlobalFilterChange: (globalFilter) => {
                    this.state.globalFilter = globalFilter;
                    this.state.pagination.pageIndex = 0; // Reset to first page
                },
                onPaginationChange: (pagination) => {
                    this.state.pagination = typeof pagination === 'function' ? pagination(this.state.pagination) : pagination;
                },
                onSortingChange: (sorting) => {
                    this.state.sorting = typeof sorting === 'function' ? sorting(this.state.sorting) : sorting;
                },
                globalFilterFn: 'includesString',
                debugTable: this.options.debugMode,
            });
            
            console.log('✅ TanStack Table instance created successfully');
        } catch (error) {
            console.error('❌ Error creating TanStack Table:', error);
            this.renderError(error);
        }
    }

    /**
     * Setup event listeners for controls
     */
    setupEventListeners() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        // Global filter
        const globalFilter = container.querySelector('#globalFilter');
        if (globalFilter) {
            globalFilter.addEventListener('input', (e) => {
                this.table.setGlobalFilter(e.target.value);
                this.render();
            });
        }

        // Page size selector
        const pageSize = container.querySelector('#pageSize');
        if (pageSize) {
            pageSize.addEventListener('change', (e) => {
                this.table.setPageSize(Number(e.target.value));
                this.render();
            });
        }

        // Pagination buttons
        this.setupPaginationListeners(container);
    }

    /**
     * Setup pagination event listeners
     */
    setupPaginationListeners(container) {
        const firstPage = container.querySelector('#firstPage');
        const prevPage = container.querySelector('#prevPage');
        const nextPage = container.querySelector('#nextPage');
        const lastPage = container.querySelector('#lastPage');
        const pageInput = container.querySelector('#pageInput');

        if (firstPage) {
            firstPage.addEventListener('click', () => {
                this.table.setPageIndex(0);
                this.render();
            });
        }

        if (prevPage) {
            prevPage.addEventListener('click', () => {
                this.table.previousPage();
                this.render();
            });
        }

        if (nextPage) {
            nextPage.addEventListener('click', () => {
                this.table.nextPage();
                this.render();
            });
        }

        if (lastPage) {
            lastPage.addEventListener('click', () => {
                this.table.setPageIndex(this.table.getPageCount() - 1);
                this.render();
            });
        }

        if (pageInput) {
            pageInput.addEventListener('change', (e) => {
                const page = e.target.value ? Number(e.target.value) - 1 : 0;
                this.table.setPageIndex(page);
                this.render();
            });
        }
    }

    /**
     * Render the complete table
     */
    render() {
        this.renderHeaders();
        this.renderBody();
        this.updatePaginationInfo();
    }

    /**
     * Render table headers
     */
    renderHeaders() {
        const container = document.getElementById(this.containerId);
        const tableElement = container?.querySelector('.tanstack-table');
        if (!tableElement) {
            console.error('❌ No se encontró el elemento tabla');
            return;
        }

        const thead = tableElement.querySelector('thead');
        thead.innerHTML = '';
        
        this.table.getHeaderGroups().forEach(headerGroup => {
            const row = document.createElement('tr');
            
            headerGroup.headers.forEach(header => {
                const th = document.createElement('th');
                th.className = 'tanstack-table th';
                
                if (header.column.getCanSort && header.column.getCanSort()) {
                    th.classList.add('sortable');
                    th.addEventListener('click', () => {
                        if (header.column.toggleSorting) {
                            header.column.toggleSorting();
                            this.render();
                        }
                    });
                }
                
                th.innerHTML = `
                    <div class="sort-indicator">
                        <span>${header.isPlaceholder ? '' : header.column.columnDef.header}</span>
                        ${(header.column.getIsSorted && header.column.getIsSorted()) ? 
                            (header.column.getIsSorted() === 'desc' ? 
                                '<span class="sort-icon active">↓</span>' : 
                                '<span class="sort-icon active">↑</span>') : 
                            '<span class="sort-icon">↕</span>'}
                    </div>
                `;
                
                row.appendChild(th);
            });
            
            thead.appendChild(row);
        });
    }

    /**
     * Render table body
     */
    renderBody() {
        const container = document.getElementById(this.containerId);
        const tableElement = container?.querySelector('.tanstack-table');
        if (!tableElement) return;

        const tbody = tableElement.querySelector('tbody');
        
        // Clear loading state explicitly
        const loadingRow = tbody.querySelector('#table-loading-row');
        if (loadingRow) {
            loadingRow.remove();
        }
        tbody.innerHTML = '';
        
        this.table.getRowModel().rows.forEach(row => {
            const tr = document.createElement('tr');
            tr.className = 'tanstack-table tr';
            
            row.getVisibleCells().forEach(cell => {
                const td = document.createElement('td');
                td.className = 'tanstack-table td';
                td.textContent = cell.renderValue() || '-';
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
    }

    /**
     * Update pagination information and controls
     */
    updatePaginationInfo() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        const currentPage = this.table.getState().pagination.pageIndex + 1;
        const totalPages = this.table.getPageCount();
        const pageSize = this.table.getState().pagination.pageSize;
        const totalRows = this.table.getFilteredRowModel().rows.length;
        const startRow = this.table.getState().pagination.pageIndex * pageSize + 1;
        const endRow = Math.min(startRow + pageSize - 1, totalRows);

        // Update page info
        const pageInfo = container.querySelector('#pageInfo');
        if (pageInfo) {
            pageInfo.textContent = `${startRow}-${endRow} de ${totalRows}`;
        }

        // Update row count display
        const tableRowCount = container.querySelector('#table-row-count');
        if (tableRowCount) {
            tableRowCount.textContent = `${totalRows} rows`;
        }

        const totalPagesSpan = container.querySelector('#totalPages');
        if (totalPagesSpan) {
            totalPagesSpan.textContent = totalPages;
        }

        const pageInput = container.querySelector('#pageInput');
        if (pageInput) {
            pageInput.value = currentPage;
        }

        // Update button states
        const firstPage = container.querySelector('#firstPage');
        const prevPage = container.querySelector('#prevPage');
        const nextPage = container.querySelector('#nextPage');
        const lastPage = container.querySelector('#lastPage');

        if (firstPage) firstPage.disabled = !this.table.getCanPreviousPage();
        if (prevPage) prevPage.disabled = !this.table.getCanPreviousPage();
        if (nextPage) nextPage.disabled = !this.table.getCanNextPage();
        if (lastPage) lastPage.disabled = !this.table.getCanNextPage();
    }

    /**
     * Render empty state
     */
    renderEmpty() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        // Update row count for empty state
        const tableRowCount = container.querySelector('#table-row-count');
        if (tableRowCount) {
            tableRowCount.textContent = '0 rows';
        }

        container.innerHTML = `
            <div class="flex items-center justify-center h-32 text-gray-500">
                <p>No hay datos disponibles para mostrar</p>
            </div>
        `;
    }

    /**
     * Render error state
     */
    renderError(error) {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        // Update row count for error state
        const tableRowCount = container.querySelector('#table-row-count');
        if (tableRowCount) {
            tableRowCount.textContent = 'Error loading';
        }

        container.innerHTML = `
            <div class="flex items-center justify-center h-32 text-red-500">
                <p>Error cargando la tabla: ${error.message}</p>
            </div>
        `;
    }

    /**
     * Update table data
     */
    updateData(newData) {
        this.data = newData || [];
        if (this.table) {
            this.createTable();
            this.render();
        }
    }

    /**
     * Get current table state
     */
    getState() {
        return this.table ? this.table.getState() : this.state;
    }

    /**
     * Export filtered data
     */
    getFilteredData() {
        return this.table ? this.table.getFilteredRowModel().rows.map(row => row.original) : [];
    }
}

// Export for global usage
window.HydroMLTanStackTable = HydroMLTanStackTable;

// Initialize function exposed globally for CDN callback
window.initializeTanStackTable = function() {
    console.log('🚀 TanStack Table initialization called');
    
    // Wait for data to be available
    function initializeTable() {
        if (window.gridRowData && window.columnDefsData && window.TableCore) {
            console.log('📊 Initializing TanStack Table with data:', {
                rows: window.gridRowData.length,
                columns: window.columnDefsData.length
            });
            
            // Initialize table
            const tableInstance = new HydroMLTanStackTable('tanstack-table-container', {
                pageSize: 25,
                debugMode: true
            });
            
            tableInstance.init(window.gridRowData, window.columnDefsData);
            
            // Store globally for debugging
            window.hydroMLTable = tableInstance;
            
        } else {
            console.log('⏳ Waiting for data and library to load...');
            setTimeout(initializeTable, 100);
        }
    }
    
    // Start initialization
    initializeTable();
};

// Auto-initialize when DOM is ready (fallback if CDN callback doesn't work)
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM loaded, checking for TanStack Table...');
    
    // Try immediate initialization if library is already loaded
    if (window.TableCore) {
        window.initializeTanStackTable();
    } else {
        // Wait for library to load
        setTimeout(() => {
            if (window.TableCore) {
                window.initializeTanStackTable();
            } else {
                console.warn('⚠️ TanStack Table library still not loaded after DOM ready');
            }
        }, 500);
    }
});