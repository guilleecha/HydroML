/**
 * WaveTable - Professional data table component with sorting, filtering, and pagination
 * Part of HydroML Wave-Inspired Component Library
 * 
 * Features:
 * - Monochromatic design with subtle highlights
 * - Column sorting and filtering
 * - Row selection and bulk actions
 * - Responsive design with mobile adaptations
 * - Loading states and empty states
 * - Pagination integration
 * - Export functionality
 */

class WaveTable extends DataComponent {
    constructor() {
        super('WaveTable');
        
        this.defaultConfig = {
            // Data configuration
            data: [],
            columns: [],
            keyField: 'id',
            
            // Feature toggles
            sortable: true,
            filterable: true,
            selectable: false,
            multiSelect: true,
            searchable: true,
            
            // Pagination
            paginated: true,
            pageSize: 10,
            pageSizeOptions: [5, 10, 25, 50, 100],
            
            // Styling
            striped: true,
            bordered: true,
            hover: true,
            compact: false,
            
            // Responsive behavior
            responsive: true,
            stackOnMobile: true,
            
            // Loading and empty states
            loading: false,
            loadingText: 'Loading data...',
            emptyText: 'No data available',
            emptyIcon: 'database',
            
            // Export options
            exportable: false,
            exportFormats: ['csv', 'json']
        };
        
        this.sortField = null;
        this.sortDirection = 'asc';
        this.selectedRows = new Set();
        this.currentPage = 1;
        this.searchQuery = '';
        this.columnFilters = new Map();
    }

    init(element, config = {}) {
        super.init(element, config);
        
        this.tableElement = this.element.querySelector('table');
        this.headerElement = this.element.querySelector('thead');
        this.bodyElement = this.element.querySelector('tbody');
        this.searchInput = this.element.querySelector('.wave-table-search');
        this.paginationElement = this.element.querySelector('.wave-table-pagination');
        this.bulkActionsElement = this.element.querySelector('.wave-table-bulk-actions');
        this.exportButton = this.element.querySelector('.wave-table-export');
        
        this.setupEventListeners();
        this.renderTable();
        
        return this.getAlpineData();
    }

