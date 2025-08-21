/**
 * HydroML Advanced Theme Manager
 * Comprehensive runtime theme configuration with smooth transitions,
 * user preferences, and API integration
 */

class HydroMLThemeManager {
  constructor(options = {}) {
    this.options = {
      transitionDuration: 200,
      previewMode: false,
      autoFollowSystem: true,
      storageKey: 'hydroml-theme-config',
      apiEndpoint: '/api/theme/preferences/',
      ...options
    };

    this.themes = {
      light: {
        name: 'Light',
        icon: '☀️',
        description: 'Clean and bright theme for daylight use',
        cssClass: 'light',
        dataTheme: 'light',
        colors: {
          primary: 'var(--color-brand-primary)',
          background: 'var(--color-background-primary)',
          foreground: 'var(--color-foreground-default)'
        }
      },
      dark: {
        name: 'Dark',
        icon: '🌙', 
        description: 'Easy on the eyes for low-light environments',
        cssClass: 'dark',
        dataTheme: 'dark',
        colors: {
          primary: 'var(--color-brand-primary)',
          background: 'var(--color-onedark-background)',
          foreground: 'var(--color-darcula-foreground)'
        }
      },
      darcula: {
        name: 'Darcula',
        icon: '🔧',
        description: 'Professional IDE-inspired dark theme',
        cssClass: '',
        dataTheme: 'darcula',
        colors: {
          primary: 'var(--color-brand-primary)',
          background: 'var(--color-darcula-background)',
          foreground: 'var(--color-darcula-foreground)'
        }
      }
    };

    this.currentTheme = 'light';
    this.previousTheme = null;
    this.transitionInProgress = false;
    this.customizations = {};
    this.subscribers = new Set();

    this.init();
  }

  /**
   * Initialize the theme manager
   */
  async init() {
    try {
      // Load user preferences
      await this.loadPreferences();
      
      // Set initial theme
      const initialTheme = this.determineInitialTheme();
      await this.setTheme(initialTheme, { skipTransition: true });
      
      // Setup system preference detection
      this.setupSystemPreferenceDetection();
      
      // Setup transition CSS
      this.setupTransitionCSS();
      
      // Initialize API integration
      this.initializeAPI();
      
      console.log('[HydroML Theme] Theme Manager initialized successfully');
    } catch (error) {
      console.error('[HydroML Theme] Initialization failed:', error);
      this.fallbackToDefaults();
    }
  }

  /**
   * Determine initial theme based on preferences and system
   */
  determineInitialTheme() {
    // Check stored preferences first
    const stored = this.getStoredPreference();
    if (stored && this.themes[stored]) {
      return stored;
    }

    // Fall back to system preference if auto-follow is enabled
    if (this.options.autoFollowSystem) {
      return this.getSystemPreference();
    }

    // Default to light theme
    return 'light';
  }

