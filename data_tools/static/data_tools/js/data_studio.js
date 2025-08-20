/**
 * Data Studio Clean - Session Management and Grid Functionality
 * Handles session state, data grid operations, and user interactions.
 */

function dataStudioApp() {
    return {
        activeForm: null,
        sessionActive: false,
        sessionInfo: null,
        
        pagination: {
            currentPage: 1,
            totalPages: 1,
            pageSize: 25,
            totalRows: 0,
            availablePageSizes: [10, 25, 50, 100, 'All'],
            jumpToPage: 1
        },

        filterManager: null,
        filterState: {
            showFilterBuilder: false,
            showFilterPresets: false,
            showSaveFilterDialog: false,
            selectedFilterColumn: '',
            availableColumns: [],
            activeFilters: {},
            presets: []
        },

        navigationState: {
            currentSection: 'overview',
            activeTab: null,
            breadcrumbPath: [],
            workflowStep: 0,
            totalSteps: 0,
            sidebarSections: ['overview', 'transformation', 'advanced-filters', 'visualization', 'export']
        },

        init() {
            this.initializeGrid();
            this.checkSessionStatus();
            this.setupFilterEventListeners();
        },

        setupFilterEventListeners() {
            // Listen for filter UI build events
            document.addEventListener('build-filter-ui', (event) => {
                this.buildFilterUI(event.detail);
            });

            // Listen for filter preset events
            document.addEventListener('save-current-filters', () => {
                this.saveCurrentFilters();
            });

            document.addEventListener('load-filter-preset', (event) => {
                this.loadFilterPreset(event.detail);
            });

            document.addEventListener('delete-filter-preset', (event) => {
                this.deleteFilterPreset(event.detail);
            });

            document.addEventListener('clear-all-filters', () => {
                this.clearAllFilters();
            });

            // Listen for filter application events
            document.addEventListener('apply-multi-select-filter', (event) => {
                this.applyMultiSelectFilter(event.detail);
            });

            document.addEventListener('apply-range-filter', (event) => {
                this.applyRangeFilter(event.detail);
            });

            document.addEventListener('apply-text-filter', (event) => {
                this.applyTextFilter(event.detail);
            });

            document.addEventListener('remove-filter', (event) => {
                this.removeFilter(event.detail);
            });

            // Listen for navigation events
            document.addEventListener('set-active-section', (event) => {
                this.setActiveSection(event.detail);
            });

            // Listen for workflow progress test
            document.addEventListener('test-workflow-progress', () => {
                this.testWorkflowProgress();
            });
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
                    
                    onFirstDataRendered: (params) => {
                        console.log('First data rendered');
                        params.api.sizeColumnsToFit();
                        this.updateRowCountDisplay(params);
                        this.updatePaginationState(params);
                        this.initializeFilterManager();
                        this.initializeNavigation();
                    },
                    
                    onPaginationChanged: (params) => {
                        this.updateRowCountDisplay(params);
                        this.updatePaginationState(params);
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

        updatePaginationState(params) {
            try {
                const totalRows = params.api.getDisplayedRowCount();
                const pageSize = params.api.paginationGetPageSize();
                const currentPage = params.api.paginationGetCurrentPage() + 1; // AG Grid is 0-based
                const totalPages = Math.ceil(totalRows / pageSize);

                this.pagination.currentPage = currentPage;
                this.pagination.totalPages = totalPages;
                this.pagination.pageSize = pageSize;
                this.pagination.totalRows = totalRows;
                this.pagination.jumpToPage = currentPage;
            } catch (error) {
                console.warn('Error updating pagination state:', error);
            }
        },

        navigateToPage(page) {
            if (this.gridApi && page >= 1 && page <= this.pagination.totalPages) {
                this.gridApi.paginationGoToPage(page - 1); // AG Grid is 0-based
            }
        },

        navigateToFirstPage() {
            this.navigateToPage(1);
        },

        navigateToLastPage() {
            this.navigateToPage(this.pagination.totalPages);
        },

        navigateToNextPage() {
            if (this.pagination.currentPage < this.pagination.totalPages) {
                this.navigateToPage(this.pagination.currentPage + 1);
            }
        },

        navigateToPreviousPage() {
            if (this.pagination.currentPage > 1) {
                this.navigateToPage(this.pagination.currentPage - 1);
            }
        },

        jumpToPageInput() {
            const page = parseInt(this.pagination.jumpToPage);
            if (page >= 1 && page <= this.pagination.totalPages) {
                this.navigateToPage(page);
            } else {
                this.pagination.jumpToPage = this.pagination.currentPage;
            }
        },

        changePageSize(newSize) {
            if (this.gridApi) {
                if (newSize === 'All') {
                    this.gridApi.paginationSetPageSize(this.pagination.totalRows);
                } else {
                    this.gridApi.paginationSetPageSize(parseInt(newSize));
                }
            }
        },

        initializeFilterManager() {
            if (!this.gridApi || !window.FilterManager) {
                console.warn('Grid API or FilterManager not available');
                return;
            }

            this.filterManager = new window.FilterManager(this.gridApi, window.columnDefsData);
            window.filterManager = this.filterManager; // Global access for sidebar
            
            this.filterState.availableColumns = (window.columnDefsData || [])
                .filter(col => col.field && col.field !== 'rowNumber')
                .map(col => ({
                    field: col.field,
                    headerName: col.headerName || col.field,
                    type: this.filterManager.getColumnType(col.field)
                }));

            this.updateActiveFiltersDisplay();
        },

        buildFilterUI(columnField) {
            if (!this.filterManager || !columnField) return;

            const container = document.getElementById('filter-builder-container');
            if (!container) return;

            const columnType = this.filterManager.getColumnType(columnField);
            const columnName = this.filterState.availableColumns.find(col => col.field === columnField)?.headerName || columnField;
            
            let html = '';

            switch (columnType) {
                case 'category':
                    html = this.buildMultiSelectFilter(columnField, columnName);
                    break;
                case 'number':
                    html = this.buildRangeFilter(columnField, columnName);
                    break;
                case 'text':
                default:
                    html = this.buildTextFilter(columnField, columnName);
                    break;
            }

            container.innerHTML = html;
            this.attachFilterEventListeners(columnField, columnType);
        },

        buildMultiSelectFilter(columnField, columnName) {
            const uniqueValues = this.filterManager.getUniqueValues(columnField, 100);
            
            return `
                <div class="space-y-2">
                    <div class="text-xs font-medium text-gray-700 dark:text-gray-300">${columnName} (Multi-Select)</div>
                    <div class="max-h-32 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded p-2 bg-white dark:bg-gray-800">
                        ${uniqueValues.map(value => `
                            <label class="flex items-center space-x-2 text-xs py-1 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer">
                                <input type="checkbox" value="${value}" data-filter-field="${columnField}" data-filter-type="multiSelect" 
                                       class="filter-checkbox w-3 h-3 text-cyan-600">
                                <span class="text-gray-700 dark:text-gray-300">${value}</span>
                            </label>
                        `).join('')}
                    </div>
                    <button onclick="document.dispatchEvent(new CustomEvent('apply-multi-select-filter', {detail: '${columnField}'}))" 
                            class="w-full px-3 py-1 text-xs bg-cyan-600 hover:bg-cyan-700 text-white rounded transition-colors">
                        Apply Filter
                    </button>
                </div>
            `;
        },

        buildRangeFilter(columnField, columnName) {
            const range = this.filterManager.getNumericRange(columnField);
            
            return `
                <div class="space-y-2">
                    <div class="text-xs font-medium text-gray-700 dark:text-gray-300">${columnName} (Range)</div>
                    <div class="grid grid-cols-2 gap-2">
                        <div>
                            <label class="text-xs text-gray-600 dark:text-gray-400">Min</label>
                            <input type="number" id="range-min-${columnField}" 
                                   value="${range.min}" min="${range.min}" max="${range.max}" 
                                   class="w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                        </div>
                        <div>
                            <label class="text-xs text-gray-600 dark:text-gray-400">Max</label>
                            <input type="number" id="range-max-${columnField}" 
                                   value="${range.max}" min="${range.min}" max="${range.max}"
                                   class="w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                        </div>
                    </div>
                    <button onclick="document.dispatchEvent(new CustomEvent('apply-range-filter', {detail: '${columnField}'}))" 
                            class="w-full px-3 py-1 text-xs bg-cyan-600 hover:bg-cyan-700 text-white rounded transition-colors">
                        Apply Range
                    </button>
                </div>
            `;
        },

        buildTextFilter(columnField, columnName) {
            return `
                <div class="space-y-2">
                    <div class="text-xs font-medium text-gray-700 dark:text-gray-300">${columnName} (Text)</div>
                    <div class="space-y-2">
                        <select id="text-filter-type-${columnField}" 
                                class="w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                            <option value="contains">Contains</option>
                            <option value="equals">Equals</option>
                            <option value="startsWith">Starts With</option>
                            <option value="endsWith">Ends With</option>
                            <option value="notEqual">Not Equal</option>
                        </select>
                        <input type="text" id="text-filter-value-${columnField}" placeholder="Enter filter text..."
                               class="w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                        <button onclick="document.dispatchEvent(new CustomEvent('apply-text-filter', {detail: '${columnField}'}))" 
                                class="w-full px-3 py-1 text-xs bg-cyan-600 hover:bg-cyan-700 text-white rounded transition-colors">
                            Apply Text Filter
                        </button>
                    </div>
                </div>
            `;
        },

        attachFilterEventListeners(columnField, columnType) {
            // Add event listeners for Enter key on inputs
            if (columnType === 'text') {
                const textInput = document.getElementById(`text-filter-value-${columnField}`);
                if (textInput) {
                    textInput.addEventListener('keydown', (e) => {
                        if (e.key === 'Enter') {
                            document.dispatchEvent(new CustomEvent('apply-text-filter', {detail: columnField}));
                        }
                    });
                }
            } else if (columnType === 'number') {
                const minInput = document.getElementById(`range-min-${columnField}`);
                const maxInput = document.getElementById(`range-max-${columnField}`);
                [minInput, maxInput].forEach(input => {
                    if (input) {
                        input.addEventListener('keydown', (e) => {
                            if (e.key === 'Enter') {
                                document.dispatchEvent(new CustomEvent('apply-range-filter', {detail: columnField}));
                            }
                        });
                    }
                });
            }
        },

        applyMultiSelectFilter(columnField) {
            const checkboxes = document.querySelectorAll(`input[data-filter-field="${columnField}"]:checked`);
            const selectedValues = Array.from(checkboxes).map(cb => cb.value);
            
            if (selectedValues.length > 0) {
                this.filterManager.applyMultiSelectFilter(columnField, selectedValues);
                this.updateActiveFiltersDisplay();
            }
        },

        applyRangeFilter(columnField) {
            const minInput = document.getElementById(`range-min-${columnField}`);
            const maxInput = document.getElementById(`range-max-${columnField}`);
            
            if (minInput && maxInput) {
                const min = parseFloat(minInput.value);
                const max = parseFloat(maxInput.value);
                
                if (!isNaN(min) && !isNaN(max) && min <= max) {
                    this.filterManager.applyRangeFilter(columnField, min, max);
                    this.updateActiveFiltersDisplay();
                }
            }
        },

        applyTextFilter(columnField) {
            const typeSelect = document.getElementById(`text-filter-type-${columnField}`);
            const valueInput = document.getElementById(`text-filter-value-${columnField}`);
            
            if (typeSelect && valueInput && valueInput.value.trim()) {
                this.filterManager.applyTextFilter(columnField, valueInput.value.trim(), typeSelect.value);
                this.updateActiveFiltersDisplay();
            }
        },

        updateActiveFiltersDisplay() {
            if (!this.filterManager) return;

            const container = document.getElementById('active-filters-container');
            if (!container) return;

            const activeFilters = this.filterManager.getActiveFiltersState();
            
            if (Object.keys(activeFilters).length === 0) {
                container.innerHTML = '';
                return;
            }

            const html = Object.entries(activeFilters).map(([field, filterData]) => {
                let displayText = '';
                switch (filterData.type) {
                    case 'multiSelect':
                        displayText = `${filterData.values.length} values`;
                        break;
                    case 'range':
                        displayText = `${filterData.min} - ${filterData.max}`;
                        break;
                    case 'text':
                        displayText = `${filterData.filterType}: "${filterData.value}"`;
                        break;
                }
                
                return `
                    <div class="flex items-center justify-between p-2 bg-cyan-50 dark:bg-cyan-900 border border-cyan-200 dark:border-cyan-700 rounded text-xs">
                        <span class="flex-1">
                            <span class="font-medium text-cyan-800 dark:text-cyan-200">${filterData.displayName}:</span>
                            <span class="text-cyan-600 dark:text-cyan-300 ml-1">${displayText}</span>
                        </span>
                        <button onclick="document.dispatchEvent(new CustomEvent('remove-filter', {detail: '${field}'}))" 
                                class="ml-2 text-cyan-600 hover:text-cyan-800 dark:text-cyan-400 dark:hover:text-cyan-200">
                            ×
                        </button>
                    </div>
                `;
            }).join('');

            container.innerHTML = html;
        },

        removeFilter(field) {
            if (this.filterManager) {
                this.filterManager.clearFilter(field);
                this.updateActiveFiltersDisplay();
            }
        },

        clearAllFilters() {
            if (this.filterManager) {
                this.filterManager.clearAllFilters();
                this.updateActiveFiltersDisplay();
                
                // Clear the filter builder UI
                const container = document.getElementById('filter-builder-container');
                if (container) {
                    container.innerHTML = '';
                }
                this.filterState.selectedFilterColumn = '';
            }
        },

        saveCurrentFilters() {
            const name = prompt('Enter a name for this filter preset:');
            if (name && name.trim()) {
                const description = prompt('Enter a description (optional):') || '';
                const presetId = this.filterManager.savePreset(name.trim(), description.trim());
                if (presetId) {
                    alert('Filter preset saved successfully!');
                    this.filterState.presets = this.filterManager.getPresets();
                } else {
                    alert('Failed to save preset. Make sure you have active filters.');
                }
            }
        },

        loadFilterPreset(presetId) {
            if (this.filterManager && this.filterManager.loadPreset(presetId)) {
                this.updateActiveFiltersDisplay();
            }
        },

        deleteFilterPreset(presetId) {
            if (confirm('Are you sure you want to delete this filter preset?')) {
                if (this.filterManager && this.filterManager.deletePreset(presetId)) {
                    this.filterState.presets = this.filterManager.getPresets();
                }
            }
        },

        initializeNavigation() {
            // Set up initial navigation state
            this.updateNavigationUI();
            console.log('Navigation system initialized');
        },

        setActiveSection(sectionName) {
            this.navigationState.currentSection = sectionName;
            this.updateNavigationUI();
        },

        updateNavigationUI() {
            const sections = ['overview', 'transformation', 'advanced-filters', 'visualization', 'export'];
            
            sections.forEach(section => {
                const element = document.querySelector(`[data-section="${section}"]`);
                if (element) {
                    const button = element.querySelector('button');
                    const title = element.querySelector('.section-title') || button?.querySelector('span:not(.text-blue-600)');
                    
                    if (section === this.navigationState.currentSection) {
                        // Active state
                        button?.classList.add('sidebar-section-active', 'border-l-4', 'border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
                        button?.classList.remove('sidebar-section-inactive', 'bg-white', 'dark:bg-gray-800');
                        title?.classList.add('text-blue-800', 'dark:text-blue-300', 'font-semibold');
                        title?.classList.remove('text-gray-900', 'dark:text-gray-100');
                        
                        // Add active indicator if not present
                        if (!element.querySelector('.active-indicator')) {
                            const indicator = document.createElement('div');
                            indicator.className = 'w-2 h-2 bg-blue-500 rounded-full animate-pulse active-indicator';
                            indicator.title = 'Active Section';
                            button?.querySelector('div')?.appendChild(indicator);
                        }
                    } else {
                        // Inactive state
                        button?.classList.remove('sidebar-section-active', 'border-l-4', 'border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
                        button?.classList.add('sidebar-section-inactive', 'bg-white', 'dark:bg-gray-800');
                        title?.classList.remove('text-blue-800', 'dark:text-blue-300', 'font-semibold');
                        title?.classList.add('text-gray-900', 'dark:text-gray-100');
                        
                        // Remove active indicator
                        const indicator = element.querySelector('.active-indicator');
                        if (indicator) {
                            indicator.remove();
                        }
                    }
                }
            });
        },

        initializeWorkflowProgress(totalSteps, currentStep = 0) {
            this.navigationState.totalSteps = totalSteps;
            this.navigationState.workflowStep = currentStep;
            this.renderWorkflowProgress();
        },

        updateWorkflowStep(step) {
            if (step >= 0 && step <= this.navigationState.totalSteps) {
                this.navigationState.workflowStep = step;
                this.renderWorkflowProgress();
            }
        },

        renderWorkflowProgress() {
            const container = document.getElementById('workflow-progress-container');
            if (!container) return;

            const progress = (this.navigationState.workflowStep / this.navigationState.totalSteps) * 100;
            
            const html = `
                <div class="workflow-progress-container">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                            Progress: Step ${this.navigationState.workflowStep} of ${this.navigationState.totalSteps}
                        </span>
                        <span class="text-sm text-gray-600 dark:text-gray-400">${Math.round(progress)}%</span>
                    </div>
                    <div class="workflow-progress-bar">
                        <div class="workflow-progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <div class="flex justify-between mt-3">
                        ${Array.from({length: this.navigationState.totalSteps}, (_, i) => {
                            const stepNum = i + 1;
                            let stepClass = 'workflow-step ';
                            
                            if (stepNum < this.navigationState.workflowStep) {
                                stepClass += 'workflow-step-completed';
                            } else if (stepNum === this.navigationState.workflowStep) {
                                stepClass += 'workflow-step-current';
                            } else {
                                stepClass += 'workflow-step-pending';
                            }
                            
                            return `<div class="${stepClass}">${stepNum}</div>`;
                        }).join('')}
                    </div>
                </div>
            `;
            
            container.innerHTML = html;
        },

        getBreadcrumbPath() {
            const path = ['Data Studio'];
            
            if (this.navigationState.currentSection !== 'overview') {
                const sectionNames = {
                    'transformation': 'Data Transformation',
                    'advanced-filters': 'Advanced Filters',
                    'visualization': 'Visualization',
                    'export': 'Export & Share'
                };
                path.push(sectionNames[this.navigationState.currentSection] || this.navigationState.currentSection);
            }
            
            return path;
        },

        testWorkflowProgress() {
            // Demo workflow progress functionality
            const container = document.getElementById('workflow-progress-container');
            if (container) {
                container.style.display = 'block';
                this.initializeWorkflowProgress(5, 1);
                
                // Simulate progress steps
                let step = 1;
                const progressInterval = setInterval(() => {
                    step++;
                    this.updateWorkflowStep(step);
                    
                    if (step >= 5) {
                        clearInterval(progressInterval);
                        // Hide after completion
                        setTimeout(() => {
                            container.style.display = 'none';
                        }, 2000);
                    }
                }, 1500);
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