    getAlpineData() {
        return {
            // State
            data: this.config.data,
            loading: this.config.loading,
            currentPage: this.currentPage,
            pageSize: this.config.pageSize,
            searchQuery: this.searchQuery,
            sortField: this.sortField,
            sortDirection: this.sortDirection,
            selectedRows: Array.from(this.selectedRows),
            
            // Computed
            get filteredData() {
                let result = this.data;
                
                // Apply search filter
                if (this.searchQuery) {
                    result = result.filter(row => 
                        Object.values(row).some(value => 
                            String(value).toLowerCase().includes(this.searchQuery.toLowerCase())
                        )
                    );
                }
                
                // Apply column filters
                for (const [column, filter] of this.columnFilters) {
                    if (filter) {
                        result = result.filter(row => 
                            String(row[column]).toLowerCase().includes(filter.toLowerCase())
                        );
                    }
                }
                
                return result;
            },
            
            get sortedData() {
                if (!this.sortField) return this.filteredData;
                
                return [...this.filteredData].sort((a, b) => {
                    const aVal = a[this.sortField];
                    const bVal = b[this.sortField];
                    
                    let comparison = 0;
                    if (aVal < bVal) comparison = -1;
                    if (aVal > bVal) comparison = 1;
                    
                    return this.sortDirection === 'desc' ? -comparison : comparison;
                });
            },
            
            get paginatedData() {
                if (!this.config.paginated) return this.sortedData;
                
                const start = (this.currentPage - 1) * this.pageSize;
                const end = start + this.pageSize;
                return this.sortedData.slice(start, end);
            },
            
            get totalPages() {
                return Math.ceil(this.sortedData.length / this.pageSize);
            },
            
            get totalItems() {
                return this.sortedData.length;
            },
            
            get hasSelection() {
                return this.selectedRows.length > 0;
            },
            
            get isAllSelected() {
                return this.selectedRows.length === this.paginatedData.length && this.paginatedData.length > 0;
            },
            
            get isPartiallySelected() {
                return this.selectedRows.length > 0 && this.selectedRows.length < this.paginatedData.length;
            },

            // Table styling
            get tableClasses() {
                const base = 'wave-table w-full';
                const striped = this.config.striped ? 'wave-table-striped' : '';
                const bordered = this.config.bordered ? 'border border-gray-200' : '';
                const hover = this.config.hover ? 'wave-table-hover' : '';
                const compact = this.config.compact ? 'wave-table-compact' : '';
                const responsive = this.config.responsive ? 'wave-table-responsive' : '';
                
                return `${base} ${striped} ${bordered} ${hover} ${compact} ${responsive}`.trim();
            },
            
            get containerClasses() {
                const base = 'wave-table-container';
                const responsive = this.config.responsive ? 'overflow-x-auto' : '';
                const loading = this.loading ? 'wave-table-loading' : '';
                
                return `${base} ${responsive} ${loading}`.trim();
            },

            // Methods
            handleSort: (column) => {
                if (!this.config.sortable || !column.sortable) return;
                
                if (this.sortField === column.key) {
                    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    this.sortField = column.key;
                    this.sortDirection = 'asc';
                }
                
                this.emit('sort', { 
                    field: this.sortField, 
                    direction: this.sortDirection,
                    data: this.sortedData
                });
            },
            
            handleSearch: (query) => {
                this.searchQuery = query;
                this.currentPage = 1; // Reset to first page
                this.emit('search', { query, results: this.filteredData });
            },
            
            handleColumnFilter: (column, filter) => {
                this.columnFilters.set(column, filter);
                this.currentPage = 1; // Reset to first page
                this.emit('filter', { column, filter, data: this.filteredData });
            },
            
            handleRowSelect: (row, selected) => {
                const rowKey = row[this.config.keyField];
                
                if (selected) {
                    this.selectedRows.add(rowKey);
                } else {
                    this.selectedRows.delete(rowKey);
                }
                
                this.emit('row-select', { 
                    row, 
                    selected, 
                    selectedRows: Array.from(this.selectedRows) 
                });
            },
            
            handleSelectAll: (selected) => {
                if (selected) {
                    this.paginatedData.forEach(row => {
                        this.selectedRows.add(row[this.config.keyField]);
                    });
                } else {
                    this.paginatedData.forEach(row => {
                        this.selectedRows.delete(row[this.config.keyField]);
                    });
                }
                
                this.emit('select-all', { 
                    selected, 
                    selectedRows: Array.from(this.selectedRows) 
                });
            },
            
            handlePageChange: (page) => {
                if (page < 1 || page > this.totalPages) return;
                
                this.currentPage = page;
                this.emit('page-change', { 
                    page, 
                    pageSize: this.pageSize,
                    data: this.paginatedData
                });
            },
            
            handlePageSizeChange: (size) => {
                this.pageSize = parseInt(size);
                this.currentPage = 1; // Reset to first page
                this.emit('page-size-change', { 
                    pageSize: this.pageSize,
                    data: this.paginatedData
                });
            },
            
            // Row and cell rendering
            getCellValue: (row, column) => {
                if (column.render && typeof column.render === 'function') {
                    return column.render(row[column.key], row);
                }
                
                if (column.formatter && typeof column.formatter === 'function') {
                    return column.formatter(row[column.key]);
                }
                
                return row[column.key] || '';
            },
            
            getCellClasses: (row, column) => {
                const base = 'wave-table-cell px-4 py-3 text-sm';
                const alignment = column.align ? `text-${column.align}` : 'text-left';
                const width = column.width ? `w-${column.width}` : '';
                const custom = column.cellClass || '';
                
                return `${base} ${alignment} ${width} ${custom}`.trim();
            },
            
            getRowClasses: (row, index) => {
                const base = 'wave-table-row border-b border-gray-200 last:border-b-0';
                const hover = this.config.hover ? 'hover:bg-gray-50' : '';
                const selected = this.selectedRows.has(row[this.config.keyField]) ? 'bg-blue-50' : '';
                const striped = this.config.striped && index % 2 === 1 ? 'bg-gray-50' : '';
                
                return `${base} ${hover} ${selected} ${striped}`.trim();
            },
            
            // Header rendering
            getHeaderClasses: (column) => {
                const base = 'wave-table-header px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
                const sortable = this.config.sortable && column.sortable ? 'cursor-pointer hover:text-gray-700' : '';
                const sorted = this.sortField === column.key ? 'text-gray-700' : '';
                
                return `${base} ${sortable} ${sorted}`.trim();
            },
            
            getSortIcon: (column) => {
                if (!this.config.sortable || !column.sortable || this.sortField !== column.key) {
                    return `
                        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"></path>
                        </svg>
                    `;
                }
                
                if (this.sortDirection === 'asc') {
                    return `
                        <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"></path>
                        </svg>
                    `;
                }
                
                return `
                    <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4"></path>
                    </svg>
                `;
            },
            
            // Export functionality
            handleExport: (format) => {
                const data = this.selectedRows.size > 0 ? 
                    this.sortedData.filter(row => this.selectedRows.has(row[this.config.keyField])) :
                    this.sortedData;
                
                if (format === 'csv') {
                    this.exportAsCSV(data);
                } else if (format === 'json') {
                    this.exportAsJSON(data);
                }
                
                this.emit('export', { format, data, rowCount: data.length });
            },
            
            exportAsCSV: (data) => {
                const headers = this.config.columns.map(col => col.title || col.key);
                const rows = data.map(row => 
                    this.config.columns.map(col => 
                        JSON.stringify(this.getCellValue(row, col))
                    )
                );
                
                const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
                this.downloadFile(csv, 'table-data.csv', 'text/csv');
            },
            
            exportAsJSON: (data) => {
                const json = JSON.stringify(data, null, 2);
                this.downloadFile(json, 'table-data.json', 'application/json');
            }
        };
    }

