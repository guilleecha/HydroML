/**
 * HydroML Component System - Main Application File
 * 
 * Initializes the component system, loads core components, and sets up
 * the global API for component management throughout the application.
 */

// Initialize HydroML namespace
window.HydroML = window.HydroML || {
  debug: document.querySelector('meta[name="debug"]')?.content === 'true',
  version: '2.0.0',
  components: new Map(),
  instances: new Map()
};

/**
 * Component System Initialization
 */
document.addEventListener('alpine:init', () => {
  console.log('[HydroML] Initializing component system...');
  
  // Register core Alpine.js components
  registerAlpineComponents();
  
  // Setup global event handling
  setupGlobalEventHandling();
  
  // Initialize theme system integration
  initializeThemeIntegration();
  
  console.log('[HydroML] Component system initialized');
});

/**
 * Register Alpine.js components with the component registry
 */
function registerAlpineComponents() {
  // Register theme switcher component (already created)
  if (window.HydroML.registry) {
    window.HydroML.registry.register('theme-switcher', {
      component: function() {
        return {
          currentTheme: 'light',
          availableThemes: [
            { value: 'light', label: 'Light', current: true },
            { value: 'dark', label: 'Dark', current: false },
            { value: 'darcula', label: 'Darcula', current: false }
          ],
          
          init() {
            const savedTheme = localStorage.getItem('hydroml-theme');
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            
            this.currentTheme = savedTheme || systemTheme;
            this.applyTheme(this.currentTheme);
            this.updateThemeState();
            
            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
              if (!localStorage.getItem('hydroml-theme')) {
                this.currentTheme = e.matches ? 'dark' : 'light';
                this.applyTheme(this.currentTheme);
                this.updateThemeState();
              }
            });
          },
          
          toggleTheme() {
            const themeOrder = ['light', 'dark', 'darcula'];
            const currentIndex = themeOrder.indexOf(this.currentTheme);
            const nextIndex = (currentIndex + 1) % themeOrder.length;
            
            this.setTheme(themeOrder[nextIndex]);
          },
          
          setTheme(theme) {
            this.currentTheme = theme;
            this.applyTheme(theme);
            this.updateThemeState();
            localStorage.setItem('hydroml-theme', theme);
            
            window.dispatchEvent(new CustomEvent('theme-changed', { 
              detail: { theme: theme } 
            }));
          },
          
          applyTheme(theme) {
            const html = document.documentElement;
            
            html.classList.remove('dark', 'light');
            html.removeAttribute('data-theme');
            
            if (theme === 'dark') {
              html.classList.add('dark');
              html.setAttribute('data-theme', 'dark');
            } else if (theme === 'darcula') {
              html.setAttribute('data-theme', 'darcula');
            } else {
              html.classList.add('light');
              html.setAttribute('data-theme', 'light');
            }
            
            document.body.classList.add('transition-theme');
            setTimeout(() => {
              document.body.classList.remove('transition-theme');
            }, 300);
          },
          
          updateThemeState() {
            this.availableThemes.forEach(theme => {
              theme.current = theme.value === this.currentTheme;
            });
          },
          
          getThemeIcon(theme) {
            const icons = {
              light: '☀️',
              dark: '🌙',
              darcula: '🔧'
            };
            return icons[theme] || '🎨';
          },
          
          getThemeLabel(theme) {
            const theme_obj = this.availableThemes.find(t => t.value === theme);
            return theme_obj ? theme_obj.label : theme;
          }
        };
      },
      autoInit: true,
      selector: '[x-data*="themeSwitcher"]'
    });
  }
  
  // Register data component for tables and lists
  Alpine.data('dataComponent', () => ({
    items: [],
    filteredItems: [],
    searchTerm: '',
    sortColumn: null,
    sortDirection: 'asc',
    page: 1,
    perPage: 10,
    
    init() {
      this.loadData();
      
      // Watch for search term changes
      this.$watch('searchTerm', () => {
        this.filterItems();
        this.page = 1; // Reset to first page
      });
    },
    
    async loadData() {
      const dataUrl = this.$el.getAttribute('data-url');
      if (!dataUrl) return;
      
      try {
        const response = await fetch(dataUrl);
        this.items = await response.json();
        this.filterItems();
      } catch (error) {
        console.error('[DataComponent] Failed to load data:', error);
      }
    },
    
    filterItems() {
      if (!this.searchTerm) {
        this.filteredItems = [...this.items];
      } else {
        const term = this.searchTerm.toLowerCase();
        this.filteredItems = this.items.filter(item => 
          Object.values(item).some(value => 
            String(value).toLowerCase().includes(term)
          )
        );
      }
      
      this.sortItems();
    },
    
    sortBy(column) {
      if (this.sortColumn === column) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortColumn = column;
        this.sortDirection = 'asc';
      }
      
      this.sortItems();
    },
    
    sortItems() {
      if (!this.sortColumn) return;
      
      this.filteredItems.sort((a, b) => {
        const aVal = a[this.sortColumn];
        const bVal = b[this.sortColumn];
        
        if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    },
    
    get paginatedItems() {
      const start = (this.page - 1) * this.perPage;
      const end = start + this.perPage;
      return this.filteredItems.slice(start, end);
    },
    
    get totalPages() {
      return Math.ceil(this.filteredItems.length / this.perPage);
    },
    
    nextPage() {
      if (this.page < this.totalPages) {
        this.page++;
      }
    },
    
    prevPage() {
      if (this.page > 1) {
        this.page--;
      }
    }
  }));
  
  // Register modal component
  Alpine.data('modalComponent', (options = {}) => ({
    isOpen: false,
    backdrop: options.backdrop !== false,
    keyboard: options.keyboard !== false,
    
    init() {
      // Close on Escape key
      if (this.keyboard) {
        document.addEventListener('keydown', (e) => {
          if (e.key === 'Escape' && this.isOpen) {
            this.close();
          }
        });
      }
    },
    
    open() {
      this.isOpen = true;
      document.body.classList.add('modal-open');
      
      // Focus trap
      this.$nextTick(() => {
        const focusableElements = this.$el.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
          focusableElements[0].focus();
        }
      });
      
      this.$dispatch('modal:opened');
    },
    
    close() {
      this.isOpen = false;
      document.body.classList.remove('modal-open');
      this.$dispatch('modal:closed');
    },
    
    closeOnBackdrop(event) {
      if (this.backdrop && event.target === this.$el) {
        this.close();
      }
    }
  }));
  
  // Register notification component
  Alpine.data('notificationComponent', () => ({
    notifications: [],
    
    init() {
      // Listen for global notification events
      window.addEventListener('hydroml:notify', (event) => {
        this.addNotification(event.detail);
      });
    },
    
    addNotification(notification) {
      const id = Date.now() + Math.random();
      const notificationWithId = {
        id,
        type: 'info',
        title: '',
        message: '',
        duration: 5000,
        persistent: false,
        ...notification
      };
      
      this.notifications.push(notificationWithId);
      
      // Auto-remove after duration
      if (!notificationWithId.persistent && notificationWithId.duration > 0) {
        setTimeout(() => {
          this.removeNotification(id);
        }, notificationWithId.duration);
      }
    },
    
    removeNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index > -1) {
        this.notifications.splice(index, 1);
      }
    },
    
    getIcon(type) {
      const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
      };
      return icons[type] || icons.info;
    }
  }));
}

