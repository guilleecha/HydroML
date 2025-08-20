/**
 * Alpine.js DataSource Workspace Selector Component
 * Handles multiple workspace selection for datasource uploads
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('datasourceWorkspaceSelector', () => ({
        selectedWorkspaces: [],
        availableWorkspaces: [],
        showWarning: false,
        
        init(currentProjectId, workspaces) {
            this.availableWorkspaces = workspaces;
            if (currentProjectId) {
                this.selectedWorkspaces = [currentProjectId];
            }
            this.updateFormInputs();
        },
        
        addWorkspace(workspaceId) {
            if (workspaceId && !this.selectedWorkspaces.includes(workspaceId)) {
                this.selectedWorkspaces.push(workspaceId);
                this.updateFormInputs();
            }
        },
        
        removeWorkspace(workspaceId) {
            this.selectedWorkspaces = this.selectedWorkspaces.filter(id => id !== workspaceId);
            this.updateFormInputs();
        },
        
        clearAll() {
            if (this.selectedWorkspaces.length > 0) {
                this.showWarning = true;
            } else {
                this.selectedWorkspaces = [];
                this.updateFormInputs();
            }
        },
        
        confirmClearAll() {
            this.selectedWorkspaces = [];
            this.showWarning = false;
            this.updateFormInputs();
        },
        
        cancelClearAll() {
            this.showWarning = false;
        },
        
        updateFormInputs() {
            // Remove existing hidden inputs
            const existingInputs = document.querySelectorAll('input[name="projects"][type="hidden"]');
            existingInputs.forEach(input => input.remove());
            
            // Add new hidden inputs for selected workspaces
            const form = document.querySelector('form');
            this.selectedWorkspaces.forEach(workspaceId => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'projects';
                input.value = workspaceId;
                form.appendChild(input);
            });
        },
        
        getWorkspaceName(workspaceId) {
            const workspace = this.availableWorkspaces.find(w => w.id === workspaceId);
            return workspace ? workspace.name : '';
        },
        
        getAvailableWorkspaces() {
            return this.availableWorkspaces.filter(w => !this.selectedWorkspaces.includes(w.id));
        }
    }));
});