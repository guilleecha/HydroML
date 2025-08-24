/**
 * Session Manager - Handles session lifecycle and state management
 * Manages session initialization, status, undo/redo operations, and cleanup
 */

class SessionManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.sessionActive = false;
        this.operationsCount = 0;
        this.canUndo = false;
        this.canRedo = false;
        this.stateChangeCallbacks = [];
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Transport controls
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-action="undo"]')) {
                e.preventDefault();
                this.undoOperation();
            }
            if (e.target.closest('[data-action="redo"]')) {
                e.preventDefault();
                this.redoOperation();
            }
            if (e.target.closest('[data-action="clear-session"]')) {
                e.preventDefault();
                this.stopSession();
            }
            if (e.target.closest('[data-action="save-session"]')) {
                e.preventDefault();
                this.saveSession();
            }
        });
    }

    onSessionStateChange(callback) {
        this.stateChangeCallbacks.push(callback);
    }

    notifyStateChange(active) {
        this.sessionActive = active;
        this.stateChangeCallbacks.forEach(callback => callback(active));
    }

    async initializeSession() {
        try {
            DataStudioUIUtils.showNotification('Initializing session...', 'info');
            
            const data = await this.api.initializeSession();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Session initialized successfully', 'success');
                this.notifyStateChange(true);
                this.updateSessionUI(true, data);
                this.refreshGrid();
            } else {
                DataStudioUIUtils.showNotification(`Failed to initialize: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Session error: ${error.message}`, 'error');
        }
    }

    async stopSession() {
        if (!this.api.datasourceId || !this.sessionActive) return;

        try {
            const data = await this.api.stopSession();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Session stopped', 'success');
                this.notifyStateChange(false);
                this.updateSessionUI(false);
            } else {
                DataStudioUIUtils.showNotification(`Failed to stop session: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Error stopping session: ${error.message}`, 'error');
        }
    }

    async undoOperation() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('No active session', 'warning');
            return;
        }

        try {
            const data = await this.api.undoOperation();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Operation undone', 'success');
                this.updateSessionUI(true, data);
                this.refreshGrid();
            } else {
                DataStudioUIUtils.showNotification(`Undo failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Undo error: ${error.message}`, 'error');
        }
    }

    async redoOperation() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('No active session', 'warning');
            return;
        }

        try {
            const data = await this.api.redoOperation();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Operation redone', 'success');
                this.updateSessionUI(true, data);
                this.refreshGrid();
            } else {
                DataStudioUIUtils.showNotification(`Redo failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Redo error: ${error.message}`, 'error');
        }
    }

    async saveSession() {
        if (!this.sessionActive) {
            DataStudioUIUtils.showNotification('No active session to save', 'warning');
            return;
        }

        try {
            DataStudioUIUtils.showNotification('Saving dataset...', 'info');
            
            const data = await this.api.saveSession();
            
            if (data.success) {
                DataStudioUIUtils.showNotification('Dataset saved successfully', 'success');
            } else {
                DataStudioUIUtils.showNotification(`Save failed: ${data.error}`, 'error');
            }
        } catch (error) {
            DataStudioUIUtils.showNotification(`Save error: ${error.message}`, 'error');
        }
    }

    updateSessionUI(sessionExists, sessionData = {}) {
        const statusContainer = document.querySelector('.grove-session-status');
        const recDot = document.querySelector('.grove-rec-dot');
        const recLabel = document.querySelector('.grove-rec-label');
        const statusText = document.querySelector('.grove-session-status-text');
        const counter = document.querySelector('.grove-session-counter');
        const undoBtn = document.querySelector('[data-action="undo"]');
        const redoBtn = document.querySelector('[data-action="redo"]');
        const stopBtn = document.querySelector('[data-action="clear-session"]');
        
        this.sessionActive = sessionExists;
        
        if (sessionExists) {
            // Update recording indicator
            if (recDot) {
                recDot.className = 'grove-rec-dot grove-rec-dot--active';
            }
            if (recLabel) {
                recLabel.textContent = 'REC';
            }
            if (statusText) {
                statusText.textContent = 'Active';
            }
            if (statusContainer) {
                statusContainer.classList.remove('grove-session-status--inactive');
                statusContainer.classList.add('grove-session-status--active');
            }
            
            // Update operations counter
            if (counter) {
                const opCount = sessionData.operations_count || this.operationsCount || 0;
                counter.textContent = `${opCount} ops`;
                counter.setAttribute('data-operations-count', opCount);
            }
            
            // Enable/disable transport controls
            if (undoBtn) {
                undoBtn.disabled = !(sessionData.can_undo || this.canUndo);
            }
            if (redoBtn) {
                redoBtn.disabled = !(sessionData.can_redo || this.canRedo);
            }
            if (stopBtn) {
                stopBtn.disabled = false;
            }
        } else {
            // Update to inactive state
            if (recDot) {
                recDot.className = 'grove-rec-dot grove-rec-dot--inactive';
            }
            if (recLabel) {
                recLabel.textContent = 'REC';
            }
            if (statusText) {
                statusText.textContent = '';
            }
            if (statusContainer) {
                statusContainer.classList.add('grove-session-status--inactive');
                statusContainer.classList.remove('grove-session-status--active');
            }
            
            // Reset counter
            if (counter) {
                counter.textContent = '0 ops';
                counter.setAttribute('data-operations-count', '0');
            }
            
            // Disable transport controls
            if (undoBtn) undoBtn.disabled = true;
            if (redoBtn) redoBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = true;
        }
    }

    refreshGrid() {
        if (window.gridManager && window.gridManager.refreshData) {
            window.gridManager.refreshData();
        }
    }
}

// Export for use in other modules
window.SessionManager = SessionManager;