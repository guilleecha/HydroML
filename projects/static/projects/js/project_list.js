/**
 * Project List Page JavaScript
 * Handles project deletion and management functionality
 * Part of HydroML Projects module
 */

class ProjectListPage {
    constructor() {
        this.csrfToken = null;
        this.init();
    }

    init() {
        this.initializeCSRF();
        this.bindEvents();
    }

    initializeCSRF() {
        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfTokenElement) {
            this.csrfToken = csrfTokenElement.value;
        } else {
            console.warn('CSRF token not found');
        }
    }

    bindEvents() {
        // Bind confirm delete events
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('delete-project-btn')) {
                event.preventDefault();
                const projectId = event.target.dataset.projectId;
                const projectName = event.target.dataset.projectName;
                this.confirmDeleteProject(projectId, projectName);
            }
        });
    }

    /**
     * Confirm project deletion with user
     * @param {string} projectId - Project ID to delete
     * @param {string} projectName - Project name for confirmation
     */
    confirmDeleteProject(projectId, projectName) {
        const message = `¿Estás seguro de que quieres eliminar el workspace "${projectName}"?\n\nEsta acción no se puede deshacer y eliminará todos los datos asociados.`;
        
        if (confirm(message)) {
            this.deleteProject(projectId);
        }
    }

    /**
     * Delete project via API
     * @param {string} projectId - Project ID to delete
     */
    async deleteProject(projectId) {
        try {
            const response = await fetch(`/projects/${projectId}/delete/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                },
            });
            
            if (response.ok) {
                // Show success message and reload
                this.showSuccessMessage('Workspace eliminado exitosamente');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.error || 'Error al eliminar el workspace. Por favor, intenta de nuevo.';
                this.showErrorMessage(errorMessage);
            }
        } catch (error) {
            console.error('Error deleting project:', error);
            this.showErrorMessage('Error de conexión. Por favor, intenta de nuevo.');
        }
    }

    /**
     * Show success message to user
     * @param {string} message - Success message
     */
    showSuccessMessage(message) {
        // Check if Grove toast system is available
        if (typeof window.GroveToast !== 'undefined') {
            window.GroveToast.success(message);
            return;
        }
        
        // Check if Alpine.js toast store is available
        if (typeof Alpine !== 'undefined' && window.Alpine?.store?.('toasts')) {
            try {
                window.Alpine.store('toasts').add({
                    type: 'success',
                    message: message,
                    duration: 3000
                });
                return;
            } catch (e) {
                console.warn('Alpine toast store not properly configured');
            }
        }
        
        // Fallback to alert
        alert(message);
    }

    /**
     * Show error message to user
     * @param {string} message - Error message
     */
    showErrorMessage(message) {
        // Check if Grove toast system is available
        if (typeof window.GroveToast !== 'undefined') {
            window.GroveToast.error(message);
            return;
        }
        
        // Check if Alpine.js toast store is available
        if (typeof Alpine !== 'undefined' && window.Alpine?.store?.('toasts')) {
            try {
                window.Alpine.store('toasts').add({
                    type: 'error',
                    message: message,
                    duration: 5000
                });
                return;
            } catch (e) {
                console.warn('Alpine toast store not properly configured');
            }
        }
        
        // Fallback to alert
        alert(message);
    }

    /**
     * Open new project panel (if available)
     */
    openNewProjectPanel() {
        // Delegate to Alpine.js or other system if available
        if (typeof Alpine !== 'undefined' && window.Alpine && window.Alpine.store) {
            // Try to trigger Alpine store method
            try {
                window.Alpine.store('app').openNewProjectPanel();
                return;
            } catch (e) {
                console.warn('Alpine store method not available');
            }
        }
        
        // Fallback: redirect to create page
        window.location.href = '/projects/create/';
    }

    /**
     * Refresh the project list
     */
    refreshProjectList() {
        window.location.reload();
    }
}

// Global functions for backward compatibility
window.confirmDeleteProject = function(projectId, projectName) {
    if (window.projectListPage) {
        window.projectListPage.confirmDeleteProject(projectId, projectName);
    }
};

window.deleteProject = function(projectId) {
    if (window.projectListPage) {
        window.projectListPage.deleteProject(projectId);
    }
};

// Auto-initialization when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const pageController = new ProjectListPage();
    
    // Make controller globally available
    window.projectListPage = pageController;
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProjectListPage;
}

// Global registration
if (typeof window !== 'undefined') {
    window.ProjectListPage = ProjectListPage;
}