  /**
   * Get system preference
   */
  getSystemPreference() {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  /**
   * Get stored preference from localStorage
   */
  getStoredPreference() {
    try {
      const config = JSON.parse(localStorage.getItem(this.options.storageKey) || '{}');
      return config.theme;
    } catch {
      return localStorage.getItem('hydroml-theme'); // Fallback to old key
    }
  }

  /**
   * Set theme with smooth transitions
   */
  async setTheme(themeName, options = {}) {
    if (!this.themes[themeName]) {
      console.warn(`[HydroML Theme] Unknown theme: ${themeName}`);
      return false;
    }

    if (this.transitionInProgress && !options.force) {
      console.log('[HydroML Theme] Transition in progress, ignoring request');
      return false;
    }

    const theme = this.themes[themeName];
    const previousTheme = this.currentTheme;

    try {
      // Start transition
      this.transitionInProgress = true;
      this.previousTheme = previousTheme;

      // Apply theme immediately in preview mode
      if (options.preview || this.options.previewMode) {
        this.applyThemeClasses(theme, themeName);
        this.notifySubscribers('preview', { theme: themeName, previous: previousTheme });
        return true;
      }

      // Show transition overlay if smooth transitions enabled
      if (!options.skipTransition) {
        await this.showTransitionOverlay();
      }

      // Apply the theme
      this.applyThemeClasses(theme, themeName);
      this.currentTheme = themeName;

      // Update storage
      await this.savePreferences();

      // Hide transition overlay
      if (!options.skipTransition) {
        await this.hideTransitionOverlay();
      }

      // Notify subscribers
      this.notifySubscribers('change', { theme: themeName, previous: previousTheme });

      // Update server preferences if API available
      if (!options.skipAPI) {
        this.updateServerPreferences();
      }

      console.log(`[HydroML Theme] Theme changed from ${previousTheme} to ${themeName}`);
      return true;

    } catch (error) {
      console.error('[HydroML Theme] Failed to set theme:', error);
      return false;
    } finally {
      this.transitionInProgress = false;
    }
  }

  /**
   * Apply theme CSS classes and attributes
   */
  applyThemeClasses(theme, themeName) {
    const html = document.documentElement;
    const body = document.body;

    // Remove all existing theme classes and attributes
    html.classList.remove('light', 'dark');
    html.removeAttribute('data-theme');
    body.classList.remove('theme-light', 'theme-dark', 'theme-darcula');

    // Apply new theme classes
    if (theme.cssClass) {
      html.classList.add(theme.cssClass);
    }
    html.setAttribute('data-theme', theme.dataTheme);
    body.classList.add(`theme-${themeName}`);

    // Apply custom colors if any
    if (this.customizations[themeName]) {
      this.applyCustomizations(this.customizations[themeName]);
    }
  }

  /**
   * Show smooth transition overlay
   */
  async showTransitionOverlay() {
    return new Promise((resolve) => {
      const overlay = document.createElement('div');
      overlay.className = 'theme-transition-overlay';
      overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: var(--color-background-primary);
        z-index: 9999;
        opacity: 0;
        transition: opacity ${this.options.transitionDuration}ms ease-in-out;
        pointer-events: none;
      `;
      
      document.body.appendChild(overlay);
      
      // Trigger opacity change
      requestAnimationFrame(() => {
        overlay.style.opacity = '0.8';
        setTimeout(() => {
          this.transitionOverlay = overlay;
          resolve();
        }, this.options.transitionDuration / 2);
      });
    });
  }

  /**
   * Hide transition overlay
   */
  async hideTransitionOverlay() {
    if (!this.transitionOverlay) return;

    return new Promise((resolve) => {
      this.transitionOverlay.style.opacity = '0';
      
      setTimeout(() => {
        if (this.transitionOverlay) {
          this.transitionOverlay.remove();
          this.transitionOverlay = null;
        }
        resolve();
      }, this.options.transitionDuration / 2);
    });
  }

  /**
   * Setup CSS for smooth transitions
   */
  setupTransitionCSS() {
    const style = document.createElement('style');
    style.textContent = `
      .theme-transition-active {
        transition: background-color ${this.options.transitionDuration}ms ease-in-out,
                   color ${this.options.transitionDuration}ms ease-in-out,
                   border-color ${this.options.transitionDuration}ms ease-in-out;
      }
      
      .theme-transition-active * {
        transition: background-color ${this.options.transitionDuration}ms ease-in-out,
                   color ${this.options.transitionDuration}ms ease-in-out,
                   border-color ${this.options.transitionDuration}ms ease-in-out;
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Setup system preference detection
   */
  setupSystemPreferenceDetection() {
    if (!this.options.autoFollowSystem) return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (e) => {
      const stored = this.getStoredPreference();
      
      // Only follow system if no explicit preference is stored
      if (!stored) {
        const systemTheme = e.matches ? 'dark' : 'light';
        this.setTheme(systemTheme);
      }
    });
  }

  /**
   * Toggle between available themes
   */
  toggleTheme() {
    const themeNames = Object.keys(this.themes);
    const currentIndex = themeNames.indexOf(this.currentTheme);
    const nextIndex = (currentIndex + 1) % themeNames.length;
    return this.setTheme(themeNames[nextIndex]);
  }

  /**
   * Preview theme without applying
   */
  previewTheme(themeName) {
    return this.setTheme(themeName, { preview: true });
  }

  /**
   * Cancel theme preview
   */
  cancelPreview() {
    if (this.previousTheme) {
      return this.setTheme(this.previousTheme, { skipTransition: true });
    }
  }

  /**
   * Apply custom theme modifications
   */
  applyCustomizations(customizations) {
    const style = document.getElementById('theme-customizations') || 
                 (() => {
                   const s = document.createElement('style');
                   s.id = 'theme-customizations';
                   document.head.appendChild(s);
                   return s;
                 })();

    const cssRules = Object.entries(customizations)
      .map(([property, value]) => `--${property}: ${value};`)
      .join('\n');

    style.textContent = `:root { ${cssRules} }`;
  }

  /**
   * Save preferences to localStorage and optionally server
   */
  async savePreferences() {
    const config = {
      theme: this.currentTheme,
      customizations: this.customizations,
      autoFollowSystem: this.options.autoFollowSystem,
      lastUpdated: Date.now()
    };

    try {
      localStorage.setItem(this.options.storageKey, JSON.stringify(config));
      
      // Also save to old key for backward compatibility
      localStorage.setItem('hydroml-theme', this.currentTheme);
    } catch (error) {
      console.warn('[HydroML Theme] Failed to save to localStorage:', error);
    }
  }

  /**
   * Load preferences from localStorage and optionally server
   */
  async loadPreferences() {
    try {
      const stored = localStorage.getItem(this.options.storageKey);
      if (stored) {
        const config = JSON.parse(stored);
        this.customizations = config.customizations || {};
        this.options.autoFollowSystem = config.autoFollowSystem ?? this.options.autoFollowSystem;
      }
    } catch (error) {
      console.warn('[HydroML Theme] Failed to load preferences:', error);
    }
  }

  /**
   * Initialize API integration for server-side preferences
   */
  initializeAPI() {
    // This will be implemented when Django backend is ready
    console.log('[HydroML Theme] API integration ready for Django backend');
  }

  /**
   * Update server preferences
   */
  async updateServerPreferences() {
    if (!this.options.apiEndpoint) return;

    try {
      const response = await fetch(this.options.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
          theme: this.currentTheme,
          customizations: this.customizations
        })
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
    } catch (error) {
      console.warn('[HydroML Theme] Failed to update server preferences:', error);
    }
  }

  /**
   * Get CSRF token for Django requests
   */
  getCSRFToken() {
    const element = document.querySelector('[name=csrfmiddlewaretoken]');
    return element ? element.value : '';
  }

  /**
   * Subscribe to theme changes
   */
  subscribe(callback) {
    this.subscribers.add(callback);
    return () => this.subscribers.delete(callback);
  }

  /**
   * Notify all subscribers of theme changes
   */
  notifySubscribers(event, data) {
    this.subscribers.forEach(callback => {
      try {
        callback(event, data);
      } catch (error) {
        console.error('[HydroML Theme] Subscriber callback failed:', error);
      }
    });

    // Also dispatch global events for backward compatibility
    window.dispatchEvent(new CustomEvent('theme-changed', {
      detail: { type: event, ...data }
    }));
  }

  /**
   * Fallback to safe defaults on errors
   */
  fallbackToDefaults() {
    console.warn('[HydroML Theme] Falling back to default configuration');
    this.currentTheme = 'light';
    this.applyThemeClasses(this.themes.light, 'light');
  }

  /**
   * Get current theme info
   */
  getCurrentTheme() {
    return {
      name: this.currentTheme,
      ...this.themes[this.currentTheme]
    };
  }

  /**
   * Get all available themes
   */
  getAvailableThemes() {
    return Object.entries(this.themes).map(([key, theme]) => ({
      value: key,
      ...theme,
      current: key === this.currentTheme
    }));
  }

  /**
   * Validate theme configuration
   */
  validateTheme(themeName) {
    return this.themes.hasOwnProperty(themeName);
  }

  /**
   * Get theme performance metrics
   */
  getMetrics() {
    return {
      currentTheme: this.currentTheme,
      transitionDuration: this.options.transitionDuration,
      subscriberCount: this.subscribers.size,
      customizationCount: Object.keys(this.customizations).length,
      isTransitioning: this.transitionInProgress
    };
  }
}

// Global instance and initialization
window.HydroMLThemeManager = null;

document.addEventListener('DOMContentLoaded', () => {
  window.HydroMLThemeManager = new HydroMLThemeManager();
  
  // Expose for Alpine.js integration
  window.HydroMLTheme = {
    manager: window.HydroMLThemeManager,
    getCurrentTheme: () => window.HydroMLThemeManager.getCurrentTheme(),
    setTheme: (theme) => window.HydroMLThemeManager.setTheme(theme),
    toggleTheme: () => window.HydroMLThemeManager.toggleTheme(),
    previewTheme: (theme) => window.HydroMLThemeManager.previewTheme(theme),
    getAvailableThemes: () => window.HydroMLThemeManager.getAvailableThemes()
  };
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HydroMLThemeManager;
}