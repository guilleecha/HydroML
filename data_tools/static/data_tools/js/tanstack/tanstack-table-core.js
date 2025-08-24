/**
 * TanStack Table Core Implementation
 * Implementación vanilla JavaScript siguiendo documentación oficial de TanStack Table
 * 
 * Patrón de documentación: https://tanstack.com/table/latest/docs/vanilla
 */

class TanStackTableCore {
    constructor(containerId, options = {}) {
        // Configuración basada en patrones de documentación
        this.containerId = containerId;
        this.options = {
            enableSorting: true,
            enableFiltering: true,
            enablePagination: true,
            pageSize: 25,
            debugMode: false,
            ...options
        };
        
        // Estado de la tabla según documentación TanStack
        this.tableInstance = null;
        this.data = [];
        this.columns = [];
        this.state = {
            pagination: { pageIndex: 0, pageSize: this.options.pageSize },
            globalFilter: '',
            sorting: []
        };
        
        console.log('🚀 TanStack Table Core initialized:', this.options);
    }

    /**
     * Inicializar tabla con datos
     * Patrón de documentación: createTable({ columns, data })
     */
    async initialize(data, columns) {
        try {
            this.data = Array.isArray(data) ? data : [];
            this.columns = Array.isArray(columns) ? columns : [];
            
            if (this.data.length === 0) {
                this.renderEmptyState();
                return false;
            }

            // Verificar que TanStack Table esté disponible
            if (typeof window.TableCore === 'undefined') {
                console.error('❌ TanStack Table library not loaded');
                this.renderErrorState('TanStack Table library not available');
                return false;
            }

            await this.createTableInstance();
            this.setupEventListeners();
            this.render();
            
            console.log('✅ TanStack Table initialized successfully');
            return true;
            
        } catch (error) {
            console.error('❌ Failed to initialize TanStack Table:', error);
            this.renderErrorState(error.message);
            return false;
        }
    }

    /**
     * Crear instancia de tabla usando patrón oficial TanStack
     * Documentación: createTable(options)
     */
    async createTableInstance() {
        // Verificar y obtener funciones de TanStack
        let createTable, getCoreRowModel, getPaginationRowModel, getSortedRowModel, getFilteredRowModel;
        
        if (window.TableCore && typeof window.TableCore === 'object') {
            // Caso 1: window.TableCore es un objeto con las funciones
            ({
                createTable,
                getCoreRowModel,
                getPaginationRowModel,
                getSortedRowModel,
                getFilteredRowModel
            } = window.TableCore);
        } else if (window.TableCore && typeof window.TableCore.createTable === 'function') {
            // Caso 2: window.TableCore es directamente la función
            createTable = window.TableCore.createTable;
            getCoreRowModel = window.TableCore.getCoreRowModel;
            getPaginationRowModel = window.TableCore.getPaginationRowModel;
            getSortedRowModel = window.TableCore.getSortedRowModel;
            getFilteredRowModel = window.TableCore.getFilteredRowModel;
        } else {
            throw new Error('TanStack Table functions not available');
        }
        
        // Crear definiciones de columnas según documentación
        const columnDefs = this.columns.map(columnName => ({
            id: columnName,
            accessorKey: columnName,
            header: columnName,
            cell: info => {
                const value = info.getValue();
                return value !== null && value !== undefined ? String(value) : '-';
            },
            enableSorting: this.options.enableSorting,
            enableColumnFilter: this.options.enableFiltering
        }));

        // Crear tabla usando patrón oficial
        this.tableInstance = createTable({
            data: this.data,
            columns: columnDefs,
            getCoreRowModel: getCoreRowModel(),
            getPaginationRowModel: getPaginationRowModel(),
            getSortedRowModel: getSortedRowModel(),
            getFilteredRowModel: getFilteredRowModel(),
            state: this.state,
            onStateChange: (updater) => {
                const newState = typeof updater === 'function' ? updater(this.state) : updater;
                this.state = { ...this.state, ...newState };
                this.render();
            },
            globalFilterFn: 'includesString',
            debugTable: this.options.debugMode
        });
        
        console.log('✅ TanStack Table instance created');
    }

    /**
     * Configurar event listeners para controles
     */
    setupEventListeners() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        // Global filter
        const globalFilter = document.getElementById('global-filter-input');
        if (globalFilter) {
            globalFilter.addEventListener('input', (e) => {
                this.tableInstance.setGlobalFilter(e.target.value);
            });
        }

        // Page size selector
        const pageSize = document.getElementById('page-size-selector');
        if (pageSize) {
            pageSize.addEventListener('change', (e) => {
                this.tableInstance.setPageSize(Number(e.target.value));
            });
        }

