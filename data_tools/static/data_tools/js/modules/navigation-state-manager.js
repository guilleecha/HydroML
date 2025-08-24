/**
 * NavigationStateManager - Navigation State Management
 * Responsabilidad única: Gestión centralizada del estado de navegación
 * 
 * Filosofía: Single source of truth for navigation state, no UI concerns
 */

class NavigationStateManager {
    constructor() {
        // Navigation state
        this.navigationState = {
            currentSection: 'overview',
            activeTab: null,
            breadcrumbPath: [],
            workflowStep: 0,
            totalSteps: 0,
            sidebarSections: ['overview', 'transformation', 'advanced-filters', 'visualization', 'export']
        };

        // Section display names mapping
        this.sectionNames = {
            'overview': 'Overview',
            'transformation': 'Data Transformation',
            'advanced-filters': 'Advanced Filters',
            'visualization': 'Visualization',
            'export': 'Export & Share'
        };

        // Event system
        this.eventTarget = new EventTarget();
    }

    // === SECTION MANAGEMENT ===

    setActiveSection(sectionName) {
        if (!sectionName || !this.sectionNames[sectionName]) {
            console.warn(`Invalid section name: ${sectionName}`);
            return false;
        }

        const previousSection = this.navigationState.currentSection;
        this.navigationState.currentSection = sectionName;
        
        // Update breadcrumb path
        this.updateBreadcrumbPath();

        this.dispatchEvent('section-changed', {
            previousSection,
            currentSection: sectionName,
            sectionDisplayName: this.sectionNames[sectionName]
        });

        return true;
    }

    getCurrentSection() {
        return this.navigationState.currentSection;
    }

    getCurrentSectionDisplayName() {
        return this.sectionNames[this.navigationState.currentSection] || this.navigationState.currentSection;
    }

    getSidebarSections() {
        return [...this.navigationState.sidebarSections];
    }

    isSectionActive(sectionName) {
        return this.navigationState.currentSection === sectionName;
    }

    // === TAB MANAGEMENT ===

    setActiveTab(tabName) {
        const previousTab = this.navigationState.activeTab;
        this.navigationState.activeTab = tabName;

        this.dispatchEvent('tab-changed', {
            previousTab,
            currentTab: tabName
        });

        return true;
    }

    getActiveTab() {
        return this.navigationState.activeTab;
    }

    clearActiveTab() {
        const previousTab = this.navigationState.activeTab;
        this.navigationState.activeTab = null;

        this.dispatchEvent('tab-cleared', { previousTab });
    }

    // === BREADCRUMB MANAGEMENT ===

    updateBreadcrumbPath() {
        const path = ['Data Studio'];
        
        if (this.navigationState.currentSection !== 'overview') {
            path.push(this.sectionNames[this.navigationState.currentSection] || this.navigationState.currentSection);
        }

        // Add active tab if present
        if (this.navigationState.activeTab) {
            path.push(this.navigationState.activeTab);
        }

        this.navigationState.breadcrumbPath = path;
        
        this.dispatchEvent('breadcrumb-updated', {
            breadcrumbPath: [...path]
        });
    }

    getBreadcrumbPath() {
        return [...this.navigationState.breadcrumbPath];
    }

    setBreadcrumbPath(path) {
        if (!Array.isArray(path)) {
            console.warn('Breadcrumb path must be an array');
            return false;
        }

        this.navigationState.breadcrumbPath = [...path];
        
        this.dispatchEvent('breadcrumb-updated', {
            breadcrumbPath: [...path]
        });

        return true;
    }

    // === WORKFLOW PROGRESS MANAGEMENT ===

    initializeWorkflowProgress(totalSteps, currentStep = 0) {
        if (typeof totalSteps !== 'number' || totalSteps <= 0) {
            console.warn('Total steps must be a positive number');
            return false;
        }

        if (typeof currentStep !== 'number' || currentStep < 0 || currentStep > totalSteps) {
            console.warn('Current step must be between 0 and total steps');
            return false;
        }

        this.navigationState.totalSteps = totalSteps;
        this.navigationState.workflowStep = currentStep;

        this.dispatchEvent('workflow-initialized', {
            totalSteps,
            currentStep,
            progress: this.getWorkflowProgress()
        });

        return true;
    }

