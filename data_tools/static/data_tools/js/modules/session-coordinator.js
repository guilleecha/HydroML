/**
 * SessionCoordinator - Coordination between SessionManager and SessionUIController
 * Responsabilidad única: Coordinar la lógica de sesión con la UI
 * 
 * Filosofía: Event-driven architecture, loose coupling
 */

class SessionCoordinator {
    constructor(datasourceId) {
        this.sessionManager = new SessionManager(datasourceId);
        this.uiController = new SessionUIController();
        
        this.setupEventListeners();
        this.exposeGlobalMethods();
    }

    setupEventListeners() {
        // Listen to session manager events and update UI
        this.sessionManager.addEventListener('session-state-changed', (event) => {
            this.uiController.updateSessionStatus(event.detail.sessionInfo);
        });

        this.sessionManager.addEventListener('session-initialized', (event) => {
            this.uiController.showNotification('Session initialized successfully', 'success');
            this.dispatchGridUpdate(event.detail);
        });

        this.sessionManager.addEventListener('session-operation-undone', (event) => {
            this.uiController.showNotification('Operation undone successfully', 'success');
            this.dispatchGridUpdate(event.detail);
        });

        this.sessionManager.addEventListener('session-operation-redone', (event) => {
            this.uiController.showNotification('Operation redone successfully', 'success');
            this.dispatchGridUpdate(event.detail);
        });

        this.sessionManager.addEventListener('session-saved', (event) => {
            const datasourceName = event.detail.newDatasource?.name || 'new dataset';
            this.uiController.showNotification(`Data saved successfully as: ${datasourceName}`, 'success');
        });

        this.sessionManager.addEventListener('session-status-updated', (event) => {
            this.dispatchGridUpdate(event.detail);
        });
    }

    dispatchGridUpdate(detail) {
        // Dispatch custom event for grid updates
        window.dispatchEvent(new CustomEvent('data-studio-grid-update', { detail }));
    }

    exposeGlobalMethods() {
        // Expose methods globally for backward compatibility
        window.initializeSession = async () => {
            try {
                await this.sessionManager.initialize();
            } catch (error) {
                this.uiController.showNotification(error.message, 'error');
            }
        };

        window.undoOperation = async () => {
            try {
                await this.sessionManager.undo();
            } catch (error) {
                this.uiController.showNotification(error.message, 'error');
            }
        };

        window.redoOperation = async () => {
            try {
                await this.sessionManager.redo();
            } catch (error) {
                this.uiController.showNotification(error.message, 'error');
            }
        };

        window.saveSession = async () => {
            const name = prompt('Enter name for the new dataset:', `${window.datasourceName}_transformed`);
            if (!name) return;
            
            const description = prompt('Enter description (optional):') || `Transformed version of ${window.datasourceName}`;
            
            try {
                await this.sessionManager.save(name, description);
            } catch (error) {
                this.uiController.showNotification(error.message, 'error');
            }
        };
    }

    // === PUBLIC METHODS ===

    async initialize() {
        await this.sessionManager.checkStatus();
    }

    getSessionManager() {
        return this.sessionManager;
    }

    getUIController() {
        return this.uiController;
    }

    // === EVENT DELEGATION METHODS ===
    // Delegate event methods to the sessionManager for external components

    addEventListener(eventName, handler) {
        return this.sessionManager.addEventListener(eventName, handler);
    }

    removeEventListener(eventName, handler) {
        return this.sessionManager.removeEventListener(eventName, handler);
    }

    dispatchEvent(eventName, detail = {}) {
        return this.sessionManager.dispatchEvent(eventName, detail);
    }
}

// Export for use in other modules
window.SessionCoordinator = SessionCoordinator;

// Export removed for script tag compatibility