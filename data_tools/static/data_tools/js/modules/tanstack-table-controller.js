/**
 * TanStackTableController - Modern Data Grid with TanStack Table
 * Responsabilidad única: Gestión de tabla de datos usando TanStack Table
 * 
 * Filosofía: Headless, performance-first, NO OVER-ENGINEERING
 */

// TanStack Table will be available from CDN as window.TableCore
// We'll create our own simplified implementation for non-React usage

class TanStackTableController {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            enableSorting: true,
            enableFiltering: true,
            enablePagination: true,
            pageSize: 25,
            ...options
        };
        
        // Data state
        this.data = [];
        this.columns = [];
        this.filters = [];
        this.sorting = [];
        this.pagination = {
            pageIndex: 0,
            pageSize: this.options.pageSize
        };
        
        // TanStack Table instance
        this.table = null;
        
        // Event system
        this.listeners = new Map();
        
        this.init();
    }

    // === INITIALIZATION ===

    init() {
        try {
            if (!this.container) {
                throw new Error(`Container element with ID '${this.containerId}' not found`);
            }

            // Initialize TanStack Table functions
            this.initializeTanStackFunctions();

            // Create React-like state management
            this.createTable();
            this.render();
            
            // Setup resize observer for responsive behavior
            this.setupResizeObserver();
            
            this.dispatchEvent('table-initialized', {
                rowCount: this.data.length,
                columnCount: this.columns.length
            });
            
            return { success: true };
            
        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleGridError(error, {
                    operation: 'tanstack_table_initialization',
                    containerId: this.containerId
                });
            } else {
                console.error('TanStack Table initialization failed:', error);
            }
            return { success: false, error: error.message };
        }
    }

    initializeTanStackFunctions() {
        // Check if TanStack Table library is loaded
        if (typeof window.TableCore !== 'undefined') {
            // Access TanStack Table functions from loaded library
            this.getCoreRowModel = window.TableCore.getCoreRowModel;
            this.getSortedRowModel = window.TableCore.getSortedRowModel;
            this.getFilteredRowModel = window.TableCore.getFilteredRowModel;
            this.getPaginationRowModel = window.TableCore.getPaginationRowModel;
            this.createTableFunc = window.TableCore.createTable;
            console.log('✅ TanStack Table functions initialized successfully');
        } else {
            console.warn('⚠️ TanStack Table library not found, using simplified implementation');
            // Fallback to simplified implementations
            this.getCoreRowModel = () => ({ rows: this.data });
            this.getSortedRowModel = () => ({ rows: this.getFilteredData() });
            this.getFilteredRowModel = () => ({ rows: this.getFilteredData() });
            this.getPaginationRowModel = () => ({ rows: this.getCurrentPageData() });
            this.createTableFunc = null;
        }
    }

    createTable() {
        // Use TanStack Table's createTable if available, otherwise use simplified implementation
        if (this.createTableFunc && typeof this.createTableFunc === 'function') {
            // Use actual TanStack Table
            const tableConfig = {
                data: this.data,
                columns: this.columns,
                getCoreRowModel: this.getCoreRowModel(),
                state: {
                    sorting: this.sorting,
                    globalFilter: this.globalFilter,
                    pagination: this.pagination,
                },
                onSortingChange: (updaterOrValue) => {
                    this.sorting = typeof updaterOrValue === 'function' 
                        ? updaterOrValue(this.sorting) 
                        : updaterOrValue;
                    this.updateTable();
                },
                onGlobalFilterChange: (value) => {
                    this.globalFilter = value;
                    this.updateTable();
                },
                onPaginationChange: (updaterOrValue) => {
                    this.pagination = typeof updaterOrValue === 'function' 
                        ? updaterOrValue(this.pagination) 
                        : updaterOrValue;
                    this.updateTable();
                },
                // Enable features
                enableSorting: this.options.enableSorting,
                enableGlobalFilter: this.options.enableFiltering,
            };

            // Add optional row models
            if (this.options.enableSorting && this.getSortedRowModel) {
                tableConfig.getSortedRowModel = this.getSortedRowModel();
            }
            
            if (this.options.enableFiltering && this.getFilteredRowModel) {
                tableConfig.getFilteredRowModel = this.getFilteredRowModel();
            }
            
            if (this.options.enablePagination && this.getPaginationRowModel) {
                tableConfig.getPaginationRowModel = this.getPaginationRowModel();
            }

            try {
                this.table = this.createTableFunc(tableConfig);
                console.log('✅ TanStack Table instance created successfully');
            } catch (error) {
                console.warn('⚠️ Failed to create TanStack Table instance, using fallback:', error);
                this.table = this.createTableInstance(tableConfig);
            }
        } else {
            // Fallback to simplified implementation
            console.log('📝 Using simplified table implementation');
            const tableConfig = {
                data: this.data,
                columns: this.columns,
                enableSorting: this.options.enableSorting,
                enableGlobalFilter: this.options.enableFiltering,
            };
            this.table = this.createTableInstance(tableConfig);
        }
    }

    // Simulate React's useReactTable hook
    createTableInstance(config) {
        // This is a simplified implementation that mimics TanStack Table behavior
        // In a real React app, you'd use the actual useReactTable hook
        return {
            getHeaderGroups: () => this.getHeaderGroups(),
            getRowModel: () => this.getRowModel(),
            getState: () => ({
                sorting: this.sorting,
                globalFilter: this.globalFilter,
                pagination: this.pagination,
            }),
            setPageSize: (size) => {
                this.pagination.pageSize = size;
                this.updateTable();
            },
            setPageIndex: (index) => {
                this.pagination.pageIndex = index;
                this.updateTable();
            },
            getPageCount: () => Math.ceil(this.getFilteredData().length / this.pagination.pageSize),
            getCanPreviousPage: () => this.pagination.pageIndex > 0,
            getCanNextPage: () => this.pagination.pageIndex < this.getPageCount() - 1,
            previousPage: () => {
                if (this.getCanPreviousPage()) {
                    this.pagination.pageIndex--;
                    this.updateTable();
                }
            },
            nextPage: () => {
                if (this.getCanNextPage()) {
                    this.pagination.pageIndex++;
                    this.updateTable();
                }
            },
            firstPage: () => {
                this.pagination.pageIndex = 0;
                this.updateTable();
            },
            lastPage: () => {
                this.pagination.pageIndex = this.getPageCount() - 1;
                this.updateTable();
            },
        };
    }

    // === DATA MANAGEMENT ===

    setData(data) {
        this.data = Array.isArray(data) ? data : [];
        this.updateTable();
        
        this.dispatchEvent('data-updated', {
            rowCount: this.data.length,
            data: this.data
        });
    }

    setColumns(columnNames) {
        // Convert simple column names to TanStack Table format
        this.columns = this.convertColumnNames(columnNames);
        this.updateTable();
        
        this.dispatchEvent('columns-updated', {
            columnCount: this.columns.length,
            columns: this.columns
        });
    }

    convertColumnNames(columnNames) {
        if (!Array.isArray(columnNames)) return [];
        
        return columnNames.map(columnName => ({
            id: columnName,
            accessorKey: columnName,
            header: columnName,
            enableSorting: true,
            enableColumnFilter: true,
        }));
    }

    // === RENDERING ===

    render() {
        if (!this.table) return;

        const tableHTML = this.createTableHTML();
        this.container.innerHTML = tableHTML;
        
        // Attach event listeners after rendering
        this.attachEventListeners();
        
        this.dispatchEvent('table-rendered', {
            visibleRows: this.getCurrentPageData().length
        });
    }

    createTableHTML() {
        const headerGroups = this.getHeaderGroups();
        const rows = this.getCurrentPageData();
        
        return `
            <div class="tanstack-table-container">
                <!-- Search Input -->
                <div class="table-controls mb-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-4">
                            <input
                                type="text"
                                id="global-filter"
                                placeholder="Search all columns..."
                                value="${this.globalFilter || ''}"
                                class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                            />
                            <span class="text-sm text-gray-600 dark:text-gray-400">
                                ${this.getFilteredData().length} rows
                            </span>
                        </div>
                        <div class="flex items-center space-x-2">
                            <span class="text-sm text-gray-600 dark:text-gray-400">Rows per page:</span>
                            <select id="page-size" class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                                <option value="10" ${this.pagination.pageSize === 10 ? 'selected' : ''}>10</option>
                                <option value="25" ${this.pagination.pageSize === 25 ? 'selected' : ''}>25</option>
                                <option value="50" ${this.pagination.pageSize === 50 ? 'selected' : ''}>50</option>
                                <option value="100" ${this.pagination.pageSize === 100 ? 'selected' : ''}>100</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Table -->
                <div class="table-wrapper overflow-auto border border-gray-200 dark:border-gray-700 rounded-lg">
                    <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                        <thead class="bg-gray-50 dark:bg-gray-800">
                            ${headerGroups.map(headerGroup => `
                                <tr>
                                    ${headerGroup.headers.map(header => `
                                        <th
                                            class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 ${header.column.getIsSorted() ? 'bg-gray-100 dark:bg-gray-700' : ''}"
                                            data-column-id="${header.id}"
                                            style="${header.getSize() ? `width: ${header.getSize()}px` : ''}"
                                        >
                                            <div class="flex items-center space-x-1">
                                                <span>${header.isPlaceholder ? '' : header.column.columnDef.header}</span>
                                                ${header.column.getIsSorted() ? `
                                                    <span class="text-blue-600 dark:text-blue-400">
                                                        ${header.column.getIsSorted() === 'desc' ? '↓' : '↑'}
                                                    </span>
                                                ` : ''}
                                            </div>
                                        </th>
                                    `).join('')}
                                </tr>
                            `).join('')}
                        </thead>
                        <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                            ${rows.map((row, index) => `
                                <tr class="hover:bg-gray-50 dark:hover:bg-gray-800 ${index % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800'}">
                                    ${this.columns.map(column => `
                                        <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                                            ${this.getCellValue(row, column)}
                                        </td>
                                    `).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <!-- Pagination Controls -->
                ${this.createPaginationHTML()}
            </div>
        `;
    }

    createPaginationHTML() {
        const currentPage = this.pagination.pageIndex + 1;
        const totalPages = this.table.getPageCount();
        const canPrevious = this.table.getCanPreviousPage();
        const canNext = this.table.getCanNextPage();
        
        return `
            <div class="pagination-controls mt-4 flex items-center justify-between">
                <div class="flex items-center space-x-2">
                    <button 
                        id="first-page" 
                        ${!canPrevious ? 'disabled' : ''}
                        class="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        ‹‹ First
                    </button>
                    <button 
                        id="prev-page" 
                        ${!canPrevious ? 'disabled' : ''}
                        class="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        ‹ Previous
                    </button>
                    <span class="text-sm text-gray-700 dark:text-gray-300">
                        Page ${currentPage} of ${totalPages}
                    </span>
                    <button 
                        id="next-page" 
                        ${!canNext ? 'disabled' : ''}
                        class="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Next ›
                    </button>
                    <button 
                        id="last-page" 
                        ${!canNext ? 'disabled' : ''}
                        class="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        Last ››
                    </button>
                </div>
                <div class="text-sm text-gray-700 dark:text-gray-300">
                    Showing ${this.pagination.pageIndex * this.pagination.pageSize + 1} to ${Math.min((this.pagination.pageIndex + 1) * this.pagination.pageSize, this.getFilteredData().length)} of ${this.getFilteredData().length} entries
                </div>
            </div>
        `;
    }

    // === EVENT HANDLING ===

    attachEventListeners() {
        // Global filter
        const globalFilter = this.container.querySelector('#global-filter');
        if (globalFilter) {
            globalFilter.addEventListener('input', (e) => {
                this.globalFilter = e.target.value;
                this.pagination.pageIndex = 0; // Reset to first page
                this.updateTable();
            });
        }

        // Page size selector
        const pageSize = this.container.querySelector('#page-size');
        if (pageSize) {
            pageSize.addEventListener('change', (e) => {
                this.table.setPageSize(Number(e.target.value));
            });
        }

        // Pagination buttons
        this.container.querySelector('#first-page')?.addEventListener('click', () => this.table.firstPage());
        this.container.querySelector('#prev-page')?.addEventListener('click', () => this.table.previousPage());
        this.container.querySelector('#next-page')?.addEventListener('click', () => this.table.nextPage());
        this.container.querySelector('#last-page')?.addEventListener('click', () => this.table.lastPage());

        // Column sorting
        this.container.querySelectorAll('[data-column-id]').forEach(header => {
            header.addEventListener('click', () => {
                const columnId = header.dataset.columnId;
                this.toggleSort(columnId);
            });
        });
    }

    // === SORTING & FILTERING ===

    toggleSort(columnId) {
        const existingSort = this.sorting.find(s => s.id === columnId);
        
        if (!existingSort) {
            this.sorting = [{ id: columnId, desc: false }];
        } else if (!existingSort.desc) {
            this.sorting = [{ id: columnId, desc: true }];
        } else {
            this.sorting = [];
        }
        
        this.updateTable();
        
        this.dispatchEvent('sorting-changed', {
            sorting: this.sorting
        });
    }

    // === DATA PROCESSING ===

    getFilteredData() {
        let filtered = [...this.data];
        
        // Apply global filter
        if (this.globalFilter) {
            const filterValue = this.globalFilter.toLowerCase();
            filtered = filtered.filter(row => {
                return this.columns.some(column => {
                    const value = this.getCellValue(row, column);
                    return String(value).toLowerCase().includes(filterValue);
                });
            });
        }
        
        // Apply sorting
        if (this.sorting.length > 0) {
            const sort = this.sorting[0];
            const column = this.columns.find(c => c.id === sort.id);
            if (column) {
                filtered.sort((a, b) => {
                    const aVal = this.getCellValue(a, column);
                    const bVal = this.getCellValue(b, column);
                    
                    if (aVal < bVal) return sort.desc ? 1 : -1;
                    if (aVal > bVal) return sort.desc ? -1 : 1;
                    return 0;
                });
            }
        }
        
        return filtered;
    }

    getCurrentPageData() {
        const filtered = this.getFilteredData();
        const start = this.pagination.pageIndex * this.pagination.pageSize;
        const end = start + this.pagination.pageSize;
        return filtered.slice(start, end);
    }

    getCellValue(row, column) {
        const value = row[column.accessorKey];
        
        // Handle custom cell rendering
        if (column.cell && typeof column.cell === 'function') {
            return column.cell({ getValue: () => value });
        }
        
        return value !== null && value !== undefined ? value : '';
    }

    getHeaderGroups() {
        return [{
            id: 'header-group',
            headers: this.columns.map(column => ({
                id: column.id,
                isPlaceholder: false,
                column: {
                    columnDef: column,
                    getIsSorted: () => {
                        const sort = this.sorting.find(s => s.id === column.id);
                        return sort ? (sort.desc ? 'desc' : 'asc') : false;
                    },
                },
                getSize: () => column.size,
            }))
        }];
    }

    getRowModel() {
        return {
            rows: this.getCurrentPageData().map((row, index) => ({
                id: index,
                original: row,
                getVisibleCells: () => this.columns.map(column => ({
                    id: `${index}-${column.id}`,
                    column: { columnDef: column },
                    getValue: () => this.getCellValue(row, column),
                    getContext: () => ({ row: { original: row }, column })
                }))
            }))
        };
    }

    // === TABLE UPDATES ===

    updateTable() {
        if (this.table) {
            this.render();
        }
    }

    // === RESIZE HANDLING ===

    setupResizeObserver() {
        if (typeof ResizeObserver !== 'undefined') {
            this.resizeObserver = new ResizeObserver(() => {
                this.handleResize();
            });
            this.resizeObserver.observe(this.container);
        }
    }

    handleResize() {
        // Handle responsive behavior
        this.dispatchEvent('table-resized', {
            containerWidth: this.container.offsetWidth,
            containerHeight: this.container.offsetHeight
        });
    }

    // === PUBLIC API ===

    getData() {
        return this.data;
    }

    getFilteredRowCount() {
        return this.getFilteredData().length;
    }

    getTotalRowCount() {
        return this.data.length;
    }

    getSelectedRows() {
        // TODO: Implement row selection if needed
        return [];
    }

    exportData(format = 'json') {
        const data = this.getFilteredData();
        
        if (format === 'csv') {
            return this.convertToCSV(data);
        }
        
        return JSON.stringify(data, null, 2);
    }

    convertToCSV(data) {
        if (!data.length) return '';
        
        const headers = this.columns.map(col => col.header).join(',');
        const rows = data.map(row => 
            this.columns.map(col => {
                const value = this.getCellValue(row, col);
                return `"${String(value).replace(/"/g, '""')}"`;
            }).join(',')
        );
        
        return [headers, ...rows].join('\n');
    }

    // === EVENT SYSTEM ===

    addEventListener(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    removeEventListener(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    dispatchEvent(event, detail = {}) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback({ type: event, detail });
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }

        // Also dispatch as DOM event
        window.dispatchEvent(new CustomEvent(`tanstack-table-${event}`, { detail }));
    }

    // === CLEANUP ===

    destroy() {
        if (this.resizeObserver) {
            this.resizeObserver.disconnect();
        }
        
        this.listeners.clear();
        this.container.innerHTML = '';
        
        this.dispatchEvent('table-destroyed');
    }
}

// Export for use in other modules
window.TanStackTableController = TanStackTableController;