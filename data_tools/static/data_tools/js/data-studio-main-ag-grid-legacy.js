/**
 * Data Studio Main Coordinator
 * Responsabilidad única: Coordinación central de todos los módulos del Data Studio
 * 
 * Filosofía: Lightweight coordinator, no business logic, event-driven architecture
 */

class DataStudioMain {
    constructor(config = {}) {
        // Configuration
        this.config = {
            datasourceId: window.datasourceId || null,
            debug: false,
            autoInit: true,
            ...config
        };

        // Module coordinators
        this.coordinators = {
            session: null,
            grid: null,
            filter: null,
            navigation: null
        };

        // Event bus for inter-module communication
        this.eventBus = new EventTarget();
        
        // Initialization state
        this.isInitialized = false;
        this.initializationOrder = ['session', 'navigation', 'grid', 'filter'];
        
        // Cleanup tasks
        this.cleanupTasks = [];

        if (this.config.autoInit) {
            this.initialize();
        }
    }

    // === INITIALIZATION ===

    async initialize() {
        if (this.isInitialized) {
            console.warn('Data Studio already initialized');
            return false;
        }

        try {

            // Validate required dependencies
            if (!this.validateDependencies()) {
                throw new Error('Required dependencies not available');
            }

            // Initialize coordinators in order
            await this.initializeCoordinators();

            // Setup inter-module communication
            this.setupEventBus();

            // Setup global event listeners
            this.setupGlobalEvents();

            // Expose global interface
            this.exposeGlobalInterface();

            this.isInitialized = true;
            this.dispatchEvent('data-studio-initialized', {
                coordinators: Object.keys(this.coordinators),
                config: this.config
            });

            return true;

        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleFatalError(error, {
                    operation: 'data_studio_initialization'
                });
            } else {
                console.error('Failed to initialize Data Studio:', error);
            }
            this.dispatchEvent('data-studio-initialization-failed', { error });
            return false;
        }
    }

    validateDependencies() {
        const required = [
            'SessionCoordinator',
            'GridCoordinator', 
            'FilterCoordinator',
            'NavigationCoordinator',
            'APIClient'
        ];

        for (const dep of required) {
            if (!window[dep]) {
                console.error(`Missing required dependency: ${dep}`);
                return false;
            }
        }

        return true;
    }

    async initializeCoordinators() {
        for (const coordinatorName of this.initializationOrder) {
            await this.initializeCoordinator(coordinatorName);
        }
    }

    async initializeCoordinator(name) {
        try {
            switch (name) {
                case 'session':
                    this.coordinators.session = new SessionCoordinator({
                        datasourceId: this.config.datasourceId
                    });
                    break;

                case 'navigation':
                    this.coordinators.navigation = new NavigationCoordinator({
                        sectionSelector: '[data-section]',
                        workflowContainer: '#workflow-progress-container',
                        breadcrumbContainer: '#breadcrumb-container'
                    });
                    break;

                case 'grid':
                    // Wait for session to be ready first
                    await this.waitForEvent('session-coordinator-ready');
                    this.coordinators.grid = new GridCoordinator({
                        gridContainer: '#dataGrid',
                        sessionManager: this.coordinators.session
                    });
                    break;

                case 'filter':
                    // Wait for grid to be ready first
                    await this.waitForEvent('grid-coordinator-ready');
                    this.coordinators.filter = new FilterCoordinator(
                        this.coordinators.grid.getGridApi(),
                        this.coordinators.grid.getColumnDefs()
                    );
                    break;

                default:
                    throw new Error(`Unknown coordinator: ${name}`);
            }

            this.dispatchEvent(`${name}-coordinator-ready`, {
                coordinator: this.coordinators[name]
            });


        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleFatalError(error, {
                    operation: `${name}_coordinator_initialization`,
                    coordinator: name
                });
            } else {
                console.error(`Failed to initialize ${name} coordinator:`, error);
            }
            throw error;
        }
    }

    // === EVENT BUS COORDINATION ===

    setupEventBus() {
        // Session events
        this.coordinators.session?.addEventListener('session-data-updated', (event) => {
            this.broadcastEvent('data-studio-session-updated', event.detail);
        });

        this.coordinators.session?.addEventListener('transformation-applied', (event) => {
            // Notify grid to refresh data
            this.coordinators.grid?.handleDataUpdate(event.detail);
            this.broadcastEvent('data-studio-data-transformed', event.detail);
        });

        // Grid events
        this.coordinators.grid?.addEventListener('grid-data-updated', (event) => {
            // Notify filters that grid data changed
            this.coordinators.filter?.handleGridUpdate(event.detail);
            this.broadcastEvent('data-studio-grid-updated', event.detail);
        });

        this.coordinators.grid?.addEventListener('columns-changed', (event) => {
            // Notify filters about column changes
            this.coordinators.filter?.handleGridUpdate(event.detail);
            this.broadcastEvent('data-studio-columns-changed', event.detail);
        });

        // Filter events
        this.coordinators.filter?.addEventListener('filter-applied', (event) => {
            this.broadcastEvent('data-studio-filter-applied', event.detail);
        });

        this.coordinators.filter?.addEventListener('filters-cleared', (event) => {
            this.broadcastEvent('data-studio-filters-cleared', event.detail);
        });

        // Navigation events
        this.coordinators.navigation?.addEventListener('section-changed', (event) => {
            this.broadcastEvent('data-studio-section-changed', event.detail);
        });

        this.coordinators.navigation?.addEventListener('workflow-progress', (event) => {
            this.broadcastEvent('data-studio-workflow-progress', event.detail);
        });
    }

    setupGlobalEvents() {
        // Browser events
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });

        // Document events
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handleVisibilityHidden();
            } else {
                this.handleVisibilityVisible();
            }
        });

        // Custom application events
        window.addEventListener('data-studio-refresh', (event) => {
            this.refresh(event.detail);
        });

        window.addEventListener('data-studio-reset', () => {
            this.reset();
        });
    }

    // === EVENT UTILITIES ===

    waitForEvent(eventName, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                this.eventBus.removeEventListener(eventName, handler);
                reject(new Error(`Timeout waiting for event: ${eventName}`));
            }, timeout);

            const handler = (event) => {
                clearTimeout(timer);
                this.eventBus.removeEventListener(eventName, handler);
                resolve(event.detail);
            };

            this.eventBus.addEventListener(eventName, handler);
        });
    }

    broadcastEvent(eventName, detail = {}) {
        // Dispatch to internal event bus
        this.eventBus.dispatchEvent(new CustomEvent(eventName, { detail }));
        
        // Dispatch to global window for external listeners
        window.dispatchEvent(new CustomEvent(eventName, { detail }));
    }

    dispatchEvent(eventName, detail = {}) {
        this.broadcastEvent(eventName, detail);
    }

    // === COORDINATOR ACCESS ===

    getSessionCoordinator() {
        return this.coordinators.session;
    }

    getGridCoordinator() {
        return this.coordinators.grid;
    }

    getFilterCoordinator() {
        return this.coordinators.filter;
    }

    getNavigationCoordinator() {
        return this.coordinators.navigation;
    }

    // === SYSTEM OPERATIONS ===

    async refresh(options = {}) {
        try {
            this.dispatchEvent('data-studio-refresh-started', options);

            // Refresh session data
            if (options.session !== false) {
                await this.coordinators.session?.refresh();
            }

            // Refresh grid
            if (options.grid !== false) {
                await this.coordinators.grid?.refresh();
            }

            // Clear filter cache
            if (options.filters !== false) {
                this.coordinators.filter?.refreshSystem();
            }

            // Refresh navigation
            if (options.navigation !== false) {
                this.coordinators.navigation?.refreshSystem();
            }

            this.dispatchEvent('data-studio-refreshed', options);

        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleError(error, {
                    type: 'refresh_error',
                    operation: 'data_studio_refresh',
                    options
                });
            } else {
                console.error('Error refreshing Data Studio:', error);
            }
            this.dispatchEvent('data-studio-refresh-failed', { error });
        }
    }

    reset() {
        try {
            // Reset all coordinators
            Object.values(this.coordinators).forEach(coordinator => {
                if (coordinator && typeof coordinator.reset === 'function') {
                    coordinator.reset();
                }
            });

            this.dispatchEvent('data-studio-reset');

        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleError(error, {
                    type: 'reset_error',
                    operation: 'data_studio_reset'
                });
            } else {
                console.error('Error resetting Data Studio:', error);
            }
        }
    }

    // === VISIBILITY HANDLING ===

    handleVisibilityHidden() {
        // Pause any periodic updates when tab is hidden
        this.coordinators.session?.pauseStatusUpdates();
        this.dispatchEvent('data-studio-visibility-hidden');
    }

    handleVisibilityVisible() {
        // Resume updates when tab becomes visible
        this.coordinators.session?.resumeStatusUpdates();
        this.dispatchEvent('data-studio-visibility-visible');
    }

    // === GLOBAL INTERFACE EXPOSURE ===

    exposeGlobalInterface() {
        // Main controller access
        window.dataStudio = this;

        // Coordinator shortcuts (backward compatibility)
        window.dataStudioSession = this.coordinators.session;
        window.dataStudioGrid = this.coordinators.grid;
        window.dataStudioFilters = this.coordinators.filter;
        window.dataStudioNavigation = this.coordinators.navigation;

        // Legacy method aliases for backward compatibility
        window.dataStudioController = {
            // Session operations
            getSessionInfo: () => this.coordinators.session?.getSessionInfo(),
            refreshSession: () => this.coordinators.session?.refresh(),
            
            // Grid operations  
            getGridData: () => this.coordinators.grid?.getGridData(),
            refreshGrid: () => this.coordinators.grid?.refresh(),
            
            // Filter operations
            getActiveFilters: () => this.coordinators.filter?.getActiveFilters(),
            clearAllFilters: () => this.coordinators.filter?.clearAllFilters(),
            
            // Navigation operations
            setActiveSection: (section) => this.coordinators.navigation?.setActiveSection(section),
            getCurrentSection: () => this.coordinators.navigation?.getCurrentSection(),
            
            // System operations
            refresh: (options) => this.refresh(options),
            reset: () => this.reset()
        };

        // Development utilities
        if (this.config.debug) {
            window.dataStudioDebug = {
                getCoordinators: () => this.coordinators,
                getEventBus: () => this.eventBus,
                getConfig: () => this.config,
                getSystemStats: () => this.getSystemStats()
            };
        }
    }

    // === UTILITIES ===

    getSystemStats() {
        return {
            initialized: this.isInitialized,
            coordinators: {
                session: !!this.coordinators.session,
                grid: !!this.coordinators.grid,
                filter: !!this.coordinators.filter,
                navigation: !!this.coordinators.navigation
            },
            config: this.config,
            eventListeners: this.eventBus.constructor.name
        };
    }

    // === CLEANUP ===

    cleanup() {
        if (!this.isInitialized) return;

        try {
            // Cleanup coordinators
            Object.values(this.coordinators).forEach(coordinator => {
                if (coordinator && typeof coordinator.destroy === 'function') {
                    coordinator.destroy();
                }
            });

            // Execute cleanup tasks
            this.cleanupTasks.forEach(task => {
                try {
                    task();
                } catch (error) {
                    console.warn('Error during cleanup task:', error);
                }
            });

            // Clear global references
            delete window.dataStudio;
            delete window.dataStudioSession;
            delete window.dataStudioGrid;
            delete window.dataStudioFilters;
            delete window.dataStudioNavigation;
            delete window.dataStudioController;
            delete window.dataStudioDebug;

            this.isInitialized = false;
            this.dispatchEvent('data-studio-destroyed');


        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleError(error, {
                    type: 'cleanup_error',
                    operation: 'data_studio_cleanup'
                });
            } else {
                console.error('Error during Data Studio cleanup:', error);
            }
        }
    }

    destroy() {
        this.cleanup();
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if datasourceId is available
    if (window.datasourceId) {
        new DataStudioMain({
            datasourceId: window.datasourceId,
            debug: window.DEBUG || false
        });
    } else {
        console.warn('Data Studio not initialized: missing datasourceId');
    }
});

// Export for module usage
export default DataStudioMain;