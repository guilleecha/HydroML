/**
 * TanStack Data Studio Main Coordinator
 * Responsabilidad única: Coordinación central usando TanStack Table
 * 
 * Filosofía: Lightweight, performance-first, NO OVER-ENGINEERING
 */

class TanStackDataStudioMain {
    constructor(config = {}) {
        // Configuration
        this.config = {
            datasourceId: window.datasourceId || null,
            debug: false,
            autoInit: true,
            tableEngine: 'tanstack', // 'tanstack' | 'ag-grid' | 'hybrid'
            ...config
        };

        // Module coordinators
        this.coordinators = {
            session: null,
            table: null,
            navigation: null
        };

        // Event bus for inter-module communication
        this.eventBus = new EventTarget();
        
        // Initialization state
        this.isInitialized = false;
        this.initializationOrder = ['session', 'navigation', 'table'];
        
        // Performance metrics
        this.performanceMetrics = {
            initStart: performance.now(),
            initEnd: null,
            firstRender: null,
            dataLoadTime: null
        };

        if (this.config.autoInit) {
            this.initialize();
        }
    }

    // === INITIALIZATION ===

    async initialize() {
        if (this.isInitialized) {
            console.warn('TanStack Data Studio already initialized');
            return false;
        }

        try {
            if (window.DataStudioErrorHandler) {
                console.log('🚀 Initializing TanStack Data Studio with ErrorHandler...');
            } else {
                console.log('🚀 Initializing TanStack Data Studio...');
            }

            // Wait for DOM to be ready
            await this.waitForDOM();

            // Initialize coordinators in order
            await this.initializeCoordinators();

            // Setup inter-module communication
            this.setupEventBridge();

            // Setup global API
            this.exposeGlobalAPI();

            this.isInitialized = true;
            this.performanceMetrics.initEnd = performance.now();

            const initTime = this.performanceMetrics.initEnd - this.performanceMetrics.initStart;
            console.log(`✅ TanStack Data Studio initialized successfully in ${initTime.toFixed(2)}ms`);

            this.dispatchSystemEvent('tanstack-data-studio-ready', {
                initTime,
                config: this.config,
                coordinators: Object.keys(this.coordinators)
            });

            return true;

        } catch (error) {
            if (window.DataStudioErrorHandler) {
                window.DataStudioErrorHandler.handleFatalError(error, {
                    operation: 'tanstack_data_studio_initialization',
                    config: this.config
                });
            } else {
                console.error('❌ TanStack Data Studio initialization failed:', error);
            }
            return false;
        }
    }

