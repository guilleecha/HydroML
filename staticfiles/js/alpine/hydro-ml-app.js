/**
 * HydroML Main Alpine.js App Component
 * Defines the main application component with core functionality
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('hydroMLApp', () => ({
        // Theme management
        darkMode: localStorage.getItem('theme') === 'dark' || 
                 (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches),
        
        // UI state management
        sidebarOpen: false,
        isUploadPanelOpen: false,
        isProjectPanelOpen: false,
        isNewExperimentPanelOpen: false,
        
        // Initialize the app
        init() {
            // Apply theme on startup
            this.applyTheme();
            
            // Listen for system theme changes
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
                if (!localStorage.getItem('theme')) {
                    this.darkMode = e.matches;
                    this.applyTheme();
                }
            });
        },
        
        // Theme methods
        toggleTheme() {
            this.darkMode = !this.darkMode;
            localStorage.setItem('theme', this.darkMode ? 'dark' : 'light');
            this.applyTheme();
        },
        
        applyTheme() {
            if (this.darkMode) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        },
        
        // Sidebar methods
        toggleSidebar() {
            this.sidebarOpen = !this.sidebarOpen;
        },
        
        closeSidebar() {
            this.sidebarOpen = false;
        },
        
        // Panel methods
        openUploadPanel() {
            this.isUploadPanelOpen = true;
        },
        
        closeUploadPanel() {
            this.isUploadPanelOpen = false;
        },
        
        openProjectPanel() {
            this.isProjectPanelOpen = true;
        },
        
        closeProjectPanel() {
            this.isProjectPanelOpen = false;
        },
        
        openNewExperimentPanel() {
            this.isNewExperimentPanelOpen = true;
        },
        
        closeNewExperimentPanel() {
            this.isNewExperimentPanelOpen = false;
        },
        
        // Utility methods
        handleEscape() {
            // Close any open panels on escape key
            this.isUploadPanelOpen = false;
            this.isProjectPanelOpen = false;
            this.isNewExperimentPanelOpen = false;
            this.sidebarOpen = false;
        }
    }));
});