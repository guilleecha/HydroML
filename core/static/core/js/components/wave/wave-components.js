/**
 * Wave Components Library - Main entry point
 * Part of HydroML Wave-Inspired Component Library
 * 
 * This file provides centralized registration and initialization
 * for all Wave components with monochromatic design system.
 */

class WaveComponents {
    constructor() {
        this.components = new Map();
        this.initialized = false;
        this.config = {
            // Global theme configuration
            theme: 'light', // light, dark, darcula
            
            // Design system tokens
            colors: {
                primary: '#374151',   // Gray-700
                secondary: '#6B7280', // Gray-500
                success: '#10B981',   // Emerald-500 (muted)
                warning: '#F59E0B',   // Amber-500 (muted)
                error: '#EF4444',     // Red-500 (muted)
                info: '#3B82F6'       // Blue-500 (muted)
            },
            
            // Component defaults
            defaults: {
                animation: true,
                animationDuration: 200,
                focusTrap: true,
                accessibility: true
            }
        };
    }

    /**
     * Initialize all Wave components
     */
    init(config = {}) {
        if (this.initialized) return;
        
        // Merge configuration
        this.config = { ...this.config, ...config };
        
        // Register all components
        this.registerComponents();
        
        // Setup global Alpine.js components
        this.setupAlpineComponents();
        
        // Setup global event listeners
        this.setupGlobalEvents();
        
        // Initialize CSS custom properties
        this.initializeDesignTokens();
        
        this.initialized = true;
        
        // Emit global initialization event
        this.emit('wave:initialized', { config: this.config });
        
        console.log('🌊 Wave Components Library initialized');
    }

    /**
     * Register all Wave component classes
     */
    registerComponents() {
        // Form Components - Only register components that exist
        if (typeof WaveInput !== 'undefined') this.register('WaveInput', WaveInput);
        if (typeof WaveButton !== 'undefined') this.register('WaveButton', WaveButton);
        if (typeof WaveSelect !== 'undefined') this.register('WaveSelect', WaveSelect);
        
        // Data Display Components - Only register components that exist
        if (typeof WaveTable !== 'undefined') this.register('WaveTable', WaveTable);
        if (typeof WaveBadge !== 'undefined') this.register('WaveBadge', WaveBadge);
        
        // Navigation Components - Only register components that exist
        if (typeof WaveTabs !== 'undefined') this.register('WaveTabs', WaveTabs);
        if (typeof WaveHeadbar !== 'undefined') this.register('WaveHeadbar', WaveHeadbar);
        
        // Interactive Components - Only register components that exist
        if (typeof WaveDropdown !== 'undefined') this.register('WaveDropdown', WaveDropdown);
        
        // Feedback Components - Only register components that exist
        if (typeof WaveModal !== 'undefined') this.register('WaveModal', WaveModal);
        if (typeof WaveToast !== 'undefined') this.register('WaveToast', WaveToast);
    }

    /**
     * Register a component class
     */
    register(name, componentClass) {
        this.components.set(name, componentClass);
        
        // Also register with global ComponentRegistry if available
        if (typeof window !== 'undefined' && window.ComponentRegistry) {
            window.ComponentRegistry.register(name, componentClass);
        }
    }

    /**
     * Get a registered component class
     */
    get(name) {
        return this.components.get(name);
    }

    /**
     * Setup Alpine.js component integrations
     */
    setupAlpineComponents() {
        if (typeof Alpine === 'undefined') {
            console.warn('Alpine.js not found. Wave components require Alpine.js for full functionality.');
            return;
        }

        // Global Wave component data
        Alpine.data('waveComponents', () => ({
            theme: this.config.theme,
            
            // Theme switching
            setTheme(theme) {
                this.theme = theme;
                document.documentElement.setAttribute('data-theme', theme);
                this.emit('wave:theme-change', { theme });
            },
            
            // Utility methods
            emit(event, data) {
                document.dispatchEvent(new CustomEvent(event, { detail: data }));
            },
            
            // Component factory
            createComponent(type, element, config = {}) {
                const ComponentClass = WaveComponents.instance.get(type);
                if (!ComponentClass) {
                    console.warn(`Wave component '${type}' not found`);
                    return null;
                }
                
                const component = new ComponentClass();
                return component.init(element, config);
            }
        }));

        // Auto-initialize components with data-wave attributes
        Alpine.data('waveAutoInit', () => ({
            init() {
                const waveType = this.$el.getAttribute('data-wave');
                if (waveType) {
                    const config = this.parseConfig(this.$el.getAttribute('data-wave-config'));
                    this.createComponent(waveType, this.$el, config);
                }
            },
            
            parseConfig(configStr) {
                if (!configStr) return {};
                try {
                    return JSON.parse(configStr);
                } catch (e) {
                    console.warn('Invalid Wave component config:', configStr);
                    return {};
                }
            }
        }));
    }

