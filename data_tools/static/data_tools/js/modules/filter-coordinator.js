/**
 * FilterCoordinator - Filter System Coordination
 * Responsabilidad única: Coordinar FilterController, FilterUIController y estado
 * 
 * Filosofía: Event-driven coordination, clean interface for external systems
 */

class FilterCoordinator {
    constructor(gridApi, columnDefs) {
        this.gridApi = gridApi;
        this.columnDefs = columnDefs;
        
        // Initialize sub-modules
        this.filterController = new FilterController(gridApi, columnDefs);
        this.filterUIController = new FilterUIController(this.filterController);
        
        // Setup event coordination
        this.setupEventListeners();
        this.exposeGlobalMethods();
        
        // Auto-initialize
        this.initialize();
    }

    // === INITIALIZATION ===

    initialize() {
        try {
            // Initialize available columns
            this.filterController.initializeAvailableColumns();
            
            // Apply any session filters that were restored
            this.filterController.applyStateFiltersToGrid();
            
            // Update UI to show any active filters
            this.filterUIController.updateActiveFiltersDisplay();
            
            this.dispatchSystemEvent('filter-system-ready', {
                availableColumns: this.filterController.getAvailableColumns(),
                activeFilters: this.filterController.getActiveFilters()
            });
            
            return true;

        } catch (error) {
            console.error('Failed to initialize filter system:', error);
            return false;
        }
    }

    // === EVENT COORDINATION ===

    setupEventListeners() {
        // Filter Controller Events -> UI Updates
        this.filterController.addEventListener('filter-applied', (event) => {
            this.dispatchSystemEvent('data-studio-filter-applied', event.detail);
        });

        this.filterController.addEventListener('filter-removed', (event) => {
            this.dispatchSystemEvent('data-studio-filter-removed', event.detail);
        });

        this.filterController.addEventListener('filters-cleared', (event) => {
            this.dispatchSystemEvent('data-studio-filters-cleared', event.detail);
        });

        this.filterController.addEventListener('preset-saved', (event) => {
            this.filterUIController.showNotification(`Filter preset "${event.detail.name}" saved`, 'success');
            this.dispatchSystemEvent('data-studio-preset-saved', event.detail);
        });

        this.filterController.addEventListener('preset-loaded', (event) => {
            this.dispatchSystemEvent('data-studio-preset-loaded', event.detail);
        });

        this.filterController.addEventListener('preset-deleted', (event) => {
            this.filterUIController.showNotification('Filter preset deleted', 'success');
            this.dispatchSystemEvent('data-studio-preset-deleted', event.detail);
        });

        // Global Events -> Filter System Updates
        window.addEventListener('data-studio-grid-update', (event) => {
            this.handleGridUpdate(event.detail);
        });

        // Filter UI Events -> Business Logic
        document.addEventListener('build-filter-ui', (event) => {
            this.buildFilterUI(event.detail);
        });

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

        // Direct filter application events
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
    }

    // === FILTER SYSTEM OPERATIONS ===

    buildFilterUI(columnField) {
        if (!columnField) {
            console.warn('Column field is required to build filter UI');
            return false;
        }

        const success = this.filterUIController.buildFilterInterface(columnField);
        
        if (success) {
            // Update state to show filter builder
            this.filterController.stateManager.setUIState('showFilterBuilder', true);
            this.filterController.stateManager.setUIState('selectedFilterColumn', columnField);
            
            this.dispatchSystemEvent('filter-ui-built', { columnField });
        }

        return success;
    }

    applyMultiSelectFilter(columnField) {
        // Extract selected values from UI
        const container = this.filterUIController.container;
        if (!container) return false;

        const checkboxes = container.querySelectorAll(`input[data-filter-field="${columnField}"]:checked`);
        const selectedValues = Array.from(checkboxes).map(cb => cb.value);
        
        if (selectedValues.length === 0) {
            this.filterUIController.showNotification('Please select at least one value', 'warning');
            return false;
        }

        return this.filterController.applyMultiSelectFilter(columnField, selectedValues);
    }

    applyRangeFilter(columnField) {
        // Extract range values from UI
        const container = this.filterUIController.container;
        if (!container) return false;

        const minInput = container.querySelector('.range-min');
        const maxInput = container.querySelector('.range-max');
        
        if (!minInput || !maxInput) return false;

        const min = parseFloat(minInput.value);
        const max = parseFloat(maxInput.value);
        
        if (isNaN(min) || isNaN(max)) {
            this.filterUIController.showNotification('Please enter valid numbers', 'warning');
            return false;
        }
        
        if (min > max) {
            this.filterUIController.showNotification('Minimum value cannot be greater than maximum', 'warning');
            return false;
        }

        return this.filterController.applyRangeFilter(columnField, min, max);
    }

    applyTextFilter(columnField) {
        // Extract text filter values from UI
        const container = this.filterUIController.container;
        if (!container) return false;

        const typeSelect = container.querySelector('.filter-type');
        const valueInput = container.querySelector('.filter-value');
        
        if (!typeSelect || !valueInput) return false;

        const filterType = typeSelect.value;
        const filterValue = valueInput.value.trim();
        
        if (!filterValue) {
            this.filterUIController.showNotification('Please enter filter text', 'warning');
            return false;
        }

        return this.filterController.applyTextFilter(columnField, filterValue, filterType);
    }

    removeFilter(field) {
        return this.filterController.clearFilter(field);
    }

