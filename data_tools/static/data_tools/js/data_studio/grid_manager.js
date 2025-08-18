/**
 * Grid Manager Module - Handles AG Grid initialization, configuration, and grid operations
 */

export class GridManager {
    constructor() {
        this.gridApi = null;
        this.columnApi = null;
        this.currentData = [];
        this.originalData = [];
        this.filteredIndices = [];
        this.gridDivId = 'data-preview-grid';
    }

    /**
     * Initialize the AG Grid with data and provided column definitions from Django
     */
    async initializeGridWithColumnDefs(data, columnDefs) {
        try {
            console.log('DEBUG: Initializing grid with provided column definitions');
            console.log('DEBUG: Data rows:', data?.length || 0);
            console.log('DEBUG: Column definitions:', columnDefs?.length || 0);
            console.log('DEBUG: Sample column def:', columnDefs?.[0]);
            
            if (!data || data.length === 0) {
                console.warn('DEBUG: No data provided for grid initialization');
                return;
            }

            if (!columnDefs || columnDefs.length === 0) {
                console.warn('DEBUG: No column definitions provided, falling back to auto-generation');
                return this.initializeGrid(data);
            }

            this.currentData = [...data];
            this.originalData = [...data];
            this.filteredIndices = data.map((_, index) => index);

            // Use provided column definitions but ensure they have the custom header component
            const enhancedColumnDefs = columnDefs.map(colDef => ({
                ...colDef,
                headerComponent: 'customHeaderComponent',
                headerComponentParams: {
                    showSelectAll: true,
                    enableColumnSelection: true,
                    enableSorting: true,
                    displayName: colDef.headerName || colDef.field
                },
                floatingFilter: true,
                tooltipField: colDef.field
            }));

            console.log('DEBUG: Enhanced column definitions:', enhancedColumnDefs.length);
            
            const gridOptions = {
                columnDefs: enhancedColumnDefs,
                rowData: data,
                defaultColDef: {
                    resizable: true,
                    sortable: true,
                    filter: true,
                    floatingFilter: true,
                    headerComponentParams: {
                        showSelectAll: true,
                        enableColumnSelection: true,
                        enableSorting: true
                    }
                },
                // Enhanced Column Management with Side Panel
                sideBar: {
                    toolPanels: [
                        {
                            id: 'columns',
                            labelDefault: 'Columns',
                            labelKey: 'columns',
                            iconKey: 'columns',
                            toolPanel: 'agColumnsToolPanel',
                            toolPanelParams: {
                                suppressRowGroups: true,
                                suppressValues: true,
                                suppressPivots: true,
                                suppressPivotMode: true,
                                suppressColumnFilter: false,
                                suppressColumnSelectAll: false,
                                suppressColumnExpandAll: false,
                                contractColumnSelection: true,
                                suppressSyncLayoutWithGrid: false
                            }
                        }
                    ],
                    defaultToolPanel: false,
                    hiddenByDefault: true
                },
                enableRangeSelection: true,
                enableCharts: true,
                enableRangeHandle: true,
                enableFillHandle: true,
                headerHeight: 60,
                floatingFiltersHeight: 35,
                animateRows: true,
                suppressMenuHide: true,
                allowContextMenuWithControlKey: true,
                getContextMenuItems: this.getContextMenuItems.bind(this),
                onGridReady: this.onGridReady.bind(this),
                onCellValueChanged: this.onCellValueChanged.bind(this),
                onFilterChanged: this.onFilterChanged.bind(this),
                onSortChanged: this.onSortChanged.bind(this),
                suppressRowClickSelection: true,
                rowSelection: 'multiple',
                suppressCellSelection: false,
                components: {
                    customHeaderComponent: this.createCustomHeaderComponent()
                }
            };

            const gridDiv = document.querySelector(`#${this.gridDivId}`);
            if (!gridDiv) {
                throw new Error(`DEBUG: Grid container element with ID '${this.gridDivId}' not found`);
            }

            console.log('DEBUG: Grid container found:', gridDiv);
            console.log('DEBUG: AG Grid available:', typeof agGrid !== 'undefined');
            console.log('DEBUG: AG Grid createGrid method:', typeof agGrid?.createGrid);

            // Clear any existing grid
            if (this.gridApi) {
                console.log('DEBUG: Destroying existing grid');
                this.gridApi.destroy();
            }

            // Check if AG Grid is available
            if (typeof agGrid === 'undefined') {
                throw new Error('DEBUG: AG Grid library not loaded');
            }

            // Create new grid
            console.log('DEBUG: Creating new AG Grid...');
            this.gridApi = agGrid.createGrid(gridDiv, gridOptions);
            
            console.log('DEBUG: Grid initialized successfully with custom column definitions');
            
        } catch (error) {
            console.error('DEBUG: Error initializing grid with column definitions:', error);
            this.showError('Failed to initialize data grid with provided column definitions. Please try again.');
        }
    }

