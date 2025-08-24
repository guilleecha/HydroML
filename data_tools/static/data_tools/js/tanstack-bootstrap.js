/**
 * TanStack Table Bootstrap - HydroML
 * 
 * Inicializa TanStack Table desde instalación local NPM
 * Compatible con Django static files y seguimiento de mejores prácticas 2024
 * 
 * @version 1.0.0
 * @author Claude Code
 * @date 2025-01-23
 */

(function() {
    'use strict';
    
    console.log('🚀 TanStack Bootstrap iniciando...');

    // Verificar si TableCore ya está disponible
    if (window.TableCore) {
        console.log('✅ TanStack Table ya disponible globalmente');
        dispatchReadyEvent();
        return;
    }

    // Cargar TanStack Table directamente desde CDN
    loadFromCDN();

    /**
     * Carga TanStack Table desde instalación NPM local
     */
    function loadTanStackTable() {
        // Intentar cargar desde instalación local
        const localScript = document.createElement('script');
        localScript.src = '/static/node_modules/@tanstack/table-core/build/umd/index.development.js';
        
        localScript.onload = function() {
            console.log('✅ TanStack Table cargado desde instalación local');
            initializeTableCore();
            dispatchReadyEvent();
        };

        localScript.onerror = function() {
            console.warn('⚠️ Instalación local no encontrada, intentando CDN como fallback...');
            loadFromCDN();
        };

        document.head.appendChild(localScript);
    }

    /**
     * Fallback: Cargar desde CDN si local falla
     */
    function loadFromCDN() {
        const cdnScript = document.createElement('script');
        cdnScript.src = 'https://unpkg.com/@tanstack/table-core@8.20.5/build/umd/index.development.js';
        
        cdnScript.onload = function() {
            console.log('✅ TanStack Table cargado desde CDN (fallback)');
            initializeTableCore();
            dispatchReadyEvent();
        };

        cdnScript.onerror = function() {
            console.error('❌ Error cargando TanStack Table desde CDN');
            handleLoadError();
        };

        document.head.appendChild(cdnScript);
    }

    /**
     * Inicializa TableCore después de la carga exitosa
     */
    function initializeTableCore() {
        // Buscar TanStack Table en diferentes namespaces posibles
        if (window.TableCore) {
            console.log('📊 TanStack Table Core ya disponible con funciones:', 
                Object.keys(window.TableCore).slice(0, 5).join(', ') + '...');
        } else if (window.TanStackTable) {
            window.TableCore = window.TanStackTable;
            console.log('📊 TanStack Table mapeado desde window.TanStackTable');
        } else if (window['@tanstack/table-core']) {
            window.TableCore = window['@tanstack/table-core'];
            console.log('📊 TanStack Table mapeado desde window["@tanstack/table-core"]');
        } else {
            // Buscar en objetos globales comunes de UMD
            const possibleGlobals = ['tanStackTableCore', 'tableCore', 'TanStack'];
            for (const globalName of possibleGlobals) {
                if (window[globalName]) {
                    window.TableCore = window[globalName];
                    console.log(`📊 TanStack Table mapeado desde window.${globalName}`);
                    break;
                }
            }
            
            if (!window.TableCore) {
                console.error('❌ TanStack Table no se pudo inicializar correctamente');
                console.log('🔍 Globals disponibles:', Object.keys(window).filter(k => k.toLowerCase().includes('table') || k.toLowerCase().includes('tanstack')));
            }
        }
        
        if (window.TableCore) {
            console.log('✅ TableCore funciones disponibles:', Object.keys(window.TableCore));
        }
    }

    /**
     * Disparar evento personalizado cuando esté listo
     */
    function dispatchReadyEvent() {
        const event = new CustomEvent('tanstack-table-ready', {
            detail: {
                timestamp: Date.now(),
                source: window.TableCore ? 'success' : 'error'
            }
        });
        
        window.dispatchEvent(event);
        console.log('🎉 Evento tanstack-table-ready disparado');
    }

    /**
     * Manejo de errores de carga
     */
    function handleLoadError() {
        console.error('💥 No se pudo cargar TanStack Table desde ninguna fuente');
        
        // Crear un stub básico para evitar errores
        window.TableCore = {
            createTable: function() {
                throw new Error('TanStack Table no pudo cargarse');
            },
            _isStub: true // Marcar como stub para detección
        };
        
        dispatchReadyEvent();
    }

})();