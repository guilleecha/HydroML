/**
 * Main Data Studio Module - Entry point and coordinator for all modules
 */

import { GridManager } from './grid_manager.js';
import { ApiClient } from './api_client.js';
import { OperationsPanel } from './operations_panel.js';

/**
 * Main DataStudio class that coordinates all modules
 */
export class DataStudio {
    constructor() {
        console.log('Initializing Data Studio...');
        
        // Initialize core modules
        this.apiClient = new ApiClient();
        this.gridManager = new GridManager();
        this.operationsPanel = new OperationsPanel(this.apiClient);
        
        // State management
        this.isInitialized = false;
        this.currentDataset = null;
        this.datasetMetadata = {};
        
        // Initialize the application
        this.initialize();
    }

    /**
     * Initialize the Data Studio application
     */
    async initialize() {
        try {
            console.log('Setting up Data Studio components...');
            
            // Initialize operations panel
            this.operationsPanel.initialize();
            
            // Setup file upload handler
            this.setupFileUpload();
            
            // Setup global event listeners
            this.setupGlobalEventListeners();
            
            // Setup keyboard shortcuts
            this.setupKeyboardShortcuts();
            
            // Initialize with sample data if available
            await this.loadInitialData();
            
            this.isInitialized = true;
            console.log('Data Studio initialized successfully');
            
            // Dispatch initialization complete event
            document.dispatchEvent(new CustomEvent('dataStudioReady', {
                detail: { dataStudio: this }
            }));
            
        } catch (error) {
            console.error('Error initializing Data Studio:', error);
            this.showError('Failed to initialize Data Studio. Please refresh the page.');
        }
    }

