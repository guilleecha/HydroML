/**
 * SessionUIController - Session User Interface Management  
 * Responsabilidad única: Actualización de la UI basada en el estado de sesión
 * 
 * Filosofía: Separar lógica de negocio de manipulación DOM
 */

class SessionUIController {
    constructor() {
        this.elements = this.initializeElements();
    }

    initializeElements() {
        return {
            statusIndicator: document.getElementById('session-status-indicator'),
            statusText: document.getElementById('session-status-text'),
            sessionInfoPanel: document.getElementById('session-info'),
            historyInfo: document.getElementById('history-info'),
            positionInfo: document.getElementById('position-info'),
            rowsInfo: document.getElementById('rows-info'),
            columnsInfo: document.getElementById('columns-info'),
            initializeBtn: document.getElementById('initialize-session-btn'),
            undoBtn: document.getElementById('undo-btn'),
            redoBtn: document.getElementById('redo-btn'),
            saveBtn: document.getElementById('save-session-btn')
        };
    }

    updateSessionStatus(sessionInfo) {
        if (!sessionInfo) return;

        const isActive = sessionInfo.session_exists;
        
        if (isActive) {
            this.showActiveSession(sessionInfo);
        } else {
            this.showInactiveSession();
        }
    }

    showActiveSession(sessionInfo) {
        // Update status indicator
        if (this.elements.statusIndicator) {
            this.elements.statusIndicator.className = 'w-3 h-3 rounded-full bg-green-400';
        }
        if (this.elements.statusText) {
            this.elements.statusText.textContent = 'Active session';
        }
        if (this.elements.sessionInfoPanel) {
            this.elements.sessionInfoPanel.classList.remove('hidden');
        }

        // Update session info details
        this.updateSessionDetails(sessionInfo);
        
        // Update button states
        this.updateButtonStates(sessionInfo);
    }

    showInactiveSession() {
        // Update status indicator  
        if (this.elements.statusIndicator) {
            this.elements.statusIndicator.className = 'w-3 h-3 rounded-full bg-gray-400';
        }
        if (this.elements.statusText) {
            this.elements.statusText.textContent = 'No session';
        }
        if (this.elements.sessionInfoPanel) {
            this.elements.sessionInfoPanel.classList.add('hidden');
        }

        // Reset button states
        this.resetButtonStates();
    }

    updateSessionDetails(sessionInfo) {
        if (this.elements.historyInfo) {
            this.elements.historyInfo.textContent = `${sessionInfo.history_length || 0} operations`;
        }
        if (this.elements.positionInfo) {
            this.elements.positionInfo.textContent = `${sessionInfo.current_position || 0}/${sessionInfo.history_length || 0}`;
        }
        if (this.elements.rowsInfo && sessionInfo.current_shape) {
            this.elements.rowsInfo.textContent = sessionInfo.current_shape[0] || '0';
        }
        if (this.elements.columnsInfo && sessionInfo.current_shape) {
            this.elements.columnsInfo.textContent = sessionInfo.current_shape[1] || '0';
        }
    }

    updateButtonStates(sessionInfo) {
        if (this.elements.initializeBtn) {
            this.elements.initializeBtn.style.display = 'none';
        }
        if (this.elements.undoBtn) {
            this.elements.undoBtn.disabled = (sessionInfo.current_position || 0) === 0;
        }
        if (this.elements.redoBtn) {
            this.elements.redoBtn.disabled = (sessionInfo.current_position || 0) === (sessionInfo.history_length || 0);
        }
        if (this.elements.saveBtn) {
            this.elements.saveBtn.disabled = false;
        }
    }

    resetButtonStates() {
        if (this.elements.initializeBtn) {
            this.elements.initializeBtn.style.display = 'flex';
        }
        if (this.elements.undoBtn) {
            this.elements.undoBtn.disabled = true;
        }
        if (this.elements.redoBtn) {
            this.elements.redoBtn.disabled = true;
        }
        if (this.elements.saveBtn) {
            this.elements.saveBtn.disabled = true;
        }
    }

    showNotification(message, type = 'info') {
        // Simple notification - can be enhanced with a proper notification system
        if (type === 'error') {
            console.error('Session Error:', message);
            alert('Error: ' + message);
        } else if (type === 'success') {
            console.log('Session Success:', message);
            alert(message);
        } else {
            console.info('Session Info:', message);
        }
    }
}

// Export for use in other modules
window.SessionUIController = SessionUIController;

// Export removed for script tag compatibility