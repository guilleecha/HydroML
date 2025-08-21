/**
 * ComponentRegistry - Centralized component registration and management system
 * 
 * Handles component registration, dependency resolution, lazy loading,
 * and lifecycle management for all HydroML components.
 */

class ComponentRegistry {
  constructor() {
    this.components = new Map();
    this.instances = new Map();
    this.loading = new Map();
    this.dependencies = new Map();
    this.hooks = new Map();
    
    // Performance tracking
    this.metrics = {
      registrationTime: new Map(),
      loadTime: new Map(),
      instantiationTime: new Map()
    };
    
    // Development mode features
    this.debug = window.HydroML?.debug || false;
    
    this.setupGlobalEventListeners();
  }
  
  /**
   * Register a component in the registry
   * @param {string} name - Component name
   * @param {Object} config - Component configuration
   */
  register(name, config) {
    const startTime = performance.now();
    
    if (this.components.has(name)) {
      console.warn(`[ComponentRegistry] Component '${name}' is already registered`);
      return this;
    }
    
    const componentConfig = this.validateComponentConfig(name, config);
    
    this.components.set(name, componentConfig);
    
    // Register dependencies
    if (componentConfig.dependencies?.length > 0) {
      this.dependencies.set(name, componentConfig.dependencies);
    }
    
    // Track registration time
    const registrationTime = performance.now() - startTime;
    this.metrics.registrationTime.set(name, registrationTime);
    
    if (this.debug) {
      console.log(`[ComponentRegistry] Registered '${name}' in ${registrationTime.toFixed(2)}ms`);
    }
    
    this.emit('component:registered', { name, config: componentConfig });
    
    return this;
  }
  
  /**
   * Validate component configuration
   * @param {string} name - Component name
   * @param {Object} config - Component configuration
   */
  validateComponentConfig(name, config) {
    if (!config.component && !config.factory && !config.module) {
      throw new Error(`[ComponentRegistry] Component '${name}' must have component, factory, or module`);
    }
    
    const defaults = {
      version: '1.0.0',
      lazy: false,
      singleton: false,
      dependencies: [],
      module: null,
      factory: null,
      component: null,
      autoInit: true,
      selector: `[data-component="${name}"]`
    };
    
    return { ...defaults, ...config, name };
  }
  
  /**
   * Get a component by name (lazy load if necessary)
   * @param {string} name - Component name
   */
  async get(name) {
    if (!this.components.has(name)) {
      throw new Error(`[ComponentRegistry] Component '${name}' is not registered`);
    }
    
    const config = this.components.get(name);
    
    // If component is already loaded, return it
    if (config.component) {
      return config.component;
    }
    
    // If component is currently loading, wait for it
    if (this.loading.has(name)) {
      return this.loading.get(name);
    }
    
    // Load component
    const loadPromise = this.loadComponent(name, config);
    this.loading.set(name, loadPromise);
    
    try {
      const component = await loadPromise;
      this.loading.delete(name);
      return component;
    } catch (error) {
      this.loading.delete(name);
      throw error;
    }
  }
  
  /**
   * Load a component (handle modules, factories, etc.)
   * @param {string} name - Component name
   * @param {Object} config - Component configuration
   */
  async loadComponent(name, config) {
    const startTime = performance.now();
    
    try {
      let ComponentClass;
      
      // Load from module
      if (config.module) {
        const module = await import(config.module);
        ComponentClass = module.default || module[name] || module;
      }
      // Use factory function
      else if (config.factory) {
        ComponentClass = await config.factory();
      }
      // Component is already provided
      else if (config.component) {
        ComponentClass = config.component;
      }
      
      if (!ComponentClass) {
        throw new Error(`[ComponentRegistry] Failed to load component '${name}'`);
      }
      
      // Update config with loaded component
      config.component = ComponentClass;
      
      // Track load time
      const loadTime = performance.now() - startTime;
      this.metrics.loadTime.set(name, loadTime);
      
      if (this.debug) {
        console.log(`[ComponentRegistry] Loaded '${name}' in ${loadTime.toFixed(2)}ms`);
      }
      
      this.emit('component:loaded', { name, component: ComponentClass });
      
      return ComponentClass;
      
    } catch (error) {
      console.error(`[ComponentRegistry] Failed to load component '${name}':`, error);
      throw error;
    }
  }
  