    /**
     * Setup file upload functionality
     */
    setupFileUpload() {
        const fileInput = document.getElementById('dataFileInput');
        const uploadBtn = document.getElementById('uploadDataBtn');
        const dropZone = document.getElementById('dropZone');

        // File input change handler
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.handleFileUpload(file);
                }
            });
        }

        // Upload button click handler
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => {
                fileInput?.click();
            });
        }

        // Drag and drop functionality
        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });

            dropZone.addEventListener('dragleave', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFileUpload(files[0]);
                }
            });
        }
    }

    /**
     * Handle file upload and load dataset
     */
    async handleFileUpload(file) {
        try {
            console.log('Processing file upload:', file.name);
            
            // Validate file type
            if (!this.isValidFileType(file)) {
                this.showError('Invalid file type. Please upload CSV, Excel, or JSON files.');
                return;
            }

            // Show loading state
            this.showLoadingState('Loading dataset...');
            
            // Upload and process file
            const result = await this.apiClient.loadDataset(file);
            
            if (result.success && result.data) {
                await this.loadDataset(result.data, {
                    filename: file.name,
                    size: file.size,
                    type: file.type,
                    uploadTime: new Date().toISOString()
                });
                
                this.showSuccess(`Dataset loaded successfully: ${result.data.length} rows`);
            } else {
                this.showError(result.error || 'Failed to load dataset');
            }
            
        } catch (error) {
            console.error('Error uploading file:', error);
            this.showError('Error uploading file: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Validate file type
     */
    isValidFileType(file) {
        const validTypes = [
            'text/csv',
            'application/csv',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/json'
        ];
        
        const validExtensions = ['.csv', '.xlsx', '.xls', '.json'];
        const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
        
        return validTypes.includes(file.type) || validExtensions.includes(fileExtension);
    }

    /**
     * Load dataset into the application
     */
    async loadDataset(data, metadata = {}) {
        try {
            console.log('DEBUG: Loading dataset with', data.length, 'rows');
            console.log('DEBUG: Metadata:', metadata);
            
            // Store dataset
            this.currentDataset = data;
            this.datasetMetadata = metadata;
            
            // Initialize grid with data
            if (metadata.columnDefs) {
                console.log('DEBUG: Using provided column definitions from Django');
                await this.gridManager.initializeGridWithColumnDefs(data, metadata.columnDefs);
            } else {
                console.log('DEBUG: Generating column definitions from data');
                await this.gridManager.initializeGrid(data);
            }
            
            // Update UI elements
            this.updateDatasetInfo();
            
            // Generate initial analysis
            await this.generateInitialAnalysis();
            
            // Enable operation buttons
            this.enableOperations();
            
            console.log('DEBUG: Dataset loaded successfully');
            
        } catch (error) {
            console.error('DEBUG: Error loading dataset:', error);
            this.showError('Error loading dataset: ' + error.message);
        }
    }

    /**
     * Update dataset information display
     */
    updateDatasetInfo() {
        const infoElement = document.getElementById('datasetInfo');
        if (infoElement && this.currentDataset) {
            const rowCount = this.currentDataset.length;
            const columnCount = this.currentDataset.length > 0 ? Object.keys(this.currentDataset[0]).length : 0;
            
            infoElement.innerHTML = `
                <div class="dataset-info">
                    <h3 class="text-lg font-semibold mb-2">Dataset Information</h3>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="font-medium">Rows:</span> 
                            <span class="text-blue-600">${rowCount.toLocaleString()}</span>
                        </div>
                        <div>
                            <span class="font-medium">Columns:</span> 
                            <span class="text-blue-600">${columnCount}</span>
                        </div>
                        ${this.datasetMetadata.filename ? `
                            <div>
                                <span class="font-medium">File:</span> 
                                <span class="text-gray-600">${this.datasetMetadata.filename}</span>
                            </div>
                        ` : ''}
                        ${this.datasetMetadata.size ? `
                            <div>
                                <span class="font-medium">Size:</span> 
                                <span class="text-gray-600">${this.formatFileSize(this.datasetMetadata.size)}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }
    }

    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Generate initial analysis of the dataset
     */
    async generateInitialAnalysis() {
        try {
            if (!this.currentDataset || this.currentDataset.length === 0) return;
            
            console.log('Generating initial analysis...');
            
            const analysis = await this.apiClient.getAnalysisSummary(this.currentDataset);
            
            if (analysis.success) {
                this.displayAnalysis(analysis.summary);
            }
            
        } catch (error) {
            console.error('Error generating initial analysis:', error);
            // Don't show error to user for optional analysis
        }
    }

    /**
     * Display analysis results
     */
    displayAnalysis(summary) {
        const analysisElement = document.getElementById('analysisResults');
        if (analysisElement && summary) {
            analysisElement.innerHTML = `
                <div class="analysis-summary">
                    <h3 class="text-lg font-semibold mb-2">Data Analysis</h3>
                    <div class="space-y-2 text-sm">
                        ${summary.missing_values ? `
                            <div>
                                <span class="font-medium">Missing Values:</span> 
                                <span class="text-red-600">${summary.missing_values}</span>
                            </div>
                        ` : ''}
                        ${summary.numeric_columns ? `
                            <div>
                                <span class="font-medium">Numeric Columns:</span> 
                                <span class="text-green-600">${summary.numeric_columns}</span>
                            </div>
                        ` : ''}
                        ${summary.categorical_columns ? `
                            <div>
                                <span class="font-medium">Categorical Columns:</span> 
                                <span class="text-blue-600">${summary.categorical_columns}</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }
    }

    /**
     * Enable operation buttons after data is loaded
     */
    enableOperations() {
        const operationElements = document.querySelectorAll('.operation-section');
        operationElements.forEach(element => {
            element.classList.remove('opacity-50', 'pointer-events-none');
        });
    }

    /**
     * Setup global event listeners
     */
    setupGlobalEventListeners() {
        // Window resize handler
        window.addEventListener('resize', () => {
            if (this.gridManager.gridApi) {
                this.gridManager.gridApi.sizeColumnsToFit();
            }
        });

        // Beforeunload handler to warn about unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (this.operationsPanel.currentRecipe.length > 0) {
                e.preventDefault();
                e.returnValue = 'You have unsaved transformation steps. Are you sure you want to leave?';
            }
        });

        // Custom events
        document.addEventListener('dataTransformed', (e) => {
            console.log('Data transformed:', e.detail);
            this.updateDatasetInfo();
        });
    }

    /**
     * Setup keyboard shortcuts
     */
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + U: Upload file
            if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
                e.preventDefault();
                document.getElementById('dataFileInput')?.click();
            }
            
            // Ctrl/Cmd + S: Save recipe
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.operationsPanel.saveCurrentRecipe();
            }
            
            // Ctrl/Cmd + L: Load recipe
            if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
                e.preventDefault();
                this.operationsPanel.showRecipeLoadDialog();
            }
            
            // Escape: Close panels
            if (e.key === 'Escape') {
                if (this.operationsPanel.isColumnPanelVisible) {
                    this.operationsPanel.toggleColumnPanel();
                }
            }
        });
    }

    /**
     * Load initial data if available
     */
    async loadInitialData() {
        // Check if there's data provided by Django template
        if (window.gridRowData && window.columnDefsData) {
            try {
                console.log('DEBUG: Loading initial data from Django template...');
                console.log('DEBUG: gridRowData type:', typeof window.gridRowData, 'length:', Array.isArray(window.gridRowData) ? window.gridRowData.length : 'Not an array');
                console.log('DEBUG: columnDefsData type:', typeof window.columnDefsData, 'length:', Array.isArray(window.columnDefsData) ? window.columnDefsData.length : 'Not an array');
                
                // Ensure data is parsed correctly
                let rowData = window.gridRowData;
                let columnDefs = window.columnDefsData;
                
                if (typeof rowData === 'string') {
                    console.log('DEBUG: Parsing gridRowData from string...');
                    rowData = JSON.parse(rowData);
                }
                
                if (typeof columnDefs === 'string') {
                    console.log('DEBUG: Parsing columnDefsData from string...');
                    columnDefs = JSON.parse(columnDefs);
                }
                
                console.log('DEBUG: Final data verification - rowData length:', rowData.length, 'columnDefs length:', columnDefs.length);
                
                if (rowData && rowData.length > 0) {
                    await this.loadDataset(rowData, { 
                        filename: 'django_datasource.json',
                        type: 'django_template',
                        columnDefs: columnDefs
                    });
                    console.log('DEBUG: Initial Django data loaded successfully');
                } else {
                    console.warn('DEBUG: No row data available from Django template');
                }
            } catch (error) {
                console.error('DEBUG: Error loading initial Django data:', error);
            }
        } else {
            console.log('DEBUG: No initial Django data available - checking for sample data...');
            
            // Check if there's sample data or previous session data
            const sampleDataElement = document.getElementById('sampleDataScript');
            if (sampleDataElement) {
                try {
                    const sampleData = JSON.parse(sampleDataElement.textContent);
                    if (sampleData && sampleData.length > 0) {
                        await this.loadDataset(sampleData, { 
                            filename: 'sample_data.json',
                            type: 'sample'
                        });
                    }
                } catch (error) {
                    console.log('No sample data available');
                }
            }
        }
    }

    /**
     * Toggle column panel (exposed globally)
     */
    toggleColumnPanel() {
        this.operationsPanel.toggleColumnPanel();
    }

    /**
     * Export current data
     */
    async exportData(format = 'csv') {
        try {
            if (!this.currentDataset || this.currentDataset.length === 0) {
                this.showError('No data to export');
                return;
            }

            const currentData = this.gridManager.getCurrentData();
            await this.apiClient.exportData(currentData, format);
            
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showError('Error exporting data: ' + error.message);
        }
    }

    /**
     * Reset application state
     */
    reset() {
        if (confirm('Are you sure you want to reset? All unsaved changes will be lost.')) {
            // Clear grid
            if (this.gridManager.gridApi) {
                this.gridManager.gridApi.setRowData([]);
            }
            
            // Reset state
            this.currentDataset = null;
            this.datasetMetadata = {};
            
            // Clear UI
            const infoElement = document.getElementById('datasetInfo');
            if (infoElement) {
                infoElement.innerHTML = '';
            }
            
            const analysisElement = document.getElementById('analysisResults');
            if (analysisElement) {
                analysisElement.innerHTML = '';
            }
            
            // Reset operations panel
            this.operationsPanel.selectedColumns.clear();
            this.operationsPanel.currentRecipe = [];
            this.operationsPanel.transformationHistory = [];
            this.operationsPanel.updateSelectedColumnsDisplay();
            this.operationsPanel.updateRecipeDisplay();
            
            console.log('Application reset');
        }
    }

    /**
     * UI state management
     */
    showLoadingState(message) {
        this.operationsPanel.showLoadingState(message);
    }

    hideLoadingState() {
        this.operationsPanel.hideLoadingState();
    }

    showSuccess(message) {
        this.operationsPanel.showSuccess(message);
    }

    showError(message) {
        this.operationsPanel.showError(message);
    }

    /**
     * Get application state
     */
    getState() {
        return {
            isInitialized: this.isInitialized,
            dataset: this.currentDataset,
            metadata: this.datasetMetadata,
            operations: this.operationsPanel.getState()
        };
    }

    /**
     * Restore application state
     */
    restoreState(state) {
        if (state.dataset) {
            this.loadDataset(state.dataset, state.metadata || {});
        }
        
        if (state.operations) {
            this.operationsPanel.restoreState(state.operations);
        }
    }

    /**
     * Cleanup and destroy
     */
    destroy() {
        if (this.gridManager) {
            this.gridManager.destroy();
        }
        
        // Remove event listeners
        window.removeEventListener('resize', this.handleResize);
        window.removeEventListener('beforeunload', this.handleBeforeUnload);
        
        console.log('Data Studio destroyed');
    }
}

// Initialize Data Studio when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Create global instance
    window.dataStudio = new DataStudio();
    
    // Make toggle function available globally for inline handlers
    window.toggleColumnPanel = function() {
        if (window.dataStudio) {
            window.dataStudio.toggleColumnPanel();
        }
    };
});
