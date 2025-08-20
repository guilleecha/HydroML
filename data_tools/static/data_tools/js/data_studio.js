/**
 * Data Studio Clean - Session Management and Grid Functionality
 * Handles session state, data grid operations, and user interactions.
 */

function dataStudioApp() {
    return {
        activeForm: null,
        sessionActive: false,
        sessionInfo: null,

        init() {
            this.initializeGrid();
            this.checkSessionStatus();
        },

        closeForm() {
            this.activeForm = null;
        },

        async checkSessionStatus() {
            try {
                const response = await fetch(`/tools/api/studio/${window.datasourceId}/session/status/`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });
                
                const data = await response.json();
                if (data.success && data.session_info.session_exists) {
                    this.updateSessionStatus(data.session_info);
                    this.updateDataGrid(data.data_preview, data.column_info);
                }
            } catch (error) {
                console.error('Failed to check session status:', error);
            }
        },

        updateSessionStatus(sessionInfo) {
            this.sessionInfo = sessionInfo;
            this.sessionActive = sessionInfo.session_exists;
            
            const statusIndicator = document.getElementById('session-status-indicator');
            const statusText = document.getElementById('session-status-text');
            const sessionInfoPanel = document.getElementById('session-info');
            
            if (this.sessionActive) {
                statusIndicator.className = 'w-3 h-3 rounded-full bg-green-400';
                statusText.textContent = 'Active session';
                sessionInfoPanel.classList.remove('hidden');
                
                // Update session info details
                document.getElementById('history-info').textContent = `${sessionInfo.history_length} operations`;
                document.getElementById('position-info').textContent = `${sessionInfo.current_position}/${sessionInfo.history_length}`;
                document.getElementById('rows-info').textContent = sessionInfo.current_shape ? sessionInfo.current_shape[0] : '0';
                document.getElementById('columns-info').textContent = sessionInfo.current_shape ? sessionInfo.current_shape[1] : '0';
                
                // Enable/disable buttons
                document.getElementById('initialize-session-btn').style.display = 'none';
                document.getElementById('undo-btn').disabled = sessionInfo.current_position === 0;
                document.getElementById('redo-btn').disabled = sessionInfo.current_position === sessionInfo.history_length;
                document.getElementById('save-session-btn').disabled = false;
            } else {
                statusIndicator.className = 'w-3 h-3 rounded-full bg-gray-400';
                statusText.textContent = 'No session';
                sessionInfoPanel.classList.add('hidden');
                
                // Reset buttons
                document.getElementById('initialize-session-btn').style.display = 'flex';
                document.getElementById('undo-btn').disabled = true;
                document.getElementById('redo-btn').disabled = true;
                document.getElementById('save-session-btn').disabled = true;
            }
        },

        updateDataGrid(dataPreview, columnInfo) {
            if (this.gridApi && dataPreview && columnInfo) {
                this.gridApi.setGridOption('columnDefs', columnInfo);
                this.gridApi.setGridOption('rowData', dataPreview);
            }
        },

        initializeGrid() {
            // Prevent double initialization
            if (this.gridApi) {
                console.log('Grid already initialized, skipping...');
                return;
            }
            
            // Initialize AG Grid with the data
            if (window.gridRowData && window.columnDefsData) {
                console.log('Initializing AG Grid with', window.columnDefsData.length, 'columns and', window.gridRowData.length, 'rows');
                
                // Add row number column as first column
                const columnDefs = [
                    {
                        headerName: '#',
                        field: 'rowNumber',
                        width: 60,
                        pinned: 'left',
                        cellStyle: { 
                            fontWeight: 'bold', 
                            backgroundColor: '#f8fafc',
                            color: '#64748b',
                            textAlign: 'center'
                        },
                        valueGetter: (params) => params.node.rowIndex + 1,
                        suppressMenu: true,
                        sortable: false,
                        filter: false,
                        resizable: false
                    },
                    ...window.columnDefsData
                ];
                
                const gridOptions = {
                    columnDefs: columnDefs,
                    rowData: window.gridRowData,
                    
                    // Column configuration for optimal width usage
                    defaultColDef: {
                        resizable: true,
                        sortable: true,
                        filter: true,
                        floatingFilter: true,
                        minWidth: 100,      // Minimum column width
                        maxWidth: 300,      // Maximum column width to prevent over-stretching
                        flex: 1,            // Flexible sizing to fill available space
                        cellStyle: {
                            'white-space': 'nowrap',
                            'overflow': 'hidden',
                            'text-overflow': 'ellipsis'
                        }
                    },
                    
                    // Grid behavior configuration
                    rowSelection: 'multiple',
                    pagination: true,
                    paginationPageSize: 25,
                    paginationPageSizeSelector: [10, 25, 50, 100, 'All'],
                    suppressRowClickSelection: false,
                    rowSelection: 'multiple',
                    enableCellTextSelection: true,
                    animateRows: true,
                    suppressHorizontalScroll: false, // Allow horizontal scroll if needed
                    
                    // Grid sizing configuration
                    suppressAutoSize: false,
                    skipHeaderOnAutoSize: false,
                    
                    // Event handlers for responsive design
                    onGridReady: (params) => {
                        console.log('Grid ready with', params.api.getDisplayedColDefs().length, 'displayed columns');
                        this.gridApi = params.api; // Store API reference
                        
                        // Size columns to fit container width
                        params.api.sizeColumnsToFit();
                        
                        // Listen for window resize
                        const handleResize = () => {
                            setTimeout(() => {
                                if (this.gridApi) {
                                    this.gridApi.sizeColumnsToFit();
                                }
                            }, 100);
                        };
                        
                        window.addEventListener('resize', handleResize);
                    },
                    
                    onSelectionChanged: (event) => {
                        const selectedRows = event.api.getSelectedRows().length;
                        const selectionInfo = document.getElementById('grid-selection-info');
                        if (selectionInfo) {
                            selectionInfo.textContent = selectedRows > 0 
                                ? `${selectedRows} rows selected` 
                                : 'No selection';
                        }
                    },
                    
                    onPaginationChanged: (event) => {
                        const displayedRows = event.api.getDisplayedRowCount();
                        const displayedInfo = document.getElementById('displayed-rows');
                        if (displayedInfo) {
                            displayedInfo.textContent = displayedRows;
                        }
                    },
                    
                    onFirstDataRendered: (params) => {
                        console.log('First data rendered');
                        params.api.sizeColumnsToFit();
                        this.updateRowCountDisplay(params);
                    },
                    
                    onPaginationChanged: (params) => {
                        this.updateRowCountDisplay(params);
                    },
                    
                    onGridSizeChanged: (params) => {
                        console.log('Grid size changed');
                        params.api.sizeColumnsToFit();
                    }
                };

                const gridDiv = document.querySelector('#data-preview-grid');
                if (gridDiv && !gridDiv.querySelector('.ag-root-wrapper')) {
                    console.log('Creating AG Grid in container:', gridDiv);
                    const gridInstance = agGrid.createGrid(gridDiv, gridOptions);
                    this.gridApi = gridInstance; // Store grid instance
                } else {
                    console.warn('Grid container not found or already has grid content');
                }
            } else {
                console.warn('Grid data not available:', {
                    rowData: !!window.gridRowData,
                    columnDefs: !!window.columnDefsData
                });
            }
        },

        updateRowCountDisplay(params) {
            try {
                const totalRows = params.api.getDisplayedRowCount();
                const pageSize = params.api.paginationGetPageSize();
                const currentPage = params.api.paginationGetCurrentPage();
                const startRow = currentPage * pageSize + 1;
                const endRow = Math.min((currentPage + 1) * pageSize, totalRows);
                
                // Update the displayed rows count
                const displayedRowsElement = document.getElementById('displayed-rows');
                if (displayedRowsElement) {
                    if (pageSize === totalRows) {
                        displayedRowsElement.textContent = 'all';
                    } else {
                        displayedRowsElement.textContent = `${startRow}-${endRow}`;
                    }
                }
                
                // Update total rows count
                const gridRowCountElement = document.getElementById('grid-row-count');
                if (gridRowCountElement) {
                    gridRowCountElement.textContent = totalRows.toLocaleString();
                }
            } catch (error) {
                console.warn('Error updating row count display:', error);
            }
        },

        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                   document.querySelector('meta[name="csrf-token"]')?.content || '';
        }
    }
}

