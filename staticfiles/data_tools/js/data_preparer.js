document.addEventListener('DOMContentLoaded', function() {
    console.log('Data Preparer JS loaded');
    console.log('Window data available:', {
        gridRowData: typeof window.gridRowData,
        columnDefsData: typeof window.columnDefsData,
        agGrid: typeof agGrid
    });
    
    // Initialize AG Grid
    initializeAGGrid();
    
    // Initialize Chart Functionality
    initializeChartFunctionality();
    
    // Set to store columns that will be removed
    // Using a Set to automatically avoid duplicates
    const removedColumns = new Set();

    // DOM elements we'll interact with
    const removedColumnsList = document.getElementById('removed-columns-list');
    const removedColumnsInput = document.getElementById('removed_columns_input');
    const removeButtons = document.querySelectorAll('.remove-col-btn');
    
    // Feature Engineering elements
    const transformationSelect = document.getElementById('transformation_type');
    const transformationParameters = document.getElementById('transformation_parameters');
    const applyTransformationBtn = document.getElementById('apply_transformation_btn');
    const transformationHistory = document.getElementById('transformation_history');
    const historyList = document.getElementById('history_list');

    // Function to update the interface and the hidden form field
    function updateRemovedColumnsDisplay() {
        // Clear the visual list
        removedColumnsList.innerHTML = '';

        if (removedColumns.size === 0) {
            removedColumnsList.innerHTML = '<span class="text-foreground-secondary text-sm">No columns selected for removal</span>';
        } else {
            // Create a badge for each column to be removed
            removedColumns.forEach(columnName => {
                const badge = document.createElement('span');
                badge.className = 'inline-flex items-center px-3 py-1 rounded-lg text-sm font-medium bg-danger-secondary text-danger-primary border border-danger-primary';
                badge.innerHTML = `
                    ${columnName}
                    <button type="button" class="ml-2 text-danger-primary hover:text-danger-secondary" onclick="removeColumnFromList('${columnName}')">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                `;
                removedColumnsList.appendChild(badge);
            });
        }

        // Update the value of the hidden form field
        // Send it as a JSON string
        removedColumnsInput.value = JSON.stringify(Array.from(removedColumns));
    }

    // Global function to remove column from list (called from badge button)
    window.removeColumnFromList = function(columnName) {
        removedColumns.delete(columnName);
        
        // Find and update the corresponding remove button
        const correspondingButton = document.querySelector(`[data-column="${columnName}"]`);
        if (correspondingButton) {
            correspondingButton.classList.remove('bg-danger-primary', 'text-white', 'border-danger-primary');
            correspondingButton.classList.add('text-danger-primary', 'bg-danger-secondary', 'border-danger-primary');
            correspondingButton.textContent = 'Remove Column';
        }
        
        updateRemovedColumnsDisplay();
    };

    // Add event listener to each "Remove" button
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const columnName = this.getAttribute('data-column');

            // Toggle selection: if column is already there, remove it. If not, add it.
            if (removedColumns.has(columnName)) {
                removedColumns.delete(columnName);
                this.classList.remove('bg-danger-primary', 'text-white', 'border-danger-primary');
                this.classList.add('text-danger-primary', 'bg-danger-secondary', 'border-danger-primary');
                this.textContent = 'Remove Column';
            } else {
                removedColumns.add(columnName);
                this.classList.remove('text-danger-primary', 'bg-danger-secondary', 'border-danger-primary');
                this.classList.add('bg-danger-primary', 'text-white', 'border-danger-primary');
                this.textContent = 'Selected';
            }

            // Update the interface after each click
            updateRemovedColumnsDisplay();
        });
    });

    // Feature Engineering Functionality
    if (transformationSelect) {
        transformationSelect.addEventListener('change', function() {
            const selectedTransformation = this.value;
            
            // Hide all parameter sections
            document.querySelectorAll('.transformation-params').forEach(section => {
                section.classList.add('hidden');
            });
            
            if (selectedTransformation) {
                // Show the parameters container
                transformationParameters.classList.remove('hidden');
                
                // Show the specific parameter section
                const paramSectionMap = {
                    'mean_median_imputer': 'imputer_params',
                    'onehot_encoder': 'encoder_params',
                    'equal_frequency_discretiser': 'discretiser_params'
                };
                
                const sectionId = paramSectionMap[selectedTransformation];
                if (sectionId) {
                    document.getElementById(sectionId).classList.remove('hidden');
                }
                
                // Enable the apply button
                applyTransformationBtn.disabled = false;
            } else {
                // Hide the parameters container
                transformationParameters.classList.add('hidden');
                // Disable the apply button
                applyTransformationBtn.disabled = true;
            }
        });
    }

    // Apply Transformation Button
    if (applyTransformationBtn) {
        applyTransformationBtn.addEventListener('click', function() {
            const selectedTransformation = transformationSelect.value;
            
            if (!selectedTransformation) {
                alert('Please select a transformation type.');
                return;
            }
            
            // Collect parameters based on transformation type
            const params = collectTransformationParams(selectedTransformation);
            
            // Apply the transformation via AJAX
            applyTransformation(selectedTransformation, params);
        });
    }

    // Function to collect transformation parameters
    function collectTransformationParams(transformationType) {
        const params = { transformation_type: transformationType };
        
        switch (transformationType) {
            case 'mean_median_imputer':
                params.strategy = document.querySelector('[name="imputer_strategy"]').value;
                params.variables = document.querySelector('[name="imputer_variables"]').value;
                break;
            case 'onehot_encoder':
                params.top_categories = document.querySelector('[name="encoder_top_categories"]').value;
                params.drop_last = document.querySelector('[name="encoder_drop_last"]').value === 'true';
                break;
            case 'equal_frequency_discretiser':
                params.bins = parseInt(document.querySelector('[name="discretiser_bins"]').value);
                params.return_boundaries = document.querySelector('[name="discretiser_return_boundaries"]').value === 'true';
                break;
        }
        
        return params;
    }

    // Function to apply transformation via AJAX
    function applyTransformation(transformationType, params) {
        // Show loading state
        applyTransformationBtn.disabled = true;
        applyTransformationBtn.textContent = 'Applying Transformation...';
        
        // Get the current datasource ID from the URL
        const urlParts = window.location.pathname.split('/');
        const datasourceId = urlParts[urlParts.length - 2]; // Gets the UUID before the final slash
        
        // Prepare form data
        const formData = new FormData();
        formData.append('action', 'apply_transformation');
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        
        // Add transformation parameters
        Object.keys(params).forEach(key => {
            formData.append(key, params[key]);
        });
        
        // Send AJAX request
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add transformation to history
                addTransformationToHistory(transformationType, params, data.message);
                
                // Update the data preview (reload the page to show new data)
                // In a more sophisticated implementation, you could update just the table
                window.location.reload();
            } else {
                alert('Error applying transformation: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error applying transformation. Please try again.');
        })
        .finally(() => {
            // Reset button state
            applyTransformationBtn.disabled = false;
            applyTransformationBtn.textContent = 'Apply Transformation';
        });
    }

    // Function to add transformation to history
    function addTransformationToHistory(transformationType, params, message) {
        // Show history section if hidden
        transformationHistory.classList.remove('hidden');
        
        // Create history item
        const historyItem = document.createElement('div');
        historyItem.className = 'flex items-center justify-between p-3 bg-success-secondary border border-success-primary rounded-lg';
        
        const transformationNames = {
            'mean_median_imputer': 'Mean/Median Imputation',
            'onehot_encoder': 'One-Hot Encoding',
            'equal_frequency_discretiser': 'Equal Frequency Discretization'
        };
        
        historyItem.innerHTML = `
            <div>
                <span class="font-medium text-success-primary">${transformationNames[transformationType]}</span>
                <p class="text-sm text-success-primary opacity-80">${message}</p>
            </div>
            <svg class="w-5 h-5 text-success-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        `;
        
        historyList.appendChild(historyItem);
    }

    // Call the function once at the beginning to initialize the screen
    updateRemovedColumnsDisplay();
});

