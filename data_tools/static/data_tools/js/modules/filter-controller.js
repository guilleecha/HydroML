/**
 * FilterController - Filter Logic Management
 * Responsabilidad única: Lógica central de filtros (NO UI)
 * 
 * Filosofía: Pure filter logic, AG Grid integration, state coordination
 */

class FilterController {
    constructor(gridApi, columnDefs) {
        this.gridApi = gridApi;
        this.columnDefs = columnDefs || [];
        
        // Initialize sub-modules
        this.stateManager = new FilterStateManager(window.datasourceId);
        this.dataAnalyzer = new FilterDataAnalyzer(gridApi);
        
        // Event system
        this.eventTarget = new EventTarget();
        
        // Initialize available columns
        this.initializeAvailableColumns();
        
        // Setup state change listeners
        this.setupStateListeners();
    }

    // === INITIALIZATION ===

    initializeAvailableColumns() {
        const availableColumns = this.columnDefs
            .filter(col => col.field && col.field !== 'rowNumber')
            .map(col => ({
                field: col.field,
                headerName: col.headerName || col.field,
                type: this.dataAnalyzer.getColumnType(col.field)
            }));

        this.stateManager.setUIState('availableColumns', availableColumns);
        
        this.dispatchEvent('columns-initialized', { 
            columns: availableColumns 
        });
    }

    setupStateListeners() {
        // Listen to state changes and dispatch events
        this.stateManager.addEventListener('active-filter-changed', (event) => {
            this.dispatchEvent('filter-applied', event.detail);
        });

        this.stateManager.addEventListener('active-filter-removed', (event) => {
            this.dispatchEvent('filter-removed', event.detail);
        });

        this.stateManager.addEventListener('active-filters-cleared', (event) => {
            this.dispatchEvent('filters-cleared', event.detail);
        });
    }

    // === CORE FILTER OPERATIONS ===

    applyMultiSelectFilter(field, selectedValues) {
        if (!field || !Array.isArray(selectedValues) || selectedValues.length === 0) {
            console.warn('Invalid multi-select filter parameters');
            return false;
        }

        try {
            // Create AG Grid set filter
            const filterInstance = this.gridApi.getFilterInstance(field);
            if (!filterInstance) {
                console.warn(`No filter instance found for field: ${field}`);
                return false;
            }

            // Apply AG Grid set filter model
            filterInstance.setModel({
                values: selectedValues,
                filterType: 'set'
            });

            // Store in state
            const filterData = {
                type: 'multiSelect',
                values: selectedValues,
                displayName: this.getColumnDisplayName(field),
                appliedAt: new Date().toISOString()
            };

            this.stateManager.setActiveFilter(field, filterData);
            
            // Refresh grid
            this.gridApi.onFilterChanged();
            
            this.dispatchEvent('multi-select-filter-applied', {
                field,
                values: selectedValues,
                filterData
            });

            return true;

        } catch (error) {
            console.error('Error applying multi-select filter:', error);
            return false;
        }
    }

    applyRangeFilter(field, min, max) {
        if (!field || typeof min !== 'number' || typeof max !== 'number' || min > max) {
            console.warn('Invalid range filter parameters');
            return false;
        }

        try {
            // Create AG Grid number filter
            const filterInstance = this.gridApi.getFilterInstance(field);
            if (!filterInstance) {
                console.warn(`No filter instance found for field: ${field}`);
                return false;
            }

            // Apply AG Grid number filter model
            filterInstance.setModel({
                type: 'inRange',
                filter: min,
                filterTo: max,
                filterType: 'number'
            });

            // Store in state
            const filterData = {
                type: 'range',
                min: min,
                max: max,
                displayName: this.getColumnDisplayName(field),
                appliedAt: new Date().toISOString()
            };

            this.stateManager.setActiveFilter(field, filterData);
            
            // Refresh grid
            this.gridApi.onFilterChanged();
            
            this.dispatchEvent('range-filter-applied', {
                field,
                min,
                max,
                filterData
            });

            return true;

        } catch (error) {
            console.error('Error applying range filter:', error);
            return false;
        }
    }

    applyTextFilter(field, value, filterType = 'contains') {
        if (!field || !value || typeof value !== 'string') {
            console.warn('Invalid text filter parameters');
            return false;
        }

        const validFilterTypes = ['contains', 'equals', 'startsWith', 'endsWith', 'notEqual'];
        if (!validFilterTypes.includes(filterType)) {
            console.warn(`Invalid filter type: ${filterType}`);
            return false;
        }

        try {
            // Create AG Grid text filter
            const filterInstance = this.gridApi.getFilterInstance(field);
            if (!filterInstance) {
                console.warn(`No filter instance found for field: ${field}`);
                return false;
            }

            // Apply AG Grid text filter model
            filterInstance.setModel({
                type: filterType,
                filter: value.trim(),
                filterType: 'text'
            });

            // Store in state
            const filterData = {
                type: 'text',
                value: value.trim(),
                filterType: filterType,
                displayName: this.getColumnDisplayName(field),
                appliedAt: new Date().toISOString()
            };

            this.stateManager.setActiveFilter(field, filterData);
            
            // Refresh grid
            this.gridApi.onFilterChanged();
            
            this.dispatchEvent('text-filter-applied', {
                field,
                value,
                filterType,
                filterData
            });

            return true;

        } catch (error) {
            console.error('Error applying text filter:', error);
            return false;
        }
    }