// Session Management Functions
async function initializeSession() {
    try {
        const response = await fetch(`/tools/api/studio/${window.datasourceId}/session/initialize/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        const data = await response.json();
        if (data.success) {
            // Update the app state
            const app = Alpine.$data(document.querySelector('[x-data]'));
            app.updateSessionStatus(data.session_info);
            app.updateDataGrid(data.data_preview, data.column_info);
            alert('Session initialized successfully');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Failed to initialize session:', error);
        alert('Failed to initialize session');
    }
}

async function undoOperation() {
    try {
        const response = await fetch(`/tools/api/studio/${window.datasourceId}/session/undo/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        const data = await response.json();
        if (data.success) {
            const app = Alpine.$data(document.querySelector('[x-data]'));
            app.updateSessionStatus(data.session_info);
            app.updateDataGrid(data.data_preview, data.column_info);
            alert('Operation undone successfully');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Failed to undo operation:', error);
        alert('Failed to undo operation');
    }
}

async function redoOperation() {
    try {
        const response = await fetch(`/tools/api/studio/${window.datasourceId}/session/redo/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });
        
        const data = await response.json();
        if (data.success) {
            const app = Alpine.$data(document.querySelector('[x-data]'));
            app.updateSessionStatus(data.session_info);
            app.updateDataGrid(data.data_preview, data.column_info);
            alert('Operation redone successfully');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Failed to redo operation:', error);
        alert('Failed to redo operation');
    }
}

async function saveSession() {
    const name = prompt('Enter name for the new dataset:', `${window.datasourceName}_transformed`);
    if (!name) return;
    
    const description = prompt('Enter description (optional):');
    
    try {
        const response = await fetch(`/tools/api/studio/${window.datasourceId}/session/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                name: name,
                description: description || `Transformed version of ${window.datasourceName}`
            })
        });
        
        const data = await response.json();
        if (data.success) {
            alert('Data saved successfully as new datasource: ' + data.new_datasource.name);
            // Session is cleared after save
            const app = Alpine.$data(document.querySelector('[x-data]'));
            app.sessionActive = false;
            app.updateSessionStatus({ session_exists: false });
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Failed to save session:', error);
        alert('Failed to save session');
    }
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name="csrf-token"]')?.content || '';
}

