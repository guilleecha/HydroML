/**
 * FilterStateManager - Filter State Management
 * Responsabilidad única: Gestión centralizada del estado de filtros
 * 
 * Filosofía: Single source of truth for filter state, no mixed concerns
 */

class FilterStateManager {
    constructor(datasourceId = null) {
        this.datasourceId = datasourceId;
        
        // UI State
        this.uiState = {
            showFilterBuilder: false,
            showFilterPresets: false,
            showSaveFilterDialog: false,
            selectedFilterColumn: '',
            availableColumns: []
        };
        
        // Active filters state
        this.activeFilters = new Map();
        
        // Presets state
        this.presets = new Map();
        
        // Event system
        this.eventTarget = new EventTarget();
        
        // Initialize from persistent storage
        this.loadFromSession();
        this.loadPresets();
    }

    // === UI STATE MANAGEMENT ===

    setUIState(key, value) {
        if (!(key in this.uiState)) {
            console.warn(`Unknown UI state key: ${key}`);
            return false;
        }
        
        const oldValue = this.uiState[key];
        this.uiState[key] = value;
        
        this.dispatchEvent('ui-state-changed', { 
            key, 
            oldValue, 
            newValue: value 
        });
        
        return true;
    }

    getUIState(key = null) {
        if (key === null) {
            return { ...this.uiState };
        }
        return this.uiState[key];
    }

    toggleUIState(key) {
        if (typeof this.uiState[key] === 'boolean') {
            return this.setUIState(key, !this.uiState[key]);
        }
        return false;
    }

    resetUIState() {
        this.uiState = {
            showFilterBuilder: false,
            showFilterPresets: false,
            showSaveFilterDialog: false,
            selectedFilterColumn: '',
            availableColumns: []
        };
        this.dispatchEvent('ui-state-reset');
    }

    // === ACTIVE FILTERS MANAGEMENT ===

    setActiveFilter(field, filterData) {
        if (!field || !filterData) {
            console.warn('Invalid filter data:', { field, filterData });
            return false;
        }

        const oldFilter = this.activeFilters.get(field);
        this.activeFilters.set(field, {
            ...filterData,
            field: field,
            timestamp: Date.now()
        });

        this.dispatchEvent('active-filter-changed', {
            field,
            oldFilter,
            newFilter: filterData
        });

        // Auto-save to session
        this.saveToSession();
        return true;
    }

    getActiveFilter(field) {
        return this.activeFilters.get(field) || null;
    }

    getActiveFilters() {
        const filters = {};
        this.activeFilters.forEach((filterData, field) => {
            filters[field] = filterData;
        });
        return filters;
    }

    removeActiveFilter(field) {
        const removedFilter = this.activeFilters.get(field);
        const deleted = this.activeFilters.delete(field);
        
        if (deleted) {
            this.dispatchEvent('active-filter-removed', {
                field,
                removedFilter
            });
            this.saveToSession();
        }
        
        return deleted;
    }

    clearActiveFilters() {
        const clearedFilters = this.getActiveFilters();
        this.activeFilters.clear();
        
        this.dispatchEvent('active-filters-cleared', {
            clearedFilters
        });
        
        this.saveToSession();
    }

    hasActiveFilters() {
        return this.activeFilters.size > 0;
    }

    getActiveFilterCount() {
        return this.activeFilters.size;
    }

    // === PRESETS MANAGEMENT ===

    savePreset(name, description = '', filters = null) {
        if (!name || !name.trim()) {
            throw new Error('Preset name is required');
        }

        const filtersToSave = filters || this.getActiveFilters();
        
        if (Object.keys(filtersToSave).length === 0) {
            throw new Error('No active filters to save');
        }

        const presetId = this.generatePresetId();
        const preset = {
            id: presetId,
            name: name.trim(),
            description: description.trim(),
            filters: filtersToSave,
            createdAt: new Date().toISOString(),
            datasourceId: this.datasourceId
        };

        this.presets.set(presetId, preset);
        this.savePresets();

        this.dispatchEvent('preset-saved', { preset });
        return presetId;
    }

    loadPreset(presetId) {
        const preset = this.presets.get(presetId);
        if (!preset) {
            console.warn(`Preset not found: ${presetId}`);
            return false;
        }

        // Clear current filters
        this.clearActiveFilters();

        // Load preset filters
        Object.entries(preset.filters).forEach(([field, filterData]) => {
            this.setActiveFilter(field, filterData);
        });

        this.dispatchEvent('preset-loaded', { preset });
        return true;
    }

