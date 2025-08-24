/**
 * HydroML Main Alpine.js App Component
 * Defines the main application component with core functionality
 */

// Define the component function
const hydroMLAppComponent = () => ({
    // Theme management - DISABLED temporarily to prevent flash
    darkMode: false, // Force light mode to prevent auto dark theme flash
        
        // UI state management
        sidebarOpen: false,
        mobileMenuOpen: false,
        userMenuOpen: false,
        quickActionsOpen: false,
        viewMode: 'grid',
        isUploadPanelOpen: false,
        isProjectPanelOpen: false,
        isNewExperimentPanelOpen: false,
        
        // Initialize the app
        init() {
            // Apply theme on startup - DISABLED temporarily
            // this.applyTheme();
            
            // Listen for system theme changes - DISABLED temporarily
            // window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            //     if (!localStorage.getItem('theme')) {
            //         this.darkMode = e.matches;
            //         this.applyTheme();
            //     }
            // });
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

        // User menu methods
        toggleUserMenu() {
            this.userMenuOpen = !this.userMenuOpen;
        },

        closeUserMenu() {
            this.userMenuOpen = false;
        },

        // Quick actions methods
        toggleQuickActions() {
            this.quickActionsOpen = !this.quickActionsOpen;
        },

        closeQuickActions() {
            this.quickActionsOpen = false;
        },

        // View mode methods
        setViewMode(mode) {
            this.viewMode = mode;
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
            this.userMenuOpen = false;
            this.quickActionsOpen = false;
        }
    });

// Register immediately if Alpine is already available, otherwise wait for alpine:init
if (window.Alpine) {
    window.Alpine.data('hydroMLApp', hydroMLAppComponent);
} else {
    document.addEventListener('alpine:init', () => {
        Alpine.data('hydroMLApp', hydroMLAppComponent);
    });
}