/**
 * Data Studio Sidebar - Tools and Column Management
 * Handles sidebar tools including column removal and missing data analysis.
 */
function dataStudioSidebar() {
    return {
        openColumnManager: false,
        openMissingDataTool: false,
        columns: window.columnListData || [],
        selected: [],
        selectedTargetColumn: '',
        selectedRequiredVars: [],
        
        toggleSelect(name) {
            const idx = this.selected.indexOf(name);
            if (idx === -1) this.selected.push(name);
            else this.selected.splice(idx, 1);
        },
        
        confirmRemoval() {
            if (!confirm('¿Confirmar eliminación de las columnas seleccionadas? Esta acción no puede deshacerse en la sesión actual.')) return;

            // Populate hidden form and submit
            const input = document.getElementById('removed_columns_input_sidebar');
            input.value = JSON.stringify(this.selected);

            // Create FormData to send via fetch (to reuse existing handler which expects POST to same URL)
            const form = document.getElementById('column-removal-form');
            const action = window.location.pathname; // current page handles POST to apply removal

            // Build form data
            const fd = new FormData(form);
            fd.set('removed_columns', input.value);

            fetch(action, {
                method: 'POST',
                body: fd,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(r => r.json())
            .then(data => {
                if (data.success === false) {
                    alert('Error al eliminar columnas: ' + (data.error || 'Unknown'));
                } else {
                    // On success, reload the page to reflect changes
                    window.location.reload();
                }
            })
            .catch(e => {
                console.error('Error removing columns:', e);
                alert('Error al contactar al servidor. Intenta de nuevo.');
            });
        },
        
        // Missing Data Analysis Functions
        init() {
            this.updateMissingDataStats();
        },
        
        updateMissingDataStats() {
            // Calculate quick stats from columns data
            const colsWithMissing = this.columns.filter(c => c.missing_percentage && c.missing_percentage > 0).length;
            const totalMissingValues = this.columns.reduce((sum, c) => sum + (c.missing_count || 0), 0);
            const totalValues = this.columns.reduce((sum, c) => sum + (c.total_values || 0), 0);
            const completeness = totalValues > 0 ? ((totalValues - totalMissingValues) / totalValues * 100).toFixed(1) : 0;
            
            // Update sidebar stats
            const missingColsEl = document.getElementById('sidebar-missing-cols');
            const missingValuesEl = document.getElementById('sidebar-missing-values');
            const completenessEl = document.getElementById('sidebar-completeness');
            
            if (missingColsEl) missingColsEl.textContent = colsWithMissing;
            if (missingValuesEl) missingValuesEl.textContent = totalMissingValues.toLocaleString();
            if (completenessEl) completenessEl.textContent = completeness + '%';
        },
        
        async startMissingDataAnalysis() {
            if (!this.selectedTargetColumn) {
                alert('Por favor selecciona una columna objetivo para el análisis.');
                return;
            }
            
            if (this.selectedRequiredVars.length === 0) {
                alert('Por favor selecciona al menos una variable requerida.');
                return;
            }
            
            const payload = {
                datasource_id: window.datasourceId,
                target_column: this.selectedTargetColumn,
                required_variables: this.selectedRequiredVars
            };
            
            try {
                const response = await fetch('/data-tools/run-deep-missing-analysis/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(payload)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Redirect to results page
                    window.location.href = `/data-tools/missing-data-results/${data.task_id}/`;
                } else {
                    alert('Error iniciando análisis: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al contactar el servidor.');
            }
        },
        
        generateHeatmap() {
            alert('🔥 Funcionalidad de heatmap próximamente!\n\nPor ahora usa "Análisis Profundo" para generar heatmaps interactivos.');
        },
        
        showPatternAnalysis() {
            alert('📊 Análisis de patrones próximamente!\n\nEsta funcionalidad mostrará patrones comunes en datos faltantes.');
        },
        
        startDataImputation() {
            // New Data Imputer functionality
            if (!this.selectedTargetColumn) {
                alert('⚠️ Por favor selecciona una columna objetivo antes de iniciar la imputación de datos.');
                return;
            }
            
            if (this.selectedRequiredVars.length === 0) {
                alert('⚠️ Por favor selecciona al menos una variable requerida para la imputación.');
                return;
            }
            
            // Show imputer configuration dialog
            const imputationMethod = prompt(
                '🔧 Selecciona el método de imputación:\n\n' +
                '1. mean - Media aritmética (solo numéricos)\n' +
                '2. median - Mediana (solo numéricos)\n' +
                '3. mode - Moda (categóricos y numéricos)\n' +
                '4. forward_fill - Llenar hacia adelante\n' +
                '5. backward_fill - Llenar hacia atrás\n' +
                '6. interpolate - Interpolación lineal\n\n' +
                'Escribe el número o nombre del método:',
                'mean'
            );
            
            if (imputationMethod && imputationMethod.trim()) {
                alert(
                    '🚀 Data Imputer configurado!\n\n' +
                    `Columna objetivo: ${this.selectedTargetColumn}\n` +
                    `Variables: ${this.selectedRequiredVars.join(', ')}\n` +
                    `Método: ${imputationMethod}\n\n` +
                    '⏳ Esta funcionalidad estará disponible próximamente.'
                );
            }
        }
    }
}