/**
 * HydroML Main Application JavaScript
 * Contains the main Alpine.js data configuration for the application
 */

// Alpine.js main application data
window.hydroMLApp = {
    // Sidebar state management
    sidebarOpen: false, 
    sidebarExpanded: false, 
    sidebarPinned: false,
    
    // Theme management
    darkMode: false,
    
    // Upload panel state management
    isUploadPanelOpen: false,
    uploadFormLoaded: false,
    
    // New Experiment panel state management
    isNewExperimentPanelOpen: false,
    newExperimentFormLoaded: false,
    
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
        
        // Debug log
        console.log('Theme initialized:', this.darkMode ? 'dark' : 'light');
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
        console.log('Theme toggled to:', this.darkMode ? 'dark' : 'light');
    },
    
    updateTheme() {
        localStorage.setItem('theme', this.darkMode ? 'dark' : 'light');
        
        // Update the document class immediately
        const htmlElement = document.documentElement;
        if (this.darkMode) {
            htmlElement.classList.add('dark');
        } else {
            htmlElement.classList.remove('dark');
        }
        
        // Also update this component's class binding
        this.$nextTick(() => {
            // Force a re-render by updating the class attribute
            htmlElement.className = htmlElement.className;
        });
    },
    
    // Upload panel methods
    async openUploadPanel() {
        this.isUploadPanelOpen = true;
        
        if (!this.uploadFormLoaded) {
            await this.loadUploadForm();
        }
    },
    
    closeUploadPanel() {
        this.isUploadPanelOpen = false;
        // Reset form loaded state so it reloads fresh next time
        this.uploadFormLoaded = false;
    },
    
    async loadUploadForm() {
        try {
            // Get current project ID from the page if we're on a project detail page
            const projectId = this.getCurrentProjectId();
            const url = projectId 
                ? `/projects/datasource/upload-form-partial/?project_id=${projectId}`
                : '/projects/datasource/upload-form-partial/';
                
            const response = await fetch(url);
            if (response.ok) {
                const html = await response.text();
                document.getElementById('upload-form-container').innerHTML = html;
                this.uploadFormLoaded = true;
                
                // Initialize any form-specific JavaScript if needed
                this.initializeUploadForm();
            } else {
                throw new Error('Failed to load form');
            }
        } catch (error) {
            console.error('Error loading upload form:', error);
            document.getElementById('upload-form-container').innerHTML = `
                <div class="text-center text-danger-600 dark:text-darcula-error">
                    <svg class="mx-auto h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p>Error al cargar el formulario</p>
                    <button onclick="location.reload()" class="mt-2 text-sm underline">Intentar de nuevo</button>
                </div>
            `;
        }
    },
    
    // New Experiment panel methods
    async openNewExperimentPanel() {
        this.isNewExperimentPanelOpen = true;
        
        if (!this.newExperimentFormLoaded) {
            await this.loadNewExperimentForm();
        }
    },
    
    closeNewExperimentPanel() {
        this.isNewExperimentPanelOpen = false;
        // Reset form loaded state so it reloads fresh next time
        this.newExperimentFormLoaded = false;
    },
    
    async loadNewExperimentForm() {
        try {
            // Get current project ID from the page if we're on a project detail page
            const projectId = this.getCurrentProjectId();
            const url = projectId 
                ? `/experiments/ml-experiment-form-partial/?project_id=${projectId}`
                : '/experiments/ml-experiment-form-partial/';
                
            const response = await fetch(url);
            if (response.ok) {
                const html = await response.text();
                document.getElementById('new-experiment-form-container').innerHTML = html;
                this.newExperimentFormLoaded = true;
                
                // Initialize any form-specific JavaScript if needed
                this.initializeNewExperimentForm();
            } else {
                throw new Error('Failed to load form');
            }
        } catch (error) {
            console.error('Error loading new experiment form:', error);
            document.getElementById('new-experiment-form-container').innerHTML = `
                <div class="text-center text-danger-600 dark:text-darcula-error">
                    <svg class="mx-auto h-8 w-8 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p>Error al cargar el formulario</p>
                    <button onclick="location.reload()" class="mt-2 text-sm underline">Intentar de nuevo</button>
                </div>
            `;
        }
    },
    
    getCurrentProjectId() {
        // Try to extract project ID from the current URL
        const path = window.location.pathname;
        const matches = path.match(/\/projects\/([a-f0-9-]+)\//);
        return matches ? matches[1] : null;
    },
    
    initializeUploadForm() {
        // Re-initialize any Alpine.js components in the dynamically loaded content
        this.$nextTick(() => {
            // Find any Alpine.js components in the uploaded form and initialize them
            const formContainer = document.getElementById('upload-form-container');
            if (formContainer && window.Alpine) {
                window.Alpine.initTree(formContainer);
            }
        });
    },
    
    initializeNewExperimentForm() {
        // Re-initialize any Alpine.js components in the dynamically loaded content
        this.$nextTick(() => {
            // Find any Alpine.js components in the new experiment form and initialize them
            const formContainer = document.getElementById('new-experiment-form-container');
            if (formContainer && window.Alpine) {
                window.Alpine.initTree(formContainer);
            }
            
            // Initialize the ML experiment form JavaScript if available
            if (window.MLExperimentForm && typeof window.MLExperimentForm.init === 'function') {
                window.MLExperimentForm.init();
            }
        });
    },
    
    async submitExperimentForm(event) {
        try {
            const form = event.target;
            const formData = new FormData(form);
            const projectId = this.getCurrentProjectId();
            const url = projectId 
                ? `/experiments/ml-experiment-form-partial/?project_id=${projectId}`
                : '/experiments/ml-experiment-form-partial/';
            
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Close the panel
                this.closeNewExperimentPanel();
                
                // Show success message
                this.showMessage(data.message, 'success');
                
                // Redirect to refresh the page
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    // Fallback - reload current page
                    window.location.reload();
                }
            } else {
                // Show error message
                this.showMessage(data.message || 'Error al crear el experimento', 'error');
                
                // If there are field-specific errors, you could handle them here
                if (data.errors) {
                    console.error('Form validation errors:', data.errors);
                    // You could implement field-specific error display here
                }
            }
        } catch (error) {
            console.error('Error submitting experiment form:', error);
            this.showMessage('Error de conexión. Por favor, intenta de nuevo.', 'error');
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
    }
};

