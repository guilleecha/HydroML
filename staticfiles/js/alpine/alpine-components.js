/**
 * Alpine.js Components Loader
 * This file provides an index of all Alpine.js components for easy inclusion
 */

// List of Alpine.js component files (for documentation)
const ALPINE_COMPONENTS = [
    'app-store.js',                    // Global app store
    'workspace-selector.js',           // Single workspace selection
    'datasource-workspace-selector.js' // Multiple workspace selection
];

// Component descriptions for developers
const COMPONENT_DESCRIPTIONS = {
    'app-store': 'Global application state and loading management',
    'workspaceSelector': 'Single project/workspace selection for forms',
    'datasourceWorkspaceSelector': 'Multiple workspace selection for datasource uploads',
    'datasourceUploadForm': 'File upload form with project selection (main app.js)'
};

// Export for debugging/development
window.AlpineComponents = {
    list: ALPINE_COMPONENTS,
    descriptions: COMPONENT_DESCRIPTIONS
};