    /**
     * Initialize the AG Grid with data and configuration
     */
    async initializeGrid(data) {
        try {
            console.log('Initializing grid with data:', data?.length || 0, 'rows');
            
            if (!data || data.length === 0) {
                console.warn('No data provided for grid initialization');
                return;
            }

            this.currentData = [...data];
            this.originalData = [...data];
            this.filteredIndices = data.map((_, index) => index);

            const columnDefs = this.generateColumnDefs(data);
            
            const gridOptions = {
                columnDefs: columnDefs,
                rowData: data,
                defaultColDef: {
                    resizable: true,
                    sortable: true,
                    filter: true,
                    floatingFilter: true,
                    headerComponentParams: {
                        showSelectAll: true,
                        enableColumnSelection: true,
                        enableSorting: true
                    }
                },
                // Enhanced Column Management with Side Panel
                sideBar: {
                    toolPanels: [
                        {
                            id: 'columns',
                            labelDefault: 'Columns',
                            labelKey: 'columns',
                            iconKey: 'columns',
                            toolPanel: 'agColumnsToolPanel',
                            toolPanelParams: {
                                suppressRowGroups: true,
                                suppressValues: true,
                                suppressPivots: true,
                                suppressPivotMode: true,
                                suppressColumnFilter: false,
                                suppressColumnSelectAll: false,
                                suppressColumnExpandAll: false,
                                contractColumnSelection: true,
                                suppressSyncLayoutWithGrid: false
                            }
                        }
                    ],
                    defaultToolPanel: false, // Don't show by default
                    hiddenByDefault: true
                },
                enableRangeSelection: true,
                enableCharts: true,
                enableRangeHandle: true,
                enableFillHandle: true,
                headerHeight: 60,
                floatingFiltersHeight: 35,
                animateRows: true,
                suppressMenuHide: true,
                allowContextMenuWithControlKey: true,
                getContextMenuItems: this.getContextMenuItems.bind(this),
                onGridReady: this.onGridReady.bind(this),
                onCellValueChanged: this.onCellValueChanged.bind(this),
                onFilterChanged: this.onFilterChanged.bind(this),
                onSortChanged: this.onSortChanged.bind(this),
                suppressRowClickSelection: true,
                rowSelection: 'multiple',
                suppressCellSelection: false,
                components: {
                    customHeaderComponent: this.createCustomHeaderComponent()
                }
            };

            const gridDiv = document.querySelector(`#${this.gridDivId}`);
            if (!gridDiv) {
                throw new Error(`Grid container element with ID '${this.gridDivId}' not found`);
            }

            console.log('DEBUG: Grid container found (initializeGrid):', gridDiv);
            console.log('DEBUG: AG Grid available (initializeGrid):', typeof agGrid !== 'undefined');

            // Clear any existing grid
            if (this.gridApi) {
                this.gridApi.destroy();
            }

            // Check if AG Grid is available
            if (typeof agGrid === 'undefined') {
                throw new Error('DEBUG: AG Grid library not loaded in initializeGrid');
            }

            // Create new grid
            this.gridApi = agGrid.createGrid(gridDiv, gridOptions);
            
            console.log('Grid initialized successfully');
            
        } catch (error) {
            console.error('Error initializing grid:', error);
            this.showError('Failed to initialize data grid. Please try again.');
        }
    }

