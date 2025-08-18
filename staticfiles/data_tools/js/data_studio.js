/**
 * Data Studio - Main entry point for modular architecture
 * 
 * This file serves as the main entry point for the refactored Data Studio application.
 * It imports the modular structure and maintains backward compatibility with existing templates.
 */

import { DataStudio } from './data_studio/main.js';

// Create global instance for backward compatibility
let dataStudioInstance = null;

/**
 * Initialize the Data Studio application
 * This function is called from the HTML template to start the application
 */
function initializeDataStudio() {
    if (!dataStudioInstance) {
        dataStudioInstance = new DataStudio();
        console.log('Data Studio initialized successfully');
    }
    return dataStudioInstance;
}

/**
 * Get the current Data Studio instance
 */
function getDataStudioInstance() {
    return dataStudioInstance;
}

// Global functions for backward compatibility with inline event handlers
window.initializeDataStudio = initializeDataStudio;
window.getDataStudioInstance = getDataStudioInstance;

// Export for ES6 module usage
export { DataStudio, initializeDataStudio, getDataStudioInstance };

// Auto-initialize if DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDataStudio);
} else {
    initializeDataStudio();
}