    deletePreset(presetId) {
        const preset = this.presets.get(presetId);
        const deleted = this.presets.delete(presetId);
        
        if (deleted) {
            this.savePresets();
            this.dispatchEvent('preset-deleted', { 
                presetId, 
                deletedPreset: preset 
            });
        }
        
        return deleted;
    }

    getPreset(presetId) {
        return this.presets.get(presetId) || null;
    }

    getPresets() {
        const presets = [];
        this.presets.forEach(preset => presets.push(preset));
        return presets.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    }

    getPresetsForDatasource(datasourceId = null) {
        const targetId = datasourceId || this.datasourceId;
        return this.getPresets().filter(preset => 
            !preset.datasourceId || preset.datasourceId === targetId
        );
    }

    // === PERSISTENCE ===

    saveToSession() {
        if (!this.datasourceId) return;

        try {
            const sessionKey = `dataStudio_filters_${this.datasourceId}`;
            const sessionData = {
                activeFilters: this.getActiveFilters(),
                timestamp: Date.now(),
                expiresAt: Date.now() + (60 * 60 * 1000) // 1 hour
            };
            
            localStorage.setItem(sessionKey, JSON.stringify(sessionData));
            this.dispatchEvent('session-saved');
        } catch (error) {
            console.error('Failed to save filters to session:', error);
        }
    }

    loadFromSession() {
        if (!this.datasourceId) return;

        try {
            const sessionKey = `dataStudio_filters_${this.datasourceId}`;
            const sessionData = localStorage.getItem(sessionKey);
            
            if (!sessionData) return;

            const data = JSON.parse(sessionData);
            
            // Check expiration
            if (data.expiresAt && Date.now() > data.expiresAt) {
                localStorage.removeItem(sessionKey);
                return;
            }

            // Restore active filters
            if (data.activeFilters) {
                Object.entries(data.activeFilters).forEach(([field, filterData]) => {
                    this.activeFilters.set(field, filterData);
                });
                
                this.dispatchEvent('session-loaded', { 
                    filtersCount: Object.keys(data.activeFilters).length 
                });
            }
        } catch (error) {
            console.error('Failed to load filters from session:', error);
        }
    }

    savePresets() {
        try {
            const presetsKey = 'dataStudio_filterPresets';
            const presetsData = [];
            this.presets.forEach(preset => presetsData.push(preset));
            
            localStorage.setItem(presetsKey, JSON.stringify(presetsData));
            this.dispatchEvent('presets-saved');
        } catch (error) {
            console.error('Failed to save presets:', error);
        }
    }

    loadPresets() {
        try {
            const presetsKey = 'dataStudio_filterPresets';
            const presetsData = localStorage.getItem(presetsKey);
            
            if (!presetsData) return;

            const presets = JSON.parse(presetsData);
            presets.forEach(preset => {
                this.presets.set(preset.id, preset);
            });

            this.dispatchEvent('presets-loaded', { 
                presetsCount: presets.length 
            });
        } catch (error) {
            console.error('Failed to load presets:', error);
        }
    }

    // === UTILITY METHODS ===

    generatePresetId() {
        return `preset_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    clearSession() {
        if (!this.datasourceId) return;
        
        const sessionKey = `dataStudio_filters_${this.datasourceId}`;
        localStorage.removeItem(sessionKey);
        this.dispatchEvent('session-cleared');
    }

    exportState() {
        return {
            uiState: { ...this.uiState },
            activeFilters: this.getActiveFilters(),
            presets: this.getPresets(),
            datasourceId: this.datasourceId
        };
    }

    importState(state) {
        if (!state) return false;

        try {
            // Import UI state
            if (state.uiState) {
                this.uiState = { ...this.uiState, ...state.uiState };
            }

            // Import active filters
            if (state.activeFilters) {
                this.clearActiveFilters();
                Object.entries(state.activeFilters).forEach(([field, filterData]) => {
                    this.setActiveFilter(field, filterData);
                });
            }

            // Import presets
            if (state.presets && Array.isArray(state.presets)) {
                state.presets.forEach(preset => {
                    this.presets.set(preset.id, preset);
                });
                this.savePresets();
            }

            this.dispatchEvent('state-imported', { state });
            return true;
        } catch (error) {
            console.error('Failed to import state:', error);
            return false;
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
        this.clearActiveFilters();
        this.presets.clear();
        this.resetUIState();
        this.dispatchEvent('destroyed');
    }
}

// Export for use in other modules
window.FilterStateManager = FilterStateManager;

// Export removed for script tag compatibility