    updateWorkflowStep(step) {
        if (typeof step !== 'number' || step < 0 || step > this.navigationState.totalSteps) {
            console.warn(`Invalid workflow step: ${step}. Must be between 0 and ${this.navigationState.totalSteps}`);
            return false;
        }

        const previousStep = this.navigationState.workflowStep;
        this.navigationState.workflowStep = step;

        this.dispatchEvent('workflow-step-updated', {
            previousStep,
            currentStep: step,
            totalSteps: this.navigationState.totalSteps,
            progress: this.getWorkflowProgress(),
            isCompleted: step === this.navigationState.totalSteps
        });

        return true;
    }

    getWorkflowProgress() {
        if (this.navigationState.totalSteps === 0) return 0;
        return (this.navigationState.workflowStep / this.navigationState.totalSteps) * 100;
    }

    getWorkflowStep() {
        return this.navigationState.workflowStep;
    }

    getTotalSteps() {
        return this.navigationState.totalSteps;
    }

    isWorkflowCompleted() {
        return this.navigationState.workflowStep === this.navigationState.totalSteps && this.navigationState.totalSteps > 0;
    }

    resetWorkflowProgress() {
        const hadProgress = this.navigationState.totalSteps > 0;
        
        this.navigationState.workflowStep = 0;
        this.navigationState.totalSteps = 0;

        if (hadProgress) {
            this.dispatchEvent('workflow-reset');
        }
    }

    // === STATE ACCESS ===

    getNavigationState() {
        return {
            ...this.navigationState,
            sectionDisplayName: this.getCurrentSectionDisplayName(),
            workflowProgress: this.getWorkflowProgress(),
            isWorkflowActive: this.navigationState.totalSteps > 0
        };
    }

    exportState() {
        return {
            ...this.navigationState,
            sectionNames: { ...this.sectionNames }
        };
    }

    importState(state) {
        if (!state || typeof state !== 'object') {
            console.warn('Invalid state object for import');
            return false;
        }

        try {
            // Import navigation state
            if (state.currentSection && this.sectionNames[state.currentSection]) {
                this.navigationState.currentSection = state.currentSection;
            }

            if (state.activeTab) {
                this.navigationState.activeTab = state.activeTab;
            }

            if (Array.isArray(state.breadcrumbPath)) {
                this.navigationState.breadcrumbPath = [...state.breadcrumbPath];
            }

            if (typeof state.workflowStep === 'number' && typeof state.totalSteps === 'number') {
                this.navigationState.workflowStep = Math.max(0, state.workflowStep);
                this.navigationState.totalSteps = Math.max(0, state.totalSteps);
            }

            if (Array.isArray(state.sidebarSections)) {
                this.navigationState.sidebarSections = [...state.sidebarSections];
            }

            // Import section names if provided
            if (state.sectionNames && typeof state.sectionNames === 'object') {
                this.sectionNames = { ...this.sectionNames, ...state.sectionNames };
            }

            this.dispatchEvent('state-imported', { importedState: state });
            return true;

        } catch (error) {
            console.error('Failed to import navigation state:', error);
            return false;
        }
    }

    // === UTILITY METHODS ===

    resetToDefaults() {
        const previousState = { ...this.navigationState };
        
        this.navigationState = {
            currentSection: 'overview',
            activeTab: null,
            breadcrumbPath: ['Data Studio'],
            workflowStep: 0,
            totalSteps: 0,
            sidebarSections: ['overview', 'transformation', 'advanced-filters', 'visualization', 'export']
        };

        this.dispatchEvent('state-reset', { previousState });
    }

    // === EVENT SYSTEM ===

    dispatchEvent(eventName, detail = {}) {
        this.eventTarget.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    addEventListener(eventName, handler) {
        this.eventTarget.addEventListener(eventName, handler);
    }

    removeEventListener(eventName, handler) {
        this.eventTarget.removeEventListener(eventName, handler);
    }

    // === CLEANUP ===

    destroy() {
        this.resetToDefaults();
        this.dispatchEvent('destroyed');
    }
}

// Export for use in other modules
window.NavigationStateManager = NavigationStateManager;

// Export removed for script tag compatibility