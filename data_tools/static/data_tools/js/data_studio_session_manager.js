/**
 * Session Management Enhancement for Data Studio
 * Provides comprehensive session persistence, recovery, and state management
 */
class DataStudioSessionManager {
    constructor(datasourceId) {
        this.datasourceId = datasourceId;
        this.sessionStorageKey = `hydroml_session_${datasourceId}`;
        this.autoSaveInterval = 30000; // 30 seconds
        this.sessionTimeout = 30 * 60 * 1000; // 30 minutes
        this.autoSaveTimer = null;
        this.timeoutWarningTimer = null;
        this.timeoutTimer = null;
        this.lastActivityTime = Date.now();
        this.sessionState = {
            isActive: false,
            sessionId: null,
            lastSaved: null,
            autoRecoveryEnabled: true,
            hasUnsavedChanges: false,
            operations: [],
            currentPosition: 0,
            metadata: {}
        };
        
        this.init();
    }

    init() {
        this.loadSessionFromStorage();
        this.setupAutoSave();
        this.setupActivityTracking();
        this.setupVisibilityHandling();
        this.setupBeforeUnloadProtection();
        
        // Try to recover session on page load
        if (this.sessionState.autoRecoveryEnabled) {
            this.attemptSessionRecovery();
        }
    }

    /**
     * Session Storage Management
     */
    saveSessionToStorage() {
        try {
            const sessionData = {
                ...this.sessionState,
                timestamp: Date.now(),
                userAgent: navigator.userAgent,
                url: window.location.href
            };
            
            localStorage.setItem(this.sessionStorageKey, JSON.stringify(sessionData));
            
            // Also save to sessionStorage for tab-specific data
            sessionStorage.setItem(`${this.sessionStorageKey}_tab`, JSON.stringify({
                tabId: this.generateTabId(),
                opened: Date.now(),
                lastActivity: this.lastActivityTime
            }));
            
            console.log('Session saved to storage');
            return true;
        } catch (error) {
            console.error('Failed to save session to storage:', error);
            return false;
        }
    }

    loadSessionFromStorage() {
        try {
            const stored = localStorage.getItem(this.sessionStorageKey);
            if (stored) {
                const sessionData = JSON.parse(stored);
                
                // Check if session is not too old (48 hours max)
                const maxAge = 48 * 60 * 60 * 1000;
                if (Date.now() - sessionData.timestamp < maxAge) {
                    this.sessionState = { ...this.sessionState, ...sessionData };
                    console.log('Session loaded from storage');
                    return true;
                } else {
                    console.log('Stored session too old, clearing');
                    this.clearStoredSession();
                }
            }
        } catch (error) {
            console.error('Failed to load session from storage:', error);
        }
        return false;
    }

    clearStoredSession() {
        localStorage.removeItem(this.sessionStorageKey);
        sessionStorage.removeItem(`${this.sessionStorageKey}_tab`);
        localStorage.removeItem(`${this.sessionStorageKey}_export`);
    }

