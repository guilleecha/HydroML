/**
 * TanStack Table Configuration
 * Configuraciones centralizadas para todas las instancias de TanStack Table
 */

class TanStackTableConfig {
    /**
     * Configuración por defecto para Data Studio
     */
    static getDataStudioConfig() {
        return {
            enableSorting: true,
            enableFiltering: true,
            enablePagination: true,
            pageSize: 25,
            pageSizeOptions: [10, 25, 50, 100],
            debugMode: window.location.hostname === 'localhost',
            
            // Configuraciones de UI
            ui: {
                loadingMessage: 'Cargando datos...',
                emptyMessage: 'No hay datos disponibles',
                errorMessage: 'Error cargando la tabla',
                searchPlaceholder: 'Buscar en todas las columnas...'
            },
            
            // Configuraciones de estilo Grove
            groveStyles: {
                headerClass: 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider',
                cellClass: 'px-6 py-4 whitespace-nowrap text-sm text-gray-900',
                rowClass: 'hover:bg-gray-50',
                sortableHeaderClass: 'cursor-pointer hover:bg-gray-100'
            }
        };
    }

    /**
     * Configuración para diferentes tipos de datos
     */
    static getColumnConfig(dataType) {
        const baseConfig = {
            enableSorting: true,
            enableColumnFilter: true
        };

        switch (dataType) {
            case 'numeric':
                return {
                    ...baseConfig,
                    sortingFn: 'alphanumeric',
                    cell: (info) => {
                        const value = info.getValue();
                        return value !== null && value !== undefined ? 
                            parseFloat(value).toLocaleString() : '-';
                    }
                };
                
            case 'date':
                return {
                    ...baseConfig,
                    sortingFn: 'datetime',
                    cell: (info) => {
                        const value = info.getValue();
                        if (!value) return '-';
                        try {
                            return new Date(value).toLocaleDateString();
                        } catch {
                            return value;
                        }
                    }
                };
                
            case 'boolean':
                return {
                    ...baseConfig,
                    cell: (info) => {
                        const value = info.getValue();
                        return value ? '✓' : '✗';
                    }
                };
                
            case 'text':
            default:
                return {
                    ...baseConfig,
                    cell: (info) => {
                        const value = info.getValue();
                        if (!value) return '-';
                        const stringValue = String(value);
                        return stringValue.length > 100 ? 
                            stringValue.slice(0, 100) + '...' : 
                            stringValue;
                    }
                };
        }
    }

    /**
     * Detectar tipo de dato automáticamente
     */
    static detectColumnType(data, columnName) {
        if (!data || data.length === 0) return 'text';
        
        const samples = data.slice(0, 10).map(row => row[columnName]).filter(val => val != null);
        if (samples.length === 0) return 'text';
        
        // Detectar números
        if (samples.every(val => !isNaN(parseFloat(val)) && isFinite(val))) {
            return 'numeric';
        }
        
        // Detectar fechas
        if (samples.every(val => !isNaN(Date.parse(val)))) {
            return 'date';
        }
        
        // Detectar booleanos
        if (samples.every(val => typeof val === 'boolean' || val === 'true' || val === 'false')) {
            return 'boolean';
        }
        
        return 'text';
    }

    /**
     * Crear definiciones de columnas automáticamente
     */
    static createColumnDefinitions(data, columns) {
        if (!columns || columns.length === 0) return [];
        
        return columns.map(columnName => {
            const dataType = this.detectColumnType(data, columnName);
            const columnConfig = this.getColumnConfig(dataType);
            
            return {
                id: columnName,
                accessorKey: columnName,
                header: this.formatColumnHeader(columnName),
                ...columnConfig
            };
        });
    }

    /**
     * Formatear nombre de columna para header
     */
    static formatColumnHeader(columnName) {
        if (!columnName) return '';
        
        return columnName
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }

    /**
     * Configuración de estado inicial
     */
    static getInitialState(options = {}) {
        return {
            pagination: { 
                pageIndex: 0, 
                pageSize: options.pageSize || 25 
            },
            globalFilter: '',
            sorting: [],
            columnVisibility: {},
            rowSelection: {}
        };
    }

    /**
     * Validar configuración
     */
    static validateConfig(config) {
        const errors = [];
        
        if (!config) {
            errors.push('Configuration object is required');
            return errors;
        }
        
        if (config.pageSize && (config.pageSize < 1 || config.pageSize > 1000)) {
            errors.push('Page size must be between 1 and 1000');
        }
        
        if (config.pageSizeOptions && !Array.isArray(config.pageSizeOptions)) {
            errors.push('Page size options must be an array');
        }
        
        return errors;
    }
}

// Exportar globalmente
window.TanStackTableConfig = TanStackTableConfig;