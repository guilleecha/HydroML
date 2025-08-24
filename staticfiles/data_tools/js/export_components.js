/**
 * Export Components - Pines UI Integration for HydroML Data Studio
 * Provides clean, simple export functionality with Alpine.js
 * 
 * Features:
 * - Simple export wizard modal
 * - Progress tracking with visual feedback
 * - Export history management
 * - One-click quick exports
 * - Mobile responsive design
 */

// Global Export Manager
window.ExportManager = {
    // Current export jobs being monitored
    activeJobs: new Map(),
    
    // Notification system
    notifications: [],
    
    /**
     * Initialize the export system
     */
    init() {
        // Set up global error handling for export operations
        this.setupGlobalErrorHandling();
        
        // Initialize notification system
        this.initNotificationSystem();
        
        // Monitor any existing active exports
        this.monitorActiveExports();
    },

    /**
     * Setup global error handling for export operations
     */
    setupGlobalErrorHandling() {
        window.addEventListener('unhandledrejection', (event) => {
            if (event.reason && event.reason.message && event.reason.message.includes('export')) {
                console.error('Export operation failed:', event.reason);
                this.showNotification('Export operation failed', 'error');
                event.preventDefault();
            }
        });
    },

    /**
     * Initialize simple notification system
     */
    initNotificationSystem() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('export-notifications')) {
            const container = document.createElement('div');
            container.id = 'export-notifications';
            container.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(container);
        }
        
        // Make notifications globally accessible
        window.dataStudioNotifications = {
            show: (message, type = 'info', duration = 5000) => {
                this.showNotification(message, type, duration);
            }
        };
    },

    /**
     * Show notification message
     */
    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('export-notifications');
        if (!container) return;

        const notification = document.createElement('div');
        const id = 'notification-' + Date.now();
        notification.id = id;
        
        // Styling based on type
        const typeClasses = {
            success: 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-700 dark:text-green-300',
            error: 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-700 dark:text-red-300',
            warning: 'bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-700 dark:text-yellow-300',
            info: 'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/20 dark:border-blue-700 dark:text-blue-300'
        };

        const typeIcons = {
            success: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>',
            error: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>',
            warning: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.314 16.5c-.77.833.192 2.5 1.732 2.5z"></path></svg>',
            info: '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
        };

        notification.className = `max-w-sm w-full shadow-lg rounded-lg pointer-events-auto border p-3 ${typeClasses[type] || typeClasses.info} transform transition-all duration-300 ease-in-out translate-x-full opacity-0`;
        
        notification.innerHTML = `
            <div class="flex items-start">
                <div class="flex-shrink-0">
                    ${typeIcons[type] || typeIcons.info}
                </div>
                <div class="ml-3 flex-1">
                    <p class="text-sm font-medium">${message}</p>
                </div>
                <div class="ml-4 flex-shrink-0 flex">
                    <button onclick="window.ExportManager.removeNotification('${id}')" class="inline-flex text-current hover:opacity-75 focus:outline-none">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            </div>
        `;

        container.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.remove('translate-x-full', 'opacity-0');
            notification.classList.add('translate-x-0', 'opacity-100');
        }, 100);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(id);
            }, duration);
        }
    },

    /**
     * Remove notification
     */
    removeNotification(id) {
        const notification = document.getElementById(id);
        if (notification) {
            notification.classList.add('translate-x-full', 'opacity-0');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    },

    /**
     * Monitor active export jobs
     */
    async monitorActiveExports() {
        try {
            const response = await fetch('/tools/api/v1/exports/?status=processing,pending');
            const result = await response.json();
            
            if (result.success && result.data.export_jobs) {
                result.data.export_jobs.forEach(job => {
                    this.startMonitoring(job.id);
                });
            }
        } catch (error) {
            console.error('Error loading active exports:', error);
        }
    },

    /**
     * Start monitoring an export job
     */
    startMonitoring(jobId) {
        if (this.activeJobs.has(jobId)) {
            return; // Already monitoring
        }

        const monitor = async () => {
            try {
                const response = await fetch(`/tools/api/v1/exports/${jobId}/`);
                const result = await response.json();
                
                if (result.success && result.data) {
                    const job = result.data;
                    
                    // Update any UI components that might be displaying this job
                    this.broadcastJobUpdate(job);
                    
                    if (job.status === 'completed') {
                        this.activeJobs.delete(jobId);
                        this.showNotification(`Export completed: ${job.datasource_name}`, 'success');
                        
                        // Auto-download if configured
                        if (job.auto_download) {
                            this.downloadExport(jobId);
                        }
                    } else if (job.status === 'failed') {
                        this.activeJobs.delete(jobId);
                        this.showNotification(`Export failed: ${job.error_message || 'Unknown error'}`, 'error');
                    } else if (job.status === 'cancelled') {
                        this.activeJobs.delete(jobId);
                        this.showNotification('Export cancelled', 'warning');
                    } else if (job.status === 'processing' || job.status === 'pending') {
                        // Continue monitoring
                        setTimeout(monitor, 2000);
                    }
                }
            } catch (error) {
                console.error('Error monitoring export job:', error);
                this.activeJobs.delete(jobId);
            }
        };

        this.activeJobs.set(jobId, monitor);
        setTimeout(monitor, 1000);
    },

    /**
     * Broadcast job update to UI components
     */
    broadcastJobUpdate(job) {
        // Dispatch custom event for components to listen to
        window.dispatchEvent(new CustomEvent('exportJobUpdate', {
            detail: job
        }));
    },

    /**
     * Download export file
     */
    downloadExport(jobId) {
        const downloadUrl = `/tools/api/v1/exports/${jobId}/download/`;
        window.open(downloadUrl, '_blank');
    },

    /**
     * Create a new export job
     */
    async createExport(data) {
        try {
            const response = await fetch('/tools/api/v1/exports/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Start monitoring the new job
                this.startMonitoring(result.data.id);
                return result.data;
            } else {
                throw new Error(result.message || 'Export creation failed');
            }
        } catch (error) {
            console.error('Error creating export:', error);
            throw error;
        }
    },

    /**
     * Get current grid filters from AG Grid
     */
    getCurrentGridFilters() {
        if (window.gridApi && typeof window.gridApi.getFilterModel === 'function') {
            return window.gridApi.getFilterModel();
        }
        return {};
    },

    /**
     * Get current grid data info
     */
    getCurrentGridInfo() {
        const info = {
            totalRows: 0,
            displayedRows: 0,
            selectedRows: 0
        };

        if (window.gridApi) {
            if (typeof window.gridApi.getDisplayedRowCount === 'function') {
                info.displayedRows = window.gridApi.getDisplayedRowCount();
            }
            if (typeof window.gridApi.getSelectedRows === 'function') {
                info.selectedRows = window.gridApi.getSelectedRows().length;
            }
        }

        // Fallback to window data
        if (window.gridRowData) {
            info.totalRows = window.gridRowData.length;
        }

        return info;
    },

    /**
     * Get CSRF token
     */
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
    },

    /**
     * Utility: Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    },

    /**
     * Utility: Format relative time
     */
    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        return `${days}d ago`;
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Small delay to ensure Alpine.js is ready
    setTimeout(() => {
        window.ExportManager.init();
    }, 100);
});

// Export utility functions globally
window.exportUtils = {
    formatFileSize: window.ExportManager.formatFileSize.bind(window.ExportManager),
    formatRelativeTime: window.ExportManager.formatRelativeTime.bind(window.ExportManager),
    showNotification: window.ExportManager.showNotification.bind(window.ExportManager),
    getCurrentGridFilters: window.ExportManager.getCurrentGridFilters.bind(window.ExportManager),
    getCurrentGridInfo: window.ExportManager.getCurrentGridInfo.bind(window.ExportManager)
};