        // Pagination buttons
        this.setupPaginationControls();
    }

    /**
     * Configurar controles de paginación
     */
    setupPaginationControls() {
        const buttons = {
            first: document.getElementById('first-page-btn'),
            prev: document.getElementById('prev-page-btn'),
            next: document.getElementById('next-page-btn'),
            last: document.getElementById('last-page-btn'),
            pageInput: document.getElementById('page-input')
        };

        if (buttons.first) {
            buttons.first.addEventListener('click', () => {
                this.tableInstance.setPageIndex(0);
            });
        }

        if (buttons.prev) {
            buttons.prev.addEventListener('click', () => {
                this.tableInstance.previousPage();
            });
        }

        if (buttons.next) {
            buttons.next.addEventListener('click', () => {
                this.tableInstance.nextPage();
            });
        }

        if (buttons.last) {
            buttons.last.addEventListener('click', () => {
                this.tableInstance.setPageIndex(this.tableInstance.getPageCount() - 1);
            });
        }

        if (buttons.pageInput) {
            buttons.pageInput.addEventListener('change', (e) => {
                const page = e.target.value ? Number(e.target.value) - 1 : 0;
                this.tableInstance.setPageIndex(page);
            });
        }
    }

    /**
     * Renderizar tabla completa
     */
    render() {
        if (!this.tableInstance) return;
        
        this.renderHeaders();
        this.renderBody();
        this.updatePaginationInfo();
        this.updateRowCount();
    }

    /**
     * Renderizar headers de la tabla
     */
    renderHeaders() {
        const thead = document.getElementById('table-head');
        if (!thead) return;

        thead.innerHTML = '';
        
        this.tableInstance.getHeaderGroups().forEach(headerGroup => {
            const row = document.createElement('tr');
            
            headerGroup.headers.forEach(header => {
                const th = document.createElement('th');
                th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
                
                if (header.column.getCanSort && header.column.getCanSort()) {
                    th.classList.add('cursor-pointer', 'hover:bg-gray-100');
                    th.addEventListener('click', () => {
                        if (header.column.toggleSorting) {
                            header.column.toggleSorting();
                        }
                    });
                }
                
                const sortIcon = (header.column.getIsSorted && header.column.getIsSorted()) ? 
                    (header.column.getIsSorted() === 'desc' ? ' ↓' : ' ↑') : '';
                
                th.textContent = header.isPlaceholder ? '' : header.column.columnDef.header + sortIcon;
                row.appendChild(th);
            });
            
            thead.appendChild(row);
        });
    }

    /**
     * Renderizar body de la tabla
     */
    renderBody() {
        const tbody = document.getElementById('table-body');
        if (!tbody) return;

        tbody.innerHTML = '';
        
        this.tableInstance.getRowModel().rows.forEach(row => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50';
            
            row.getVisibleCells().forEach(cell => {
                const td = document.createElement('td');
                td.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-900';
                
                const value = cell.renderValue();
                td.textContent = value || '-';
                
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
    }

    /**
     * Actualizar información de paginación
     */
    updatePaginationInfo() {
        if (!this.tableInstance) return;

        const currentPage = this.tableInstance.getState().pagination.pageIndex + 1;
        const totalPages = this.tableInstance.getPageCount();
        const pageSize = this.tableInstance.getState().pagination.pageSize;
        const totalRows = this.tableInstance.getFilteredRowModel().rows.length;
        const startRow = (currentPage - 1) * pageSize + 1;
        const endRow = Math.min(startRow + pageSize - 1, totalRows);

        // Actualizar displays
        const pageInfo = document.getElementById('pagination-info');
        if (pageInfo) {
            pageInfo.textContent = `${startRow}-${endRow} de ${totalRows}`;
        }

        const totalPagesSpan = document.getElementById('total-pages-span');
        if (totalPagesSpan) {
            totalPagesSpan.textContent = totalPages;
        }

        const pageInput = document.getElementById('page-input');
        if (pageInput) {
            pageInput.value = currentPage;
        }

        // Actualizar estados de botones
        const buttons = {
            first: document.getElementById('first-page-btn'),
            prev: document.getElementById('prev-page-btn'),
            next: document.getElementById('next-page-btn'),
            last: document.getElementById('last-page-btn')
        };

        const canPrev = this.tableInstance.getCanPreviousPage();
        const canNext = this.tableInstance.getCanNextPage();

        if (buttons.first) buttons.first.disabled = !canPrev;
        if (buttons.prev) buttons.prev.disabled = !canPrev;
        if (buttons.next) buttons.next.disabled = !canNext;
        if (buttons.last) buttons.last.disabled = !canNext;
    }

    /**
     * Actualizar contador de filas
     */
    updateRowCount() {
        const rowCount = document.getElementById('table-row-count');
        if (rowCount && this.tableInstance) {
            const total = this.tableInstance.getCoreRowModel().rows.length;
            const filtered = this.tableInstance.getFilteredRowModel().rows.length;
            
            if (total === filtered) {
                rowCount.textContent = `${total} filas`;
            } else {
                rowCount.textContent = `${filtered} de ${total} filas`;
            }
        }
    }

    /**
     * Renderizar estado vacío
     */
    renderEmptyState() {
        const tbody = document.getElementById('table-body');
        if (!tbody) return;

        tbody.innerHTML = `
            <tr>
                <td colspan="100%" class="px-6 py-8 text-center text-gray-500">
                    <div class="flex flex-col items-center">
                        <svg class="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                        <p>No hay datos disponibles para mostrar</p>
                    </div>
                </td>
            </tr>
        `;
    }

    /**
     * Renderizar estado de error
     */
    renderErrorState(message) {
        const tbody = document.getElementById('table-body');
        if (!tbody) return;

        tbody.innerHTML = `
            <tr>
                <td colspan="100%" class="px-6 py-8 text-center text-red-500">
                    <div class="flex flex-col items-center">
                        <svg class="w-12 h-12 text-red-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        <p>Error cargando la tabla: ${message}</p>
                    </div>
                </td>
            </tr>
        `;
    }

    /**
     * API pública para actualizar datos
     */
    updateData(newData) {
        this.data = Array.isArray(newData) ? newData : [];
        if (this.tableInstance) {
            this.createTableInstance();
            this.render();
        }
    }

    /**
     * API pública para obtener datos filtrados
     */
    getFilteredData() {
        return this.tableInstance ? 
            this.tableInstance.getFilteredRowModel().rows.map(row => row.original) : 
            [];
    }
}

// Exportar globalmente para uso en Django
window.TanStackTableCore = TanStackTableCore;