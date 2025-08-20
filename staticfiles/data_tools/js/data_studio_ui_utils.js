/**
 * Data Studio UI Utilities - Modal and Notification Management
 * Handles UI components like modals, notifications, and dropdowns
 */

class DataStudioUIUtils {
    
    // Modal HTML Templates
    static HTML_TEMPLATES = {
        nanCleaningModal: `
            <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
                <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">NaN Cleaning Options</h3>
                
                <div class="space-y-4">
                    <label class="flex items-center">
                        <input type="checkbox" id="remove-nan-rows" checked class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                        <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Remove rows with NaN values</span>
                    </label>
                    
                    <label class="flex items-center">
                        <input type="checkbox" id="remove-nan-columns" class="rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                        <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Remove columns with all NaN values</span>
                    </label>
                </div>
                
                <div class="flex justify-end space-x-3 mt-6">
                    <button onclick="window.dataStudioSidebar.closeNaNCleaningModal()" 
                            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600">
                        Cancel
                    </button>
                    <button onclick="window.dataStudioSidebar.performNaNCleaning()" 
                            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
                        Clean Data
                    </button>
                </div>
            </div>
        `
    };

    // Notification color schemes
    static NOTIFICATION_COLORS = {
        success: 'bg-green-100 border-green-500 text-green-800 dark:bg-green-900/20 dark:border-green-600 dark:text-green-200',
        error: 'bg-red-100 border-red-500 text-red-800 dark:bg-red-900/20 dark:border-red-600 dark:text-red-200',
        warning: 'bg-yellow-100 border-yellow-500 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-600 dark:text-yellow-200',
        info: 'bg-blue-100 border-blue-500 text-blue-800 dark:bg-blue-900/20 dark:border-blue-600 dark:text-blue-200'
    };

    /**
     * Show notification toast
     */
    static showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-md shadow-lg max-w-sm transition-all duration-300 transform translate-x-full`;
        
        notification.className += ` border-l-4 ${this.NOTIFICATION_COLORS[type] || this.NOTIFICATION_COLORS.info}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.remove('translate-x-full'), 100);
        setTimeout(() => {
            notification.classList.add('translate-x-full');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    /**
     * Create modal element
     */
    static createModal(templateKey, modalId) {
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden';
        modal.id = modalId;
        modal.innerHTML = this.HTML_TEMPLATES[templateKey];
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) this.closeModal(modalId);
        });
        
        return modal;
    }

    /**
     * Close and remove modal
     */
    static closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.remove();
    }

    /**
     * Open modal
     */
    static openModal(modal) {
        document.body.appendChild(modal);
        modal.classList.remove('hidden');
    }

    /**
     * Initialize dropdown functionality
     */
    static initDropdowns(closeAllCallback) {
        const dropdownSections = document.querySelectorAll('.dropdown-section');
        
        dropdownSections.forEach(section => {
            const button = section.querySelector('button');
            const content = section.querySelector('.dropdown-content');
            const arrow = section.querySelector('.dropdown-arrow');
            
            if (button && content && arrow) {
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Check if current dropdown is open BEFORE closing all
                    const isCurrentlyOpen = !content.classList.contains('hidden');
                    
                    // Close all dropdowns first
                    closeAllCallback();
                    
                    // If current dropdown was closed, open it
                    if (!isCurrentlyOpen) {
                        content.classList.remove('hidden');
                        arrow.style.transform = 'rotate(180deg)';
                    }
                });
            }
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown-section')) {
                closeAllCallback();
            }
        });
    }

    /**
     * Close all dropdowns
     */
    static closeAllDropdowns() {
        const dropdownContents = document.querySelectorAll('.dropdown-content');
        const dropdownArrows = document.querySelectorAll('.dropdown-arrow');
        
        dropdownContents.forEach(content => {
            content.classList.add('hidden');
        });
        
        dropdownArrows.forEach(arrow => {
            arrow.style.transform = 'rotate(0deg)';
        });
    }

    /**
     * Show placeholder feature notification
     */
    static showPlaceholderFeature(featureName) {
        this.showNotification(`${featureName} feature coming soon`, 'info');
    }
}

// Export for use in other modules
window.DataStudioUIUtils = DataStudioUIUtils;