    /**
     * Generate column definitions from data
     */
    generateColumnDefs(data) {
        if (!data || data.length === 0) return [];

        const firstRow = data[0];
        const columnDefs = Object.keys(firstRow).map(key => {
            const values = data.map(row => row[key]).filter(val => val !== null && val !== undefined);
            const isNumeric = values.length > 0 && values.every(val => 
                !isNaN(parseFloat(val)) && isFinite(val)
            );

            return {
                headerName: key,
                field: key,
                type: isNumeric ? 'numericColumn' : 'textColumn',
                filter: isNumeric ? 'agNumberColumnFilter' : 'agTextColumnFilter',
                headerComponent: 'customHeaderComponent',
                headerComponentParams: {
                    showSelectAll: true,
                    displayName: key
                },
                cellRenderer: params => {
                    if (params.value === null || params.value === undefined) {
                        return '<span style="color: #999; font-style: italic;">null</span>';
                    }
                    return params.value;
                },
                tooltipField: key
            };
        });

        return columnDefs;
    }

    /**
     * Create custom header component for column selection with improved layout and interactions
     */
    createCustomHeaderComponent() {
        function CustomHeaderComponent() {}
        
        CustomHeaderComponent.prototype.init = function(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.className = 'custom-header-container';
            
            // Improved container styling with better flex layout
            this.eGui.style.cssText = `
                display: flex;
                align-items: center;
                justify-content: flex-start;
                height: 100%;
                padding: 8px 12px;
                gap: 12px;
                background: var(--ag-header-background-color);
                border-bottom: 1px solid var(--ag-border-color);
                min-height: 50px;
            `;
            
            // Create checkbox first (always on the left)
            if (params.showSelectAll || params.enableColumnSelection !== false) {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'column-select-checkbox';
                checkbox.style.cssText = `
                    margin: 0;
                    cursor: pointer;
                    transform: scale(1.1);
                    accent-color: var(--ag-accent-color, #3b82f6);
                    flex-shrink: 0;
                    order: -1;
                `;
                checkbox.setAttribute('aria-label', `Select column ${params.displayName}`);
                
                // Separate checkbox interaction from sorting
                checkbox.addEventListener('change', (e) => {
                    e.stopPropagation(); // Prevent sorting when clicking checkbox
                    const columnField = params.column.getColId();
                    const event = new CustomEvent('columnSelectionChanged', {
                        detail: { columnField, selected: e.target.checked }
                    });
                    document.dispatchEvent(event);
                });
                
                // Prevent checkbox click from propagating to header
                checkbox.addEventListener('click', (e) => {
                    e.stopPropagation();
                });
                
                this.eGui.appendChild(checkbox);
                this.checkbox = checkbox;
            }
            
            // Create header text with improved layout
            const headerText = document.createElement('div');
            headerText.textContent = params.displayName;
            headerText.className = 'header-text';
            
            // Check if column is sortable
            const isSortable = params.column.getSort !== undefined && params.enableSorting !== false;
            
            if (isSortable) {
                headerText.classList.add('sortable');
                headerText.style.cssText = `
                    font-weight: 600;
                    cursor: pointer;
                    flex: 1;
                    text-align: left;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    transition: all 0.2s ease;
                    color: var(--ag-foreground-color);
                    user-select: none;
                    padding: 4px 0;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                `;
                headerText.setAttribute('title', `Sort by ${params.displayName}`);
                
                // Create sort indicator container
                const sortIndicator = document.createElement('span');
                sortIndicator.className = 'sort-indicator';
                sortIndicator.style.cssText = `
                    margin-left: 8px;
                    font-size: 12px;
                    opacity: 0.7;
                    transition: all 0.3s ease;
                    color: var(--ag-foreground-color, #666);
                    flex-shrink: 0;
                `;
                
                // Create text container for better layout
                const textContainer = document.createElement('span');
                textContainer.textContent = params.displayName;
                textContainer.style.cssText = `
                    flex: 1;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                `;
                
                headerText.innerHTML = '';
                headerText.appendChild(textContainer);
                headerText.appendChild(sortIndicator);
                
                // Only header text triggers sorting (not checkbox)
                headerText.addEventListener('click', (e) => {
                    e.stopPropagation();
                    params.progressSort();
                });
                
                // Enhanced hover effects for sortable headers
                headerText.addEventListener('mouseenter', () => {
                    if (!headerText.classList.contains('sorting')) {
                        headerText.style.color = 'var(--ag-accent-color, #3b82f6)';
                        sortIndicator.style.opacity = '1';
                        sortIndicator.style.color = 'var(--ag-accent-color, #3b82f6)';
                    }
                });
                
                headerText.addEventListener('mouseleave', () => {
                    if (!headerText.classList.contains('sorting')) {
                        headerText.style.color = 'var(--ag-foreground-color)';
                        sortIndicator.style.opacity = '0.7';
                        sortIndicator.style.color = 'var(--ag-foreground-color, #666)';
                    }
                });
                
                // Enhanced sort indicator update with better visual feedback
                this.updateSortIndicator = () => {
                    const sort = params.column.getSort();
                    sortIndicator.style.transition = 'all 0.3s ease';
                    
                    if (sort === 'asc') {
                        sortIndicator.textContent = '↑';
                        sortIndicator.style.color = 'var(--ag-accent-color, #3b82f6)';
                        sortIndicator.style.opacity = '1';
                        sortIndicator.style.transform = 'scale(1.2)';
                        headerText.classList.add('sorting');
                        headerText.setAttribute('aria-label', `Sorted ascending by ${params.displayName}. Click to sort descending.`);
                    } else if (sort === 'desc') {
                        sortIndicator.textContent = '↓';
                        sortIndicator.style.color = 'var(--ag-accent-color, #3b82f6)';
                        sortIndicator.style.opacity = '1';
                        sortIndicator.style.transform = 'scale(1.2)';
                        headerText.classList.add('sorting');
                        headerText.setAttribute('aria-label', `Sorted descending by ${params.displayName}. Click to remove sort.`);
                    } else {
                        sortIndicator.textContent = '';
                        sortIndicator.style.color = 'var(--ag-foreground-color, #666)';
                        sortIndicator.style.opacity = '0.7';
                        sortIndicator.style.transform = 'scale(1)';
                        headerText.classList.remove('sorting');
                        headerText.setAttribute('aria-label', `Sort by ${params.displayName}`);
                    }
                };
                
                // Listen for sort changes
                params.column.addEventListener('sortChanged', this.updateSortIndicator);
                this.updateSortIndicator();
                
                // Store references for cleanup
                this.headerText = headerText;
                this.sortIndicator = sortIndicator;
                this.textContainer = textContainer;
            } else {
                // Non-sortable header styling
                headerText.style.cssText = `
                    font-weight: 600; 
                    text-align: left; 
                    white-space: nowrap; 
                    overflow: hidden; 
                    text-overflow: ellipsis;
                    color: var(--ag-foreground-color);
                    flex: 1;
                    padding: 4px 0;
                `;
                headerText.setAttribute('title', params.displayName);
                this.headerText = headerText;
            }
            
            this.eGui.appendChild(headerText);
        };
        
        CustomHeaderComponent.prototype.getGui = function() {
            return this.eGui;
        };
        
        CustomHeaderComponent.prototype.destroy = function() {
            if (this.params && this.params.column && this.updateSortIndicator) {
                this.params.column.removeEventListener('sortChanged', this.updateSortIndicator);
            }
            
            // Clean up DOM references
            if (this.checkbox) {
                this.checkbox = null;
            }
            if (this.headerText) {
                this.headerText = null;
            }
            if (this.sortIndicator) {
                this.sortIndicator = null;
            }
        };
        
        return CustomHeaderComponent;
    }

