/**
 * Data Studio Advanced Filters - Filter Management System
 * Provides advanced filtering capabilities with multi-select, range filters, and presets.
 */

class FilterManager {
    constructor(gridApi, columnDefs) {
        this.gridApi = gridApi;
        this.columnDefs = columnDefs || [];
        this.activeFilters = new Map();
        this.filterPresets = this.loadPresets();
        this.storageKey = 'hydroml_filter_presets';
        this.sessionKey = 'hydroml_filter_session';
        
        this.init();
    }

    init() {
        this.detectColumnTypes();
        this.loadSessionFilters();
    }

    detectColumnTypes() {
        this.columnTypes = new Map();
        
        if (!this.columnDefs || !Array.isArray(this.columnDefs)) {
            console.warn('Column definitions not available for filter type detection');
            return;
        }

        this.columnDefs.forEach(colDef => {
            if (colDef.field && colDef.field !== 'rowNumber') {
                let type = 'text'; // default

                // Detect type based on headerName or field patterns
                const fieldLower = colDef.field.toLowerCase();
                const headerLower = (colDef.headerName || '').toLowerCase();
                
                if (fieldLower.includes('date') || fieldLower.includes('time') || 
                    headerLower.includes('date') || headerLower.includes('time')) {
                    type = 'date';
                } else if (fieldLower.includes('id') || fieldLower.includes('count') ||
                          headerLower.includes('number') || headerLower.includes('amount') ||
                          headerLower.includes('price') || headerLower.includes('score')) {
                    type = 'number';
                } else if (fieldLower.includes('category') || fieldLower.includes('type') ||
                          fieldLower.includes('status') || headerLower.includes('category')) {
                    type = 'category';
                }

                this.columnTypes.set(colDef.field, type);
            }
        });
    }

    getColumnType(field) {
        return this.columnTypes.get(field) || 'text';
    }

    getUniqueValues(field, maxValues = 1000) {
        if (!this.gridApi || typeof this.gridApi.forEachNode !== 'function') {
            return [];
        }

        const values = new Set();
        let count = 0;

        this.gridApi.forEachNode((node) => {
            if (count >= maxValues) return;
            
            const value = node.data[field];
            if (value != null && value !== '') {
                values.add(value);
                count++;
            }
        });

        return Array.from(values).sort();
    }

    getNumericRange(field) {
        if (!this.gridApi || typeof this.gridApi.forEachNode !== 'function') {
            return { min: 0, max: 100 };
        }

        let min = Infinity;
        let max = -Infinity;
        let hasValues = false;

        this.gridApi.forEachNode((node) => {
            const value = parseFloat(node.data[field]);
            if (!isNaN(value)) {
                min = Math.min(min, value);
                max = Math.max(max, value);
                hasValues = true;
            }
        });

        return hasValues ? { min, max } : { min: 0, max: 100 };
    }

    applyMultiSelectFilter(field, selectedValues) {
        if (!selectedValues || selectedValues.length === 0) {
            this.clearFilter(field);
            return;
        }

        const filterInstance = this.gridApi.getFilterInstance(field);
        if (filterInstance && typeof filterInstance.setModel === 'function') {
            filterInstance.setModel({
                filterType: 'set',
                values: selectedValues
            });
            
            this.activeFilters.set(field, {
                type: 'multiSelect',
                values: selectedValues,
                displayName: this.getColumnDisplayName(field)
            });

            this.gridApi.onFilterChanged();
            this.saveSessionFilters();
        }
    }

    applyRangeFilter(field, min, max) {
        const filterInstance = this.gridApi.getFilterInstance(field);
        if (filterInstance && typeof filterInstance.setModel === 'function') {
            filterInstance.setModel({
                filterType: 'number',
                type: 'inRange',
                filter: min,
                filterTo: max
            });
            
            this.activeFilters.set(field, {
                type: 'range',
                min: min,
                max: max,
                displayName: this.getColumnDisplayName(field)
            });

            this.gridApi.onFilterChanged();
            this.saveSessionFilters();
        }
    }

    applyTextFilter(field, value, filterType = 'contains') {
        const filterInstance = this.gridApi.getFilterInstance(field);
        if (filterInstance && typeof filterInstance.setModel === 'function') {
            filterInstance.setModel({
                filterType: 'text',
                type: filterType,
                filter: value
            });
            
            this.activeFilters.set(field, {
                type: 'text',
                value: value,
                filterType: filterType,
                displayName: this.getColumnDisplayName(field)
            });

            this.gridApi.onFilterChanged();
            this.saveSessionFilters();
        }
    }

