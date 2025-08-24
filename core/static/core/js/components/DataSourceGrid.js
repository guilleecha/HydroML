/**
 * DataSourceGrid - Reusable AG Grid Component for Data Sources
 * Extracted from projects/templates/projects/datasources_list.html
 * Provides consistent data source grid functionality across the application
 */

class DataSourceGrid {
    constructor(containerId, datasources = []) {
        this.containerId = containerId;
        this.datasources = datasources;
        this.gridApi = null;
        this.gridOptions = null;
        this.init();
    }

    /**
     * Status badge renderer for AG Grid cells
     */
    statusRenderer(params) {
        const status = params.value;
        let badgeClass = '';
        let statusText = '';
        
        switch(status) {
            case 'READY':
                badgeClass = 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800';
                statusText = 'Listo';
                break;
            case 'PROCESSING':
                badgeClass = 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-800';
                statusText = 'Procesando';
                break;
            case 'FAILED':
                badgeClass = 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800';
                statusText = 'Error';
                break;
            default:
                badgeClass = 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-900/20 dark:text-gray-400 dark:border-gray-800';
                statusText = status;
        }
        
        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${badgeClass}">${statusText}</span>`;
    }

    /**
     * Actions renderer for AG Grid cells with Edit and Delete buttons
     */
    actionsRenderer(params) {
        const datasourceId = params.data.id;
        const editUrl = `/projects/datasource/${datasourceId}/edit/`;
        const deleteUrl = `/projects/datasource/${datasourceId}/delete/`;
        
        return `
            <div class="flex items-center space-x-2">
                <a href="${editUrl}" 
                   class="inline-flex items-center px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                   title="Editar fuente de datos">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                    </svg>
                    Editar
                </a>
                <a href="${deleteUrl}" 
                   class="inline-flex items-center px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                   title="Eliminar fuente de datos"
                   onclick="return confirm('¿Estás seguro de que deseas eliminar esta fuente de datos?')">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                    </svg>
                    Eliminar
                </a>
            </div>`;
    }

    /**
     * Format file size in human readable format
     */
    formatFileSize(bytes) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * File size renderer for AG Grid cells
     */
    fileSizeRenderer(params) {
        return this.formatFileSize(params.value);
    }

    /**
     * Date formatter for AG Grid cells
     */
    dateRenderer(params) {
        if (!params.value) return '';
        const date = new Date(params.value);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Initialize grid options and column definitions
     */
    init() {
        this.gridOptions = {
            columnDefs: [
                {
                    field: 'name',
                    headerName: 'Nombre',
                    flex: 2,
                    minWidth: 200,
                    cellRenderer: params => {
                        const name = params.value;
                        const description = params.data.description || 'Sin descripción';
                        return `
                            <div class="py-2">
                                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">${name}</div>
                                <div class="text-sm text-gray-500 dark:text-gray-400 truncate">${description}</div>
                            </div>`;
                    }
                },
                {
                    field: 'format',
                    headerName: 'Formato',
                    width: 100,
                    cellRenderer: params => {
                        const format = params.value?.toUpperCase() || 'N/A';
                        const formatClass = {
                            'CSV': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
                            'JSON': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
                            'XML': 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
                            'PARQUET': 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400'
                        }[format] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
                        
                        return `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${formatClass}">${format}</span>`;
                    }
                },
                {
                    field: 'status',
                    headerName: 'Estado',
                    width: 120,
                    cellRenderer: this.statusRenderer.bind(this)
                },
                {
                    field: 'file_size',
                    headerName: 'Tamaño',
                    width: 100,
                    cellRenderer: this.fileSizeRenderer.bind(this)
                },
                {
                    field: 'rows_count',
                    headerName: 'Filas',
                    width: 100,
                    valueFormatter: params => {
                        return params.value ? params.value.toLocaleString('es-ES') : '0';
                    }
                },
                {
                    field: 'created_at',
                    headerName: 'Creado',
                    width: 140,
                    cellRenderer: this.dateRenderer.bind(this)
                },
                {
                    field: 'actions',
                    headerName: 'Acciones',
                    width: 160,
                    cellRenderer: this.actionsRenderer.bind(this),
                    sortable: false,
                    filter: false,
                    pinned: 'right'
                }
            ],
            rowData: this.datasources,
            defaultColDef: {
                sortable: true,
                filter: true,
                resizable: true,
                floatingFilter: true
            },
            rowHeight: 60,
            headerHeight: 50,
            floatingFiltersHeight: 40,
            animateRows: true,
            pagination: true,
            paginationPageSize: 20,
            paginationPageSizeSelector: [10, 20, 50, 100],
            domLayout: 'normal',
            suppressRowClickSelection: true,
            rowSelection: 'multiple',
            suppressCellFocus: true,
            getRowStyle: params => {
                if (params.data.status === 'FAILED') {
                    return { 
                        backgroundColor: 'rgba(254, 242, 242, 0.5)',
                        borderLeft: '3px solid #ef4444'
                    };
                }
                return null;
            },
            onGridReady: params => {
                this.gridApi = params.api;
                this.autoSizeColumns();
            },
            onFirstDataRendered: () => {
                this.autoSizeColumns();
            }
        };

        // Create the grid
        const gridDiv = document.querySelector(`#${this.containerId}`);
        if (gridDiv) {
            agGrid.createGrid(gridDiv, this.gridOptions);
        } else {
            console.error(`Grid container #${this.containerId} not found`);
        }
    }

    /**
     * Auto-size columns to fit content
     */
    autoSizeColumns() {
        if (this.gridApi) {
            this.gridApi.sizeColumnsToFit();
        }
    }

    /**
     * Update grid data
     */
    updateData(newData) {
        if (this.gridApi) {
            this.gridApi.setGridOption('rowData', newData);
        }
    }

    /**
     * Get selected rows
     */
    getSelectedRows() {
        return this.gridApi ? this.gridApi.getSelectedRows() : [];
    }

    /**
     * Clear selection
     */
    clearSelection() {
        if (this.gridApi) {
            this.gridApi.deselectAll();
        }
    }

    /**
     * Export grid data to CSV
     */
    exportToCsv(filename = 'datasources.csv') {
        if (this.gridApi) {
            this.gridApi.exportDataAsCsv({ fileName: filename });
        }
    }

    /**
     * Search/filter grid data
     */
    setQuickFilter(searchText) {
        if (this.gridApi) {
            this.gridApi.setGridOption('quickFilterText', searchText);
        }
    }

    /**
     * Refresh grid data
     */
    refreshData() {
        if (this.gridApi) {
            this.gridApi.refreshCells();
        }
    }

    /**
     * Destroy grid instance
     */
    destroy() {
        if (this.gridApi) {
            this.gridApi.destroy();
        }
    }
}

// Export for use in templates
window.DataSourceGrid = DataSourceGrid;