  /**
   * Create an instance of a component
   * @param {string} name - Component name
   * @param {HTMLElement} element - Element to attach component to
   * @param {Object} options - Component options
   */
  async create(name, element, options = {}) {
    const startTime = performance.now();
    
    // Check for singleton
    const config = this.components.get(name);
    if (config?.singleton) {
      const existingInstance = this.instances.get(name);
      if (existingInstance) {
        return existingInstance;
      }
    }
    
    // Load dependencies first
    await this.loadDependencies(name);
    
    // Get component class
    const ComponentClass = await this.get(name);
    
    // Create instance
    const instance = new ComponentClass(element, options);
    
    // Initialize if auto-init is enabled
    if (config.autoInit) {
      instance.init();
    }
    
    // Store instance
    const instanceId = instance.componentId || `${name}_${Date.now()}`;
    this.instances.set(instanceId, instance);
    
    // Store singleton reference
    if (config.singleton) {
      this.instances.set(name, instance);
    }
    
    // Track instantiation time
    const instantiationTime = performance.now() - startTime;
    this.metrics.instantiationTime.set(instanceId, instantiationTime);
    
    if (this.debug) {
      console.log(`[ComponentRegistry] Created '${name}' instance in ${instantiationTime.toFixed(2)}ms`);
    }
    
    this.emit('component:created', { name, instance, element });
    
    return instance;
  }

  /**
   * Create Alpine.js data for a component (synchronous for template use)
   * @param {string} name - Component name
   * @param {Object} config - Component configuration
   */
  createAlpineData(name, config = {}) {
    try {
      if (!this.components.has(name)) {
        console.warn(`[ComponentRegistry] Component '${name}' is not registered`);
        return {};
      }
      
      const componentConfig = this.components.get(name);
      const ComponentClass = componentConfig.component;
      
      if (!ComponentClass) {
        console.warn(`[ComponentRegistry] Component '${name}' class not available`);
        return {};
      }
      
      // Check if component has Alpine data creation method
      if (typeof ComponentClass.createAlpineData === 'function') {
        return ComponentClass.createAlpineData(config);
      }
      
      // Fallback: create instance and get Alpine data
      const instance = new ComponentClass();
      if (typeof instance.getAlpineData === 'function') {
        return instance.getAlpineData();
      }
      
      console.warn(`[ComponentRegistry] Component '${name}' does not support Alpine.js data creation`);
      return {};
      
    } catch (error) {
      console.error(`[ComponentRegistry] Failed to create Alpine data for '${name}':`, error);
      return {};
    }
  }
  
  /**
   * Load component dependencies
   * @param {string} name - Component name
   */
  async loadDependencies(name) {
    const dependencies = this.dependencies.get(name);
    if (!dependencies || dependencies.length === 0) {
      return;
    }
    
    const loadPromises = dependencies.map(depName => {
      if (this.components.has(depName)) {
        return this.get(depName);
      } else {
        console.warn(`[ComponentRegistry] Dependency '${depName}' for '${name}' is not registered`);
        return Promise.resolve();
      }
    });
    
    await Promise.all(loadPromises);
  }
  
  /**
   * Auto-discover and initialize components in the DOM
   * @param {HTMLElement} root - Root element to search (defaults to document)
   */
  async autoInit(root = document) {
    const discoveries = [];
    
    // Find all components in the DOM
    this.components.forEach((config, name) => {
      const elements = root.querySelectorAll(config.selector);
      
      elements.forEach(element => {
        // Skip if already initialized
        if (element.hasAttribute('data-component-initialized')) {
          return;
        }
        
        // Mark as initialized to prevent double initialization
        element.setAttribute('data-component-initialized', 'true');
        
        // Extract options from data attributes
        const options = this.extractElementOptions(element);
        
        // Create component instance
        discoveries.push(
          this.create(name, element, options).catch(error => {
            console.error(`[ComponentRegistry] Failed to auto-init '${name}':`, error);
            element.removeAttribute('data-component-initialized');
          })
        );
      });
    });
    
    const instances = await Promise.allSettled(discoveries);
    const successCount = instances.filter(result => result.status === 'fulfilled').length;
    const failureCount = instances.length - successCount;
    
    if (this.debug) {
      console.log(`[ComponentRegistry] Auto-initialized ${successCount} components, ${failureCount} failed`);
    }
    
    this.emit('components:auto-initialized', { successCount, failureCount });
    
    return instances;
  }
  