    clearFilter(field) {
        if (!field) {
            console.warn('Field is required to clear filter');
            return false;
        }

        try {
            // Clear AG Grid filter
            const filterInstance = this.gridApi.getFilterInstance(field);
            if (filterInstance) {
                filterInstance.setModel(null);
            }

            // Remove from state
            const removed = this.stateManager.removeActiveFilter(field);
            
            if (removed) {
                // Refresh grid
                this.gridApi.onFilterChanged();
                
                this.dispatchEvent('filter-cleared', { field });
            }

            return removed;

        } catch (error) {
            console.error('Error clearing filter:', error);
            return false;
        }
    }

    clearAllFilters() {
        try {
            // Clear all AG Grid filters
            this.gridApi.setFilterModel(null);
            
            // Clear state
            this.stateManager.clearActiveFilters();
            
            // Refresh grid
            this.gridApi.onFilterChanged();
            
            this.dispatchEvent('all-filters-cleared');
            return true;

        } catch (error) {
            console.error('Error clearing all filters:', error);
            return false;
        }
    }

    // === PRESET MANAGEMENT ===

    savePreset(name, description = '') {
        try {
            const presetId = this.stateManager.savePreset(name, description);
            
            this.dispatchEvent('preset-saved', {
                presetId,
                name,
                description
            });

            return presetId;

        } catch (error) {
            console.error('Error saving preset:', error);
            throw error;
        }
    }

    loadPreset(presetId) {
        try {
            const success = this.stateManager.loadPreset(presetId);
            
            if (success) {
                // Apply all loaded filters to the grid
                this.applyStateFiltersToGrid();
                
                this.dispatchEvent('preset-loaded', { presetId });
            }

            return success;

        } catch (error) {
            console.error('Error loading preset:', error);
            return false;
        }
    }

    deletePreset(presetId) {
        try {
            const success = this.stateManager.deletePreset(presetId);
            
            if (success) {
                this.dispatchEvent('preset-deleted', { presetId });
            }

            return success;

        } catch (error) {
            console.error('Error deleting preset:', error);
            return false;
        }
    }

    // === FILTER APPLICATION FROM STATE ===

    applyStateFiltersToGrid() {
        const activeFilters = this.stateManager.getActiveFilters();
        
        try {
            // Build AG Grid filter model
            const filterModel = {};
            
            Object.entries(activeFilters).forEach(([field, filterData]) => {
                const agGridModel = this.convertStateToAGGridModel(filterData);
                if (agGridModel) {
                    filterModel[field] = agGridModel;
                }
            });

            // Apply to grid
            this.gridApi.setFilterModel(filterModel);
            this.gridApi.onFilterChanged();
            
            this.dispatchEvent('state-filters-applied', {
                filterCount: Object.keys(filterModel).length
            });

        } catch (error) {
            console.error('Error applying state filters to grid:', error);
        }
    }

    convertStateToAGGridModel(filterData) {
        switch (filterData.type) {
            case 'multiSelect':
                return {
                    values: filterData.values,
                    filterType: 'set'
                };
                
            case 'range':
                return {
                    type: 'inRange',
                    filter: filterData.min,
                    filterTo: filterData.max,
                    filterType: 'number'
                };
                
            case 'text':
                return {
                    type: filterData.filterType,
                    filter: filterData.value,
                    filterType: 'text'
                };
                
            default:
                console.warn(`Unknown filter type: ${filterData.type}`);
                return null;
        }
    }

    // === DATA ACCESS METHODS ===

    getColumnType(field) {
        return this.dataAnalyzer.getColumnType(field);
    }

    getUniqueValues(field, maxValues = 100) {
        return this.dataAnalyzer.getUniqueValues(field, maxValues);
    }

    getNumericRange(field) {
        return this.dataAnalyzer.getNumericRange(field);
    }

    getFilterSuggestions(field, query, limit = 10) {
        return this.dataAnalyzer.getFilterSuggestions(field, query, limit);
    }

    getFieldStatistics(field) {
        return this.dataAnalyzer.getFieldStatistics(field);
    }

    // === STATE ACCESS METHODS ===

    getActiveFilters() {
        return this.stateManager.getActiveFilters();
    }

    getActiveFiltersState() {
        // Backward compatibility method
        return this.getActiveFilters();
    }

    getPresets() {
        return this.stateManager.getPresets();
    }

    getAvailableColumns() {
        return this.stateManager.getUIState('availableColumns') || [];
    }

    hasActiveFilters() {
        return this.stateManager.hasActiveFilters();
    }

    getFilterCount() {
        return this.stateManager.getActiveFilterCount();
    }

    // === UTILITY METHODS ===

    getColumnDisplayName(field) {
        const columns = this.getAvailableColumns();
        const column = columns.find(col => col.field === field);
        return column ? column.headerName : field;
    }

    invalidateCache(field = null) {
        if (field) {
            this.dataAnalyzer.invalidateFieldCache(field);
        } else {
            this.dataAnalyzer.clearCache();
        }
    }

    // === EVENT SYSTEM ===

    dispatchEvent(eventName, detail = {}) {
        this.eventTarget.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    addEventListener(eventName, handler) {
        this.eventTarget.addEventListener(eventName, handler);
    }

    removeEventListener(eventName, handler) {
        this.eventTarget.removeEventListener(eventName, handler);
    }

    // === CLEANUP ===

    destroy() {
        this.stateManager.destroy();
        this.dataAnalyzer.destroy();
        this.gridApi = null;
        this.columnDefs = [];
        this.dispatchEvent('destroyed');
    }

    // === GETTERS ===

    get stateManager() {
        return this.stateManager;
    }

    get dataAnalyzer() {
        return this.dataAnalyzer;
    }
}

// Export for use in other modules
window.FilterController = FilterController;

export default FilterController;