/**
 * HydroML Theme Controller for Alpine.js
 * Advanced theme interface with preview, customization, and smooth UX
 */

document.addEventListener('alpine:init', () => {
  Alpine.data('themeController', () => ({
    // State
    currentTheme: 'light',
    availableThemes: [],
    isPreviewMode: false,
    isTransitioning: false,
    showCustomizer: false,
    autoFollowSystem: true,
    
    // Customization state
    customizations: {},
    tempCustomizations: {},
    
    // UI state
    dropdownOpen: false,
    customizerOpen: false,
    
    init() {
      this.initializeThemeSystem();
      this.setupEventListeners();
      this.loadInitialState();
    },

    /**
     * Initialize connection with theme manager
     */
    initializeThemeSystem() {
      // Wait for theme manager to be ready
      const checkManager = () => {
        if (window.HydroMLThemeManager) {
          this.connectToManager();
        } else {
          setTimeout(checkManager, 100);
        }
      };
      checkManager();
    },

    /**
     * Connect to the global theme manager
     */
    connectToManager() {
      const manager = window.HydroMLThemeManager;
      
      // Subscribe to theme changes
      manager.subscribe((event, data) => {
        this.handleThemeEvent(event, data);
      });
      
      // Load initial state
      this.currentTheme = manager.currentTheme;
      this.availableThemes = manager.getAvailableThemes();
      this.autoFollowSystem = manager.options.autoFollowSystem;
      this.customizations = { ...manager.customizations };
    },

    /**
     * Handle theme events from manager
     */
    handleThemeEvent(event, data) {
      switch (event) {
        case 'change':
          this.currentTheme = data.theme;
          this.isPreviewMode = false;
          this.isTransitioning = false;
          this.updateAvailableThemes();
          break;
          
        case 'preview':
          this.isPreviewMode = true;
          break;
          
        case 'transition-start':
          this.isTransitioning = true;
          break;
          
        case 'transition-end':
          this.isTransitioning = false;
          break;
      }
    },

    /**
     * Setup event listeners
     */
    setupEventListeners() {
      // Listen for keyboard shortcuts
      document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Shift + T for theme toggle
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
          e.preventDefault();
          this.toggleTheme();
        }
        
        // Escape to cancel preview
        if (e.key === 'Escape' && this.isPreviewMode) {
          this.cancelPreview();
        }
      });

      // Close dropdowns when clicking outside
      document.addEventListener('click', (e) => {
        if (!e.target.closest('[data-theme-dropdown]')) {
          this.dropdownOpen = false;
        }
        if (!e.target.closest('[data-theme-customizer]')) {
          this.customizerOpen = false;
        }
      });
    },

    /**
     * Load initial state from storage
     */
    loadInitialState() {
      try {
        const stored = localStorage.getItem('hydroml-theme-ui-state');
        if (stored) {
          const state = JSON.parse(stored);
          this.showCustomizer = state.showCustomizer || false;
          this.autoFollowSystem = state.autoFollowSystem ?? true;
        }
      } catch (error) {
        console.warn('[HydroML Theme UI] Failed to load UI state:', error);
      }
    },

    /**
     * Save UI state
     */
    saveUIState() {
      const state = {
        showCustomizer: this.showCustomizer,
        autoFollowSystem: this.autoFollowSystem,
        lastUpdated: Date.now()
      };
      
      try {
        localStorage.setItem('hydroml-theme-ui-state', JSON.stringify(state));
      } catch (error) {
        console.warn('[HydroML Theme UI] Failed to save UI state:', error);
      }
    },

    /**
     * Set theme with UI feedback
     */
    async setTheme(themeName) {
      if (!window.HydroMLThemeManager) return;
      
      this.isTransitioning = true;
      const success = await window.HydroMLThemeManager.setTheme(themeName);
      
      if (success) {
        this.currentTheme = themeName;
        this.updateAvailableThemes();
        this.dropdownOpen = false;
        
        // Show brief success feedback
        this.showSuccessFeedback(`Switched to ${this.getThemeLabel(themeName)} theme`);
      } else {
        this.showErrorFeedback('Failed to change theme');
      }
      
      this.isTransitioning = false;
    },

    /**
     * Toggle between themes
     */
    async toggleTheme() {
      if (!window.HydroMLThemeManager) return;
      
      this.isTransitioning = true;
      const success = await window.HydroMLThemeManager.toggleTheme();
      
      if (success) {
        this.currentTheme = window.HydroMLThemeManager.currentTheme;
        this.updateAvailableThemes();
        this.showSuccessFeedback(`Switched to ${this.getThemeLabel(this.currentTheme)} theme`);
      }
      
      this.isTransitioning = false;
    },

    /**
     * Preview theme without applying
     */
    previewTheme(themeName) {
      if (!window.HydroMLThemeManager || themeName === this.currentTheme) return;
      
      window.HydroMLThemeManager.previewTheme(themeName);
      this.isPreviewMode = true;
    },

    /**
     * Cancel theme preview
     */
    cancelPreview() {
      if (!window.HydroMLThemeManager || !this.isPreviewMode) return;
      
      window.HydroMLThemeManager.cancelPreview();
      this.isPreviewMode = false;
    },

    /**
     * Apply previewed theme
     */
    applyPreview() {
      if (!window.HydroMLThemeManager || !this.isPreviewMode) return;
      
      // The theme is already applied in preview, just confirm it
      this.isPreviewMode = false;
      this.updateAvailableThemes();
      this.dropdownOpen = false;
    },

    /**
     * Toggle system preference following
     */
    toggleAutoFollowSystem() {
      this.autoFollowSystem = !this.autoFollowSystem;
      
      if (window.HydroMLThemeManager) {
        window.HydroMLThemeManager.options.autoFollowSystem = this.autoFollowSystem;
        window.HydroMLThemeManager.savePreferences();
      }
      
      this.saveUIState();
    },

    /**
     * Open theme customizer
     */
    openCustomizer() {
      this.customizerOpen = true;
      this.tempCustomizations = { ...this.customizations };
    },

    /**
     * Close theme customizer
     */
    closeCustomizer() {
      this.customizerOpen = false;
      this.tempCustomizations = {};
    },

    /**
     * Apply customizations
     */
    applyCustomizations() {
      if (!window.HydroMLThemeManager) return;
      
      this.customizations = { ...this.tempCustomizations };
      window.HydroMLThemeManager.customizations = this.customizations;
      window.HydroMLThemeManager.applyCustomizations(this.customizations);
      window.HydroMLThemeManager.savePreferences();
      
      this.closeCustomizer();
      this.showSuccessFeedback('Theme customizations applied');
    },

    /**
     * Reset customizations
     */
    resetCustomizations() {
      this.customizations = {};
      this.tempCustomizations = {};
      
      if (window.HydroMLThemeManager) {
        window.HydroMLThemeManager.customizations = {};
        window.HydroMLThemeManager.applyCustomizations({});
        window.HydroMLThemeManager.savePreferences();
      }
      
      this.showSuccessFeedback('Theme customizations reset');
    },

    /**
     * Update available themes current state
     */
    updateAvailableThemes() {
      this.availableThemes = this.availableThemes.map(theme => ({
        ...theme,
        current: theme.value === this.currentTheme
      }));
    },

    /**
     * Get theme label
     */
    getThemeLabel(themeName) {
      const theme = this.availableThemes.find(t => t.value === themeName);
      return theme ? theme.name : themeName;
    },

    /**
     * Get theme icon
     */
    getThemeIcon(themeName) {
      const theme = this.availableThemes.find(t => t.value === themeName);
      return theme ? theme.icon : '🎨';
    },

    /**
     * Get theme description
     */
    getThemeDescription(themeName) {
      const theme = this.availableThemes.find(t => t.value === themeName);
      return theme ? theme.description : '';
    },

    /**
     * Check if theme is current
     */
    isCurrentTheme(themeName) {
      return this.currentTheme === themeName;
    },

    /**
     * Show success feedback
     */
    showSuccessFeedback(message) {
      this.showToast(message, 'success');
    },

    /**
     * Show error feedback
     */
    showErrorFeedback(message) {
      this.showToast(message, 'error');
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
      // Create toast element
      const toast = document.createElement('div');
      toast.className = `theme-toast theme-toast-${type}`;
      toast.textContent = message;
      toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--color-background-secondary);
        color: var(--color-foreground-default);
        padding: 12px 16px;
        border-radius: 8px;
        border: 1px solid var(--color-border-default);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 300ms ease-in-out;
        font-size: 14px;
        max-width: 300px;
      `;

      document.body.appendChild(toast);

      // Show toast
      requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
      });

      // Hide and remove toast
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    },

    /**
     * Get system theme preference
     */
    getSystemPreference() {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    },

    /**
     * Export theme configuration
     */
    exportConfiguration() {
      const config = {
        currentTheme: this.currentTheme,
        customizations: this.customizations,
        autoFollowSystem: this.autoFollowSystem,
        exportedAt: new Date().toISOString()
      };

      const blob = new Blob([JSON.stringify(config, null, 2)], { 
        type: 'application/json' 
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `hydroml-theme-config-${Date.now()}.json`;
      a.click();
      
      URL.revokeObjectURL(url);
      this.showSuccessFeedback('Theme configuration exported');
    },

    /**
     * Import theme configuration
     */
    importConfiguration(event) {
      const file = event.target.files[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const config = JSON.parse(e.target.result);
          
          // Validate configuration
          if (config.currentTheme && this.availableThemes.find(t => t.value === config.currentTheme)) {
            this.setTheme(config.currentTheme);
          }
          
          if (config.customizations) {
            this.customizations = config.customizations;
            if (window.HydroMLThemeManager) {
              window.HydroMLThemeManager.customizations = config.customizations;
              window.HydroMLThemeManager.applyCustomizations(config.customizations);
            }
          }
          
          if (typeof config.autoFollowSystem === 'boolean') {
            this.autoFollowSystem = config.autoFollowSystem;
          }
          
          this.showSuccessFeedback('Theme configuration imported successfully');
        } catch (error) {
          this.showErrorFeedback('Invalid configuration file');
          console.error('[HydroML Theme] Import failed:', error);
        }
      };
      
      reader.readAsText(file);
      event.target.value = ''; // Reset file input
    }
  }));
});