    /**
     * Setup global event listeners
     */
    setupGlobalEvents() {
        // Theme system integration
        document.addEventListener('wave:theme-change', (event) => {
            this.config.theme = event.detail.theme;
            this.updateDesignTokens();
        });
        
        // Global keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            this.handleGlobalKeyboard(event);
        });
        
        // Auto-initialize on DOM changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        this.autoInitializeComponents(node);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * Auto-initialize components in a given element
     */
    autoInitializeComponents(element = document) {
        const waveElements = element.querySelectorAll('[data-wave]');
        waveElements.forEach((el) => {
            if (!el.hasAttribute('data-wave-initialized')) {
                const waveType = el.getAttribute('data-wave');
                const configStr = el.getAttribute('data-wave-config');
                const config = configStr ? JSON.parse(configStr) : {};
                
                this.createComponent(waveType, el, config);
                el.setAttribute('data-wave-initialized', 'true');
            }
        });
    }

    /**
     * Create a component instance
     */
    createComponent(type, element, config = {}) {
        const ComponentClass = this.get(type);
        if (!ComponentClass) {
            console.warn(`Wave component '${type}' not found`);
            return null;
        }
        
        const component = new ComponentClass();
        return component.init(element, { ...this.config.defaults, ...config });
    }

    /**
     * Initialize design tokens as CSS custom properties
     */
    initializeDesignTokens() {
        const root = document.documentElement;
        
        // Color tokens
        Object.entries(this.config.colors).forEach(([name, value]) => {
            root.style.setProperty(`--wave-color-${name}`, value);
        });
        
        // Animation tokens
        root.style.setProperty('--wave-animation-duration', `${this.config.defaults.animationDuration}ms`);
        
        // Theme attribute
        root.setAttribute('data-theme', this.config.theme);
    }

    /**
     * Update design tokens when configuration changes
     */
    updateDesignTokens() {
        this.initializeDesignTokens();
    }

    /**
     * Handle global keyboard shortcuts
     */
    handleGlobalKeyboard(event) {
        // Ctrl/Cmd + Shift + T: Toggle theme
        if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'T') {
            event.preventDefault();
            this.toggleTheme();
        }
        
        // Escape: Close all modals/dropdowns
        if (event.key === 'Escape') {
            this.closeAllOverlays();
        }
    }

    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const newTheme = this.config.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    /**
     * Set theme
     */
    setTheme(theme) {
        this.config.theme = theme;
        this.updateDesignTokens();
        this.emit('wave:theme-change', { theme });
    }

    /**
     * Close all overlay components (modals, dropdowns, etc.)
     */
    closeAllOverlays() {
        this.emit('wave:close-overlays');
    }

    /**
     * Emit global event
     */
    emit(event, data = {}) {
        document.dispatchEvent(new CustomEvent(event, { detail: data }));
    }

    /**
     * Get current theme
     */
    getTheme() {
        return this.config.theme;
    }

    /**
     * Get configuration
     */
    getConfig() {
        return { ...this.config };
    }

    /**
     * Update configuration
     */
    updateConfig(updates) {
        this.config = { ...this.config, ...updates };
        this.updateDesignTokens();
        this.emit('wave:config-change', { config: this.config });
    }

    // Utility methods for component integration
    static toast = {
        success: (message, options) => WaveToast.success(message, options),
        error: (message, options) => WaveToast.error(message, options),
        warning: (message, options) => WaveToast.warning(message, options),
        info: (message, options) => WaveToast.info(message, options),
        show: (message, options) => WaveToast.show(message, options)
    };

    static modal = {
        create: (options) => WaveModal.create(options),
        confirm: (options) => WaveModal.confirm(options),
        alert: (options) => WaveModal.alert(options)
    };
}

// Create global instance
WaveComponents.instance = new WaveComponents();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        WaveComponents.instance.init();
    });
} else {
    WaveComponents.instance.init();
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WaveComponents;
}

// Global access
if (typeof window !== 'undefined') {
    window.WaveComponents = WaveComponents;
    window.Wave = WaveComponents.instance;
    
    // Convenient global shortcuts
    window.Toast = WaveComponents.toast;
    window.Modal = WaveComponents.modal;
}