/**
 * FilterUIController - Filter User Interface Management
 * Responsabilidad única: Generación y manejo de UI de filtros (NO lógica de negocio)
 * 
 * Filosofía: Pure UI generation, event handling with proper cleanup, no mixed concerns
 */

class FilterUIController {
    constructor(filterController, container = null) {
        this.filterController = filterController;
        this.container = container || document.getElementById('filter-builder-container');
        
        // Event handlers cleanup map
        this.eventHandlers = new Map();
        this.activeCleanupTasks = [];
        
        // UI state
        this.currentFilterField = null;
        this.currentFilterType = null;
        
        // Setup controller event listeners
        this.setupControllerListeners();
    }

    // === CONTROLLER EVENT LISTENERS ===

    setupControllerListeners() {
        // Listen to filter controller events and update UI
        this.filterController.addEventListener('filter-applied', () => {
            this.updateActiveFiltersDisplay();
        });

        this.filterController.addEventListener('filter-removed', () => {
            this.updateActiveFiltersDisplay();
        });

        this.filterController.addEventListener('filters-cleared', () => {
            this.updateActiveFiltersDisplay();
            this.clearFilterBuilder();
        });

        this.filterController.addEventListener('preset-loaded', () => {
            this.updateActiveFiltersDisplay();
            this.showNotification('Filter preset loaded', 'success');
        });
    }

    // === MAIN FILTER UI GENERATION ===

    buildFilterInterface(columnField) {
        if (!this.filterController || !columnField) {
            console.warn('Invalid parameters for filter interface');
            return false;
        }

        if (!this.container) {
            console.warn('Filter UI container not found');
            return false;
        }

        // Clean up previous interface
        this.cleanup();

        const columnType = this.filterController.getColumnType(columnField);
        const columnName = this.getColumnDisplayName(columnField);
        
        this.currentFilterField = columnField;
        this.currentFilterType = columnType;

        let html = '';

        try {
            switch (columnType) {
                case 'category':
                    html = this.buildMultiSelectUI(columnField, columnName);
                    break;
                case 'number':
                    html = this.buildRangeUI(columnField, columnName);
                    break;
                case 'text':
                default:
                    html = this.buildTextUI(columnField, columnName);
                    break;
            }

            this.container.innerHTML = html;
            this.attachEventListeners(columnField, columnType);
            
            return true;

        } catch (error) {
            console.error('Error building filter interface:', error);
            this.showError('Failed to build filter interface');
            return false;
        }
    }

    buildMultiSelectUI(columnField, columnName) {
        const uniqueValues = this.filterController.getUniqueValues(columnField, 100);
        
        if (uniqueValues.length === 0) {
            return this.buildEmptyFilterUI(columnName, 'No values available for filtering');
        }

        // Build checkboxes with proper escaping
        const checkboxes = uniqueValues.map(value => {
            const escapedValue = this.escapeHtml(value);
            const valueId = `filter-${columnField}-${this.sanitizeId(value)}`;
            
            return `
                <label class="flex items-center space-x-2 text-xs py-1 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer">
                    <input type="checkbox" 
                           id="${valueId}"
                           value="${escapedValue}" 
                           data-filter-field="${columnField}" 
                           data-filter-type="multiSelect" 
                           class="filter-checkbox w-3 h-3 text-cyan-600">
                    <span class="text-gray-700 dark:text-gray-300" title="${escapedValue}">${this.truncateText(escapedValue, 30)}</span>
                </label>
            `;
        }).join('');

        return `
            <div class="space-y-2" data-filter-ui="multiSelect">
                <div class="flex items-center justify-between">
                    <div class="text-xs font-medium text-gray-700 dark:text-gray-300">${this.escapeHtml(columnName)} (Multi-Select)</div>
                    <div class="text-xs text-gray-500">${uniqueValues.length} options</div>
                </div>
                
                <div class="flex items-center space-x-2 mb-2">
                    <button type="button" class="select-all-btn text-xs text-cyan-600 hover:text-cyan-800">Select All</button>
                    <span class="text-gray-400">|</span>
                    <button type="button" class="clear-all-btn text-xs text-gray-600 hover:text-gray-800">Clear All</button>
                </div>
                
                <div class="max-h-32 overflow-y-auto border border-gray-300 dark:border-gray-600 rounded p-2 bg-white dark:bg-gray-800">
                    ${checkboxes}
                </div>
                
                <button type="button" class="apply-filter-btn w-full px-3 py-1 text-xs bg-cyan-600 hover:bg-cyan-700 text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                    Apply Filter
                </button>
                
                <div class="selection-info text-xs text-gray-500 text-center"></div>
            </div>
        `;
    }