    clearFilter(field) {
        const filterInstance = this.gridApi.getFilterInstance(field);
        if (filterInstance && typeof filterInstance.setModel === 'function') {
            filterInstance.setModel(null);
            this.activeFilters.delete(field);
            this.gridApi.onFilterChanged();
            this.saveSessionFilters();
        }
    }

    clearAllFilters() {
        if (this.gridApi && typeof this.gridApi.setFilterModel === 'function') {
            this.gridApi.setFilterModel(null);
            this.activeFilters.clear();
            this.saveSessionFilters();
        }
    }

    getColumnDisplayName(field) {
        const colDef = this.columnDefs.find(col => col.field === field);
        return colDef ? (colDef.headerName || field) : field;
    }

    savePreset(name, description = '') {
        if (!name.trim()) return false;

        const currentFilters = this.getActiveFiltersState();
        if (Object.keys(currentFilters).length === 0) return false;

        const preset = {
            id: Date.now().toString(),
            name: name.trim(),
            description: description.trim(),
            filters: currentFilters,
            created: new Date().toISOString(),
            datasourceId: window.datasourceId || 'unknown'
        };

        this.filterPresets.set(preset.id, preset);
        this.savePresets();
        return preset.id;
    }

    loadPreset(presetId) {
        const preset = this.filterPresets.get(presetId);
        if (!preset) return false;

        this.clearAllFilters();
        
        Object.entries(preset.filters).forEach(([field, filterData]) => {
            switch (filterData.type) {
                case 'multiSelect':
                    this.applyMultiSelectFilter(field, filterData.values);
                    break;
                case 'range':
                    this.applyRangeFilter(field, filterData.min, filterData.max);
                    break;
                case 'text':
                    this.applyTextFilter(field, filterData.value, filterData.filterType);
                    break;
            }
        });

        return true;
    }

    deletePreset(presetId) {
        const deleted = this.filterPresets.delete(presetId);
        if (deleted) {
            this.savePresets();
        }
        return deleted;
    }

    getPresets() {
        return Array.from(this.filterPresets.values())
            .filter(preset => preset.datasourceId === window.datasourceId)
            .sort((a, b) => new Date(b.created) - new Date(a.created));
    }

    getActiveFiltersState() {
        const state = {};
        this.activeFilters.forEach((filterData, field) => {
            state[field] = filterData;
        });
        return state;
    }

    getActiveFiltersCount() {
        return this.activeFilters.size;
    }

    loadPresets() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            if (stored) {
                const data = JSON.parse(stored);
                return new Map(Object.entries(data));
            }
        } catch (error) {
            console.warn('Error loading filter presets:', error);
        }
        return new Map();
    }

    savePresets() {
        try {
            const data = Object.fromEntries(this.filterPresets);
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        } catch (error) {
            console.warn('Error saving filter presets:', error);
        }
    }

    loadSessionFilters() {
        try {
            const stored = localStorage.getItem(this.sessionKey);
            if (stored) {
                const data = JSON.parse(stored);
                const datasourceKey = window.datasourceId || 'default';
                
                if (data[datasourceKey] && data[datasourceKey].timestamp) {
                    const age = Date.now() - data[datasourceKey].timestamp;
                    // Only restore filters if less than 1 hour old
                    if (age < 3600000) {
                        return data[datasourceKey].filters || {};
                    }
                }
            }
        } catch (error) {
            console.warn('Error loading session filters:', error);
        }
        return {};
    }

    saveSessionFilters() {
        try {
            const datasourceKey = window.datasourceId || 'default';
            let sessionData = {};
            
            try {
                const stored = localStorage.getItem(this.sessionKey);
                if (stored) {
                    sessionData = JSON.parse(stored);
                }
            } catch (e) {
                sessionData = {};
            }

            sessionData[datasourceKey] = {
                filters: this.getActiveFiltersState(),
                timestamp: Date.now()
            };

            localStorage.setItem(this.sessionKey, JSON.stringify(sessionData));
        } catch (error) {
            console.warn('Error saving session filters:', error);
        }
    }

    getFilterSuggestions(field, query, limit = 10) {
        const uniqueValues = this.getUniqueValues(field, 500);
        const queryLower = query.toLowerCase();
        
        return uniqueValues
            .filter(value => 
                value.toString().toLowerCase().includes(queryLower)
            )
            .slice(0, limit);
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.FilterManager = FilterManager;
}