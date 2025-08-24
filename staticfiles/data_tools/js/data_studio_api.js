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
            method: 'GET',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
            }
        });

        return await response.json();
    }

    /**
     * Perform NaN cleaning
     */
    async performNaNCleaning(removeRows, removeColumns) {
        const formData = new FormData();
        formData.append('remove_nan_rows', removeRows ? 'true' : 'false');
        formData.append('remove_nan_columns', removeColumns ? 'true' : 'false');

        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/nan/quick-clean/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: formData
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

    /**
     * Get comprehensive column statistics for current session
     */
    async getColumnStatistics() {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/column-statistics/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
            }
        });

        return await response.json();
    }

    /**
     * Rename a column
     */
    async renameColumn(oldName, newName) {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/rename-column/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({
                'old_name': oldName,
                'new_name': newName
            })
        });

        return await response.json();
    }

    /**
     * Change column data type
     */
    async changeColumnType(columnName, newType) {
        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/change-column-type/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify({
                'column_name': columnName,
                'new_type': newType
            })
        });

        return await response.json();
    }

    /**
     * Fill missing values using various strategies
     */
    async fillMissingValues(columns, strategy, fillValue = null) {
        const payload = {
            'columns': columns,
            'strategy': strategy
        };

        if (fillValue !== null) {
            payload['fill_value'] = fillValue;
        }

        const response = await fetch(`/data-tools/api/studio/${this.datasourceId}/session/fill-missing-values/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: JSON.stringify(payload)
        });

        return await response.json();
    }
}

// Export for use in other modules
window.DataStudioAPI = DataStudioAPI;