    buildRangeUI(columnField, columnName) {
        const range = this.filterController.getNumericRange(columnField);
        
        const minId = `range-min-${columnField}`;
        const maxId = `range-max-${columnField}`;

        return `
            <div class="space-y-2" data-filter-ui="range">
                <div class="text-xs font-medium text-gray-700 dark:text-gray-300">${this.escapeHtml(columnName)} (Range)</div>
                <div class="text-xs text-gray-500 mb-2">Available range: ${range.min} - ${range.max}</div>
                
                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label for="${minId}" class="text-xs text-gray-600 dark:text-gray-400">Min</label>
                        <input type="number" 
                               id="${minId}"
                               value="${range.min}" 
                               min="${range.min}" 
                               max="${range.max}" 
                               step="any"
                               class="range-min w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                    </div>
                    <div>
                        <label for="${maxId}" class="text-xs text-gray-600 dark:text-gray-400">Max</label>
                        <input type="number" 
                               id="${maxId}"
                               value="${range.max}" 
                               min="${range.min}" 
                               max="${range.max}"
                               step="any"
                               class="range-max w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                    </div>
                </div>
                
                <button type="button" class="apply-filter-btn w-full px-3 py-1 text-xs bg-cyan-600 hover:bg-cyan-700 text-white rounded transition-colors">
                    Apply Range Filter
                </button>
                
                <div class="range-validation text-xs text-red-500 hidden"></div>
            </div>
        `;
    }

    buildTextUI(columnField, columnName) {
        const typeId = `text-filter-type-${columnField}`;
        const valueId = `text-filter-value-${columnField}`;

        return `
            <div class="space-y-2" data-filter-ui="text">
                <div class="text-xs font-medium text-gray-700 dark:text-gray-300">${this.escapeHtml(columnName)} (Text)</div>
                
                <div class="space-y-2">
                    <div>
                        <label for="${typeId}" class="text-xs text-gray-600 dark:text-gray-400">Filter Type</label>
                        <select id="${typeId}" 
                                class="filter-type w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                            <option value="contains">Contains</option>
                            <option value="equals">Equals</option>
                            <option value="startsWith">Starts With</option>
                            <option value="endsWith">Ends With</option>
                            <option value="notEqual">Not Equal</option>
                        </select>
                    </div>
                    
                    <div>
                        <label for="${valueId}" class="text-xs text-gray-600 dark:text-gray-400">Filter Text</label>
                        <input type="text" 
                               id="${valueId}"
                               placeholder="Enter filter text..."
                               class="filter-value w-full px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
                    </div>
                    
                    <button type="button" class="apply-filter-btn w-full px-3 py-1 text-xs bg-cyan-600 hover:bg-cyan-700 text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed" disabled>
                        Apply Text Filter
                    </button>
                </div>
                
                <div class="suggestions-container hidden">
                    <div class="text-xs text-gray-600 dark:text-gray-400 mb-1">Suggestions:</div>
                    <div class="suggestions-list space-y-1"></div>
                </div>
            </div>
        `;
    }

    buildEmptyFilterUI(columnName, message) {
        return `
            <div class="space-y-2 text-center py-4">
                <div class="text-xs font-medium text-gray-700 dark:text-gray-300">${this.escapeHtml(columnName)}</div>
                <div class="text-xs text-gray-500">${this.escapeHtml(message)}</div>
                <svg class="w-8 h-8 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8V4a1 1 0 00-1-1H7a1 1 0 00-1 1v1m8 0V4a1 1 0 00-1-1H9a1 1 0 00-1 1v1"></path>
                </svg>
            </div>
        `;
    }

