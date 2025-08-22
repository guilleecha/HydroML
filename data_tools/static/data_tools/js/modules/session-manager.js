/**
 * SessionManager - Data Studio Session Management
 * Responsabilidad única: Gestión del estado y operaciones de sesiones
 * 
 * Filosofía: Simple, enfocado, sin mixed concerns
 */

class SessionManager {
    constructor(datasourceId) {
        this.datasourceId = datasourceId;
        this.sessionInfo = null;
        this.isActive = false;
        this.eventTarget = new EventTarget();
    }

    // === CORE SESSION OPERATIONS ===

    async initialize() {
        try {
            const data = await APIClient.post(`/tools/api/studio/${this.datasourceId}/session/initialize/`);
            
            if (data.success) {
                this.updateState(data.session_info);
                this.dispatchEvent('session-initialized', {
                    sessionInfo: data.session_info,
                    dataPreview: data.data_preview,
                    columnInfo: data.column_info
                });
                return { success: true, data };
            } else {
                throw new Error(data.error || 'Failed to initialize session');
            }
        } catch (error) {
            console.error('Failed to initialize session:', error);
            throw error;
        }
    }

    async checkStatus() {
        try {
            const data = await APIClient.get(`/tools/api/studio/${this.datasourceId}/session/status/`);
            
            if (data.success && data.session_info.session_exists) {
                this.updateState(data.session_info);
                this.dispatchEvent('session-status-updated', {
                    sessionInfo: data.session_info,
                    dataPreview: data.data_preview,
                    columnInfo: data.column_info
                });
            }
            return data;
        } catch (error) {
            console.error('Failed to check session status:', error);
            return { success: false, error: error.message };
        }
    }

    async undo() {
        return this.executeOperation('undo', 'session-operation-undone');
    }

    async redo() {
        return this.executeOperation('redo', 'session-operation-redone');
    }

    async save(name, description) {
        try {
            const data = await APIClient.post(`/tools/api/studio/${this.datasourceId}/session/save/`, {
                name: name,
                description: description
            });
            
            if (data.success) {
                this.updateState({ session_exists: false });
                this.dispatchEvent('session-saved', {
                    newDatasource: data.new_datasource
                });
                return { success: true, data };
            } else {
                throw new Error(data.error || 'Failed to save session');
            }
        } catch (error) {
            console.error('Failed to save session:', error);
            throw error;
        }
    }

    // === PRIVATE METHODS ===

    async executeOperation(operation, eventName) {
        try {
            const data = await APIClient.post(`/tools/api/studio/${this.datasourceId}/session/${operation}/`);
            
            if (data.success) {
                this.updateState(data.session_info);
                this.dispatchEvent(eventName, {
                    sessionInfo: data.session_info,
                    dataPreview: data.data_preview,
                    columnInfo: data.column_info
                });
                return { success: true, data };
            } else {
                throw new Error(data.error || `Failed to ${operation} operation`);
            }
        } catch (error) {
            console.error(`Failed to ${operation} operation:`, error);
            throw error;
        }
    }

    updateState(sessionInfo) {
        this.sessionInfo = sessionInfo;
        this.isActive = sessionInfo.session_exists;
        this.dispatchEvent('session-state-changed', { sessionInfo });
    }

    dispatchEvent(eventName, detail) {
        this.eventTarget.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    addEventListener(eventName, handler) {
        this.eventTarget.addEventListener(eventName, handler);
    }

    removeEventListener(eventName, handler) {
        this.eventTarget.removeEventListener(eventName, handler);
    }


    // === GETTERS ===

    get canUndo() {
        return this.isActive && this.sessionInfo?.current_position > 0;
    }

    get canRedo() {
        return this.isActive && this.sessionInfo?.current_position < this.sessionInfo?.history_length;
    }

    get stats() {
        if (!this.sessionInfo) return null;
        
        return {
            historyLength: this.sessionInfo.history_length || 0,
            currentPosition: this.sessionInfo.current_position || 0,
            currentShape: this.sessionInfo.current_shape || [0, 0]
        };
    }
}

// Export for use in other modules
window.SessionManager = SessionManager;

// Export removed for script tag compatibility