  /**
   * Extract component options from element data attributes
   * @param {HTMLElement} element - Element to extract options from
   */
  extractElementOptions(element) {
    const options = {};
    
    // Extract data-option-* attributes
    Array.from(element.attributes).forEach(attr => {
      if (attr.name.startsWith('data-option-')) {
        const optionName = attr.name.substring('data-option-'.length);
        const camelCaseName = optionName.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
        
        // Try to parse as JSON, fallback to string
        try {
          options[camelCaseName] = JSON.parse(attr.value);
        } catch {
          options[camelCaseName] = attr.value;
        }
      }
    });
    
    return options;
  }
  
  /**
   * Destroy a component instance
   * @param {string} instanceId - Instance ID or component name (for singletons)
   */
  destroy(instanceId) {
    const instance = this.instances.get(instanceId);
    if (!instance) {
      console.warn(`[ComponentRegistry] Instance '${instanceId}' not found`);
      return;
    }
    
    // Call destroy method if available
    if (typeof instance.destroy === 'function') {
      instance.destroy();
    }
    
    // Remove from registry
    this.instances.delete(instanceId);
    
    this.emit('component:destroyed', { instanceId, instance });
  }
  
  /**
   * Destroy all component instances
   */
  destroyAll() {
    const instanceIds = Array.from(this.instances.keys());
    instanceIds.forEach(instanceId => this.destroy(instanceId));
    
    this.emit('components:all-destroyed');
  }
  
  /**
   * Register a lifecycle hook
   * @param {string} event - Event name (registered, loaded, created, destroyed)
   * @param {Function} handler - Hook handler
   */
  registerHook(event, handler) {
    if (!this.hooks.has(event)) {
      this.hooks.set(event, new Set());
    }
    
    this.hooks.get(event).add(handler);
    return this;
  }
  
  /**
   * Emit an event to all registered hooks
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  emit(event, data) {
    if (this.hooks.has(event)) {
      this.hooks.get(event).forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`[ComponentRegistry] Hook error for '${event}':`, error);
        }
      });
    }
    
    // Also emit as custom event
    const customEvent = new CustomEvent(`hydroml:registry:${event}`, {
      detail: data,
      bubbles: true
    });
    
    document.dispatchEvent(customEvent);
  }
  
  /**
   * Setup global event listeners
   */
  setupGlobalEventListeners() {
    // Auto-initialize components when DOM content is loaded
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        this.autoInit();
      });
    } else {
      // DOM is already loaded
      setTimeout(() => this.autoInit(), 0);
    }
    
    // Re-initialize components when new content is added (e.g., AJAX)
    document.addEventListener('hydroml:content-updated', (event) => {
      const root = event.detail?.root || document;
      this.autoInit(root);
    });
  }
  
  /**
   * Get registry statistics and metrics
   */
  getStats() {
    return {
      registeredComponents: this.components.size,
      activeInstances: this.instances.size,
      loadingComponents: this.loading.size,
      metrics: {
        averageRegistrationTime: this.calculateAverageTime(this.metrics.registrationTime),
        averageLoadTime: this.calculateAverageTime(this.metrics.loadTime),
        averageInstantiationTime: this.calculateAverageTime(this.metrics.instantiationTime)
      }
    };
  }
  
  /**
   * Calculate average time from metrics map
   * @param {Map} timeMap - Map of times
   */
  calculateAverageTime(timeMap) {
    if (timeMap.size === 0) return 0;
    
    const times = Array.from(timeMap.values());
    return times.reduce((sum, time) => sum + time, 0) / times.length;
  }
  
  /**
   * Get list of registered components
   */
  list() {
    return Array.from(this.components.keys());
  }
  
  /**
   * Check if a component is registered
   * @param {string} name - Component name
   */
  has(name) {
    return this.components.has(name);
  }
  
  /**
   * Clear all registered components and instances
   */
  clear() {
    this.destroyAll();
    this.components.clear();
    this.dependencies.clear();
    this.hooks.clear();
    this.metrics.registrationTime.clear();
    this.metrics.loadTime.clear();
    this.metrics.instantiationTime.clear();
  }
}

// Create singleton instance
const componentRegistry = new ComponentRegistry();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = componentRegistry;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.HydroML = window.HydroML || {};
  window.HydroML.ComponentRegistry = ComponentRegistry;
  window.HydroML.registry = componentRegistry;
  window.ComponentRegistry = componentRegistry; // Make directly available for Alpine.js templates
}