    /**
     * Grid event handlers
     */
    onGridReady(params) {
        this.gridApi = params.api;
        this.columnApi = params.columnApi;
        
        // Auto-size columns to fit content
        this.gridApi.sizeColumnsToFit();
        
        // Set up resize observer for responsive design
        const gridDiv = document.querySelector(`#${this.gridDivId}`);
        if (gridDiv && window.ResizeObserver) {
            const resizeObserver = new ResizeObserver(() => {
                if (this.gridApi) {
                    this.gridApi.sizeColumnsToFit();
                }
            });
            resizeObserver.observe(gridDiv);
        }

        console.log('Grid ready with', this.gridApi.getDisplayedRowCount(), 'rows');
    }

    onCellValueChanged(event) {
        console.log('Cell value changed:', event);
        // Handle cell value changes if needed
    }

    onFilterChanged() {
        if (this.gridApi) {
            const rowCount = this.gridApi.getDisplayedRowCount();
            console.log('Filter changed, displaying', rowCount, 'rows');
            
            // Update filtered indices
            this.filteredIndices = [];
            this.gridApi.forEachNodeAfterFilter((node) => {
                this.filteredIndices.push(node.rowIndex);
            });
        }
    }

    onSortChanged() {
        console.log('Sort changed');
    }

    /**
     * Context menu items with enhanced column management
     */
    getContextMenuItems(params) {
        const result = [
            {
                name: 'Copy',
                action: () => {
                    if (params.value !== undefined) {
                        navigator.clipboard.writeText(params.value);
                    }
                }
            },
            {
                name: 'Export Selection',
                action: () => {
                    this.exportSelectedData();
                }
            },
            'separator'
        ];
        
        // Add column-specific actions if we're in a column header
        if (params.column) {
            result.push(
                {
                    name: `Hide "${params.column.getColDef().headerName || params.column.getColId()}"`,
                    action: () => {
                        this.hideColumn(params.column.getColId());
                    },
                    icon: '<i class="fas fa-eye-slash"></i>'
                },
                {
                    name: 'Auto-size This Column',
                    action: () => {
                        this.autoSizeColumn(params.column.getColId());
                    },
                    icon: '<i class="fas fa-arrows-alt-h"></i>'
                },
                'separator'
            );
        }
        
        result.push(
            'autoSizeAll',
            'resetColumns',
            {
                name: 'Show Column Management Panel',
                action: () => {
                    this.toggleColumnPanel();
                },
                icon: '<i class="fas fa-columns"></i>'
            }
        );
        
        return result;
    }