// AG Grid Initialization Function
function initializeAGGrid() {
    console.log('Initializing AG Grid...');
    
    const gridContainer = document.getElementById('data-preview-grid');
    if (!gridContainer) {
        console.error('Grid container not found!');
        return;
    }
    
    // Get data from Django context (these should be available in the template)
    const columnDefs = window.columnDefsData || [];
    const rowData = window.gridRowData || [];
    
    console.log('Column definitions:', columnDefs);
    console.log('Row data:', rowData);
    console.log('Column defs length:', columnDefs.length);
    console.log('Row data length:', rowData.length);
    
    if (columnDefs.length === 0 || rowData.length === 0) {
        console.warn('No data available for AG Grid preview');
        gridContainer.innerHTML = '<div class="flex items-center justify-center h-full text-foreground-secondary"><p>No data available for preview</p></div>';
        return;
    }
    
    const gridOptions = {
        columnDefs: columnDefs,
        rowData: rowData,
        defaultColDef: {
            sortable: true,
            filter: true,
            resizable: true,
            minWidth: 100,
            flex: 1
        },
        pagination: true,
        paginationPageSize: 20,
        animateRows: true,
        suppressCellFocus: true,
        rowSelection: 'single',
        onGridReady: function(event) {
            console.log('AG Grid ready!');
            // Auto-size columns to fit content
            event.api.sizeColumnsToFit();
        },
        onFirstDataRendered: function(event) {
            console.log('AG Grid first data rendered!');
            // Auto-size columns when data is first loaded
            event.api.sizeColumnsToFit();
        }
    };
    
    // Check if agGrid is available
    if (typeof agGrid === 'undefined') {
        console.error('AG Grid library not loaded!');
        gridContainer.innerHTML = '<div class="flex items-center justify-center h-full text-danger-600"><p>AG Grid library not loaded</p></div>';
        return;
    }
    
    console.log('Creating AG Grid...');
    
    // Create the grid
    try {
        const grid = agGrid.createGrid(gridContainer, gridOptions);
        console.log('AG Grid created successfully:', grid);
        
        // Store grid instance globally for potential future use
        window.dataPreviewGrid = grid;
    } catch (error) {
        console.error('Error creating AG Grid:', error);
        gridContainer.innerHTML = '<div class="flex items-center justify-center h-full text-danger-600"><p>Error creating grid: ' + error.message + '</p></div>';
    }
}

