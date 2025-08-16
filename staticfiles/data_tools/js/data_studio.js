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
        // Create column definitions - only first column gets checkbox selection
        const columnDefs = window.columnDefsData.map((col, index) => {
            const colDef = {
                headerName: col.headerName,
                field: col.field,
                ...col
            };
            
            // Only apply checkbox selection to the first column
            if (index === 0) {
                colDef.headerCheckboxSelection = true;
                colDef.headerCheckboxSelectionFilteredOnly = true;
                colDef.checkboxSelection = true;
                // Prevent sorting when clicking on checkbox
                colDef.suppressHeaderMenuButton = true;
                colDef.sortable = true; // Keep sortable but handle click events
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
            
            // Default column definitions with sensible defaults and tooltips
            defaultColDef: {
                width: 150,
                minWidth: 120,
                resizable: true,
                tooltipValueGetter: (params) => params.value
            },
            
            // Selection configuration
            rowSelection: 'multiple',
            suppressRowClickSelection: false,
            
            // Header configuration for column selection
            headerHeight: 60,
            suppressMenuHide: true,
            
            // Header component configuration
            components: {
                customHeaderComponent: this.createCustomHeaderComponent()
            },
            
            // Grid behavior
            animateRows: true,
            enableCellTextSelection: true,
            suppressCellFocus: true,
            
            // Theme - dynamically set based on dark mode
            theme: this.getCurrentTheme(),
            
            // Event handlers
            onSelectionChanged: () => this.onSelectionChanged(),
            onColumnMoved: () => this.onColumnChanged(),
            onColumnVisible: () => this.onColumnChanged(),
            onColumnPinned: () => this.onColumnChanged(),
            
            // Grid ready callback
            onGridReady: (params) => {
                this.gridApi = params.api;
                this.columnApi = params.columnApi;
                
                // Set up theme change listener
                this.setupThemeChangeListener();
                
                // Intelligently resize columns to fit their content and headers
                const allVisibleColumnIds = params.api.getColumns().map(column => column.getId());
                params.api.autoSizeColumns(allVisibleColumnIds, false);
                
                console.log('Data Studio Grid initialized with', window.gridRowData.length, 'rows');
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
    }
    
    populateNumericColumns() {
        const columnSelect = document.getElementById('analysis_column_select');
        if (!columnSelect || !window.columnDefsData) return;
        
        // Clear existing options except the first one
        while (columnSelect.children.length > 1) {
            columnSelect.removeChild(columnSelect.lastChild);
        }
        
        // Get numeric columns from grid data
        const numericColumns = this.getNumericColumns();
        
        // Add numeric columns to select
        numericColumns.forEach(columnName => {
            const option = document.createElement('option');
            option.value = columnName;
            option.textContent = columnName;
            columnSelect.appendChild(option);
        });
        
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
        // Column selection change
        const columnSelect = document.getElementById('analysis_column_select');
        if (columnSelect) {
            columnSelect.addEventListener('change', () => {
                this.onColumnSelectionChange();
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
    
    onColumnSelectionChange() {
        const columnSelect = document.getElementById('analysis_column_select');
        const generateBtn = document.getElementById('generate_chart_btn');
        
        if (columnSelect && generateBtn) {
            generateBtn.disabled = !columnSelect.value;
        }
        
        // Hide chart container when selection changes
        this.hideChart();
    }
    
    async generateChart() {
        const columnSelect = document.getElementById('analysis_column_select');
        const chartTypeSelect = document.getElementById('chart_type_select');
        
        if (!columnSelect.value) {
            alert('Por favor seleccione una columna');
            return;
        }
        
        const columnName = columnSelect.value;
        const chartType = chartTypeSelect.value;
        
        console.log('Generating chart for column:', columnName, 'type:', chartType);
        
        // Show loading
        this.showChartLoading();
        
        try {
            const response = await fetch(`/data_tools/api/generate-chart/?datasource_id=${window.datasourceId}&column_name=${encodeURIComponent(columnName)}&chart_type=${chartType}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.showChart(data.chart_html);
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
        // Custom header component to separate checkbox and sorting functionality
        function CustomHeaderComponent() {}
        
        CustomHeaderComponent.prototype.init = function(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.className = 'custom-header-container';
            this.eGui.style.cssText = 'display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 8px 4px;';
            
            if (params.enableSorting) {
                // Sortable header text
                const headerText = document.createElement('div');
                headerText.textContent = params.displayName;
                headerText.className = 'header-text';
                headerText.style.cssText = 'cursor: pointer; user-select: none; font-weight: 600; text-align: center; margin-bottom: 4px;';
                
                // Add sort indicator
                const sortIndicator = document.createElement('span');
                sortIndicator.className = 'sort-indicator';
                sortIndicator.style.cssText = 'margin-left: 4px; font-size: 10px;';
                
                headerText.appendChild(sortIndicator);
                this.eGui.appendChild(headerText);
                
                // Handle sorting click on text only
                headerText.addEventListener('click', (e) => {
                    e.stopPropagation();
                    params.progressSort();
                });
                
                // Update sort indicator
                this.updateSortIndicator = () => {
                    const sort = params.column.getSort();
                    sortIndicator.textContent = sort === 'asc' ? '↑' : sort === 'desc' ? '↓' : '';
                };
                
                params.column.addEventListener('sortChanged', this.updateSortIndicator);
                this.updateSortIndicator();
            } else {
                // Non-sortable header
                const headerText = document.createElement('div');
                headerText.textContent = params.displayName;
                headerText.style.cssText = 'font-weight: 600; text-align: center; margin-bottom: 4px;';
                this.eGui.appendChild(headerText);
            }
            
            // Add checkbox for selection column
            if (params.enableRowSelection) {
                const checkboxContainer = document.createElement('div');
                checkboxContainer.style.cssText = 'margin-top: 4px;';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.style.cssText = 'cursor: pointer;';
                
                // Handle checkbox click separately from sorting
                checkbox.addEventListener('change', (e) => {
                    e.stopPropagation();
                    params.api.selectAll(e.target.checked);
                });
                
                checkboxContainer.appendChild(checkbox);
                this.eGui.appendChild(checkboxContainer);
            }
        };
        
        CustomHeaderComponent.prototype.getGui = function() {
            return this.eGui;
        };
        
        CustomHeaderComponent.prototype.destroy = function() {
            if (this.params && this.params.column && this.updateSortIndicator) {
                this.params.column.removeEventListener('sortChanged', this.updateSortIndicator);
            }
        };
        
        return CustomHeaderComponent;
    }
}

// Initialize Data Studio when script loads
const dataStudio = new DataStudio();

// Make it globally available for inline event handlers
window.dataStudio = dataStudio;
