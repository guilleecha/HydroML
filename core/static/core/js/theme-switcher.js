/**
 * HydroML Theme Switcher
 * Manages theme switching with design token integration
 */

document.addEventListener('alpine:init', () => {
  Alpine.data('themeSwitcher', () => ({
    currentTheme: 'light',
    
    availableThemes: [
      { value: 'light', label: 'Light', current: true },
      { value: 'dark', label: 'Dark', current: false },
      { value: 'darcula', label: 'Darcula', current: false }
    ],
    
    init() {
      // Load saved theme or detect system preference
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
      
      // Dispatch custom event for other components
      window.dispatchEvent(new CustomEvent('theme-changed', { 
        detail: { theme: theme } 
      }));
    },
    
    applyTheme(theme) {
      const html = document.documentElement;
      
      // Remove all theme classes
      html.classList.remove('dark', 'light');
      html.removeAttribute('data-theme');
      
      // Apply new theme
      if (theme === 'dark') {
        html.classList.add('dark');
        html.setAttribute('data-theme', 'dark');
      } else if (theme === 'darcula') {
        html.setAttribute('data-theme', 'darcula');
      } else {
        html.classList.add('light');
        html.setAttribute('data-theme', 'light');
      }
      
      // Add transition class temporarily for smooth transitions
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
  }));
});

// Theme detection utility
window.HydroMLTheme = {
  getCurrentTheme() {
    return localStorage.getItem('hydroml-theme') || 
           (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  },
  
  setTheme(theme) {
    const event = new CustomEvent('set-theme', { detail: { theme } });
    window.dispatchEvent(event);
  }
};