    /**
     * Hide a specific column using AG Grid's native API
     */
    hideColumn(columnId) {
        if (this.gridApi) {
            this.gridApi.applyColumnState({
                state: [{ colId: columnId, hide: true }]
            });
            console.log(`Column "${columnId}" hidden`);
            
            // Dispatch event for external listeners
            document.dispatchEvent(new CustomEvent('columnHidden', {
                detail: { columnId }
            }));
        }
    }

    /**
     * Show a specific column using AG Grid's native API
     */
    showColumn(columnId) {
        if (this.gridApi) {
            this.gridApi.applyColumnState({
                state: [{ colId: columnId, hide: false }]
            });
            console.log(`Column "${columnId}" shown`);
            
            // Dispatch event for external listeners
            document.dispatchEvent(new CustomEvent('columnShown', {
                detail: { columnId }
            }));
        }
    }

    /**
     * Hide multiple columns at once (for bulk operations)
     */
    hideColumns(columnIds) {
        if (this.gridApi && columnIds.length > 0) {
            const columnState = columnIds.map(colId => ({
                colId: colId,
                hide: true
            }));
            
            this.gridApi.applyColumnState({
                state: columnState
            });
            
            console.log(`Hidden ${columnIds.length} columns:`, columnIds);
            
            // Dispatch event for external listeners
            document.dispatchEvent(new CustomEvent('columnsHidden', {
                detail: { columnIds, count: columnIds.length }
            }));
        }
    }

