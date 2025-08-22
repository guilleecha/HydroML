/**
 * Error Handler - Centralized Error Management with Sentry Integration
 * Responsabilidad única: Manejo centralizado de errores con integración Sentry
 * 
 * Filosofía: Single point of error handling, graceful degradation, user-friendly messages
 */

class ErrorHandler {
    constructor() {
        this.sentryEnabled = false;
        this.debugMode = window.DEBUG || false;
        this.fallbackNotifications = true;
        
        // Initialize Sentry if available
        this.initializeSentry();
        
        // Setup global error handlers
        this.setupGlobalHandlers();
    }

    // === SENTRY INITIALIZATION ===

    initializeSentry() {
        // Check if Sentry is available (loaded via CDN or bundle)
        if (typeof Sentry !== 'undefined' && Sentry.init) {
            try {
                // Sentry should be initialized in Django template with DSN
                // We just configure additional options here
                this.sentryEnabled = true;
                
                // Configure user context if available
                if (window.user_info) {
                    Sentry.setUser({
                        id: window.user_info.id,
                        username: window.user_info.username,
                        email: window.user_info.email
                    });
                }

                // Set tags for Data Studio context
                Sentry.setTag('component', 'data-studio');
                Sentry.setTag('datasource_id', window.datasourceId || 'unknown');
                
                console.log('Sentry error handling initialized');
                
            } catch (error) {
                console.warn('Failed to configure Sentry:', error);
                this.sentryEnabled = false;
            }
        } else {
            console.warn('Sentry not available, using fallback error handling');
        }
    }

    // === GLOBAL ERROR HANDLERS ===