    /**
     * Session Recovery
     */
    async attemptSessionRecovery() {
        if (!this.sessionState.sessionId || !this.sessionState.isActive) {
            return false;
        }

        try {
            // Check if server session still exists
            const response = await fetch(`/tools/api/studio/${this.datasourceId}/session/status/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();
            
            if (data.success && data.session_info.session_exists) {
                // Session exists on server, restore UI state
                this.showRecoveryNotification('Session recovered successfully', 'success');
                this.updateSessionState(data.session_info);
                return true;
            } else {
                // Server session expired, offer recovery options
                this.showRecoveryDialog();
                return false;
            }
        } catch (error) {
            console.error('Session recovery failed:', error);
            this.showRecoveryNotification('Session recovery failed', 'error');
            return false;
        }
    }

    showRecoveryDialog() {
        const dialog = document.createElement('div');
        dialog.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        dialog.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md mx-4">
                <div class="flex items-center mb-4">
                    <svg class="w-6 h-6 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Session Recovery</h3>
                </div>
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                    Your previous session has expired. Would you like to restore from saved data or start fresh?
                </p>
                <div class="flex justify-end space-x-3">
                    <button onclick="this.closest('.fixed').remove()" 
                            class="px-4 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200">
                        Start Fresh
                    </button>
                    <button onclick="window.dataStudioSessionManager?.restoreFromExport(); this.closest('.fixed').remove()" 
                            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded">
                        Restore Data
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
    }

    /**
     * Auto-Save and Timeout Management
     */
    setupAutoSave() {
        this.autoSaveTimer = setInterval(() => {
            if (this.sessionState.isActive && this.sessionState.hasUnsavedChanges) {
                this.saveSessionToStorage();
                this.sessionState.hasUnsavedChanges = false;
                this.updateUISessionStatus();
            }
        }, this.autoSaveInterval);
    }

    setupActivityTracking() {
        const updateActivity = () => {
            this.lastActivityTime = Date.now();
            this.resetSessionTimeout();
        };

        // Track various user activities
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
            document.addEventListener(event, updateActivity, true);
        });
    }

    resetSessionTimeout() {
        // Clear existing timers
        if (this.timeoutWarningTimer) clearTimeout(this.timeoutWarningTimer);
        if (this.timeoutTimer) clearTimeout(this.timeoutTimer);

        if (!this.sessionState.isActive) return;

        // Set warning timer (5 minutes before timeout)
        this.timeoutWarningTimer = setTimeout(() => {
            this.showTimeoutWarning();
        }, this.sessionTimeout - 5 * 60 * 1000);

        // Set actual timeout timer
        this.timeoutTimer = setTimeout(() => {
            this.handleSessionTimeout();
        }, this.sessionTimeout);
    }

    showTimeoutWarning() {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded shadow-lg z-50 max-w-sm';
        notification.innerHTML = `
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm">
                        Your session will expire in 5 minutes due to inactivity.
                    </p>
                    <div class="mt-2">
                        <button onclick="window.dataStudioSessionManager?.extendSession(); this.closest('.fixed').remove();" 
                                class="text-xs bg-yellow-600 hover:bg-yellow-700 text-white px-2 py-1 rounded">
                            Extend Session
                        </button>
                    </div>
                </div>
                <button onclick="this.remove()" class="ml-auto pl-3">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
        `;
        document.body.appendChild(notification);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }

    async extendSession() {
        this.lastActivityTime = Date.now();
        this.resetSessionTimeout();
        this.showRecoveryNotification('Session extended', 'success');
    }

    async handleSessionTimeout() {
        if (this.sessionState.hasUnsavedChanges) {
            // Save current state before timeout
            this.saveSessionToStorage();
            this.exportSession();
        }

        // Clear session state
        this.sessionState.isActive = false;
        this.updateUISessionStatus();
        
        this.showRecoveryNotification('Session expired due to inactivity. Data has been saved locally.', 'warning');
    }

    /**
     * Session Export/Import
     */
    exportSession() {
        try {
            const exportData = {
                datasourceId: this.datasourceId,
                sessionState: this.sessionState,
                filterState: window.dataStudioApp?.filterState || {},
                paginationState: window.dataStudioApp?.pagination || {},
                navigationState: window.dataStudioApp?.navigationState || {},
                timestamp: Date.now(),
                version: '1.0.0'
            };

            const exportKey = `${this.sessionStorageKey}_export`;
            localStorage.setItem(exportKey, JSON.stringify(exportData));
            
            // Also create downloadable export
            const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                type: 'application/json'
            });
            const url = URL.createObjectURL(blob);
            
            // Store the URL for manual download if needed
            this.lastExportUrl = url;
            
            console.log('Session exported successfully');
            return exportData;
        } catch (error) {
            console.error('Failed to export session:', error);
            return null;
        }
    }

    async restoreFromExport() {
        try {
            const exportKey = `${this.sessionStorageKey}_export`;
            const stored = localStorage.getItem(exportKey);
            
            if (!stored) {
                this.showRecoveryNotification('No export data found', 'warning');
                return false;
            }

            const exportData = JSON.parse(stored);
            
            // Validate export data
            if (exportData.datasourceId !== this.datasourceId) {
                this.showRecoveryNotification('Export data is for a different dataset', 'error');
                return false;
            }

            // Restore session state
            this.sessionState = { ...this.sessionState, ...exportData.sessionState };
            
            // Restore other states if available
            if (window.dataStudioApp) {
                if (exportData.filterState) {
                    window.dataStudioApp.filterState = { ...window.dataStudioApp.filterState, ...exportData.filterState };
                }
                if (exportData.paginationState) {
                    window.dataStudioApp.pagination = { ...window.dataStudioApp.pagination, ...exportData.paginationState };
                }
                if (exportData.navigationState) {
                    window.dataStudioApp.navigationState = { ...window.dataStudioApp.navigationState, ...exportData.navigationState };
                }
            }

            this.updateUISessionStatus();
            this.showRecoveryNotification('Session restored from export data', 'success');
            
            return true;
        } catch (error) {
            console.error('Failed to restore from export:', error);
            this.showRecoveryNotification('Failed to restore session data', 'error');
            return false;
        }
    }

    downloadSessionExport() {
        if (this.lastExportUrl) {
            const link = document.createElement('a');
            link.href = this.lastExportUrl;
            link.download = `hydroml_session_${this.datasourceId}_${new Date().toISOString().slice(0, 10)}.json`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            // Create fresh export
            const exportData = this.exportSession();
            if (exportData) {
                const blob = new Blob([JSON.stringify(exportData, null, 2)], {
                    type: 'application/json'
                });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `hydroml_session_${this.datasourceId}_${new Date().toISOString().slice(0, 10)}.json`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
            }
        }
    }

    /**
     * Visibility and Page Unload Handling
     */
    setupVisibilityHandling() {
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Page hidden, save current state
                if (this.sessionState.isActive) {
                    this.saveSessionToStorage();
                }
            } else {
                // Page visible again, check if session is still valid
                if (this.sessionState.isActive) {
                    this.lastActivityTime = Date.now();
                    this.resetSessionTimeout();
                }
            }
        });
    }

    setupBeforeUnloadProtection() {
        window.addEventListener('beforeunload', (event) => {
            if (this.sessionState.isActive && this.sessionState.hasUnsavedChanges) {
                // Save session before unload
                this.saveSessionToStorage();
                this.exportSession();
                
                // Show warning for unsaved changes
                const message = 'You have unsaved changes. Are you sure you want to leave?';
                event.preventDefault();
                event.returnValue = message;
                return message;
            }
        });
    }

    /**
     * UI Integration Methods
     */
    updateSessionState(sessionInfo) {
        this.sessionState.isActive = sessionInfo.session_exists || false;
        this.sessionState.sessionId = sessionInfo.session_id || null;
        this.sessionState.operations = sessionInfo.operations || [];
        this.sessionState.currentPosition = sessionInfo.current_position || 0;
        this.sessionState.metadata = sessionInfo.metadata || {};
        this.sessionState.hasUnsavedChanges = true;
        
        this.saveSessionToStorage();
        this.updateUISessionStatus();
        
        if (this.sessionState.isActive) {
            this.resetSessionTimeout();
        }
    }

    updateUISessionStatus() {
        // Update main app session status if available
        if (window.dataStudioApp && typeof window.dataStudioApp.updateSessionStatus === 'function') {
            window.dataStudioApp.updateSessionStatus({
                session_exists: this.sessionState.isActive,
                ...this.sessionState.metadata
            });
        }

        // Update session manager UI elements
        this.updateSessionManagerUI();
    }

    updateSessionManagerUI() {
        // Update auto-save indicator
        const autoSaveIndicator = document.getElementById('session-autosave-indicator');
        if (autoSaveIndicator) {
            if (this.sessionState.hasUnsavedChanges) {
                autoSaveIndicator.className = 'w-2 h-2 bg-yellow-500 rounded-full animate-pulse';
                autoSaveIndicator.title = 'Unsaved changes';
            } else {
                autoSaveIndicator.className = 'w-2 h-2 bg-green-500 rounded-full';
                autoSaveIndicator.title = 'All changes saved';
            }
        }

        // Update last saved time
        const lastSavedElement = document.getElementById('session-last-saved');
        if (lastSavedElement && this.sessionState.lastSaved) {
            const lastSaved = new Date(this.sessionState.lastSaved);
            lastSavedElement.textContent = `Last saved: ${lastSaved.toLocaleTimeString()}`;
        }
    }

    /**
     * Utility Methods
     */
    generateTabId() {
        return Math.random().toString(36).substring(2, 15);
    }

    getCSRFToken() {
        const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return tokenElement ? tokenElement.value : '';
    }

    showRecoveryNotification(message, type = 'info') {
        const notification = document.createElement('div');
        const colors = {
            success: 'bg-green-100 border-green-500 text-green-700',
            error: 'bg-red-100 border-red-500 text-red-700',
            warning: 'bg-yellow-100 border-yellow-500 text-yellow-700',
            info: 'bg-blue-100 border-blue-500 text-blue-700'
        };
        
        notification.className = `fixed top-4 right-4 ${colors[type]} border-l-4 p-4 rounded shadow-lg z-50 max-w-sm`;
        notification.innerHTML = `
            <div class="flex items-center">
                <div class="flex-1">
                    <p class="text-sm">${message}</p>
                </div>
                <button onclick="this.closest('.fixed').remove()" class="ml-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    /**
     * Public API Methods
     */
    markUnsavedChanges() {
        this.sessionState.hasUnsavedChanges = true;
        this.updateUISessionStatus();
    }

    markChangesSaved() {
        this.sessionState.hasUnsavedChanges = false;
        this.sessionState.lastSaved = Date.now();
        this.updateUISessionStatus();
    }

    getSessionState() {
        return { ...this.sessionState };
    }

    destroy() {
        // Clean up timers and event listeners
        if (this.autoSaveTimer) clearInterval(this.autoSaveTimer);
        if (this.timeoutWarningTimer) clearTimeout(this.timeoutWarningTimer);
        if (this.timeoutTimer) clearTimeout(this.timeoutTimer);
        
        // Save final state
        if (this.sessionState.isActive) {
            this.saveSessionToStorage();
        }
    }
}

// Make SessionManager globally available
window.DataStudioSessionManager = DataStudioSessionManager;