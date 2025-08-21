/**
 * BaseComponent - Foundation class for all HydroML Alpine.js components
 * 
 * Provides consistent lifecycle management, event handling, state management,
 * and development tools integration for all components in the system.
 */

class BaseComponent {
  /**
   * @param {HTMLElement} element - The DOM element this component is attached to
   * @param {Object} options - Component configuration options
   */
  constructor(element, options = {}) {
    this.element = element;
    this.options = this.validateOptions(options);
    this.state = this.initializeState();
    this.events = new Map();
    this.isInitialized = false;
    this.isMounted = false;
    this.isDestroyed = false;
    
    // Unique component ID for debugging
    this.componentId = this.generateComponentId();
    
    // Development mode features
    if (window.HydroML?.debug) {
      this.setupDevTools();
    }
    
    // Bind lifecycle methods to maintain context
    this.init = this.init.bind(this);
    this.mount = this.mount.bind(this);
    this.update = this.update.bind(this);
    this.destroy = this.destroy.bind(this);
  }
  
  /**
   * Initialize component - called once during component creation
   * Override in subclasses for component-specific initialization
   */
  init() {
    if (this.isInitialized) {
      console.warn(`[${this.constructor.name}] Already initialized`);
      return this;
    }
    
    this.validateElement();
    this.setupEventListeners();
    this.initializeState();
    
    this.isInitialized = true;
    this.emit('component:initialized', { componentId: this.componentId });
    
    return this;
  }
  
  /**
   * Mount component to DOM - called when component becomes active
   * Override in subclasses for mounting logic
   */
  mount() {
    if (!this.isInitialized) {
      throw new Error(`[${this.constructor.name}] Must initialize before mounting`);
    }
    
    if (this.isMounted) {
      console.warn(`[${this.constructor.name}] Already mounted`);
      return this;
    }
    
    this.element.setAttribute('data-component-id', this.componentId);
    this.element.setAttribute('data-component-type', this.constructor.name);
    
    this.isMounted = true;
    this.emit('component:mounted', { componentId: this.componentId });
    
    return this;
  }
  
  /**
   * Update component with new data/options
   * @param {Object} changes - Changes to apply to component
   */
  update(changes = {}) {
    if (this.isDestroyed) {
      console.warn(`[${this.constructor.name}] Cannot update destroyed component`);
      return this;
    }
    
    const previousState = { ...this.state };
    const previousOptions = { ...this.options };
    
    // Update options if provided
    if (changes.options) {
      this.options = { ...this.options, ...this.validateOptions(changes.options) };
    }
    
    // Update state if provided
    if (changes.state) {
      this.setState(changes.state);
    }
    
    this.emit('component:updated', {
      componentId: this.componentId,
      previousState,
      previousOptions,
      changes
    });
    
    return this;
  }
  
  /**
   * Destroy component and clean up resources
   */
  destroy() {
    if (this.isDestroyed) {
      console.warn(`[${this.constructor.name}] Already destroyed`);
      return;
    }
    
    this.cleanupEventListeners();
    this.clearState();
    
    // Remove component attributes
    this.element.removeAttribute('data-component-id');
    this.element.removeAttribute('data-component-type');
    
    this.emit('component:destroyed', { componentId: this.componentId });
    
    this.isDestroyed = true;
    this.isMounted = false;
    this.isInitialized = false;
  }
  
  /**
   * Event System - Emit custom events
   * @param {string} eventName - Name of the event
   * @param {*} data - Data to pass with the event
   */
  emit(eventName, data = null) {
    const event = new CustomEvent(`hydroml:${eventName}`, {
      detail: { component: this, data },
      bubbles: true,
      cancelable: true
    });
    
    this.element.dispatchEvent(event);
    
    // Also emit on internal event system for component-to-component communication
    if (this.events.has(eventName)) {
      this.events.get(eventName).forEach(handler => {
        try {
          handler(data, this);
        } catch (error) {
          console.error(`[${this.constructor.name}] Event handler error:`, error);
        }
      });
    }
    
    return this;
  }
  
