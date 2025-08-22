/**
 * NavigationCoordinator - Navigation System Coordination
 * Responsabilidad única: Coordinar NavigationStateManager y NavigationUIController
 * 
 * Filosofía: Event-driven coordination, clean interface for external systems
 */

class NavigationCoordinator {
    constructor(config = {}) {
        // Initialize sub-modules
        this.stateManager = new NavigationStateManager();
        this.uiController = new NavigationUIController(this.stateManager, config);
        
        // Setup event coordination
        this.setupEventListeners();
        this.exposeGlobalMethods();
        
        // Auto-initialize
        this.initialize();
    }

    // === INITIALIZATION ===

    initialize() {
        try {
            // Initialize navigation state
            this.stateManager.updateBreadcrumbPath();
            
            // Initialize UI
            const currentState = this.stateManager.getNavigationState();
            this.uiController.updateSectionUI({
                previousSection: null,
                currentSection: currentState.currentSection
            });
            
            this.dispatchSystemEvent('navigation-system-ready', {
                currentSection: currentState.currentSection,
                navigationState: currentState
            });
            
            return true;

        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleNavigationError(error, {
                    operation: 'navigation_system_initialization'
                });
            } else {
                console.error('Failed to initialize navigation system:', error);
            }
            return false;
        }
    }

    // === EVENT COORDINATION ===

    setupEventListeners() {
        // State Manager Events -> System Events
        this.stateManager.addEventListener('section-changed', (event) => {
            this.dispatchSystemEvent('data-studio-section-changed', event.detail);
        });

        this.stateManager.addEventListener('workflow-initialized', (event) => {
            this.dispatchSystemEvent('data-studio-workflow-started', event.detail);
        });

        this.stateManager.addEventListener('workflow-step-updated', (event) => {
            this.dispatchSystemEvent('data-studio-workflow-progress', event.detail);
            
            if (event.detail.isCompleted) {
                this.dispatchSystemEvent('data-studio-workflow-completed', event.detail);
            }
        });

        this.stateManager.addEventListener('breadcrumb-updated', (event) => {
            this.dispatchSystemEvent('data-studio-breadcrumb-updated', event.detail);
        });

        // Global Events -> Navigation System Updates
        window.addEventListener('data-studio-grid-update', (event) => {
            this.handleGridUpdate(event.detail);
        });

        // Navigation control events
        document.addEventListener('set-active-section', (event) => {
            this.setActiveSection(event.detail);
        });

        document.addEventListener('navigate-to-section', (event) => {
            this.navigateToSection(event.detail);
        });

        document.addEventListener('start-workflow', (event) => {
            this.startWorkflow(event.detail);
        });

        document.addEventListener('update-workflow-step', (event) => {
            this.updateWorkflowStep(event.detail);
        });

        document.addEventListener('reset-workflow', () => {
            this.resetWorkflow();
        });

        document.addEventListener('set-breadcrumb', (event) => {
            this.setBreadcrumb(event.detail);
        });
    }

    // === NAVIGATION OPERATIONS ===

    setActiveSection(sectionName) {
        if (typeof sectionName === 'object' && sectionName.sectionName) {
            sectionName = sectionName.sectionName;
        }

        const success = this.stateManager.setActiveSection(sectionName);
        
        if (success) {
            this.dispatchSystemEvent('navigation-section-activated', {
                sectionName,
                sectionDisplayName: this.stateManager.getCurrentSectionDisplayName()
            });
        }

        return success;
    }

    navigateToSection(navigationData) {
        const { sectionName, tabName, breadcrumb } = navigationData;
        
        // Set section
        if (sectionName) {
            this.setActiveSection(sectionName);
        }

        // Set tab if provided
        if (tabName) {
            this.setActiveTab(tabName);
        }

        // Set custom breadcrumb if provided
        if (breadcrumb && Array.isArray(breadcrumb)) {
            this.setBreadcrumb(breadcrumb);
        }

        return true;
    }

    setActiveTab(tabName) {
        const success = this.stateManager.setActiveTab(tabName);
        
        if (success) {
            this.dispatchSystemEvent('navigation-tab-activated', { tabName });
        }

        return success;
    }

    clearActiveTab() {
        this.stateManager.clearActiveTab();
        this.dispatchSystemEvent('navigation-tab-cleared');
    }

    // === WORKFLOW OPERATIONS ===

    startWorkflow(workflowData) {
        const { totalSteps, currentStep = 0, showUI = true } = workflowData;
        
        const success = this.stateManager.initializeWorkflowProgress(totalSteps, currentStep);
        
        if (success && showUI) {
            this.uiController.showWorkflowProgress();
        }

        return success;
    }

    updateWorkflowStep(stepData) {
        let step;
        
        if (typeof stepData === 'number') {
            step = stepData;
        } else if (typeof stepData === 'object' && typeof stepData.step === 'number') {
            step = stepData.step;
        } else {
            console.warn('Invalid workflow step data:', stepData);
            return false;
        }

        return this.stateManager.updateWorkflowStep(step);
    }

    resetWorkflow() {
        this.stateManager.resetWorkflowProgress();
        this.dispatchSystemEvent('navigation-workflow-reset');
    }

    // === BREADCRUMB OPERATIONS ===

    setBreadcrumb(breadcrumbData) {
        let breadcrumbPath;
        
        if (Array.isArray(breadcrumbData)) {
            breadcrumbPath = breadcrumbData;
        } else if (typeof breadcrumbData === 'object' && Array.isArray(breadcrumbData.path)) {
            breadcrumbPath = breadcrumbData.path;
        } else {
            console.warn('Invalid breadcrumb data:', breadcrumbData);
            return false;
        }

        return this.stateManager.setBreadcrumbPath(breadcrumbPath);
    }

    // === EXTERNAL INTEGRATIONS ===

    handleGridUpdate(detail) {
        // Navigation can respond to grid updates if needed
        // Currently no specific navigation actions required
        this.dispatchSystemEvent('navigation-grid-update-received', detail);
    }

    // === WORKFLOW TESTING (REMOVED FROM PRODUCTION) ===
    // Note: Removed testWorkflowProgress() as recommended by code-analyzer
    // This functionality should be in test utilities, not production code

    // === GLOBAL METHOD EXPOSURE ===

    exposeGlobalMethods() {
        // Expose navigation methods globally for backward compatibility
        window.dataStudioNavigation = {
            // Section operations
            setActiveSection: (sectionName) => this.setActiveSection(sectionName),
            getCurrentSection: () => this.stateManager.getCurrentSection(),
            getCurrentSectionDisplayName: () => this.stateManager.getCurrentSectionDisplayName(),
            
            // Tab operations
            setActiveTab: (tabName) => this.setActiveTab(tabName),
            getActiveTab: () => this.stateManager.getActiveTab(),
            clearActiveTab: () => this.clearActiveTab(),
            
            // Workflow operations
            startWorkflow: (totalSteps, currentStep) => this.startWorkflow({ totalSteps, currentStep }),
            updateWorkflowStep: (step) => this.updateWorkflowStep(step),
            resetWorkflow: () => this.resetWorkflow(),
            getWorkflowProgress: () => this.stateManager.getWorkflowProgress(),
            
            // Breadcrumb operations
            setBreadcrumb: (path) => this.setBreadcrumb(path),
            getBreadcrumbPath: () => this.stateManager.getBreadcrumbPath(),
            
            // State access
            getNavigationState: () => this.stateManager.getNavigationState(),
            exportState: () => this.stateManager.exportState(),
            importState: (state) => this.stateManager.importState(state),
            
            // UI operations
            showWorkflowProgress: () => this.uiController.showWorkflowProgress(),
            hideWorkflowProgress: () => this.uiController.hideWorkflowProgress(),
            updateConfig: (config) => this.uiController.updateConfig(config)
        };

        // Expose individual components for advanced usage
        window.navigationStateManager = this.stateManager;
        window.navigationUIController = this.uiController;
        window.navigationManager = this; // Backward compatibility
    }

    // === SYSTEM EVENT DISPATCH ===

    dispatchSystemEvent(eventName, detail = {}) {
        window.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    // === GETTERS ===

    getStateManager() {
        return this.stateManager;
    }

    getUIController() {
        return this.uiController;
    }

    getCurrentSection() {
        return this.stateManager.getCurrentSection();
    }

    getNavigationState() {
        return this.stateManager.getNavigationState();
    }

    // === UTILITY METHODS ===

    refreshSystem() {
        // Refresh navigation UI
        const currentState = this.stateManager.getNavigationState();
        this.uiController.updateSectionUI({
            previousSection: null,
            currentSection: currentState.currentSection
        });
        
        this.dispatchSystemEvent('navigation-system-refreshed');
    }

    getSystemStats() {
        const state = this.stateManager.getNavigationState();
        return {
            currentSection: state.currentSection,
            activeTab: state.activeTab,
            workflowActive: state.isWorkflowActive,
            workflowProgress: state.workflowProgress,
            breadcrumbLength: state.breadcrumbPath.length
        };
    }

    // === CLEANUP ===

    destroy() {
        this.stateManager.destroy();
        this.uiController.destroy();
        
        // Clean up global references
        delete window.dataStudioNavigation;
        delete window.navigationStateManager;
        delete window.navigationUIController;
        delete window.navigationManager;
        
        this.dispatchSystemEvent('navigation-system-destroyed');
    }
}

// Export for use in other modules
window.NavigationCoordinator = NavigationCoordinator;

// Export removed for script tag compatibility