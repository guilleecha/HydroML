/**
 * TanStack Data Studio Table Coordinator
 * Coordinador principal para integración Django + TanStack Table
 * 
 * Implementa patrones oficiales de documentación TanStack Table
 */

class DataStudioTableCoordinator {
    constructor() {
        this.tableCore = null;
        this.isInitialized = false;
        this.containerId = 'tanstack-table-container';
        
        console.log('🚀 DataStudio Table Coordinator initialized');
    }

    /**
     * Inicializar tabla con datos de Django
     */
    async initialize() {
        try {
            // Esperar a que DOM esté listo
            await this.waitForDOM();

            // Verificar dependencias
            if (!this.checkDependencies()) {
                throw new Error('TanStack Table dependencies not loaded');
            }

            // Inicializar tabla core
            await this.initializeTableCore();

            // Cargar datos iniciales
            await this.loadInitialData();

            this.isInitialized = true;
            console.log('✅ DataStudio Table Coordinator ready');
            
            // Dispatch evento de inicialización
            this.dispatchEvent('data-studio-table-ready', {
                coordinator: this,
                containerId: this.containerId
            });

            return true;

        } catch (error) {
            console.error('❌ Failed to initialize DataStudio Table:', error);
            this.renderErrorState(error.message);
            return false;
        }
    }

    /**
     * Verificar dependencias necesarias
     */
    checkDependencies() {
        const required = [
            'window.TanStackTableCore',
            'window.TanStackTableConfig'
        ];

        for (const dep of required) {
            const obj = dep.split('.').reduce((o, i) => o && o[i], window);
            if (!obj) {
                console.error(`❌ Missing dependency: ${dep}`);
                return false;
            }
        }

        return true;
    }

    /**
     * Inicializar TanStack Table Core
     */
    async initializeTableCore() {
        // Obtener configuración para Data Studio
        const config = window.TanStackTableConfig.getDataStudioConfig();
        
        // Crear instancia core
        this.tableCore = new window.TanStackTableCore(this.containerId, config);
        
        console.log('✅ TanStack Table Core initialized');
    }

    /**
     * Cargar datos iniciales desde Django
     */
    async loadInitialData() {
        // Datos pasados desde Django template
        const data = window.gridRowData || [];
        const columns = window.columnDefsData || [];

        if (data.length === 0 || columns.length === 0) {
            console.warn('⚠️ No data available from Django');
            this.renderEmptyState();
            return;
        }

        console.log('📊 Loading Django data:', {
            rows: data.length,
            columns: columns.length
        });

        // Inicializar tabla con datos
        await this.tableCore.initialize(data, columns);
    }

    /**
     * Esperar a que DOM esté listo
     */
    async waitForDOM() {
        return new Promise((resolve) => {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', resolve);
            } else {
                resolve();
            }
        });
    }

    /**
     * Renderizar estado vacío
     */
    renderEmptyState() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        const tableBody = container.querySelector('#table-body');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="100%" class="px-6 py-8 text-center text-gray-500">
                        <div class="flex flex-col items-center">
                            <svg class="w-12 h-12 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                            <p>No hay datos disponibles para mostrar</p>
                            <p class="text-xs text-gray-400 mt-2">Verifica que el DataSource tenga datos</p>
                        </div>
                    </td>
                </tr>
            `;
        }
    }

    /**
     * Renderizar estado de error
     */
    renderErrorState(message) {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        const tableBody = container.querySelector('#table-body');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="100%" class="px-6 py-8 text-center text-red-500">
                        <div class="flex flex-col items-center">
                            <svg class="w-12 h-12 text-red-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            <p>Error cargando la tabla</p>
                            <p class="text-xs text-red-400 mt-2">{message}</p>
                        </div>
                    </td>
                </tr>
            `;
        }
    }

    /**
     * API pública para actualizar datos
     */
    updateData(newData, newColumns) {
        if (this.tableCore) {
            this.tableCore.updateData(newData);
            console.log('🔄 Table data updated');
        }
    }

    /**
     * API pública para exportar datos
     */
    exportData(format = 'csv') {
        if (this.tableCore) {
            return this.tableCore.getFilteredData();
        }
        return [];
    }

    /**
     * API pública para obtener estado
     */
    getTableState() {
        return {
            initialized: this.isInitialized,
            dataCount: window.gridRowData?.length || 0,
            columnCount: window.columnDefsData?.length || 0,
            hasCore: !!this.tableCore
        };
    }

    /**
     * Dispatch eventos personalizados
     */
    dispatchEvent(eventName, detail = {}) {
        window.dispatchEvent(new CustomEvent(eventName, { 
            detail: {
                ...detail,
                timestamp: Date.now(),
                source: 'data-studio-table-coordinator'
            }
        }));
    }

    /**
     * Cleanup
     */
    destroy() {
        this.isInitialized = false;
        this.tableCore = null;
        console.log('🗑️ DataStudio Table Coordinator destroyed');
    }
}

// Auto-inicializar cuando DOM esté listo
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 DOM ready, initializing DataStudio Table...');
    
    // Crear coordinador global
    window.dataStudioTableCoordinator = new DataStudioTableCoordinator();
    
    // Inicializar automáticamente
    await window.dataStudioTableCoordinator.initialize();
});

// Export para compatibilidad
window.DataStudioTableCoordinator = DataStudioTableCoordinator;