    setupGlobalHandlers() {
        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, {
                type: 'unhandled_promise_rejection',
                context: 'global'
            });
        });

        // Global JavaScript errors
        window.addEventListener('error', (event) => {
            this.handleError(event.error || new Error(event.message), {
                type: 'javascript_error',
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                context: 'global'
            });
        });
    }

    // === CORE ERROR HANDLING ===

    handleError(error, context = {}) {
        // Prepare error data
        const errorData = this.prepareErrorData(error, context);
        
        // Log to Sentry if available
        if (this.sentryEnabled) {
            this.logToSentry(error, errorData);
        }
        
        // Log to console in debug mode
        if (this.debugMode) {
            console.error('Data Studio Error:', errorData);
        }
        
        // Show user-friendly notification
        this.showUserNotification(errorData);
        
        // Dispatch error event for components to handle
        this.dispatchErrorEvent(errorData);
    }

    prepareErrorData(error, context) {
        const timestamp = new Date().toISOString();
        
        return {
            message: error.message || 'Unknown error',
            stack: error.stack,
            name: error.name || 'Error',
            timestamp,
            context: {
                component: 'data-studio',
                datasource_id: window.datasourceId,
                user_agent: navigator.userAgent,
                url: window.location.href,
                ...context
            },
            fingerprint: this.generateFingerprint(error, context)
        };
    }

    generateFingerprint(error, context) {
        // Create a unique fingerprint for error grouping
        const components = [
            error.name || 'Error',
            error.message || 'unknown',
            context.type || 'general',
            context.component || 'data-studio'
        ];
        
        return components.join('|').replace(/[^a-zA-Z0-9|]/g, '_');
    }

    // === SENTRY INTEGRATION ===

    logToSentry(error, errorData) {
        try {
            // Set additional context
            Sentry.withScope((scope) => {
                // Set level based on error type
                scope.setLevel(this.getSentryLevel(errorData.context.type));
                
                // Set tags
                scope.setTag('error_type', errorData.context.type);
                scope.setTag('component', errorData.context.component);
                
                if (errorData.context.datasource_id) {
                    scope.setTag('datasource_id', errorData.context.datasource_id);
                }
                
                // Set extra context
                scope.setContext('error_details', {
                    timestamp: errorData.timestamp,
                    fingerprint: errorData.fingerprint,
                    context: errorData.context
                });
                
                // Capture the error
                Sentry.captureException(error);
            });
            
        } catch (sentryError) {
            console.warn('Failed to log error to Sentry:', sentryError);
        }
    }

    getSentryLevel(errorType) {
        const levelMap = {
            'fatal': 'fatal',
            'critical': 'error',
            'session_error': 'error',
            'grid_error': 'error',
            'filter_error': 'warning',
            'navigation_error': 'warning',
            'api_error': 'error',
            'validation_error': 'warning',
            'network_error': 'error',
            'javascript_error': 'error',
            'unhandled_promise_rejection': 'error'
        };
        
        return levelMap[errorType] || 'error';
    }

    // === USER NOTIFICATIONS ===

    showUserNotification(errorData) {
        const userMessage = this.getUserFriendlyMessage(errorData);
        
        // Try to use the app's notification system
        if (window.dataStudioNotifications && window.dataStudioNotifications.show) {
            window.dataStudioNotifications.show(userMessage, 'error', 5000);
        } else if (this.fallbackNotifications) {
            // Fallback notification
            this.showFallbackNotification(userMessage);
        }
    }

    getUserFriendlyMessage(errorData) {
        const messageMap = {
            'session_error': 'Error en la sesión. Por favor, recarga la página.',
            'grid_error': 'Error en la tabla de datos. Algunos datos pueden no mostrarse correctamente.',
            'filter_error': 'Error en los filtros. Por favor, intenta nuevamente.',
            'navigation_error': 'Error de navegación. La página puede no responder correctamente.',
            'api_error': 'Error de conexión. Por favor, verifica tu conexión a internet.',
            'network_error': 'Error de red. Por favor, intenta más tarde.',
            'validation_error': 'Error de validación. Por favor, verifica los datos ingresados.',
            'fatal': 'Error crítico. La página será recargada automáticamente.'
        };
        
        const contextType = errorData.context.type;
        return messageMap[contextType] || 'Ha ocurrido un error inesperado. Por favor, intenta nuevamente.';
    }

    showFallbackNotification(message) {
        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 max-w-sm';
        toast.innerHTML = `
            <div class="flex items-center">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                </svg>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    // === ERROR EVENT DISPATCH ===

    dispatchErrorEvent(errorData) {
        window.dispatchEvent(new CustomEvent('data-studio-error', {
            detail: errorData
        }));
    }

    // === SPECIFIC ERROR HANDLERS ===

    handleSessionError(error, additionalContext = {}) {
        this.handleError(error, {
            type: 'session_error',
            component: 'session-manager',
            ...additionalContext
        });
    }

    handleGridError(error, additionalContext = {}) {
        this.handleError(error, {
            type: 'grid_error',
            component: 'grid-controller',
            ...additionalContext
        });
    }

    handleFilterError(error, additionalContext = {}) {
        this.handleError(error, {
            type: 'filter_error',
            component: 'filter-system',
            ...additionalContext
        });
    }

    handleNavigationError(error, additionalContext = {}) {
        this.handleError(error, {
            type: 'navigation_error',
            component: 'navigation-manager',
            ...additionalContext
        });
    }

    handleAPIError(error, additionalContext = {}) {
        this.handleError(error, {
            type: 'api_error',
            component: 'api-client',
            ...additionalContext
        });
    }

    handleValidationError(error, additionalContext = {}) {
        this.handleError(error, {
            type: 'validation_error',
            severity: 'warning',
            ...additionalContext
        });
    }

    handleFatalError(error, additionalContext = {}) {
        this.handleError(error, {
            type: 'fatal',
            component: 'data-studio-main',
            ...additionalContext
        });
        
        // Create detailed error message for debugging
        const errorDetails = {
            message: error.message || 'Unknown error',
            component: additionalContext.component || 'unknown',
            operation: additionalContext.operation || 'unknown',
            timestamp: new Date().toISOString(),
            stack: error.stack
        };
        
        // More specific error message with context
        const detailedMessage = `ERROR CRÍTICO DETECTADO:
        
🔍 Componente: ${errorDetails.component}
⚙️ Operación: ${errorDetails.operation}  
📄 Error: ${errorDetails.message}
🕐 Tiempo: ${errorDetails.timestamp}

¿Deseas recargar la página para intentar solucionarlo?`;
        
        // For fatal errors, consider reloading the page
        if (confirm(detailedMessage)) {
            window.location.reload();
        }
    }

    // === UTILITY METHODS ===

    captureMessage(message, level = 'info', context = {}) {
        if (this.sentryEnabled) {
            Sentry.withScope((scope) => {
                scope.setLevel(level);
                scope.setContext('message_context', context);
                Sentry.captureMessage(message);
            });
        }
        
        if (this.debugMode) {
            console.log(`Data Studio ${level.toUpperCase()}:`, message, context);
        }
    }

    captureBreadcrumb(message, category = 'default', data = {}) {
        if (this.sentryEnabled) {
            Sentry.addBreadcrumb({
                message,
                category,
                data,
                timestamp: Date.now() / 1000
            });
        }
    }

    setUserContext(userInfo) {
        if (this.sentryEnabled) {
            Sentry.setUser(userInfo);
        }
    }

    setExtraContext(key, value) {
        if (this.sentryEnabled) {
            Sentry.setContext(key, value);
        }
    }

    // === STATUS ===

    isHealthy() {
        return {
            sentry_enabled: this.sentryEnabled,
            debug_mode: this.debugMode,
            fallback_notifications: this.fallbackNotifications
        };
    }
}

// Create global instance
window.DataStudioErrorHandler = new ErrorHandler();

// Export removed for script tag compatibility
window.ErrorHandler = ErrorHandler;