    clearAllFilters() {
        const success = this.filterController.clearAllFilters();
        
        if (success) {
            // Clear the filter builder UI
            this.filterUIController.clearFilterBuilder();
            
            // Reset UI state
            this.filterController.stateManager.setUIState('showFilterBuilder', false);
            this.filterController.stateManager.setUIState('selectedFilterColumn', '');
        }

        return success;
    }

    // === PRESET MANAGEMENT ===

    saveCurrentFilters() {
        try {
            const activeFilters = this.filterController.getActiveFilters();
            
            if (Object.keys(activeFilters).length === 0) {
                this.filterUIController.showNotification('No active filters to save', 'warning');
                return false;
            }

            const name = prompt('Enter a name for this filter preset:');
            if (!name || !name.trim()) {
                return false;
            }
            
            const description = prompt('Enter a description (optional):') || '';
            
            const presetId = this.filterController.savePreset(name.trim(), description.trim());
            return presetId;

        } catch (error) {
            this.filterUIController.showNotification(error.message, 'error');
            return false;
        }
    }

    loadFilterPreset(presetId) {
        if (!presetId) {
            console.warn('Preset ID is required');
            return false;
        }

        const success = this.filterController.loadPreset(presetId);
        
        if (success) {
            // Clear any existing filter UI
            this.filterUIController.clearFilterBuilder();
            
            // Reset UI state
            this.filterController.stateManager.setUIState('showFilterBuilder', false);
            this.filterController.stateManager.setUIState('selectedFilterColumn', '');
        }

        return success;
    }

    deleteFilterPreset(presetId) {
        if (!presetId) {
            console.warn('Preset ID is required');
            return false;
        }

        if (!confirm('Are you sure you want to delete this filter preset?')) {
            return false;
        }

        return this.filterController.deletePreset(presetId);
    }

    // === GRID INTEGRATION ===

    handleGridUpdate(detail) {
        const { dataPreview, columnInfo } = detail;
        
        if (columnInfo) {
            // Update column definitions
            this.columnDefs = columnInfo;
            
            // Reinitialize available columns
            this.filterController.initializeAvailableColumns();
            
            // Clear cache for data analysis
            this.filterController.invalidateCache();
        }
        
        // Update UI if needed
        this.filterUIController.updateActiveFiltersDisplay();
    }

    // === GLOBAL METHOD EXPOSURE ===

    exposeGlobalMethods() {
        // Expose filter methods globally for backward compatibility
        window.dataStudioFilters = {
            // UI operations
            buildFilterUI: (columnField) => this.buildFilterUI(columnField),
            clearFilterBuilder: () => this.filterUIController.clearFilterBuilder(),
            
            // Filter operations
            applyMultiSelectFilter: (field, values) => this.filterController.applyMultiSelectFilter(field, values),
            applyRangeFilter: (field, min, max) => this.filterController.applyRangeFilter(field, min, max),
            applyTextFilter: (field, value, type) => this.filterController.applyTextFilter(field, value, type),
            clearFilter: (field) => this.filterController.clearFilter(field),
            clearAllFilters: () => this.clearAllFilters(),
            
            // State access
            getActiveFilters: () => this.filterController.getActiveFilters(),
            hasActiveFilters: () => this.filterController.hasActiveFilters(),
            getFilterCount: () => this.filterController.getFilterCount(),
            
            // Preset operations
            savePreset: (name, description) => this.filterController.savePreset(name, description),
            loadPreset: (presetId) => this.loadFilterPreset(presetId),
            deletePreset: (presetId) => this.deleteFilterPreset(presetId),
            getPresets: () => this.filterController.getPresets(),
            
            // Data analysis
            getColumnType: (field) => this.filterController.getColumnType(field),
            getUniqueValues: (field, max) => this.filterController.getUniqueValues(field, max),
            getNumericRange: (field) => this.filterController.getNumericRange(field),
            
            // State management for Alpine.js
            getUIState: () => this.filterController.stateManager.getUIState(),
            setUIState: (key, value) => this.filterController.stateManager.setUIState(key, value)
        };

        // Expose individual components for advanced usage
        window.filterController = this.filterController;
        window.filterUIController = this.filterUIController;
        window.filterManager = this; // Backward compatibility
    }

    // === SYSTEM EVENT DISPATCH ===

    dispatchSystemEvent(eventName, detail = {}) {
        window.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    // === GETTERS ===

    getFilterController() {
        return this.filterController;
    }

    getUIController() {
        return this.filterUIController;
    }

    getStateManager() {
        return this.filterController.stateManager;
    }

    getDataAnalyzer() {
        return this.filterController.dataAnalyzer;
    }

    // === UTILITY METHODS ===

    refreshSystem() {
        // Refresh data analysis cache
        this.filterController.invalidateCache();
        
        // Reinitialize columns
        this.filterController.initializeAvailableColumns();
        
        // Update UI
        this.filterUIController.updateActiveFiltersDisplay();
        
        this.dispatchSystemEvent('filter-system-refreshed');
    }

    getSystemStats() {
        return {
            activeFilters: this.filterController.getFilterCount(),
            availableColumns: this.filterController.getAvailableColumns().length,
            presets: this.filterController.getPresets().length,
            cacheSize: this.filterController.dataAnalyzer.cacheSize
        };
    }

    // === CLEANUP ===

    destroy() {
        this.filterController.destroy();
        this.filterUIController.destroy();
        
        // Clean up global references
        delete window.dataStudioFilters;
        delete window.filterController;
        delete window.filterUIController;
        delete window.filterManager;
        
        this.dispatchSystemEvent('filter-system-destroyed');
    }
}

// Export for use in other modules
window.FilterCoordinator = FilterCoordinator;

// Export removed for script tag compatibility