// Chart Functionality Initialization
function initializeChartFunctionality() {
    const columnSelector = document.getElementById('column-selector');
    const chartTypeSelector = document.getElementById('chart-type-selector');
    const chartContainer = document.getElementById('chart-container');
    
    if (!columnSelector || !chartTypeSelector || !chartContainer) return;
    
    // Add event listeners for chart generation
    columnSelector.addEventListener('change', generateChart);
    chartTypeSelector.addEventListener('change', generateChart);
    
    function generateChart() {
        const selectedColumn = columnSelector.value;
        const chartType = chartTypeSelector.value;
        
        if (!selectedColumn) {
            // Show placeholder message
            chartContainer.innerHTML = `
                <div class="min-h-[400px] bg-background-secondary border border-border-primary rounded-lg flex items-center justify-center">
                    <div class="text-center text-foreground-secondary">
                        <svg class="w-16 h-16 mx-auto mb-4 text-foreground-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                        <p class="text-sm">Selecciona una columna para ver su distribución</p>
                    </div>
                </div>
            `;
            return;
        }
        
        // Show loading state
        chartContainer.innerHTML = `
            <div class="min-h-[400px] bg-background-secondary border border-border-primary rounded-lg flex items-center justify-center">
                <div class="text-center">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary mx-auto mb-4"></div>
                    <p class="text-sm text-foreground-secondary">Generando gráfico...</p>
                </div>
            </div>
        `;
        
        // Get datasource ID from URL
        const urlParts = window.location.pathname.split('/');
        const datasourceId = urlParts[urlParts.length - 2];
        
        // Make API call to generate chart
        const params = new URLSearchParams({
            datasource_id: datasourceId,
            column_name: selectedColumn,
            chart_type: chartType
        });
        
        fetch(`/data-tools/api/generate-chart/?${params}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Display the chart
                    chartContainer.innerHTML = data.chart_html;
                    
                    // Add some styling to the chart container
                    const plotlyDiv = chartContainer.querySelector('#plotly-chart');
                    if (plotlyDiv) {
                        plotlyDiv.style.width = '100%';
                        plotlyDiv.style.height = '400px';
                    }
                } else {
                    // Show error message
                    chartContainer.innerHTML = `
                        <div class="min-h-[400px] bg-background-secondary border border-border-primary rounded-lg flex items-center justify-center">
                            <div class="text-center text-danger-600">
                                <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                </svg>
                                <p class="text-sm">Error: ${data.error}</p>
                            </div>
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error generating chart:', error);
                chartContainer.innerHTML = `
                    <div class="min-h-[400px] bg-background-secondary border border-border-primary rounded-lg flex items-center justify-center">
                        <div class="text-center text-danger-600">
                            <svg class="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            <p class="text-sm">Error al generar el gráfico. Inténtalo de nuevo.</p>
                        </div>
                    </div>
                `;
            });
    }
}