    // === EVENT HANDLING ===

    attachEventListeners(columnField, columnType) {
        if (!this.container) return;

        // Clean up any existing listeners first
        this.cleanup();

        switch (columnType) {
            case 'category':
                this.attachMultiSelectListeners(columnField);
                break;
            case 'number':
                this.attachRangeListeners(columnField);
                break;
            case 'text':
                this.attachTextListeners(columnField);
                break;
        }
    }

    attachMultiSelectListeners(columnField) {
        // Apply filter button
        const applyBtn = this.container.querySelector('.apply-filter-btn');
        if (applyBtn) {
            const handler = () => this.handleMultiSelectApply(columnField);
            applyBtn.addEventListener('click', handler);
            this.addCleanupTask(() => applyBtn.removeEventListener('click', handler));
        }

        // Select all button
        const selectAllBtn = this.container.querySelector('.select-all-btn');
        if (selectAllBtn) {
            const handler = () => this.handleSelectAll();
            selectAllBtn.addEventListener('click', handler);
            this.addCleanupTask(() => selectAllBtn.removeEventListener('click', handler));
        }

        // Clear all button
        const clearAllBtn = this.container.querySelector('.clear-all-btn');
        if (clearAllBtn) {
            const handler = () => this.handleClearAll();
            clearAllBtn.addEventListener('click', handler);
            this.addCleanupTask(() => clearAllBtn.removeEventListener('click', handler));
        }

        // Checkbox change listeners
        const checkboxes = this.container.querySelectorAll('.filter-checkbox');
        checkboxes.forEach(checkbox => {
            const handler = () => this.updateMultiSelectInfo();
            checkbox.addEventListener('change', handler);
            this.addCleanupTask(() => checkbox.removeEventListener('change', handler));
        });

        // Initial update
        this.updateMultiSelectInfo();
    }

    attachRangeListeners(columnField) {
        // Apply filter button
        const applyBtn = this.container.querySelector('.apply-filter-btn');
        if (applyBtn) {
            const handler = () => this.handleRangeApply(columnField);
            applyBtn.addEventListener('click', handler);
            this.addCleanupTask(() => applyBtn.removeEventListener('click', handler));
        }

        // Input validation
        const minInput = this.container.querySelector('.range-min');
        const maxInput = this.container.querySelector('.range-max');
        
        [minInput, maxInput].forEach(input => {
            if (input) {
                const inputHandler = () => this.validateRangeInputs();
                const keyHandler = (e) => {
                    if (e.key === 'Enter') {
                        this.handleRangeApply(columnField);
                    }
                };
                
                input.addEventListener('input', inputHandler);
                input.addEventListener('keydown', keyHandler);
                
                this.addCleanupTask(() => {
                    input.removeEventListener('input', inputHandler);
                    input.removeEventListener('keydown', keyHandler);
                });
            }
        });
    }

    attachTextListeners(columnField) {
        // Apply filter button
        const applyBtn = this.container.querySelector('.apply-filter-btn');
        if (applyBtn) {
            const handler = () => this.handleTextApply(columnField);
            applyBtn.addEventListener('click', handler);
            this.addCleanupTask(() => applyBtn.removeEventListener('click', handler));
        }

        // Text input
        const textInput = this.container.querySelector('.filter-value');
        if (textInput) {
            const inputHandler = () => this.handleTextInputChange(columnField);
            const keyHandler = (e) => {
                if (e.key === 'Enter' && textInput.value.trim()) {
                    this.handleTextApply(columnField);
                }
            };
            
            textInput.addEventListener('input', inputHandler);
            textInput.addEventListener('keydown', keyHandler);
            
            this.addCleanupTask(() => {
                textInput.removeEventListener('input', inputHandler);
                textInput.removeEventListener('keydown', keyHandler);
            });
        }
    }

    // === EVENT HANDLERS ===

    handleMultiSelectApply(columnField) {
        const checkboxes = this.container.querySelectorAll('.filter-checkbox:checked');
        const selectedValues = Array.from(checkboxes).map(cb => cb.value);
        
        if (selectedValues.length === 0) {
            this.showNotification('Please select at least one value', 'warning');
            return;
        }

        const success = this.filterController.applyMultiSelectFilter(columnField, selectedValues);
        if (success) {
            this.showNotification(`Applied filter with ${selectedValues.length} values`, 'success');
        } else {
            this.showNotification('Failed to apply filter', 'error');
        }
    }

