/**
 * GridUIController - Grid User Interface Management
 * Responsabilidad única: Actualizaciones visuales del grid (NO lógica de negocio)
 * 
 * Filosofía: Pure UI updates, no mixed concerns
 */

class GridUIController {
    constructor() {
        this.elements = this.initializeElements();
    }

    initializeElements() {
        return {
            // Row count displays
            gridRowCount: document.getElementById('grid-row-count'),
            displayedRows: document.getElementById('displayed-rows'),
            
            // Selection info
            selectionInfo: document.getElementById('grid-selection-info'),
            
            // Pagination displays (handled by PaginationUIController in next step)
        };
    }

    // === ROW COUNT UPDATES ===

    updateRowCountDisplay(paginationInfo) {
        try {
            const { currentPage, pageSize, totalRows } = paginationInfo;
            
            const startRow = (currentPage - 1) * pageSize + 1;
            const endRow = Math.min(currentPage * pageSize, totalRows);
            
            // Update the displayed rows count
            if (this.elements.displayedRows) {
                if (pageSize === totalRows) {
                    this.elements.displayedRows.textContent = 'all';
                } else {
                    this.elements.displayedRows.textContent = `${startRow}-${endRow}`;
                }
            }
            
            // Update total rows count
            if (this.elements.gridRowCount) {
                this.elements.gridRowCount.textContent = totalRows.toLocaleString();
            }
            
        } catch (error) {
            console.warn('Error updating row count display:', error);
        }
    }

    // === SELECTION UPDATES ===

    updateSelectionInfo(selectedCount) {
        if (!this.elements.selectionInfo) return;
        
        try {
            this.elements.selectionInfo.textContent = selectedCount > 0 
                ? `${selectedCount} rows selected` 
                : 'No selection';
        } catch (error) {
            console.warn('Error updating selection info:', error);
        }
    }

    // === VISUAL FEEDBACK ===

    showGridLoading() {
        const gridContainer = document.querySelector('#data-preview-grid');
        if (gridContainer) {
            gridContainer.style.opacity = '0.5';
            gridContainer.style.pointerEvents = 'none';
        }
    }

    hideGridLoading() {
        const gridContainer = document.querySelector('#data-preview-grid');
        if (gridContainer) {
            gridContainer.style.opacity = '1';
            gridContainer.style.pointerEvents = 'auto';
        }
    }

    showGridError(errorMessage) {
        const gridContainer = document.querySelector('#data-preview-grid');
        if (gridContainer) {
            gridContainer.innerHTML = `
                <div class="flex items-center justify-center h-64 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded">
                    <div class="text-center">
                        <svg class="w-12 h-12 mx-auto text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                        <h3 class="text-lg font-semibold text-red-800 dark:text-red-300 mb-2">Grid Error</h3>
                        <p class="text-red-600 dark:text-red-400">${errorMessage}</p>
                        <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors">
                            Reload Page
                        </button>
                    </div>
                </div>
            `;
        }
    }

    showGridEmpty() {
        const gridContainer = document.querySelector('#data-preview-grid');
        if (gridContainer) {
            gridContainer.innerHTML = `
                <div class="flex items-center justify-center h-64 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded">
                    <div class="text-center">
                        <svg class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">No Data</h3>
                        <p class="text-gray-500 dark:text-gray-400">No data available to display</p>
                    </div>
                </div>
            `;
        }
    }

    // === GRID STATUS INDICATORS ===

    updateGridStatus(status, message = '') {
        const statusElement = document.querySelector('.grid-status-indicator');
        if (!statusElement) return;

        const statusClasses = {
            loading: 'bg-yellow-100 text-yellow-800 border-yellow-200',
            ready: 'bg-green-100 text-green-800 border-green-200',
            error: 'bg-red-100 text-red-800 border-red-200',
            empty: 'bg-gray-100 text-gray-800 border-gray-200'
        };

        const statusIcons = {
            loading: '⏳',
            ready: '✅',
            error: '❌',
            empty: '📭'
        };

        statusElement.className = `grid-status-indicator px-2 py-1 text-xs rounded border ${statusClasses[status] || statusClasses.ready}`;
        statusElement.innerHTML = `${statusIcons[status] || '•'} ${message || status}`;
    }

    // === RESPONSIVE GRID UPDATES ===

    handleResponsiveChanges() {
        // Handle mobile/desktop grid layout changes
        const gridContainer = document.querySelector('#data-preview-grid');
        if (!gridContainer) return;

        const isMobile = window.innerWidth < 768;
        
        if (isMobile) {
            gridContainer.classList.add('mobile-grid');
            // Adjust for mobile view
        } else {
            gridContainer.classList.remove('mobile-grid');
            // Adjust for desktop view
        }
    }

    // === NOTIFICATION HELPERS ===

    showNotification(message, type = 'info') {
        // Simple notification - can be enhanced with a proper notification system
        if (window.dataStudioNotifications && window.dataStudioNotifications.show) {
            window.dataStudioNotifications.show(message, type);
        } else {
            console.log(`Grid ${type}:`, message);
        }
    }

    // === ACCESSIBILITY UPDATES ===

    updateAriaLabels(paginationInfo) {
        const { currentPage, totalPages, totalRows } = paginationInfo;
        
        const gridContainer = document.querySelector('#data-preview-grid');
        if (gridContainer) {
            gridContainer.setAttribute('aria-label', 
                `Data grid showing page ${currentPage} of ${totalPages}, total ${totalRows} rows`
            );
        }
    }

    // === CLEANUP ===

    destroy() {
        // Clean up any UI-specific listeners or intervals
        this.elements = {};
    }
}

// Export for use in other modules
window.GridUIController = GridUIController;

export default GridUIController;