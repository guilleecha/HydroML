/**
 * HydroML Main Application JavaScript
 * Contains the main Alpine.js data configuration for the application
 */

// Wait for Alpine.js to load before initializing stores
document.addEventListener('alpine:init', () => {
    
    // Alpine.js Store for global state management
    Alpine.store('app', {
        // Loading state management
        isLoading: false,
        loadingMessage: '',
        
        // Methods for loading management
        startLoading(message = 'Processing') {
            this.loadingMessage = message;
            this.isLoading = true;
        },
        
        stopLoading() {
            this.isLoading = false;
            this.loadingMessage = '';
        }
    });
});

// Alpine.js main application data - MUST be a function that returns an object
window.hydroMLApp = () => ({
    // Sidebar state management
    sidebarOpen: false, 
    sidebarExpanded: false, 
    sidebarPinned: false,
    isMobile: window.innerWidth < 1024,
    
    // Theme management
    darkMode: false,
    
    // Upload panel state management
    isUploadPanelOpen: false,
    uploadFormLoaded: false,
    
    // New Experiment panel state management
    isNewExperimentPanelOpen: false,
    newExperimentFormLoaded: false,
    
    // New Project panel state management
    isNewProjectPanelOpen: false,
    newProjectFormLoaded: false,
    
    // New Suite panel state management
    isNewSuitePanelOpen: false,
    newSuiteFormLoaded: false,
    
    // Initialization
    init() {
        // Check for saved theme preference or default to system preference
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.darkMode = savedTheme === 'dark';
        } else {
            this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
        this.updateTheme();
        
        // Check for saved sidebar pin state
        const savedSidebarPinned = localStorage.getItem('sidebarPinned');
        if (savedSidebarPinned !== null) {
            this.sidebarPinned = savedSidebarPinned === 'true';
            if (this.sidebarPinned) {
                this.sidebarExpanded = true;
            }
        }
        
        // Add window resize listener
        window.addEventListener('resize', () => {
            this.isMobile = window.innerWidth < 1024;
        });
    },
    
    // Sidebar methods
    expandSidebar() {
        if (!this.sidebarPinned) {
            this.sidebarExpanded = true;
        }
    },
    
    collapseSidebar() {
        if (!this.sidebarPinned) {
            this.sidebarExpanded = false;
        }
    },
    
    togglePin() {
        this.sidebarPinned = !this.sidebarPinned;
        // Persist the sidebar pin state
        localStorage.setItem('sidebarPinned', this.sidebarPinned.toString());
        
        if (!this.sidebarPinned) {
            this.sidebarExpanded = false;
        } else {
            this.sidebarExpanded = true;
        }
    },
    
    // Theme methods
    toggleTheme() {
        this.darkMode = !this.darkMode;
        this.updateTheme();
    },
    
    updateTheme() {
        if (this.darkMode) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
        localStorage.setItem('theme', this.darkMode ? 'dark' : 'light');
    },
    
    // Upload panel methods
    async openUploadPanel(forceProjectSelection = false) {
        // Close all other panels first
        this.isNewExperimentPanelOpen = false;
        this.isNewProjectPanelOpen = false;
        this.isNewSuitePanelOpen = false;
        
        // Then open the requested panel
        this.isUploadPanelOpen = true;
        
        if (!this.uploadFormLoaded) {
            await this.loadUploadForm(forceProjectSelection);
        }
    },
    
    closeUploadPanel() {
        this.isUploadPanelOpen = false;
        // Reset form loaded state so it reloads fresh next time
        this.uploadFormLoaded = false;
    },
    
    async loadUploadForm(forceProjectSelection = false) {
        try {
            const params = new URLSearchParams();
            if (forceProjectSelection) {
                params.append('force_project_selection', 'true');
            }
            
            const url = forceProjectSelection 
                ? `/projects/datasource/upload-form-partial/?${params}`
                : '/projects/datasource/upload-form-partial/';
                
            const response = await fetch(url);
            const html = await response.text();
            
            const container = document.getElementById('upload-form-container');
            if (container) {
                container.innerHTML = html;
                this.uploadFormLoaded = true;
                this.initializeUploadForm();
            }
        } catch (error) {
            console.error('Error loading upload form:', error);
            const container = document.getElementById('upload-form-container');
            if (container) {
                container.innerHTML = '<div class="text-red-600">Error al cargar el formulario</div>';
            }
        }
    },
    
    // New Experiment panel methods
    async openNewExperimentPanel() {
        console.log('🧪 Opening New Experiment Panel...');
        // Close all other panels first
        this.isUploadPanelOpen = false;
        this.isNewProjectPanelOpen = false;
        this.isNewSuitePanelOpen = false;
        
        // Then open the requested panel
        this.isNewExperimentPanelOpen = true;
        console.log('✅ New Experiment Panel opened');
        
        if (!this.newExperimentFormLoaded) {
            console.log('📝 Loading experiment form for first time...');
            await this.loadNewExperimentForm();
        } else {
            console.log('♻️ Using cached experiment form');
        }
    },

    closeNewExperimentPanel() {
        this.isNewExperimentPanelOpen = false;
        // Reset form loaded state so it reloads fresh next time
        this.newExperimentFormLoaded = false;
    },
    
    // New Project panel methods
    async openNewProjectPanel() {
        // Close all other panels first
        this.isUploadPanelOpen = false;
        this.isNewExperimentPanelOpen = false;
        this.isNewSuitePanelOpen = false;
        
        // Then open the requested panel
        this.isNewProjectPanelOpen = true;
        
        if (!this.newProjectFormLoaded) {
            await this.loadNewProjectForm();
        }
    },

    closeNewProjectPanel() {
        this.isNewProjectPanelOpen = false;
        // Reset form loaded state so it reloads fresh next time
        this.newProjectFormLoaded = false;
    },
    
    // New Suite panel methods
    async openNewSuitePanel() {
        // Close all other panels first
        this.isUploadPanelOpen = false;
        this.isNewExperimentPanelOpen = false;
        this.isNewProjectPanelOpen = false;
        
        // Then open the requested panel
        this.isNewSuitePanelOpen = true;
        
        if (!this.newSuiteFormLoaded) {
            await this.loadNewSuiteForm();
        }
    },

    closeNewSuitePanel() {
        this.isNewSuitePanelOpen = false;
        // Reset form loaded state so it reloads fresh next time
        this.newSuiteFormLoaded = false;
    },
    
    async loadNewExperimentForm() {
        console.log('📋 loadNewExperimentForm() called');
        try {
            // Get current project ID from URL
            const projectId = this.getCurrentProjectId();
            console.log('🆔 Current project ID:', projectId);
            const url = projectId 
                ? `/experiments/ml-experiment-form-partial/?project_id=${projectId}`
                : '/experiments/ml-experiment-form-partial/';
            console.log('🌐 Fetching form from URL:', url);
                
            const response = await fetch(url);
            console.log('📡 Form fetch response status:', response.status);
            const html = await response.text();
            console.log('📄 Form HTML length:', html.length);
            
            const container = document.getElementById('new-experiment-form-container');
            if (container) {
                container.innerHTML = html;
                this.newExperimentFormLoaded = true;
                console.log('✅ Form loaded and container updated');
                this.initializeNewExperimentForm();
            } else {
                console.error('❌ Form container not found!');
            }
        } catch (error) {
            console.error('❌ Error loading new experiment form:', error);
            const container = document.getElementById('new-experiment-form-container');
            if (container) {
                container.innerHTML = '<div class="text-red-600">Error al cargar el formulario</div>';
            }
        }
    },
    
    async loadNewProjectForm() {
        try {
            const response = await fetch('/projects/create-partial/');
            const html = await response.text();
            
            const container = document.getElementById('new-project-form-container');
            if (container) {
                container.innerHTML = html;
                this.newProjectFormLoaded = true;
                this.initializeNewProjectForm();
            }
        } catch (error) {
            console.error('Error loading new project form:', error);
            const container = document.getElementById('new-project-form-container');
            if (container) {
                container.innerHTML = '<div class="text-red-600">Error al cargar el formulario</div>';
            }
        }
    },
    
    async loadNewSuiteForm() {
        try {
            // Get current project ID from URL
            const projectId = this.getCurrentProjectId();
            if (!projectId) {
                throw new Error('No project ID found in URL');
            }
            
            const url = `/experiments/projects/${projectId}/suites/create-partial/`;
            const response = await fetch(url);
            const html = await response.text();
            
            const container = document.getElementById('new-suite-form-container');
            if (container) {
                container.innerHTML = html;
                this.newSuiteFormLoaded = true;
                this.initializeNewSuiteForm();
            }
        } catch (error) {
            console.error('Error loading new suite form:', error);
            const container = document.getElementById('new-suite-form-container');
            if (container) {
                container.innerHTML = '<div class="text-red-600">Error al cargar el formulario</div>';
            }
        }
    },
    
    getCurrentProjectId() {
        // Extract project ID from current URL
        const pathParts = window.location.pathname.split('/');
        const projectIndex = pathParts.indexOf('projects');
        if (projectIndex !== -1 && pathParts[projectIndex + 1]) {
            return pathParts[projectIndex + 1];
        }
        return null;
    },
    
    initializeUploadForm() {
        // Re-initialize any Alpine.js components in the dynamically loaded content
        this.$nextTick(() => {
            // Find any Alpine.js components in the upload form and initialize them
            const formContainer = document.getElementById('upload-form-container');
            if (formContainer && window.Alpine) {
                window.Alpine.initTree(formContainer);
            }
        });
    },
    
    initializeNewExperimentForm() {
        console.log('🔧 initializeNewExperimentForm() called');
        // Re-initialize any Alpine.js components in the dynamically loaded content
        this.$nextTick(() => {
            // Find any Alpine.js components in the new experiment form and initialize them
            const formContainer = document.getElementById('new-experiment-form-container');
            if (formContainer && window.Alpine) {
                console.log('♻️ Re-initializing Alpine.js components in form container');
                window.Alpine.initTree(formContainer);
            } else {
                console.warn('⚠️ Form container or Alpine.js not found for initialization');
            }
            
            // Initialize the ML experiment form JavaScript if available
            if (window.MLExperimentForm && typeof window.MLExperimentForm.init === 'function') {
                console.log('🧪 Initializing MLExperimentForm custom JavaScript');
                window.MLExperimentForm.init();
            } else {
                console.log('ℹ️ MLExperimentForm.init not found - form JS will self-initialize');
            }
        });
    },
    
    initializeNewProjectForm() {
        // Re-initialize any Alpine.js components in the dynamically loaded content
        this.$nextTick(() => {
            // Find any Alpine.js components in the new project form and initialize them
            const formContainer = document.getElementById('new-project-form-container');
            if (formContainer && window.Alpine) {
                window.Alpine.initTree(formContainer);
            }
        });
    },
    
    initializeNewSuiteForm() {
        // Re-initialize any Alpine.js components in the dynamically loaded content
        this.$nextTick(() => {
            // Find any Alpine.js components in the new suite form and initialize them
            const formContainer = document.getElementById('new-suite-form-container');
            if (formContainer && window.Alpine) {
                window.Alpine.initTree(formContainer);
            }
        });
    },
    
    async submitExperimentForm(event) {
        console.log('🚀 submitExperimentForm() called');
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        
        console.log('📝 Form data entries:');
        for (let [key, value] of formData.entries()) {
            console.log(`  ${key}:`, value);
        }
        
        try {
            console.log('📤 Submitting to:', form.action);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            
            console.log('📡 Submit response status:', response.status);
            const result = await response.json();
            console.log('📋 Submit result:', result);
            
            if (result.success) {
                console.log('✅ Form submission successful');
                this.closeNewExperimentPanel();
                this.showMessage(result.message, 'success');
                
                // Redirect if specified
                if (result.redirect_url) {
                    console.log('🔀 Redirecting to:', result.redirect_url);
                    window.location.href = result.redirect_url;
                }
            } else {
                console.error('❌ Form submission failed:', result);
                // Handle form errors
                this.showMessage('Error en el formulario. Revisa los campos.', 'error');
            }
        } catch (error) {
            console.error('❌ Error submitting experiment form:', error);
            this.showMessage('Error al crear el experimento', 'error');
        }
    },
    
    showMessage(message, type = 'info') {
        // Create a temporary message element
        const messageEl = document.createElement('div');
        messageEl.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 ${
            type === 'success' ? 'bg-green-500 text-white' : 
            type === 'error' ? 'bg-red-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        messageEl.textContent = message;
        
        document.body.appendChild(messageEl);
        
        // Remove after 5 seconds
        setTimeout(() => {
            messageEl.remove();
        }, 5000);
    },
    
    // Utility method to close all slide-over panels
    closeAllPanels() {
        this.isUploadPanelOpen = false;
        this.isNewExperimentPanelOpen = false;
        this.isNewProjectPanelOpen = false;
        this.isNewSuitePanelOpen = false;
        
        // Reset form loaded states
        this.uploadFormLoaded = false;
        this.newExperimentFormLoaded = false;
        this.newProjectFormLoaded = false;
        this.newSuiteFormLoaded = false;
    }
});

// Notification dropdown Alpine.js component
window.notificationDropdown = () => ({
    isOpen: false,
    notifications: [],
    unreadCount: 0,
    loading: false,
    
    async init() {
        await this.fetchNotifications();
    },
    
    toggleDropdown() {
        this.isOpen = !this.isOpen;
        if (this.isOpen) {
            this.fetchNotifications();
        }
    },
    
    closeDropdown() {
        this.isOpen = false;
    },
    
    async fetchNotifications() {
        this.loading = true;
        try {
            // TODO: Implement notifications API endpoint
            console.log('Notifications API not implemented yet');
            this.notifications = [];
            this.unreadCount = 0;
            return;
            
            const response = await fetch('/accounts/api/notifications/');
            const data = await response.json();
            this.notifications = data.notifications || [];
            this.unreadCount = data.unread_count || 0;
        } catch (error) {
            console.error('Error fetching notifications:', error);
            this.notifications = [];
            this.unreadCount = 0;
        } finally {
            this.loading = false;
        }
    },
    
    async markAllAsRead() {
        try {
            const response = await fetch('/accounts/api/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value,
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                this.unreadCount = 0;
                this.notifications.forEach(notification => {
                    notification.is_read = true;
                });
            }
        } catch (error) {
            console.error('Error marking notifications as read:', error);
        }
    },
    
    handleNotificationClick(notification) {
        // Handle click on notification
        if (notification.target_url) {
            window.location.href = notification.target_url;
        }
        this.closeDropdown();
    }
});
