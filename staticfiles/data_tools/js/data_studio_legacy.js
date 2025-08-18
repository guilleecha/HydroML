// Data Studio JavaScript - Modern interactive data manipulation interface
// Combines data viewing and preparation functionality with AG Grid

class DataStudio {
    constructor() {
        this.gridApi = null;
        this.columnApi = null;
        this.selectedColumns = new Set();
        this.removedColumns = new Set();
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeGrid();
            this.setupEventListeners();
            this.initializeTransformationSelector();
            this.initializeColumnAnalysis();
        });
    }
    
    initializeGrid() {
        // Create column definitions with improved header components
        const columnDefs = window.columnDefsData.map((col, index) => {
            const colDef = {
                headerName: col.headerName,
                field: col.field,
                ...col,
                // Use custom header component for all columns
                headerComponent: 'customHeaderComponent'
            };
            
            // Enable column selection for all columns, row selection only for first column
            if (index === 0) {
                colDef.headerCheckboxSelection = false; // Disable built-in checkbox
                colDef.checkboxSelection = true;
                colDef.headerComponentParams = {
                    enableColumnSelection: true, // Column selection checkbox
                    enableRowSelection: true, // Row selection for first column
                    enableSorting: true
                };
            } else {
                colDef.headerComponentParams = {
                    enableColumnSelection: true, // Column selection checkbox
                    enableRowSelection: false,
                    enableSorting: true
                };
            }
            
            // Implement flex width for primary column (station_code or first data column)
            if (col.field === 'station_code' || (index === 1 && !window.columnDefsData.some(c => c.field === 'station_code'))) {
                colDef.flex = 1;
            }
            
            // Add value formatter for numeric columns
            if (this.isNumericColumnType(col)) {
                colDef.valueFormatter = (params) => {
                    if (params.value == null || params.value === undefined || params.value === '') {
                        return params.value;
                    }
                    
                    const numValue = Number(params.value);
                    
                    // Check if it's a valid number
                    if (isNaN(numValue) || !isFinite(numValue)) {
                        return params.value;
                    }
                    
                    // Check if it has decimal places
                    if (numValue % 1 !== 0) {
                        // Format to 3 decimal places for floating point numbers
                        return numValue.toFixed(3);
                    }
                    
                    // Return integers as is
                    return numValue.toString();
                };
            }
            
            return colDef;
        });
        
        // Log column definitions for debugging
        console.log('Column definitions:', JSON.stringify(columnDefs));
        
        const gridOptions = {
            columnDefs: columnDefs,
            rowData: window.gridRowData,
            
            // Enhanced default column definitions with AG Grid best practices
            defaultColDef: {
                width: 150,
                minWidth: 120,
                resizable: true,
                sortable: true,
                filter: true,
                floatingFilter: true, // Enhanced filtering UX from AG Grid docs
                menuTabs: ['filterMenuTab', 'generalMenuTab', 'columnsMenuTab'],
                
                // Performance optimizations from AG Grid documentation
                suppressSizeToFit: false,
                suppressAutoSize: false,
                
                // Enhanced tooltip with better null handling
                tooltipValueGetter: (params) => {
                    if (params.value == null || params.value === undefined) {
                        return 'No data';
                    }
                    return params.value.toString();
                },
                
                // Improved keyboard navigation
                suppressKeyboardEvent: (params) => {
                    // Allow navigation but prevent editing conflicts
                    return params.event.key === 'Enter' && params.editing;
                }
            },
            
            // Enhanced selection configuration
            rowSelection: 'multiple',
            suppressRowClickSelection: false,
            rowMultiSelectWithClick: true, // Better multi-selection UX
            
            // Enhanced header configuration for improved custom headers
            headerHeight: 60,
            suppressMenuHide: true,
            
            // Performance optimizations from AG Grid best practices
            suppressColumnVirtualisation: false, // Enable column virtualization for better performance
            rowBuffer: 10, // Rows to render outside the visible area
            suppressAnimationFrame: false, // Enable animation frame for smoother rendering
            
            // Register our custom header component
            components: {
                customHeaderComponent: this.createCustomHeaderComponent()
            },
            
            // Enhanced side panels for column management with AG Grid best practices
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
                            contractColumnSelection: true, // Better UX
                            suppressSyncLayoutWithGrid: false // Keep sync with grid
                        }
                    },
                    {
                        id: 'filters',
                        labelDefault: 'Filters',
                        labelKey: 'filters',
                        iconKey: 'filter',
                        toolPanel: 'agFiltersToolPanel',
                        toolPanelParams: {
                            suppressExpandAll: false,
                            suppressFilterSearch: false
                        }
                    }
                ],
                defaultToolPanel: '',
                hiddenByDefault: true,
                position: 'right',
                width: 300 // Fixed width for better UX
            },
            
            // Enhanced grid behavior with AG Grid optimizations
            animateRows: true,
            enableCellTextSelection: true,
            suppressCellFocus: false, // Enable cell focus for better accessibility
            enableRangeSelection: true, // Enable range selection for data analysis
            enableFillHandle: false, // Disable fill handle to prevent accidental edits
            
            // Pagination for better performance with large datasets
            pagination: true,
            paginationPageSize: 100,
            paginationAutoPageSize: false,
            
            // Enhanced scrolling performance
            suppressHorizontalScroll: false,
            suppressScrollOnNewData: true,
            
            // Theme - dynamically set based on dark mode
            theme: this.getCurrentTheme(),
            
            // Event handlers
            onSelectionChanged: () => this.onSelectionChanged(),
            onColumnMoved: () => this.onColumnChanged(),
            onColumnVisible: () => this.onColumnChanged(),
            onColumnPinned: () => this.onColumnChanged(),
            
            // Enhanced grid ready callback with AG Grid best practices
            onGridReady: (params) => {
                this.gridApi = params.api;
                this.columnApi = params.columnApi;
                
                // Set up theme change listener
                this.setupThemeChangeListener();
                
                // Intelligent column sizing with AG Grid best practices
                const allVisibleColumnIds = params.api.getColumns().map(column => column.getId());
                
                // Use autoSizeColumns for better content fitting
                params.api.autoSizeColumns(allVisibleColumnIds, false);
                
                // Ensure grid fits the container width after auto-sizing
                setTimeout(() => {
                    params.api.sizeColumnsToFit();
                }, 100);
                
                // Performance: Pre-load visible rows for smoother scrolling
                if (window.gridRowData && window.gridRowData.length > 100) {
                    params.api.setRowData(window.gridRowData);
                }
                
                console.log('Data Studio Grid initialized with', window.gridRowData.length, 'rows and', allVisibleColumnIds.length, 'columns');
                console.log('Performance features: Column virtualization, row buffering, pagination enabled');
            }
        };
        
        // Initialize the grid
        const eGridDiv = document.querySelector('#data-preview-grid');
        if (eGridDiv) {
            new agGrid.Grid(eGridDiv, gridOptions);
        }
    }
    
    onSelectionChanged() {
        if (!this.gridApi) return;
        
        const selectedRows = this.gridApi.getSelectedRows();
        console.log('Selected rows:', selectedRows.length);
        
        // Note: For column selection, we'll need to use a different approach
        // This is for row selection, but we might want to focus on column selection
        
        this.updateSelectedColumnsDisplay();
    }
    
    onColumnChanged() {
        // Handle column changes (moved, hidden, etc.)
        this.updateSelectedColumnsDisplay();
    }
    
    updateSelectedColumnsDisplay() {
        const selectedCountElement = document.getElementById('selected-count');
        const selectedColumnsListElement = document.getElementById('selected-columns-list');
        
        if (selectedCountElement) {
            selectedCountElement.textContent = this.selectedColumns.size;
        }
        
        if (selectedColumnsListElement) {
            if (this.selectedColumns.size === 0) {
                selectedColumnsListElement.innerHTML = '<span class="text-foreground-muted italic">Ninguna columna seleccionada</span>';
            } else {
                const columnTags = Array.from(this.selectedColumns).map(colName => 
                    `<span class="inline-flex items-center px-2 py-1 bg-brand-100 text-brand-800 text-xs font-medium rounded-full">
                        ${colName}
                        <button type="button" class="ml-1 text-brand-600 hover:text-brand-800" onclick="dataStudio.deselectColumn('${colName}')">
                            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                            </svg>
                        </button>
                    </span>`
                ).join(' ');
                selectedColumnsListElement.innerHTML = columnTags;
            }
        }
        
        // Update remove button state
        this.updateRemoveButtonState();
    }
    
    updateRemoveButtonState() {
        const removeButton = document.getElementById('remove-selected-columns-btn');
        if (removeButton) {
            removeButton.disabled = this.selectedColumns.size === 0;
        }
    }
    
    selectColumn(columnName) {
        this.selectedColumns.add(columnName);
        this.updateSelectedColumnsDisplay();
    }
    
    deselectColumn(columnName) {
        this.selectedColumns.delete(columnName);
        this.updateSelectedColumnsDisplay();
    }
    
    removeSelectedColumns() {
        if (this.selectedColumns.size === 0) return;
        
        // Add selected columns to removed list
        this.selectedColumns.forEach(col => {
            this.removedColumns.add(col);
        });
        
        // Clear selected columns
        this.selectedColumns.clear();
        
        // Update hidden input
        const removedColumnsInput = document.getElementById('removed_columns_input');
        if (removedColumnsInput) {
            removedColumnsInput.value = JSON.stringify(Array.from(this.removedColumns));
        }
        
        // Hide columns in grid
        if (this.columnApi) {
            this.columnApi.setColumnsVisible(Array.from(this.removedColumns), false);
        }
        
        this.updateSelectedColumnsDisplay();
        
        console.log('Removed columns:', Array.from(this.removedColumns));
    }
    
    setupEventListeners() {
        // Remove selected columns button
        const removeButton = document.getElementById('remove-selected-columns-btn');
        if (removeButton) {
            removeButton.addEventListener('click', () => {
                this.removeSelectedColumns();
            });
        }
        
        // Apply transformation button
        const applyTransformationBtn = document.getElementById('apply_transformation_btn');
        if (applyTransformationBtn) {
            applyTransformationBtn.addEventListener('click', () => {
                this.applyTransformation();
            });
        }
        
        // Form submission
        const form = document.getElementById('data-studio-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                this.onFormSubmit(e);
            });
        }
        
        // Column header clicks for selection (custom implementation)
        // We'll need to add this when AG Grid is ready
        setTimeout(() => {
            this.setupColumnHeaderSelection();
        }, 500);
    }
    
    setupColumnHeaderSelection() {
        if (!this.gridApi) return;
        
        // Add click listeners to column headers for selection
        const headerElements = document.querySelectorAll('.ag-header-cell');
        headerElements.forEach(headerEl => {
            const colId = headerEl.getAttribute('col-id');
            if (colId) {
                // Add checkbox to header
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'mr-2';
                checkbox.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        this.selectColumn(colId);
                    } else {
                        this.deselectColumn(colId);
                    }
                });
                
                const headerContainer = headerEl.querySelector('.ag-header-cell-label');
                if (headerContainer) {
                    headerContainer.insertBefore(checkbox, headerContainer.firstChild);
                }
            }
        });
    }
    
    initializeTransformationSelector() {
        const selector = document.getElementById('transformation_type');
        if (selector) {
            selector.addEventListener('change', (e) => {
                this.showTransformationParameters(e.target.value);
            });
        }
    }
    
    showTransformationParameters(transformationType) {
        const parametersContainer = document.getElementById('transformation_parameters');
        const applyButton = document.getElementById('apply_transformation_btn');
        
        if (!parametersContainer || !applyButton) return;
        
        // Hide all parameter sections first
        parametersContainer.classList.add('hidden');
        applyButton.disabled = true;
        
        if (transformationType) {
            // Show parameters container
            parametersContainer.classList.remove('hidden');
            applyButton.disabled = false;
            
            // Here you can add specific parameter forms for each transformation type
            // This is a simplified version - you might want to expand this
            let parametersHTML = '';
            
            switch(transformationType) {
                case 'mean_median_imputer':
                    parametersHTML = `
                        <div class="space-y-3">
                            <div>
                                <label class="block text-sm font-medium text-foreground-default mb-2">Strategy</label>
                                <select name="imputer_strategy" class="w-full px-3 py-2 bg-background-primary border border-border-default rounded-lg">
                                    <option value="mean">Mean</option>
                                    <option value="median">Median</option>
                                </select>
                            </div>
                        </div>
                    `;
                    break;
                case 'onehot_encoder':
                    parametersHTML = `
                        <div class="space-y-3">
                            <div>
                                <label class="block text-sm font-medium text-foreground-default mb-2">Top Categories</label>
                                <input type="number" name="encoder_top_categories" value="10" min="1" max="50" 
                                       class="w-full px-3 py-2 bg-background-primary border border-border-default rounded-lg">
                            </div>
                        </div>
                    `;
                    break;
                case 'equal_frequency_discretiser':
                    parametersHTML = `
                        <div class="space-y-3">
                            <div>
                                <label class="block text-sm font-medium text-foreground-default mb-2">Number of Bins</label>
                                <input type="number" name="discretiser_bins" value="5" min="2" max="20" 
                                       class="w-full px-3 py-2 bg-background-primary border border-border-default rounded-lg">
                            </div>
                        </div>
                    `;
                    break;
            }
            
            parametersContainer.innerHTML = parametersHTML;
        }
    }
    
    applyTransformation() {
        const transformationType = document.getElementById('transformation_type').value;
        if (!transformationType) return;
        
        // Collect transformation parameters
        const parameters = {};
        const form = document.getElementById('data-studio-form');
        if (form) {
            const formData = new FormData(form);
            for (let [key, value] of formData.entries()) {
                if (key.startsWith(transformationType.split('_')[0])) {
                    parameters[key] = value;
                }
            }
        }
        
        console.log('Applying transformation:', transformationType, 'with parameters:', parameters);
        
        // Here you would typically make an AJAX call to apply the transformation
        // For now, we'll just show a success message
        this.showTransformationSuccess(transformationType);
    }
    
    showTransformationSuccess(transformationType) {
        const historyContainer = document.getElementById('transformation_history');
        const historyList = document.getElementById('history_list');
        
        if (historyContainer && historyList) {
            historyContainer.classList.remove('hidden');
            
            const historyItem = document.createElement('div');
            historyItem.className = 'flex items-center justify-between p-2 bg-success-50 border border-success-200 rounded-lg text-sm';
            historyItem.innerHTML = `
                <span class="text-success-800">${transformationType.replace(/_/g, ' ').toUpperCase()}</span>
                <span class="text-success-600 text-xs">${new Date().toLocaleTimeString()}</span>
            `;
            
            historyList.appendChild(historyItem);
        }
    }
    
    onFormSubmit(e) {
        // Update removed columns input before submission
        const removedColumnsInput = document.getElementById('removed_columns_input');
        if (removedColumnsInput) {
            removedColumnsInput.value = JSON.stringify(Array.from(this.removedColumns));
        }
        
        console.log('Submitting Data Studio form with removed columns:', Array.from(this.removedColumns));
        
        // Let the form submit normally
        return true;
    }
    
    // === COLUMN ANALYSIS METHODS ===
    
    initializeColumnAnalysis() {
        this.populateNumericColumns();
        this.setupChartEventListeners();
        
        // Initialize chart type and button text
        const chartTypeSelect = document.getElementById('chart_type_select');
        if (chartTypeSelect) {
            this.updateGenerateButtonText(chartTypeSelect.value);
        }
    }
    
    populateNumericColumns() {
        const columnSelect = document.getElementById('analysis_column_select');
        const xColumnSelect = document.getElementById('x_axis_column_select');
        const yColumnSelect = document.getElementById('y_axis_column_select');
        
        if (!window.columnDefsData) return;

        // Get numeric columns from grid data
        const numericColumns = this.getNumericColumns();
        
        // Populate single column select (for histogram and boxplot)
        if (columnSelect) {
            // Clear existing options except the first one
            while (columnSelect.children.length > 1) {
                columnSelect.removeChild(columnSelect.lastChild);
            }
            
            // Add numeric columns to select
            numericColumns.forEach(columnName => {
                const option = document.createElement('option');
                option.value = columnName;
                option.textContent = columnName;
                columnSelect.appendChild(option);
            });
        }

        // Populate X axis column select (for scatter plots)
        if (xColumnSelect) {
            // Clear existing options except the first one
            while (xColumnSelect.children.length > 1) {
                xColumnSelect.removeChild(xColumnSelect.lastChild);
            }
            
            // Add numeric columns to select
            numericColumns.forEach(columnName => {
                const option = document.createElement('option');
                option.value = columnName;
                option.textContent = columnName;
                xColumnSelect.appendChild(option);
            });
        }

        // Populate Y axis column select (for scatter plots)
        if (yColumnSelect) {
            // Clear existing options except the first one
            while (yColumnSelect.children.length > 1) {
                yColumnSelect.removeChild(yColumnSelect.lastChild);
            }
            
            // Add numeric columns to select
            numericColumns.forEach(columnName => {
                const option = document.createElement('option');
                option.value = columnName;
                option.textContent = columnName;
                yColumnSelect.appendChild(option);
            });
        }
        
        console.log('Populated numeric columns:', numericColumns);
    }
    
    getNumericColumns() {
        if (!window.gridRowData || window.gridRowData.length === 0) return [];
        
        const numericColumns = [];
        const firstRow = window.gridRowData[0];
        
        for (const [columnName, value] of Object.entries(firstRow)) {
            // Skip if column is removed
            if (this.removedColumns.has(columnName)) continue;
            
            // Check if the column contains numeric values
            if (this.isNumericColumn(columnName)) {
                numericColumns.push(columnName);
            }
        }
        
        return numericColumns;
    }
    
    isNumericColumn(columnName) {
        if (!window.gridRowData || window.gridRowData.length === 0) return false;
        
        // Sample a few rows to determine if column is numeric
        const sampleSize = Math.min(10, window.gridRowData.length);
        let numericCount = 0;
        
        for (let i = 0; i < sampleSize; i++) {
            const value = window.gridRowData[i][columnName];
            if (value !== null && value !== undefined && value !== '') {
                const numValue = Number(value);
                if (!isNaN(numValue) && isFinite(numValue)) {
                    numericCount++;
                }
            }
        }
        
        // Consider it numeric if at least 70% of sampled values are numeric
        return (numericCount / sampleSize) >= 0.7;
    }
    
    isNumericColumnType(col) {
        // Check if column type indicates it's numeric
        if (col.type) {
            const numericTypes = ['float64', 'float32', 'int64', 'int32', 'int16', 'int8', 'number'];
            if (numericTypes.includes(col.type.toLowerCase())) {
                return true;
            }
        }
        
        // Fallback: check the actual data values for this column
        return this.isNumericColumn(col.field);
    }
    
    setupChartEventListeners() {
        // Chart type selection change
        const chartTypeSelect = document.getElementById('chart_type_select');
        if (chartTypeSelect) {
            chartTypeSelect.addEventListener('change', () => {
                this.onChartTypeChange();
            });
        }

        // Single column selection change (for histogram and boxplot)
        const columnSelect = document.getElementById('analysis_column_select');
        if (columnSelect) {
            columnSelect.addEventListener('change', () => {
                this.onColumnSelectionChange();
            });
        }

        // X and Y axis column selections (for scatter plots)
        const xColumnSelect = document.getElementById('x_axis_column_select');
        const yColumnSelect = document.getElementById('y_axis_column_select');
        
        if (xColumnSelect) {
            xColumnSelect.addEventListener('change', () => {
                this.onScatterColumnSelectionChange();
            });
        }
        
        if (yColumnSelect) {
            yColumnSelect.addEventListener('change', () => {
                this.onScatterColumnSelectionChange();
            });
        }
        
        // Generate chart button
        const generateBtn = document.getElementById('generate_chart_btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.generateChart();
            });
        }
    }

    onChartTypeChange() {
        const chartTypeSelect = document.getElementById('chart_type_select');
        const singleColumnSection = document.getElementById('single_column_section');
        const dualColumnSection = document.getElementById('dual_column_section');
        
        if (!chartTypeSelect || !singleColumnSection || !dualColumnSection) return;
        
        const chartType = chartTypeSelect.value;
        
        if (chartType === 'scatter') {
            // Show dual column selection for scatter plots
            singleColumnSection.classList.add('hidden');
            dualColumnSection.classList.remove('hidden');
            this.onScatterColumnSelectionChange();
        } else {
            // Show single column selection for histogram and boxplot
            singleColumnSection.classList.remove('hidden');
            dualColumnSection.classList.add('hidden');
            this.onColumnSelectionChange();
        }
        
        // Hide chart when changing type
        this.hideChart();
        
        // Update button text based on chart type
        this.updateGenerateButtonText(chartType);
    }

    updateGenerateButtonText(chartType) {
        const generateBtn = document.getElementById('generate_chart_btn');
        if (!generateBtn) return;
        
        const chartTypeNames = {
            'histogram': 'Histograma',
            'boxplot': 'Diagrama de Caja',
            'scatter': 'Diagrama de Dispersión'
        };
        
        const chartTypeName = chartTypeNames[chartType] || 'Gráfico';
        generateBtn.innerHTML = `
            <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 00-2-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4"></path>
            </svg>
            Generar ${chartTypeName}
        `;
    }

    onColumnSelectionChange() {
        const columnSelect = document.getElementById('analysis_column_select');
        const generateBtn = document.getElementById('generate_chart_btn');
        
        if (columnSelect && generateBtn) {
            generateBtn.disabled = !columnSelect.value;
        }
        
        // Hide chart container when selection changes
        this.hideChart();
    }

    onScatterColumnSelectionChange() {
        const xColumnSelect = document.getElementById('x_axis_column_select');
        const yColumnSelect = document.getElementById('y_axis_column_select');
        const generateBtn = document.getElementById('generate_chart_btn');
        
        if (xColumnSelect && yColumnSelect && generateBtn) {
            generateBtn.disabled = !xColumnSelect.value || !yColumnSelect.value;
        }
        
        // Hide chart container when selection changes
        this.hideChart();
    }
    
    async generateChart() {
        const chartTypeSelect = document.getElementById('chart_type_select');
        const chartType = chartTypeSelect.value;
        
        let apiUrl;
        let validationMessage;
        
        if (chartType === 'scatter') {
            // Handle scatter plot with two columns
            const xColumnSelect = document.getElementById('x_axis_column_select');
            const yColumnSelect = document.getElementById('y_axis_column_select');
            
            if (!xColumnSelect.value) {
                this.showValidationError('Por favor seleccione una columna para el eje X');
                return;
            }
            
            if (!yColumnSelect.value) {
                this.showValidationError('Por favor seleccione una columna para el eje Y');
                return;
            }
            
            if (xColumnSelect.value === yColumnSelect.value) {
                this.showValidationError('Por favor seleccione columnas diferentes para los ejes X e Y');
                return;
            }
            
            const xColumn = xColumnSelect.value;
            const yColumn = yColumnSelect.value;
            
            console.log('Generating scatter plot for columns:', xColumn, 'vs', yColumn);
            
            apiUrl = `/data_tools/api/generate-chart/?datasource_id=${window.datasourceId}&x_column=${encodeURIComponent(xColumn)}&y_column=${encodeURIComponent(yColumn)}&chart_type=${chartType}`;
            validationMessage = `scatter plot: ${xColumn} vs ${yColumn}`;
            
        } else {
            // Handle single column charts (histogram, boxplot)
            const columnSelect = document.getElementById('analysis_column_select');
            
            if (!columnSelect.value) {
                this.showValidationError('Por favor seleccione una columna');
                return;
            }
            
            const columnName = columnSelect.value;
            
            console.log('Generating chart for column:', columnName, 'type:', chartType);
            
            apiUrl = `/data_tools/api/generate-chart/?datasource_id=${window.datasourceId}&column_name=${encodeURIComponent(columnName)}&chart_type=${chartType}`;
            validationMessage = `${chartType} for ${columnName}`;
        }
        
        // Show loading
        this.showChartLoading();
        
        try {
            const response = await fetch(apiUrl);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showChart(data.chart_html);
                this.showChartSuccess(data, chartType);
                console.log('Chart generated successfully for', data.data_points, 'data points');
            } else {
                throw new Error(data.error || 'Error desconocido al generar el gráfico');
            }
            
        } catch (error) {
            console.error('Error generating chart:', error);
            this.showChartError(error.message);
        } finally {
            this.hideChartLoading();
        }
    }

    showValidationError(message) {
        // Show temporary error message
        const generateBtn = document.getElementById('generate_chart_btn');
        if (generateBtn) {
            const originalText = generateBtn.innerHTML;
            generateBtn.innerHTML = `
                <svg class="w-4 h-4 inline mr-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                ${message}
            `;
            generateBtn.classList.add('bg-red-600', 'hover:bg-red-700');
            generateBtn.classList.remove('bg-brand-600', 'hover:bg-brand-700');
            
            // Reset after 3 seconds
            setTimeout(() => {
                generateBtn.innerHTML = originalText;
                generateBtn.classList.remove('bg-red-600', 'hover:bg-red-700');
                generateBtn.classList.add('bg-brand-600', 'hover:bg-brand-700');
            }, 3000);
        }
    }

    showChartSuccess(data, chartType) {
        // Show success feedback based on chart type
        let message = '';
        if (chartType === 'scatter') {
            message = `Diagrama de dispersión generado: ${data.x_column} vs ${data.y_column} (${data.data_points} puntos)`;
        } else {
            message = `${chartType === 'histogram' ? 'Histograma' : 'Diagrama de caja'} generado para ${data.column_name} (${data.data_points} valores)`;
        }
        
        // Temporarily update button with success message
        const generateBtn = document.getElementById('generate_chart_btn');
        if (generateBtn) {
            const originalText = generateBtn.innerHTML;
            generateBtn.innerHTML = `
                <svg class="w-4 h-4 inline mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                ¡Gráfico generado!
            `;
            generateBtn.classList.add('bg-green-600', 'hover:bg-green-700');
            generateBtn.classList.remove('bg-brand-600', 'hover:bg-brand-700');
            
            // Reset after 2 seconds
            setTimeout(() => {
                generateBtn.innerHTML = originalText;
                generateBtn.classList.remove('bg-green-600', 'hover:bg-green-700');
                generateBtn.classList.add('bg-brand-600', 'hover:bg-brand-700');
            }, 2000);
        }
        
        console.log('Chart success:', message);
    }
    
    showChartLoading() {
        const loadingDiv = document.getElementById('chart_loading');
        const chartContainer = document.getElementById('chart_container');
        
        if (loadingDiv) {
            loadingDiv.classList.remove('hidden');
        }
        if (chartContainer) {
            chartContainer.classList.add('hidden');
        }
    }
    
    hideChartLoading() {
        const loadingDiv = document.getElementById('chart_loading');
        if (loadingDiv) {
            loadingDiv.classList.add('hidden');
        }
    }
    
    showChart(chartHtml) {
        const chartContainer = document.getElementById('chart_container');
        const chartContent = document.getElementById('chart_content');
        
        if (chartContainer && chartContent) {
            chartContent.innerHTML = chartHtml;
            chartContainer.classList.remove('hidden');
            
            // Ensure Plotly chart is responsive
            setTimeout(() => {
                if (window.Plotly) {
                    const plotElement = chartContent.querySelector('.plotly-graph-div');
                    if (plotElement) {
                        window.Plotly.Plots.resize(plotElement);
                    }
                }
            }, 100);
        }
    }
    
    hideChart() {
        const chartContainer = document.getElementById('chart_container');
        if (chartContainer) {
            chartContainer.classList.add('hidden');
        }
    }
    
    showChartError(errorMessage) {
        const chartContainer = document.getElementById('chart_container');
        const chartContent = document.getElementById('chart_content');
        
        if (chartContainer && chartContent) {
            chartContent.innerHTML = `
                <div class="flex items-center justify-center h-64">
                    <div class="text-center">
                        <svg class="w-12 h-12 text-error-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                        <h3 class="text-lg font-medium text-foreground-default mb-2">Error al generar gráfico</h3>
                        <p class="text-sm text-foreground-muted">${errorMessage}</p>
                    </div>
                </div>
            `;
            chartContainer.classList.remove('hidden');
        }
    }
    
    // Column management functionality
    toggleColumnPanel() {
        if (this.gridApi) {
            const isOpen = this.gridApi.isSideBarVisible();
            if (isOpen) {
                this.gridApi.setSideBarVisible(false);
            } else {
                this.gridApi.setSideBarVisible(true);
                this.gridApi.openToolPanel('columns');
            }
        }
    }
    
    getCurrentTheme() {
        // Check if dark mode is active
        const isDarkMode = document.documentElement.classList.contains('dark');
        return isDarkMode ? 'ag-theme-quartz-dark' : 'ag-theme-quartz';
    }
    
    setupThemeChangeListener() {
        // Watch for theme changes and update grid
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'class') {
                    const gridContainer = document.querySelector('#data-preview-grid');
                    if (gridContainer) {
                        const newTheme = this.getCurrentTheme();
                        // Remove old theme classes
                        gridContainer.classList.remove('ag-theme-quartz', 'ag-theme-quartz-dark');
                        // Add new theme class
                        gridContainer.classList.add(newTheme);
                    }
                }
            });
        });
        
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class']
        });
    }
    
    createCustomHeaderComponent() {
        // Enhanced custom header component following AG Grid best practices
        function CustomHeaderComponent() {}
        
        CustomHeaderComponent.prototype.init = function(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.className = 'custom-header-container';
            
            // Enhanced horizontal flexbox layout with proper accessibility and improved spacing
            this.eGui.style.cssText = 'display: flex; align-items: center; justify-content: flex-start; height: 100%; padding: 6px 8px; gap: 12px; min-width: 0;';
            this.eGui.setAttribute('role', 'columnheader');
            this.eGui.setAttribute('aria-label', `Column ${params.displayName}`);
            
            // Add checkbox for column selection (for all columns) or row selection (first column only)
            if (params.enableColumnSelection || params.enableRowSelection) {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'column-select-checkbox';
                checkbox.style.cssText = 'cursor: pointer; margin: 0; flex-shrink: 0; accent-color: var(--ag-accent-color); order: -1;';
                
                if (params.enableColumnSelection) {
                    checkbox.setAttribute('aria-label', `Select column ${params.displayName}`);
                    // Enhanced checkbox interaction for column selection
                    checkbox.addEventListener('change', (e) => {
                        e.stopPropagation();
                        // Prevent sorting when clicking checkbox
                        if (e.target.checked) {
                            if (window.dataStudio) {
                                window.dataStudio.selectColumn(params.column.getColId());
                            }
                        } else {
                            if (window.dataStudio) {
                                window.dataStudio.deselectColumn(params.column.getColId());
                            }
                        }
                        
                        // Visual feedback for selection state
                        this.eGui.classList.toggle('column-selected', e.target.checked);
                    });
                } else {
                    checkbox.setAttribute('aria-label', `Select row ${params.displayName}`);
                    // Row selection logic can be implemented here if needed
                }
                
                this.eGui.appendChild(checkbox);
                this.checkbox = checkbox; // Store reference for cleanup
            }
            
            // Enhanced header text container with better overflow handling
            const headerTextContainer = document.createElement('div');
            headerTextContainer.style.cssText = 'flex: 1; display: flex; align-items: center; justify-content: center; min-width: 0; overflow: hidden;';
            
            if (params.enableSorting) {
                // Enhanced sortable header text with improved accessibility
                const headerText = document.createElement('div');
                headerText.textContent = params.displayName;
                headerText.className = 'header-text sortable';
                headerText.style.cssText = `
                    cursor: pointer; 
                    user-select: none; 
                    font-weight: 600; 
                    text-align: center; 
                    white-space: nowrap; 
                    overflow: hidden; 
                    text-overflow: ellipsis;
                    transition: color 0.2s ease, text-shadow 0.2s ease;
                    flex: 1;
                `;
                headerText.setAttribute('tabindex', '0'); // Make focusable
                headerText.setAttribute('role', 'button');
                headerText.setAttribute('aria-label', `Sort by ${params.displayName}`);
                
                // Enhanced sort indicator with better visual feedback
                const sortIndicator = document.createElement('span');
                sortIndicator.className = 'sort-indicator';
                sortIndicator.style.cssText = 'margin-left: 4px; font-size: 12px; opacity: 0.7; transition: all 0.2s ease;';
                sortIndicator.setAttribute('aria-hidden', 'true');
                
                headerText.appendChild(sortIndicator);
                headerTextContainer.appendChild(headerText);
                
                // Enhanced sorting interaction with keyboard support
                const handleSort = (e) => {
                    e.stopPropagation();
                    params.progressSort();
                };
                
                headerText.addEventListener('click', handleSort);
                headerText.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleSort(e);
                    }
                });
                
                // Enhanced hover effects for better UX
                headerText.addEventListener('mouseenter', () => {
                    headerText.style.color = 'var(--ag-accent-color)';
                    headerText.style.textShadow = '0 0 4px var(--ag-accent-color-alpha, rgba(97, 175, 239, 0.3))';
                    sortIndicator.style.opacity = '1';
                });
                
                headerText.addEventListener('mouseleave', () => {
                    headerText.style.color = '';
                    headerText.style.textShadow = '';
                    sortIndicator.style.opacity = '0.7';
                });
                
                // Enhanced sort indicator update with animations
                this.updateSortIndicator = () => {
                    const sort = params.column.getSort();
                    sortIndicator.style.transition = 'all 0.3s ease';
                    
                    if (sort === 'asc') {
                        sortIndicator.textContent = '↑';
                        sortIndicator.style.color = 'var(--ag-accent-color)';
                        sortIndicator.style.transform = 'scale(1.2)';
                        headerText.setAttribute('aria-label', `Sorted ascending by ${params.displayName}. Click to sort descending.`);
                    } else if (sort === 'desc') {
                        sortIndicator.textContent = '↓';
                        sortIndicator.style.color = 'var(--ag-accent-color)';
                        sortIndicator.style.transform = 'scale(1.2)';
                        headerText.setAttribute('aria-label', `Sorted descending by ${params.displayName}. Click to remove sort.`);
                    } else {
                        sortIndicator.textContent = '';
                        sortIndicator.style.color = 'var(--ag-foreground-color, #666)';
                        sortIndicator.style.transform = 'scale(1)';
                        headerText.setAttribute('aria-label', `Sort by ${params.displayName}`);
                    }
                };
                
                // Listen for sort changes
                params.column.addEventListener('sortChanged', this.updateSortIndicator);
                this.updateSortIndicator();
                
                // Store references for cleanup
                this.headerText = headerText;
                this.sortIndicator = sortIndicator;
            } else {
                // Enhanced non-sortable header
                const headerText = document.createElement('div');
                headerText.textContent = params.displayName;
                headerText.className = 'header-text';
                headerText.style.cssText = `
                    font-weight: 600; 
                    text-align: center; 
                    white-space: nowrap; 
                    overflow: hidden; 
                    text-overflow: ellipsis;
                    color: var(--ag-foreground-color);
                `;
                headerText.setAttribute('title', params.displayName); // Tooltip for truncated text
                headerTextContainer.appendChild(headerText);
                
                this.headerText = headerText;
            }
            
            this.eGui.appendChild(headerTextContainer);
        };
        
        CustomHeaderComponent.prototype.getGui = function() {
            return this.eGui;
        };
        
        // Enhanced cleanup with proper event listener removal
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
}

// Initialize Data Studio when script loads
const dataStudio = new DataStudio();

// Make it globally available for inline event handlers
window.dataStudio = dataStudio;

// Global functions for Alpine.js
window.toggleColumnPanel = function() {
    if (window.dataStudio) {
        window.dataStudio.toggleColumnPanel();
    }
};
