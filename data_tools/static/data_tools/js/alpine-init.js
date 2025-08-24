/**
 * Alpine.js Initialization with localStorage State
 * Prevents sidebar and UI flashing during page load
 * 
 * Must be loaded BEFORE Alpine.js starts processing templates
 */

// Initialize Alpine variables from localStorage to prevent sidebar state flash
window.alpineInitialState = {
    showFilterBuilder: localStorage.getItem('dataStudio_showFilterBuilder') === 'true',
    showFilterPresets: localStorage.getItem('dataStudio_showFilterPresets') === 'true', 
    showHistory: localStorage.getItem('dataStudio_showHistory') === 'true',
    showExportHistory: false
};

// Initialize global variables needed by Alpine.js templates IMMEDIATELY
window.filterManager = {
    getActiveFiltersCount: () => 0,
    getActiveFilter: () => null,
    getPresets: () => []
};

window.pagination = {
    pageSize: 25,
    availablePageSizes: [10, 25, 50, 100],
    currentPage: 1,
    totalPages: 1,
    totalRows: 0,
    jumpToPage: 1
};

// Initialize filter UI variables with localStorage values to prevent flash
window.showFilterBuilder = window.alpineInitialState.showFilterBuilder;
window.showFilterPresets = window.alpineInitialState.showFilterPresets;
window.selectedFilterColumn = null;
window.availableColumns = [];

// Alpine.js initialization callback to mark components as ready
document.addEventListener('alpine:init', () => {
    console.log('🎿 Alpine.js initialized with localStorage state');
    
    // Mark all Alpine components as initialized to make them visible
    document.querySelectorAll('[x-data]').forEach(el => {
        el.classList.add('alpine-initialized');
    });
});

// Additional Alpine.js ready callback
document.addEventListener('alpine:initialized', () => {
    console.log('✅ Alpine.js components fully initialized - FOUC prevention complete');
});