/**
 * TanStack Table Component for HydroML
 * Vanilla JavaScript implementation for data tables
 */

class HydroMLTanStackTable {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.options = {
            pageSize: 10,
            enableSorting: true,
            enableFiltering: true,
            enablePagination: true,
            debugMode: false,
            ...options
        };
        
        this.table = null;
        this.data = [];
        this.columns = [];
        
        console.log('🚀 HydroMLTanStackTable inicializada:', { containerId, options: this.options });
    }

    /**
     * Initialize the table with data and columns
     */
    init(data, columns) {
        this.data = data || [];
        this.columns = columns || [];
        
        if (this.options.debugMode) {
            console.log('📊 Datos recibidos:', { 
                dataLength: this.data.length, 
                columnsLength: this.columns.length 
            });
        }
        
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
        // Create column definitions
        const columnDefs = this.columns.map(columnName => ({
            id: columnName,
            accessorKey: columnName,
            header: columnName,
            cell: info => {
                const value = info.getValue();
                return value !== null && value !== undefined ? String(value).slice(0, 50) : '-';
            },
            enableSorting: this.options.enableSorting,
            enableColumnFilter: this.options.enableFiltering,
        }));

        if (this.options.debugMode) {
            console.log('📋 Columnas definidas:', columnDefs.length);
        }

        // Create table instance
        this.table = TableCore.createTable({
            data: this.data,
            columns: columnDefs,
            getCoreRowModel: TableCore.getCoreRowModel(),
            getPaginationRowModel: TableCore.getPaginationRowModel(),
            getSortedRowModel: TableCore.getSortedRowModel(),
            getFilteredRowModel: TableCore.getFilteredRowModel(),
            globalFilterFn: 'includesString',
            initialState: {
                pagination: {
                    pageSize: this.options.pageSize
                }
            },
            debugTable: this.options.debugMode,
        });
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
                
                if (header.column.getCanSort()) {
                    th.classList.add('sortable');
                    th.addEventListener('click', () => {
                        header.column.toggleSorting();
                        this.render();
                    });
                }
                
                th.innerHTML = `
                    <div class="sort-indicator">
                        <span>${header.isPlaceholder ? '' : header.column.columnDef.header}</span>
                        ${header.column.getIsSorted() ? 
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

        container.innerHTML = `
            <div class="tanstack-table-empty">
                <p>No hay datos disponibles para mostrar</p>
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
        return this.table ? this.table.getState() : null;
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