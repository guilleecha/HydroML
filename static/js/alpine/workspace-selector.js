/**
 * Alpine.js Workspace Selector Component
 * Handles workspace/project selection in forms
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('workspaceSelector', () => ({
        availableWorkspaces: [],
        selectedProjectId: '',
        
        init() {
            // Will be populated by initializeWorkspaceSelector()
        },
        
        selectProject(projectId) {
            this.selectedProjectId = projectId;
            // Update the hidden select field
            const hiddenSelect = document.getElementById('id_project');
            if (hiddenSelect) {
                hiddenSelect.value = projectId;
            }
        },
        
        getProjectName(projectId) {
            const project = this.availableWorkspaces.find(w => w.id === projectId);
            return project ? project.name : '';
        }
    }));
});