  /**
   * Event System - Listen to component events
   * @param {string} eventName - Name of the event to listen to
   * @param {Function} handler - Event handler function
   */
  on(eventName, handler) {
    if (typeof handler !== 'function') {
      throw new Error(`[${this.constructor.name}] Event handler must be a function`);
    }
    
    if (!this.events.has(eventName)) {
      this.events.set(eventName, new Set());
    }
    
    this.events.get(eventName).add(handler);
    return this;
  }
  
  /**
   * Event System - Remove event listener
   * @param {string} eventName - Name of the event
   * @param {Function} handler - Handler to remove
   */
  off(eventName, handler) {
    if (this.events.has(eventName)) {
      this.events.get(eventName).delete(handler);
    }
    return this;
  }
  
  /**
   * State Management - Update component state
   * @param {Object} updates - State updates to apply
   */
  setState(updates) {
    if (typeof updates !== 'object' || updates === null) {
      throw new Error(`[${this.constructor.name}] State updates must be an object`);
    }
    
    const previousState = { ...this.state };
    this.state = { ...this.state, ...updates };
    
    this.emit('state:changed', {
      previousState,
      newState: this.state,
      updates
    });
    
    return this;
  }
  
  /**
   * State Management - Get current state
   * @param {string} key - Optional key to get specific state value
   */
  getState(key = null) {
    return key ? this.state[key] : { ...this.state };
  }
  
  /**
   * Initialize component state - override in subclasses
   */
  initializeState() {
    return {
      isLoading: false,
      hasError: false,
      errorMessage: null,
      isVisible: true,
      isDisabled: false
    };
  }
  
  /**
   * Validate component options - override in subclasses
   * @param {Object} options - Options to validate
   */
  validateOptions(options) {
    const defaults = {
      debug: false,
      theme: 'default',
      lazy: false
    };
    
    return { ...defaults, ...options };
  }
  
  /**
   * Validate that element exists and is valid
   */
  validateElement() {
    if (!this.element || !(this.element instanceof HTMLElement)) {
      throw new Error(`[${this.constructor.name}] Invalid or missing element`);
    }
  }
  
  /**
   * Setup event listeners - override in subclasses
   */
  setupEventListeners() {
    // Base implementation - can be overridden
  }
  
  /**
   * Cleanup event listeners
   */
  cleanupEventListeners() {
    this.events.clear();
  }
  
  /**
   * Clear component state
   */
  clearState() {
    this.state = {};
  }
  
  /**
   * Generate unique component ID for debugging
   */
  generateComponentId() {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substring(2, 8);
    return `${this.constructor.name.toLowerCase()}_${timestamp}_${random}`;
  }
  
  /**
   * Setup development tools integration
   */
  setupDevTools() {
    // Add component to global registry for debugging
    if (!window.HydroML.components) {
      window.HydroML.components = new Map();
    }
    
    window.HydroML.components.set(this.componentId, this);
    
    // Add debug logging
    this.on('component:initialized', () => {
      console.group(`[${this.constructor.name}] Initialized`);
      console.log('Element:', this.element);
      console.log('Options:', this.options);
      console.log('State:', this.state);
      console.groupEnd();
    });
    
    this.on('component:destroyed', () => {
      window.HydroML.components.delete(this.componentId);
      console.log(`[${this.constructor.name}] Destroyed and removed from registry`);
    });
  }
  
  /**
   * Get component information for debugging
   */
  getDebugInfo() {
    return {
      componentId: this.componentId,
      type: this.constructor.name,
      element: this.element,
      state: this.state,
      options: this.options,
      isInitialized: this.isInitialized,
      isMounted: this.isMounted,
      isDestroyed: this.isDestroyed,
      eventListeners: Array.from(this.events.keys())
    };
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BaseComponent;
}

// Global registration for browser usage
if (typeof window !== 'undefined') {
  window.HydroML = window.HydroML || {};
  window.HydroML.BaseComponent = BaseComponent;
}