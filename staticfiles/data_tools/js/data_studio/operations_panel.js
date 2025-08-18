/**
 * Operations Panel Module - Handles UI panels, transformations, and column operations
 */

export class OperationsPanel {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.selectedColumns = new Set();
        this.isColumnPanelVisible = false;
        this.transformationHistory = [];
        this.currentRecipe = [];
    }

    /**
     * Initialize event listeners and UI components
     */
    initialize() {
        this.setupColumnSelectionListener();
        this.setupTransformationForms();
        this.setupRecipeBuilder();
        this.setupChartGeneration();
    }

    /**
     * Toggle column selection panel visibility
     */
    toggleColumnPanel() {
        console.log('Toggling column panel');
        const panel = document.getElementById('columnSelectionPanel');
        if (panel) {
            this.isColumnPanelVisible = !this.isColumnPanelVisible;
            panel.style.display = this.isColumnPanelVisible ? 'block' : 'none';
            
            // Update button text
            const toggleBtn = document.getElementById('toggleColumnBtn');
            if (toggleBtn) {
                toggleBtn.textContent = this.isColumnPanelVisible ? 'Hide Columns' : 'Show Columns';
            }
        }
    }

    /**
     * Setup column selection event listener
     */
    setupColumnSelectionListener() {
        document.addEventListener('columnSelectionChanged', (event) => {
            const { columnField, selected } = event.detail;
            
            if (selected) {
                this.selectedColumns.add(columnField);
            } else {
                this.selectedColumns.delete(columnField);
            }
            
            this.updateSelectedColumnsDisplay();
            this.updateOperationButtons();
            
            console.log('Selected columns:', Array.from(this.selectedColumns));
        });
    }

    /**
     * Update selected columns display
     */
    updateSelectedColumnsDisplay() {
        const display = document.getElementById('selectedColumnsDisplay');
        if (display) {
            const columnList = Array.from(this.selectedColumns);
            if (columnList.length === 0) {
                display.innerHTML = '<p class="text-gray-500">No columns selected</p>';
            } else {
                display.innerHTML = `
                    <div class="selected-columns-list">
                        <h4 class="text-sm font-medium mb-2">Selected Columns (${columnList.length}):</h4>
                        <div class="flex flex-wrap gap-2">
                            ${columnList.map(col => `
                                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                                    ${col}
                                    <button type="button" class="ml-1 text-blue-600 hover:text-blue-800" 
                                            onclick="window.dataStudio.operationsPanel.removeSelectedColumn('${col}')">
                                        ×
                                    </button>
                                </span>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
        }
    }

    /**
     * Remove a column from selection
     */
    removeSelectedColumn(columnField) {
        this.selectedColumns.delete(columnField);
        this.updateSelectedColumnsDisplay();
        this.updateOperationButtons();
        
        // Update checkbox in grid header
        const checkbox = document.querySelector(`input[data-column="${columnField}"]`);
        if (checkbox) {
            checkbox.checked = false;
        }
    }

    /**
     * Update operation buttons state
     */
    updateOperationButtons() {
        const hasSelection = this.selectedColumns.size > 0;
        const buttons = document.querySelectorAll('.column-operation-btn');
        
        buttons.forEach(btn => {
            btn.disabled = !hasSelection;
            btn.classList.toggle('opacity-50', !hasSelection);
            btn.classList.toggle('cursor-not-allowed', !hasSelection);
        });
    }

    /**
     * Setup transformation forms
     */
    setupTransformationForms() {
        // Scaling transformation
        const scalingForm = document.getElementById('scalingForm');
        if (scalingForm) {
            scalingForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.applyScaling();
            });
        }

        // Normalization transformation
        const normalizationForm = document.getElementById('normalizationForm');
        if (normalizationForm) {
            normalizationForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.applyNormalization();
            });
        }

        // Encoding transformation
        const encodingForm = document.getElementById('encodingForm');
        if (encodingForm) {
            encodingForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.applyEncoding();
            });
        }

        // Missing values handling
        const missingValuesForm = document.getElementById('missingValuesForm');
        if (missingValuesForm) {
            missingValuesForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleMissingValues();
            });
        }
    }

    /**
     * Apply scaling transformation
     */
    async applyScaling() {
        if (this.selectedColumns.size === 0) {
            alert('Please select columns to scale');
            return;
        }

        try {
            const scalingType = document.getElementById('scalingType')?.value || 'standard';
            const columns = Array.from(this.selectedColumns);
            
            this.showLoadingState('Applying scaling...');
            
            const currentData = window.dataStudio.gridManager.getCurrentData();
            const result = await this.apiClient.applyTransformation('scaling', {
                method: scalingType,
                columns: columns
            }, currentData);

            if (result.success) {
                window.dataStudio.gridManager.updateGridData(result.data);
                this.addToTransformationHistory('scaling', { method: scalingType, columns });
                this.showSuccess('Scaling applied successfully');
            } else {
                this.showError(result.error || 'Failed to apply scaling');
            }
        } catch (error) {
            this.showError('Error applying scaling: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Apply normalization transformation
     */
    async applyNormalization() {
        if (this.selectedColumns.size === 0) {
            alert('Please select columns to normalize');
            return;
        }

        try {
            const normalizationType = document.getElementById('normalizationType')?.value || 'min_max';
            const columns = Array.from(this.selectedColumns);
            
            this.showLoadingState('Applying normalization...');
            
            const currentData = window.dataStudio.gridManager.getCurrentData();
            const result = await this.apiClient.applyTransformation('normalization', {
                method: normalizationType,
                columns: columns
            }, currentData);

            if (result.success) {
                window.dataStudio.gridManager.updateGridData(result.data);
                this.addToTransformationHistory('normalization', { method: normalizationType, columns });
                this.showSuccess('Normalization applied successfully');
            } else {
                this.showError(result.error || 'Failed to apply normalization');
            }
        } catch (error) {
            this.showError('Error applying normalization: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Apply encoding transformation
     */
    async applyEncoding() {
        if (this.selectedColumns.size === 0) {
            alert('Please select columns to encode');
            return;
        }

        try {
            const encodingType = document.getElementById('encodingType')?.value || 'label';
            const columns = Array.from(this.selectedColumns);
            
            this.showLoadingState('Applying encoding...');
            
            const currentData = window.dataStudio.gridManager.getCurrentData();
            const result = await this.apiClient.applyTransformation('encoding', {
                method: encodingType,
                columns: columns
            }, currentData);

            if (result.success) {
                window.dataStudio.gridManager.updateGridData(result.data);
                this.addToTransformationHistory('encoding', { method: encodingType, columns });
                this.showSuccess('Encoding applied successfully');
            } else {
                this.showError(result.error || 'Failed to apply encoding');
            }
        } catch (error) {
            this.showError('Error applying encoding: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Handle missing values
     */
    async handleMissingValues() {
        if (this.selectedColumns.size === 0) {
            alert('Please select columns to handle missing values');
            return;
        }

        try {
            const strategy = document.getElementById('missingStrategy')?.value || 'drop';
            const fillValue = document.getElementById('fillValue')?.value || '';
            const columns = Array.from(this.selectedColumns);
            
            this.showLoadingState('Handling missing values...');
            
            const currentData = window.dataStudio.gridManager.getCurrentData();
            const result = await this.apiClient.applyTransformation('missing_values', {
                strategy: strategy,
                fill_value: fillValue,
                columns: columns
            }, currentData);

            if (result.success) {
                window.dataStudio.gridManager.updateGridData(result.data);
                this.addToTransformationHistory('missing_values', { strategy, fill_value: fillValue, columns });
                this.showSuccess('Missing values handled successfully');
            } else {
                this.showError(result.error || 'Failed to handle missing values');
            }
        } catch (error) {
            this.showError('Error handling missing values: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Setup recipe builder functionality
     */
    setupRecipeBuilder() {
        const saveRecipeBtn = document.getElementById('saveRecipeBtn');
        if (saveRecipeBtn) {
            saveRecipeBtn.addEventListener('click', () => this.saveCurrentRecipe());
        }

        const loadRecipeBtn = document.getElementById('loadRecipeBtn');
        if (loadRecipeBtn) {
            loadRecipeBtn.addEventListener('click', () => this.showRecipeLoadDialog());
        }

        const clearRecipeBtn = document.getElementById('clearRecipeBtn');
        if (clearRecipeBtn) {
            clearRecipeBtn.addEventListener('click', () => this.clearCurrentRecipe());
        }
    }

    /**
     * Add transformation to history and recipe
     */
    addToTransformationHistory(transformationType, params) {
        const step = {
            id: Date.now(),
            type: transformationType,
            params: params,
            timestamp: new Date().toISOString()
        };

        this.transformationHistory.push(step);
        this.currentRecipe.push(step);
        this.updateRecipeDisplay();
    }

    /**
     * Update recipe display
     */
    updateRecipeDisplay() {
        const recipeDisplay = document.getElementById('recipeStepsDisplay');
        if (recipeDisplay) {
            if (this.currentRecipe.length === 0) {
                recipeDisplay.innerHTML = '<p class="text-gray-500">No transformation steps</p>';
            } else {
                recipeDisplay.innerHTML = `
                    <div class="recipe-steps">
                        <h4 class="text-sm font-medium mb-2">Recipe Steps (${this.currentRecipe.length}):</h4>
                        <div class="space-y-2">
                            ${this.currentRecipe.map((step, index) => `
                                <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
                                    <div class="flex-1">
                                        <span class="text-sm font-medium">${index + 1}. ${step.type}</span>
                                        <div class="text-xs text-gray-600">
                                            ${this.formatStepParams(step.params)}
                                        </div>
                                    </div>
                                    <button type="button" 
                                            class="text-red-600 hover:text-red-800 text-xs"
                                            onclick="window.dataStudio.operationsPanel.removeRecipeStep(${step.id})">
                                        Remove
                                    </button>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
        }
    }

    /**
     * Format step parameters for display
     */
    formatStepParams(params) {
        if (params.columns) {
            return `Columns: ${params.columns.join(', ')} | Method: ${params.method || params.strategy || 'default'}`;
        }
        return JSON.stringify(params);
    }

    /**
     * Remove step from recipe
     */
    removeRecipeStep(stepId) {
        this.currentRecipe = this.currentRecipe.filter(step => step.id !== stepId);
        this.updateRecipeDisplay();
    }

    /**
     * Save current recipe
     */
    async saveCurrentRecipe() {
        if (this.currentRecipe.length === 0) {
            alert('No transformation steps to save');
            return;
        }

        const recipeName = prompt('Enter recipe name:');
        if (!recipeName) return;

        try {
            this.showLoadingState('Saving recipe...');
            
            const result = await this.apiClient.saveRecipe({
                name: recipeName,
                steps: this.currentRecipe,
                created_at: new Date().toISOString()
            });

            if (result.success) {
                this.showSuccess('Recipe saved successfully');
            } else {
                this.showError(result.error || 'Failed to save recipe');
            }
        } catch (error) {
            this.showError('Error saving recipe: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Show recipe load dialog
     */
    async showRecipeLoadDialog() {
        try {
            this.showLoadingState('Loading recipes...');
            const recipes = await this.apiClient.getRecipeList();
            
            if (recipes.length === 0) {
                alert('No saved recipes found');
                return;
            }

            // Create simple selection dialog
            const recipeNames = recipes.map(r => r.name);
            const selection = prompt(`Select recipe:\n${recipeNames.map((name, i) => `${i + 1}. ${name}`).join('\n')}\n\nEnter number:`);
            
            if (selection) {
                const index = parseInt(selection) - 1;
                if (index >= 0 && index < recipes.length) {
                    await this.loadRecipe(recipes[index].id);
                }
            }
        } catch (error) {
            this.showError('Error loading recipes: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Load recipe by ID
     */
    async loadRecipe(recipeId) {
        try {
            this.showLoadingState('Loading recipe...');
            const recipe = await this.apiClient.loadRecipe(recipeId);
            
            this.currentRecipe = recipe.steps || [];
            this.updateRecipeDisplay();
            this.showSuccess('Recipe loaded successfully');
        } catch (error) {
            this.showError('Error loading recipe: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Clear current recipe
     */
    clearCurrentRecipe() {
        if (this.currentRecipe.length > 0) {
            if (confirm('Are you sure you want to clear the current recipe?')) {
                this.currentRecipe = [];
                this.updateRecipeDisplay();
            }
        }
    }

    /**
     * Setup chart generation
     */
    setupChartGeneration() {
        const generateChartBtn = document.getElementById('generateChartBtn');
        if (generateChartBtn) {
            generateChartBtn.addEventListener('click', () => this.generateChart());
        }
    }

    /**
     * Generate chart from selected columns
     */
    async generateChart() {
        if (this.selectedColumns.size === 0) {
            alert('Please select columns for chart generation');
            return;
        }

        try {
            const chartType = document.getElementById('chartType')?.value || 'scatter';
            const columns = Array.from(this.selectedColumns);
            
            this.showLoadingState('Generating chart...');
            
            const currentData = window.dataStudio.gridManager.getCurrentData();
            const result = await this.apiClient.generateChart(chartType, columns, currentData);

            if (result.success) {
                this.displayChart(result.chart_data);
                this.showSuccess('Chart generated successfully');
            } else {
                this.showError(result.error || 'Failed to generate chart');
            }
        } catch (error) {
            this.showError('Error generating chart: ' + error.message);
        } finally {
            this.hideLoadingState();
        }
    }

    /**
     * Display chart in chart container
     */
    displayChart(chartData) {
        const chartContainer = document.getElementById('chartContainer');
        if (chartContainer && chartData) {
            // Clear previous chart
            chartContainer.innerHTML = '';
            
            // Create chart using Plotly
            if (window.Plotly) {
                Plotly.newPlot(chartContainer, chartData.data, chartData.layout, {
                    responsive: true,
                    displayModeBar: true
                });
            } else {
                chartContainer.innerHTML = '<p class="text-red-500">Plotly.js not loaded</p>';
            }
        }
    }

    /**
     * UI state management
     */
    showLoadingState(message) {
        const loadingElement = document.getElementById('loadingIndicator');
        if (loadingElement) {
            loadingElement.textContent = message;
            loadingElement.style.display = 'block';
        }
    }

    hideLoadingState() {
        const loadingElement = document.getElementById('loadingIndicator');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    showSuccess(message) {
        console.log('Success:', message);
        // Could integrate with toast notification system
        this.showNotification(message, 'success');
    }

    showError(message) {
        console.error('Error:', message);
        // Could integrate with toast notification system
        this.showNotification(message, 'error');
    }

    showNotification(message, type = 'info') {
        // Simple notification - could be enhanced with a proper toast system
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 16px;
            border-radius: 4px;
            color: white;
            background-color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            z-index: 9999;
            max-width: 400px;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    /**
     * Get current state
     */
    getState() {
        return {
            selectedColumns: Array.from(this.selectedColumns),
            transformationHistory: this.transformationHistory,
            currentRecipe: this.currentRecipe,
            isColumnPanelVisible: this.isColumnPanelVisible
        };
    }

    /**
     * Restore state
     */
    restoreState(state) {
        if (state.selectedColumns) {
            this.selectedColumns = new Set(state.selectedColumns);
            this.updateSelectedColumnsDisplay();
            this.updateOperationButtons();
        }
        
        if (state.transformationHistory) {
            this.transformationHistory = state.transformationHistory;
        }
        
        if (state.currentRecipe) {
            this.currentRecipe = state.currentRecipe;
            this.updateRecipeDisplay();
        }
        
        if (state.isColumnPanelVisible !== undefined) {
            this.isColumnPanelVisible = state.isColumnPanelVisible;
            const panel = document.getElementById('columnSelectionPanel');
            if (panel) {
                panel.style.display = this.isColumnPanelVisible ? 'block' : 'none';
            }
        }
    }
}