// Notification dropdown Alpine.js component
window.notificationDropdown = () => ({
    isOpen: false,
    notifications: [],
    unreadCount: 0,
    loading: false,
    
    async init() {
        await this.fetchNotifications();
        // Poll for new notifications every 30 seconds
        setInterval(() => {
            this.fetchNotifications();
        }, 30000);
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
        try {
            this.loading = true;
            const response = await fetch('/api/notifications/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.notifications = data.notifications || [];
                this.unreadCount = data.unread_count || 0;
            } else {
                console.error('Failed to fetch notifications:', response.status);
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
        } finally {
            this.loading = false;
        }
    },
    
    async markAsRead(notificationId) {
        try {
            const response = await fetch('/api/notifications/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    notification_id: notificationId
                })
            });
            
            if (response.ok) {
                // Remove from notifications list
                this.notifications = this.notifications.filter(n => n.id !== notificationId);
                this.unreadCount = Math.max(0, this.unreadCount - 1);
            } else {
                console.error('Failed to mark notification as read:', response.status);
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    },
    
    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                this.notifications = [];
                this.unreadCount = 0;
                this.closeDropdown();
            } else {
                console.error('Failed to mark all notifications as read:', response.status);
            }
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
        }
    },
    
    async handleNotificationClick(notification) {
        // Mark as read
        await this.markAsRead(notification.id);
        
        // Navigate to the link if it exists
        if (notification.link) {
            window.location.href = notification.link;
        }
        
        this.closeDropdown();
    }
});