    handleRangeApply(columnField) {
        const minInput = this.container.querySelector('.range-min');
        const maxInput = this.container.querySelector('.range-max');
        
        if (!minInput || !maxInput) return;

        const min = parseFloat(minInput.value);
        const max = parseFloat(maxInput.value);
        
        if (isNaN(min) || isNaN(max)) {
            this.showValidationError('Please enter valid numbers');
            return;
        }
        
        if (min > max) {
            this.showValidationError('Minimum value cannot be greater than maximum');
            return;
        }

        const success = this.filterController.applyRangeFilter(columnField, min, max);
        if (success) {
            this.showNotification(`Applied range filter: ${min} - ${max}`, 'success');
            this.hideValidationError();
        } else {
            this.showNotification('Failed to apply range filter', 'error');
        }
    }

    handleTextApply(columnField) {
        const typeSelect = this.container.querySelector('.filter-type');
        const valueInput = this.container.querySelector('.filter-value');
        
        if (!typeSelect || !valueInput) return;

        const filterType = typeSelect.value;
        const filterValue = valueInput.value.trim();
        
        if (!filterValue) {
            this.showNotification('Please enter filter text', 'warning');
            return;
        }

        const success = this.filterController.applyTextFilter(columnField, filterValue, filterType);
        if (success) {
            this.showNotification(`Applied ${filterType} filter: "${filterValue}"`, 'success');
        } else {
            this.showNotification('Failed to apply text filter', 'error');
        }
    }

    handleSelectAll() {
        const checkboxes = this.container.querySelectorAll('.filter-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        });
        this.updateMultiSelectInfo();
    }

    handleClearAll() {
        const checkboxes = this.container.querySelectorAll('.filter-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.checked = false;
        });
        this.updateMultiSelectInfo();
    }

    handleTextInputChange(columnField) {
        const textInput = this.container.querySelector('.filter-value');
        const applyBtn = this.container.querySelector('.apply-filter-btn');
        
        if (textInput && applyBtn) {
            const hasValue = textInput.value.trim().length > 0;
            applyBtn.disabled = !hasValue;
            
            // Show suggestions for non-empty input
            if (hasValue && textInput.value.length >= 2) {
                this.showFilterSuggestions(columnField, textInput.value);
            } else {
                this.hideFilterSuggestions();
            }
        }
    }

    // === UI UPDATES ===

    updateMultiSelectInfo() {
        const checkboxes = this.container.querySelectorAll('.filter-checkbox');
        const selectedCheckboxes = this.container.querySelectorAll('.filter-checkbox:checked');
        const infoElement = this.container.querySelector('.selection-info');
        
        if (infoElement) {
            const selectedCount = selectedCheckboxes.length;
            const totalCount = checkboxes.length;
            
            if (selectedCount === 0) {
                infoElement.textContent = 'No values selected';
                infoElement.className = 'selection-info text-xs text-gray-500 text-center';
            } else {
                infoElement.textContent = `${selectedCount} of ${totalCount} values selected`;
                infoElement.className = 'selection-info text-xs text-cyan-600 text-center font-medium';
            }
        }
    }

    validateRangeInputs() {
        const minInput = this.container.querySelector('.range-min');
        const maxInput = this.container.querySelector('.range-max');
        
        if (!minInput || !maxInput) return;

        const min = parseFloat(minInput.value);
        const max = parseFloat(maxInput.value);
        
        if (!isNaN(min) && !isNaN(max) && min > max) {
            this.showValidationError('Min value cannot be greater than max value');
        } else {
            this.hideValidationError();
        }
    }