    /**
     * Auto-size a specific column
     */
    autoSizeColumn(columnId) {
        if (this.gridApi) {
            this.gridApi.autoSizeColumn(columnId);
            console.log(`Auto-sized column "${columnId}"`);
        }
    }

    /**
     * Toggle the column management panel
     */
    toggleColumnPanel() {
        if (this.gridApi) {
            const currentPanel = this.gridApi.getOpenedToolPanel();
            if (currentPanel === 'columns') {
                this.gridApi.closeToolPanel();
            } else {
                this.gridApi.openToolPanel('columns');
            }
        }
    }

    /**
     * Get current column state for persistence
     */
    getColumnState() {
        if (this.gridApi) {
            return this.gridApi.getColumnState();
        }
        return null;
    }

    /**
     * Restore column state from saved configuration
     */
    restoreColumnState(columnState) {
        if (this.gridApi && columnState) {
            this.gridApi.applyColumnState({
                state: columnState,
                applyOrder: true
            });
            console.log('Column state restored');
        }
    }

    /**
     * Reset columns to their original state
     */
    resetColumns() {
        if (this.gridApi) {
            this.gridApi.resetColumnState();
            console.log('Columns reset to original state');
            
            // Dispatch event for external listeners
            document.dispatchEvent(new CustomEvent('columnsReset'));
        }
    }

    /**
     * Get list of hidden columns
     */
    getHiddenColumns() {
        if (this.gridApi) {
            return this.gridApi.getColumnState()
                .filter(col => col.hide)
                .map(col => col.colId);
        }
        return [];
    }

    /**
     * Get list of visible columns
     */
    getVisibleColumns() {
        if (this.gridApi) {
            return this.gridApi.getColumnState()
                .filter(col => !col.hide)
                .map(col => col.colId);
        }
        return [];
    }

    /**
     * Grid utility methods
     */
    getCurrentData() {
        if (!this.gridApi) return [];
        
        const rowData = [];
        this.gridApi.forEachNode((node) => {
            rowData.push(node.data);
        });
        return rowData;
    }

    getSelectedRows() {
        if (!this.gridApi) return [];
        return this.gridApi.getSelectedRows();
    }

    updateGridData(newData) {
        if (this.gridApi && newData) {
            this.currentData = [...newData];
            this.gridApi.setRowData(newData);
            this.gridApi.sizeColumnsToFit();
        }
    }

    exportSelectedData() {
        if (!this.gridApi) return;
        
        const selectedRows = this.gridApi.getSelectedRows();
        if (selectedRows.length === 0) {
            alert('Please select rows to export');
            return;
        }
        
        // Convert to CSV
        const headers = Object.keys(selectedRows[0]);
        const csvContent = [
            headers.join(','),
            ...selectedRows.map(row => 
                headers.map(header => 
                    `"${(row[header] || '').toString().replace(/"/g, '""')}"`
                ).join(',')
            )
        ].join('\n');
        
        // Download
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'selected_data.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    }

    /**
     * Error handling
     */
    showError(message) {
        console.error(message);
        // Could integrate with a toast notification system
        alert(message);
    }

    /**
     * Cleanup
     */
    destroy() {
        if (this.gridApi) {
            this.gridApi.destroy();
            this.gridApi = null;
            this.columnApi = null;
        }
    }
}
