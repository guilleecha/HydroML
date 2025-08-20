/**
 * HydroML Main Application JavaScript
 * Loads modular Alpine.js components for better maintainability
 */

// Import modular Alpine.js components
// Note: These are loaded via script tags in the template for now
// In the future, we can implement proper ES6 modules

// The actual Alpine.js components are now in:
// - app-store.js: Global app store and state management
// - workspace-selector.js: Workspace/project selection
// - datasource-workspace-selector.js: Multiple workspace selection

// Wait for Alpine.js to load before initializing any remaining components
document.addEventListener('alpine:init', () => {
    
    // Large datasourceUploadForm component - TODO: Further modularize this
    Alpine.data('datasourceUploadForm', (projectId = '') => ({
        // State management
        submitting: false,
        showSuccess: false,
        showError: false,
        errorMessage: '',
        quickProjectMode: false,
        selectedProjectId: projectId,

        // Quick project selection
        setQuickProject(projectId) {
            this.quickProjectMode = true;
            this.selectedProjectId = projectId;
            this.updateProjectSelection(projectId);
            this.showQuickProjectFeedback();
        },

        updateProjectSelection(projectId) {
            const projectField = document.querySelector('select[name=project], input[name=project]');
            if (projectField) {
                projectField.value = projectId;
            }
            
            if (this.$refs.workspaceSelector) {
                this.$refs.workspaceSelector.selectProject(projectId);
            }
        },

        showQuickProjectFeedback() {
            const feedback = this.$el.querySelector('.quick-project-feedback');
            if (feedback) {
                feedback.classList.remove('hidden');
                setTimeout(() => {
                    feedback.classList.add('hidden');
                }, 2000);
            }
        },

        // Form submission
        async submitForm() {
            if (this.submitting) return;
            
            this.submitting = true;
            this.showError = false;
            this.showSuccess = false;

            try {
                const result = await this.performSubmission();
                this.handleSubmissionSuccess(result);
            } catch (error) {
                this.handleSubmissionError(error);
            } finally {
                this.submitting = false;
            }
        },

        async performSubmission() {
            const form = this.$refs.uploadForm;
            const formData = new FormData(form);
            
            // Add quick project if selected
            if (this.quickProjectMode && this.selectedProjectId) {
                formData.set('project', this.selectedProjectId);
            }

            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        },

        handleSubmissionSuccess(result) {
            if (result.success) {
                this.showSuccess = true;
                this.refreshDataSources();
                this.resetForm();
            } else {
                throw new Error(result.error || 'Unknown error occurred');
            }
        },

        handleSubmissionError(error) {
            this.showError = true;
            this.errorMessage = error.message || 'An unexpected error occurred';
            this.scrollToError();
        },

        // Utility methods
        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                   document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        },

        refreshDataSources() {
            if (window.Alpine?.store?.('app')?.refreshDataSourceLists) {
                window.Alpine.store('app').refreshDataSourceLists();
            }
        },

        resetForm() {
            if (this.$refs.uploadForm) {
                this.$refs.uploadForm.reset();
            }
            this.quickProjectMode = false;
            this.selectedProjectId = '';
        },

        scrollToError() {
            setTimeout(() => {
                const errorElement = this.$el.querySelector('.error-message, .alert-error');
                if (errorElement) {
                    errorElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'center'
                    });
                }
            }, 100);
        }
    }));

});

// Global utility functions (if needed)
window.HydroMLApp = {
    version: '2.0.0',
    initialized: true
};