    updateActiveFiltersDisplay() {
        const container = document.getElementById('active-filters-container');
        if (!container) return;

        const activeFilters = this.filterController.getActiveFilters();
        
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
                        <span class="font-medium text-cyan-800 dark:text-cyan-200">${this.escapeHtml(filterData.displayName)}:</span>
                        <span class="text-cyan-600 dark:text-cyan-300 ml-1">${this.escapeHtml(displayText)}</span>
                    </span>
                    <button data-remove-filter="${field}" 
                            class="ml-2 text-cyan-600 hover:text-cyan-800 dark:text-cyan-400 dark:hover:text-cyan-200 font-bold"
                            title="Remove filter">
                        ×
                    </button>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
        
        // Attach remove filter listeners
        container.querySelectorAll('[data-remove-filter]').forEach(button => {
            const field = button.getAttribute('data-remove-filter');
            const handler = () => this.filterController.clearFilter(field);
            button.addEventListener('click', handler);
            this.addCleanupTask(() => button.removeEventListener('click', handler));
        });
    }

    showFilterSuggestions(columnField, query) {
        const suggestions = this.filterController.getFilterSuggestions(columnField, query, 5);
        const suggestionsContainer = this.container.querySelector('.suggestions-container');
        const suggestionsList = this.container.querySelector('.suggestions-list');
        
        if (!suggestionsContainer || !suggestionsList) return;

        if (suggestions.length === 0) {
            suggestionsContainer.classList.add('hidden');
            return;
        }

        const suggestionsHtml = suggestions.map(suggestion => {
            return `
                <button type="button" class="suggestion-item w-full text-left px-2 py-1 text-xs text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
                    ${this.escapeHtml(suggestion)}
                </button>
            `;
        }).join('');

        suggestionsList.innerHTML = suggestionsHtml;
        suggestionsContainer.classList.remove('hidden');

        // Attach suggestion click handlers
        suggestionsList.querySelectorAll('.suggestion-item').forEach(button => {
            const handler = () => {
                const textInput = this.container.querySelector('.filter-value');
                if (textInput) {
                    textInput.value = button.textContent.trim();
                    this.hideFilterSuggestions();
                    this.handleTextInputChange(columnField);
                }
            };
            button.addEventListener('click', handler);
            this.addCleanupTask(() => button.removeEventListener('click', handler));
        });
    }

    hideFilterSuggestions() {
        const suggestionsContainer = this.container.querySelector('.suggestions-container');
        if (suggestionsContainer) {
            suggestionsContainer.classList.add('hidden');
        }
    }

    showValidationError(message) {
        const errorElement = this.container.querySelector('.range-validation');
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.remove('hidden');
        }
    }

    hideValidationError() {
        const errorElement = this.container.querySelector('.range-validation');
        if (errorElement) {
            errorElement.classList.add('hidden');
        }
    }

    clearFilterBuilder() {
        if (this.container) {
            this.cleanup();
            this.container.innerHTML = '';
            this.currentFilterField = null;
            this.currentFilterType = null;
        }
    }

    // === UTILITY METHODS ===

    getColumnDisplayName(field) {
        const columns = this.filterController.getAvailableColumns();
        const column = columns.find(col => col.field === field);
        return column ? column.headerName : field;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    sanitizeId(text) {
        return String(text).replace(/[^a-zA-Z0-9-_]/g, '_');
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }

    showNotification(message, type = 'info') {
        if (window.dataStudioNotifications && window.dataStudioNotifications.show) {
            window.dataStudioNotifications.show(message, type);
        } else {
            console.log(`Filter ${type}:`, message);
        }
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    // === CLEANUP MANAGEMENT ===

    addCleanupTask(task) {
        this.activeCleanupTasks.push(task);
    }

    cleanup() {
        // Execute all cleanup tasks
        this.activeCleanupTasks.forEach(task => {
            try {
                task();
            } catch (error) {
                console.warn('Error during cleanup:', error);
            }
        });
        
        this.activeCleanupTasks = [];
        this.eventHandlers.clear();
    }

    // === CLEANUP ===

    destroy() {
        this.cleanup();
        this.clearFilterBuilder();
        this.filterController = null;
        this.container = null;
    }

    // === GETTERS ===

    get currentField() {
        return this.currentFilterField;
    }

    get currentType() {
        return this.currentFilterType;
    }
}

// Export for use in other modules
window.FilterUIController = FilterUIController;

// Export removed for script tag compatibility