    async waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }

    async initializeCoordinators() {
        for (const coordinatorName of this.initializationOrder) {
            const startTime = performance.now();
            
            try {
                await this.initializeCoordinator(coordinatorName);
                
                const endTime = performance.now();
                console.log(`✓ ${coordinatorName} coordinator initialized in ${(endTime - startTime).toFixed(2)}ms`);
                
            } catch (error) {
                if (window.DataStudioErrorHandler) {
                    window.DataStudioErrorHandler.handleError(error, {
                        operation: `${coordinatorName}_coordinator_initialization`
                    });
                } else {
                    console.error(`❌ Failed to initialize ${coordinatorName} coordinator:`, error);
                }
                throw error;
            }
        }
    }

    async initializeCoordinator(name) {
        switch (name) {
            case 'session':
                if (typeof SessionCoordinator !== 'undefined') {
                    this.coordinators.session = new SessionCoordinator({
                        datasourceId: this.config.datasourceId,
                        autoLoadData: true
                    });
                }
                break;

            case 'table':
                if (typeof TanStackTableCoordinator !== 'undefined') {
                    this.coordinators.table = new TanStackTableCoordinator({
                        containerId: 'data-preview-grid',
                        enableSearch: true,
                        enablePagination: true,
                        pageSize: 25
                    });
                    
                    // Expose for backward compatibility
                    this.coordinators.table.exposeGlobalMethods();
                } else {
                    console.warn('TanStackTableCoordinator not available');
                }
                break;

            case 'navigation':
                if (typeof NavigationCoordinator !== 'undefined') {
                    this.coordinators.navigation = new NavigationCoordinator({
                        enableWorkflow: false // Simplified for table focus
                    });
                }
                break;

            default:
                console.warn(`Unknown coordinator: ${name}`);
        }
    }

    // === EVENT BRIDGE ===

    setupEventBridge() {
        // Connect session to table
        if (this.coordinators.session && this.coordinators.table) {
            this.coordinators.table.integrateWithSessionCoordinator(this.coordinators.session);
        }

        // Listen to key system events
        window.addEventListener('tanstack-table-system-ready', (event) => {
            this.handleTableReady(event.detail);
        });

        window.addEventListener('session-data-loaded', (event) => {
            this.handleSessionDataLoaded(event.detail);
        });

        // Performance monitoring
        window.addEventListener('tanstack-table-data-updated', (event) => {
            if (!this.performanceMetrics.firstRender) {
                this.performanceMetrics.firstRender = performance.now();
                const renderTime = this.performanceMetrics.firstRender - this.performanceMetrics.initStart;
                console.log(`📊 First table render completed in ${renderTime.toFixed(2)}ms`);
            }
        });
    }

    // === EVENT HANDLERS ===

    handleTableReady(detail) {
        console.log('📊 TanStack Table system ready:', detail);
        
        // Update performance metrics
        this.performanceMetrics.dataLoadTime = performance.now();
        
        this.dispatchSystemEvent('data-studio-table-ready', {
            engine: 'tanstack',
            ...detail
        });
    }

    handleSessionDataLoaded(detail) {
        console.log('🔗 Session data loaded, updating table...');
        
        if (this.coordinators.table && detail.gridData && detail.columnDefs) {
            this.coordinators.table.setGridData(detail.gridData);
            this.coordinators.table.setColumnDefinitions(detail.columnDefs);
        }
    }

    // === GLOBAL API ===

    exposeGlobalAPI() {
        // Main API
        window.tanStackDataStudio = {
            // Core methods
            isReady: () => this.isInitialized,
            getConfig: () => this.config,
            getCoordinators: () => this.coordinators,
            getMetrics: () => this.getPerformanceMetrics(),
            
            // Table operations
            table: {
                getData: () => this.coordinators.table?.getData() || [],
                getRowCount: () => this.coordinators.table?.getRowCount() || 0,
                getFilteredRowCount: () => this.coordinators.table?.getFilteredRowCount() || 0,
                refresh: () => this.coordinators.table?.refreshGrid(),
                export: (format) => this.coordinators.table?.exportData(format),
                getApi: () => this.coordinators.table?.getApi(), // AG Grid compatibility
            },
            
            // Session operations
            session: {
                refresh: () => this.coordinators.session?.refreshSession(),
                getData: () => this.coordinators.session?.getCurrentData(),
                getStatus: () => this.coordinators.session?.getSessionStatus(),
            },
            
            // System operations
            system: {
                reinitialize: () => this.reinitialize(),
                destroy: () => this.destroy(),
                benchmark: () => this.runBenchmark(),
            }
        };

        // Backward compatibility aliases
        window.dataStudioMain = window.tanStackDataStudio;
        window.gridCoordinator = this.coordinators.table;
    }

    // === PERFORMANCE & DEBUGGING ===

    getPerformanceMetrics() {
        const metrics = { ...this.performanceMetrics };
        
        if (metrics.initEnd && metrics.initStart) {
            metrics.totalInitTime = metrics.initEnd - metrics.initStart;
        }
        
        if (metrics.firstRender && metrics.initStart) {
            metrics.totalRenderTime = metrics.firstRender - metrics.initStart;
        }
        
        return metrics;
    }

    async runBenchmark() {
        console.log('🏃‍♂️ Running TanStack Table benchmark...');
        
        const startTime = performance.now();
        const initialMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
        
        // Simulate data operations
        const testData = this.generateTestData(1000, 20);
        
        if (this.coordinators.table) {
            const tableStart = performance.now();
            await this.coordinators.table.setGridData(testData);
            const tableEnd = performance.now();
            
            const finalMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;
            const endTime = performance.now();
            
            const results = {
                engine: 'TanStack Table',
                dataSize: {
                    rows: testData.length,
                    columns: 20,
                    totalCells: testData.length * 20
                },
                performance: {
                    totalTime: endTime - startTime,
                    tableRenderTime: tableEnd - tableStart,
                    memoryUsage: finalMemory - initialMemory,
                    memoryUsageMB: (finalMemory - initialMemory) / (1024 * 1024)
                },
                timestamp: new Date().toISOString()
            };
            
            console.log('📊 Benchmark Results:', results);
            return results;
        }
        
        return null;
    }

    generateTestData(rows, columns) {
        const data = [];
        for (let i = 0; i < rows; i++) {
            const row = {};
            for (let j = 0; j < columns; j++) {
                row[`col_${j}`] = `Row ${i + 1} Col ${j + 1}`;
            }
            data.push(row);
        }
        return data;
    }

    // === LIFECYCLE MANAGEMENT ===

    async reinitialize() {
        console.log('🔄 Reinitializing TanStack Data Studio...');
        
        this.destroy();
        
        // Reset state
        this.isInitialized = false;
        this.performanceMetrics = {
            initStart: performance.now(),
            initEnd: null,
            firstRender: null,
            dataLoadTime: null
        };
        
        return await this.initialize();
    }

    destroy() {
        console.log('🗑️ Destroying TanStack Data Studio...');
        
        // Destroy coordinators
        Object.values(this.coordinators).forEach(coordinator => {
            if (coordinator && typeof coordinator.destroy === 'function') {
                coordinator.destroy();
            }
        });
        
        // Clear references
        this.coordinators = {
            session: null,
            table: null,
            navigation: null
        };
        
        // Clean up global references
        delete window.tanStackDataStudio;
        delete window.dataStudioMain;
        delete window.gridCoordinator;
        
        this.isInitialized = false;
        
        this.dispatchSystemEvent('tanstack-data-studio-destroyed');
    }

    // === SYSTEM EVENTS ===

    dispatchSystemEvent(eventName, detail = {}) {
        window.dispatchEvent(new CustomEvent(eventName, { 
            detail: {
                ...detail,
                timestamp: Date.now(),
                source: 'tanstack-data-studio'
            }
        }));
    }

    // === ERROR RECOVERY ===

    handleError(error, context = {}) {
        if (window.DataStudioErrorHandler) {
            window.DataStudioErrorHandler.handleError(error, {
                component: 'tanstack-data-studio-main',
                ...context
            });
        } else {
            console.error('TanStack Data Studio Error:', error, context);
        }
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if TanStack Table dependencies are loaded
    if (typeof TanStackTableController === 'undefined') {
        console.error('❌ TanStackTableController not loaded. Check script loading order.');
        return;
    }
    
    // Initialize the main coordinator
    window.tanStackDataStudioMain = new TanStackDataStudioMain({
        debug: window.location.hostname === 'localhost',
        tableEngine: 'tanstack'
    });
    
    // Initialize global variables needed by Alpine.js templates
    window.filterManager = window.tanStackDataStudioMain?.filterCoordinator || {
        getActiveFiltersCount: () => 0,
        getActiveFilter: () => null,
        getPresets: () => []
    };
    
    window.pagination = window.tanStackDataStudioMain?.tableCoordinator?.tableController?.pagination || {
        pageSize: 25,
        availablePageSizes: [10, 25, 50, 100],
        currentPage: 1,
        totalPages: 1,
        totalRows: 0,
        jumpToPage: 1
    };
    
    // Initialize filter UI variables
    window.showFilterBuilder = false;
    window.showFilterPresets = false;
    window.selectedFilterColumn = null;
    window.availableColumns = [];
});

// Global error handler
window.addEventListener('error', (event) => {
    if (window.tanStackDataStudioMain) {
        window.tanStackDataStudioMain.handleError(event.error, {
            operation: 'global_error_handler',
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno
        });
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TanStackDataStudioMain;
}