/**
 * Setup global event handling for component communication
 */
function setupGlobalEventHandling() {
  // Global notification system
  window.HydroML.notify = function(notification) {
    window.dispatchEvent(new CustomEvent('hydroml:notify', {
      detail: notification
    }));
  };
  
  // Global theme change handler
  window.addEventListener('theme-changed', (event) => {
    const theme = event.detail.theme;
    
    // Update all chart components
    document.querySelectorAll('[data-component="chart"]').forEach(element => {
      const event = new CustomEvent('chart:theme-changed', {
        detail: { theme },
        bubbles: true
      });
      element.dispatchEvent(event);
    });
    
    // Update all data visualization components
    document.querySelectorAll('[data-component="visualization"]').forEach(element => {
      const event = new CustomEvent('visualization:theme-changed', {
        detail: { theme },
        bubbles: true
      });
      element.dispatchEvent(event);
    });
  });
  
  // Global content update handler for dynamic content
  window.HydroML.updateContent = function(root = document) {
    window.dispatchEvent(new CustomEvent('hydroml:content-updated', {
      detail: { root }
    }));
  };
}

/**
 * Initialize theme system integration
 */
function initializeThemeIntegration() {
  // Apply initial theme
  const savedTheme = localStorage.getItem('hydroml-theme');
  if (savedTheme) {
    const html = document.documentElement;
    
    html.classList.remove('dark', 'light');
    html.removeAttribute('data-theme');
    
    if (savedTheme === 'dark') {
      html.classList.add('dark');
      html.setAttribute('data-theme', 'dark');
    } else if (savedTheme === 'darcula') {
      html.setAttribute('data-theme', 'darcula');
    } else {
      html.classList.add('light');
      html.setAttribute('data-theme', 'light');
    }
  }
}

/**
 * Component helper functions for global access
 */
window.HydroML.helpers = {
  /**
   * Get component instance by element
   * @param {HTMLElement} element - Element with component
   */
  getComponent(element) {
    const componentId = element.getAttribute('data-component-id');
    return componentId ? window.HydroML.components.get(componentId) : null;
  },
  
  /**
   * Create notification
   * @param {string} message - Notification message
   * @param {string} type - Notification type (success, error, warning, info)
   * @param {Object} options - Additional options
   */
  notify(message, type = 'info', options = {}) {
    window.HydroML.notify({
      message,
      type,
      ...options
    });
  },
  
  /**
   * Debounce function for performance optimization
   * @param {Function} func - Function to debounce
   * @param {number} wait - Wait time in milliseconds
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },
  
  /**
   * Throttle function for performance optimization
   * @param {Function} func - Function to throttle
   * @param {number} limit - Limit in milliseconds
   */
  throttle(func, limit) {
    let inThrottle;
    return function(...args) {
      if (!inThrottle) {
        func.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  }
};

// Log system initialization
console.log('[HydroML] Component system loaded successfully');

// Expose main API
window.HydroML.version = '2.0.0';
window.HydroML.ready = true;