/**
 * Alpine.js Global App Store
 * Manages global application state and loading states
 */

document.addEventListener('alpine:init', () => {
    Alpine.store('app', {
        // Loading state management
        isLoading: false,
        loadingMessage: '',
        
        // Methods for loading management
        startLoading(message = 'Processing') {
            this.loadingMessage = message;
            this.isLoading = true;
        },
        
        stopLoading() {
            this.isLoading = false;
            this.loadingMessage = '';
        },

        // Data source management
        refreshDataSourceLists() {
            // Refresh any data source lists in the UI
            // This can be overridden by specific components
            console.log('Refreshing data source lists...');
        }
    });
});