    setupEventListeners() {
        // Search input handling
        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.debounce((event) => {
                this.searchQuery = event.target.value;
                this.currentPage = 1;
                this.emit('search', { query: this.searchQuery, results: this.getFilteredData() });
            }, 300));
        }
        
        // Export button handling
        if (this.exportButton) {
            this.exportButton.addEventListener('click', () => {
                // Show export format options
                this.showExportOptions();
            });
        }
    }

    renderTable() {
        if (!this.tableElement) return;
        
        this.renderHeader();
        this.renderBody();
        this.renderPagination();
    }

    renderHeader() {
        if (!this.headerElement || !this.config.columns.length) return;
        
        let headerHTML = '<tr>';
        
        // Selection column
        if (this.config.selectable) {
            headerHTML += `
                <th class="wave-table-header px-4 py-3 w-12">
                    <input type="checkbox" 
                           class="wave-table-select-all rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                           ${this.isAllSelected ? 'checked' : ''}
                           ${this.isPartiallySelected ? 'indeterminate' : ''}>
                </th>
            `;
        }
        
        // Data columns
        this.config.columns.forEach(column => {
            const sortable = this.config.sortable && column.sortable;
            const classes = this.getHeaderClasses(column);
            
            headerHTML += `
                <th class="${classes}" ${sortable ? 'data-sortable="true"' : ''}>
                    <div class="flex items-center gap-2">
                        <span>${column.title || column.key}</span>
                        ${sortable ? this.getSortIcon(column) : ''}
                    </div>
                </th>
            `;
        });
        
        headerHTML += '</tr>';
        this.headerElement.innerHTML = headerHTML;
    }

    renderBody() {
        if (!this.bodyElement) return;
        
        const data = this.getPaginatedData();
        
        if (this.config.loading) {
            this.renderLoadingState();
            return;
        }
        
        if (data.length === 0) {
            this.renderEmptyState();
            return;
        }
        
        let bodyHTML = '';
        
        data.forEach((row, index) => {
            const rowClasses = this.getRowClasses(row, index);
            const rowKey = row[this.config.keyField];
            
            bodyHTML += `<tr class="${rowClasses}" data-row-key="${rowKey}">`;
            
            // Selection column
            if (this.config.selectable) {
                const checked = this.selectedRows.has(rowKey);
                bodyHTML += `
                    <td class="wave-table-cell px-4 py-3 w-12">
                        <input type="checkbox" 
                               class="wave-table-row-select rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                               ${checked ? 'checked' : ''}
                               data-row-key="${rowKey}">
                    </td>
                `;
            }
            
            // Data columns
            this.config.columns.forEach(column => {
                const cellClasses = this.getCellClasses(row, column);
                const cellValue = this.getCellValue(row, column);
                
                bodyHTML += `<td class="${cellClasses}">${cellValue}</td>`;
            });
            
            bodyHTML += '</tr>';
        });
        
        this.bodyElement.innerHTML = bodyHTML;
    }

    renderLoadingState() {
        const colspan = this.config.columns.length + (this.config.selectable ? 1 : 0);
        
        this.bodyElement.innerHTML = `
            <tr>
                <td colspan="${colspan}" class="px-4 py-8 text-center text-gray-500">
                    <div class="flex items-center justify-center gap-3">
                        <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        ${this.config.loadingText}
                    </div>
                </td>
            </tr>
        `;
    }

    renderEmptyState() {
        const colspan = this.config.columns.length + (this.config.selectable ? 1 : 0);
        
        this.bodyElement.innerHTML = `
            <tr>
                <td colspan="${colspan}" class="px-4 py-8 text-center text-gray-500">
                    <div class="flex flex-col items-center gap-3">
                        <svg class="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            ${this.getIconPath(this.config.emptyIcon)}
                        </svg>
                        <p class="text-lg font-medium">${this.config.emptyText}</p>
                    </div>
                </td>
            </tr>
        `;
    }

    getIconPath(iconName) {
        const icons = {
            database: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4"></path>',
            search: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>'
        };
        
        return icons[iconName] || icons.database;
    }

    // Public API
    setData(data) {
        this.config.data = data;
        this.currentPage = 1;
        this.selectedRows.clear();
        this.renderTable();
        this.emit('data-change', { data });
    }

    addRow(row) {
        this.config.data.push(row);
        this.renderTable();
        this.emit('row-add', { row });
    }

    removeRow(rowKey) {
        this.config.data = this.config.data.filter(row => row[this.config.keyField] !== rowKey);
        this.selectedRows.delete(rowKey);
        this.renderTable();
        this.emit('row-remove', { rowKey });
    }

    updateRow(rowKey, updates) {
        const rowIndex = this.config.data.findIndex(row => row[this.config.keyField] === rowKey);
        if (rowIndex !== -1) {
            this.config.data[rowIndex] = { ...this.config.data[rowIndex], ...updates };
            this.renderTable();
            this.emit('row-update', { rowKey, updates });
        }
    }

    getSelectedRows() {
        return this.config.data.filter(row => this.selectedRows.has(row[this.config.keyField]));
    }

    clearSelection() {
        this.selectedRows.clear();
        this.renderTable();
        this.emit('selection-clear');
    }

    setLoading(loading) {
        this.config.loading = loading;
        this.renderBody();
        this.emit('loading-change', { loading });
    }

    refresh() {
        this.renderTable();
        this.emit('refresh');
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveTable;
}

// Register with ComponentRegistry if available
if (typeof window !== 'undefined' && window.ComponentRegistry) {
    window.ComponentRegistry.register('WaveTable', WaveTable);
}