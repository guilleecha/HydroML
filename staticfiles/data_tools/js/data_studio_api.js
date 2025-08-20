/**
 * Data Studio API Operations - Backend Integration
 * Handles all API calls to backend services
 */

class DataStudioAPI {
    
    constructor(datasourceId) {
        this.datasourceId = datasourceId;
    }

    /**
     * Get CSRF Token for API requests
     */
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }

    /**
     * Check session status
     */
    async checkSessionStatus() {
        if (!this.datasourceId) return { session_exists: false };
        
        try {
            const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/status/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                }
            });

            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.log('Session status check failed:', error);
        }
        
        return { session_exists: false };
    }

    /**
     * Initialize session
     */
    async initializeSession() {
        if (!this.datasourceId) {
            throw new Error('No datasource available');
        }

        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/initialize/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            }
        });

        return await response.json();
    }

    /**
     * Stop/clear session
     */
    async stopSession() {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/clear/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            }
        });

        return await response.json();
    }

    /**
     * Undo operation
     */
    async undoOperation() {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/undo/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
            }
        });

        return await response.json();
    }

    /**
     * Redo operation
     */
    async redoOperation() {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/redo/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
            }
        });

        return await response.json();
    }

    /**
     * Save session as new dataset
     */
    async saveSession(name, description) {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({
                'name': name || `${window.datasourceName || 'Dataset'}_modified`,
                'description': description || 'Modified dataset from Data Studio'
            })
        });

        return await response.json();
    }

    /**
     * Run NaN analysis
     */
    async runNaNAnalysis() {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/nan/analysis/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            }
        });

        return await response.json();
    }

    /**
     * Perform NaN cleaning
     */
    async performNaNCleaning(removeRows, removeColumns) {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/nan/quick-clean/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({
                'remove_nan_rows': removeRows,
                'remove_nan_columns': removeColumns
            })
        });

        return await response.json();
    }

    /**
     * Delete selected columns
     */
    async deleteColumns(columns) {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/transform/columns/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({
                'operation': 'drop',
                'columns': columns
            })
        });

        return await response.json();
    }
}

// Export for use in other modules
window.DataStudioAPI = DataStudioAPI;