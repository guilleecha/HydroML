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
    async openUploadPanel(forceProjectSelection = false, uxMode = null) {
        // Close all other panels first
        this.isNewExperimentPanelOpen = false;
        this.isNewProjectPanelOpen = false;
        this.isNewSuitePanelOpen = false;
        
        // Then open the requested panel
        this.isUploadPanelOpen = true;
        
        if (!this.uploadFormLoaded) {
            await this.loadUploadForm(forceProjectSelection, uxMode);
        }
    },
    
    closeUploadPanel() {
        this.isUploadPanelOpen = false;
        // Reset form loaded state so it reloads fresh next time
        this.uploadFormLoaded = false;
    },
    
    async loadUploadForm(forceProjectSelection = false, uxMode = null) {
        try {
            // Get current project ID from URL
            const projectId = this.getCurrentProjectId();
            const params = new URLSearchParams();
            
            // Auto-detect UX mode if not specified
            if (!uxMode) {
                if (projectId && !forceProjectSelection) {
                    uxMode = 'project';  // We're in a project context
                } else if (window.location.pathname.includes('/data-tools/') || 
                           window.location.pathname.includes('/data_tools/')) {
                    uxMode = 'data_tools';  // We're in data tools
                } else {
                    uxMode = 'dashboard';  // We're in dashboard or general context
                }
            }
            
            // Set parameters based on context
            if (projectId && !forceProjectSelection) {
                params.append('project_id', projectId);
            }
            if (forceProjectSelection) {
                params.append('force_selection', 'true');
            }
            
            // Always send UX mode for contextual experience
            params.append('ux_mode', uxMode);
            
            const url = `/projects/datasource/upload-form-partial/?${params}`;
                
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
        // Close all other panels first
        this.isUploadPanelOpen = false;
        this.isNewProjectPanelOpen = false;
        this.isNewSuitePanelOpen = false;
        
        // Then open the requested panel
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
        try {
            // Get current project ID from URL
            const projectId = this.getCurrentProjectId();
            const url = projectId 
                ? `/experiments/ml-experiment-form-partial/?project_id=${projectId}`
                : '/experiments/ml-experiment-form-partial/';
                
            const response = await fetch(url);
            const html = await response.text();
            
            const container = document.getElementById('new-experiment-form-container');
            if (container) {
                container.innerHTML = html;
                this.newExperimentFormLoaded = true;
                // Initialize ML experiment form logic after DOM is ready
                setTimeout(() => {
                    this.initializeMLExperimentFormLogic();
                }, 100);
            }
        } catch (error) {
            console.error('Error loading new experiment form:', error);
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
                // Initialize form logic after DOM is ready
                setTimeout(() => {
                    this.initializeNewProjectForm();
                }, 100);
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
                // Initialize form logic after DOM is ready
                setTimeout(() => {
                    this.initializeNewSuiteForm();
                }, 100);
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
        console.log('🚀 [APP.JS] ================================');
        console.log('🚀 [APP.JS] initializeNewExperimentForm called');
        
        // Re-initialize any Alpine.js components in the dynamically loaded content
        this.$nextTick(() => {
            console.log('🔧 [APP.JS] Inside $nextTick - DOM should be ready');
            
            // Find any Alpine.js components in the new experiment form and initialize them
            const formContainer = document.getElementById('new-experiment-form-container');
            console.log('🔧 [APP.JS] Form container found:', !!formContainer);
            
            if (formContainer && window.Alpine) {
                console.log('🔧 [APP.JS] Initializing Alpine.js tree for form container');
                window.Alpine.initTree(formContainer);
            }
            
            // NUEVA IMPLEMENTACIÓN: Ejecutar directamente la lógica del ml_experiment_form.js
            console.log('🔧 [APP.JS] Manually initializing ML experiment form logic...');
            this.initializeMLExperimentFormLogic();
        });
    },
    
    // Nueva función para inicializar manualmente la lógica del formulario ML
    initializeMLExperimentFormLogic() {
        console.log('🧪 [MANUAL INIT] ================================');
        console.log('🧪 [MANUAL INIT] Starting manual ML experiment form initialization');
        
        // Verificar que el formulario existe
        const experimentForm = document.getElementById('experiment-form');
        if (!experimentForm) {
            console.error('❌ [MANUAL INIT] Experiment form not found, aborting initialization');
            return;
        }
        console.log('✅ [MANUAL INIT] Experiment form found:', experimentForm);
        
        // Obtener referencias a los elementos críticos
        const datasourceSelect = document.getElementById('id_input_datasource');
        const targetColumnSelect = document.getElementById('id_target_column_select');
        const featuresAvailable = document.getElementById('features-available');
        const featuresSelected = document.getElementById('features-selected');
        const hiddenTargetInput = document.getElementById('id_target_column');
        const hiddenFeatureSet = document.getElementById('id_feature_set');
        const btnAdd = document.getElementById('btn-add-feature');
        const btnRemove = document.getElementById('btn-remove-feature');
        
        console.log('🔍 [MANUAL INIT] Element validation:');
        console.log('🔍 [MANUAL INIT] - datasourceSelect:', !!datasourceSelect);
        console.log('🔍 [MANUAL INIT] - targetColumnSelect:', !!targetColumnSelect);
        console.log('🔍 [MANUAL INIT] - featuresAvailable:', !!featuresAvailable);
        console.log('🔍 [MANUAL INIT] - featuresSelected:', !!featuresSelected);
        console.log('🔍 [MANUAL INIT] - hiddenTargetInput:', !!hiddenTargetInput);
        console.log('🔍 [MANUAL INIT] - hiddenFeatureSet:', !!hiddenFeatureSet);
        console.log('🔍 [MANUAL INIT] - btnAdd:', !!btnAdd);
        console.log('🔍 [MANUAL INIT] - btnRemove:', !!btnRemove);
        
        if (!datasourceSelect) {
            console.error('❌ [MANUAL INIT] Critical element datasourceSelect not found!');
            return;
        }
        
        // Obtener la URL template del dataset
        const getColumnsUrlTemplate = experimentForm.dataset.getColumnsUrlTemplate || experimentForm.dataset.getColumnsUrl;
        console.log('🌐 [MANUAL INIT] URL template:', getColumnsUrlTemplate);
        
        if (!getColumnsUrlTemplate) {
            console.error('❌ [MANUAL INIT] getColumnsUrlTemplate missing from form dataset!');
            return;
        }
        
        // Función para sincronizar campos ocultos
        const syncHiddenInputs = () => {
            if (hiddenTargetInput && targetColumnSelect) {
                hiddenTargetInput.value = targetColumnSelect.value;
            }
            if (hiddenFeatureSet && featuresSelected) {
                const values = Array.from(featuresSelected.options).map(opt => opt.value);
                hiddenFeatureSet.value = JSON.stringify(values);
            }
            console.log('🔄 [MANUAL INIT] Hidden inputs synchronized');
        };
        
        // Función para mover opciones entre listas
        const moveOptions = (source, destination) => {
            Array.from(source.selectedOptions).forEach(opt => {
                destination.appendChild(opt);
            });
            syncHiddenInputs();
        };
        
        // Función para poblar opciones de select
        const populateSelectOptions = (selectElement, columns, defaultText) => {
            console.log('🔧 [MANUAL INIT] Populating select with', columns?.length, 'columns');
            
            if (!selectElement) {
                console.error('❌ [MANUAL INIT] Select element not provided');
                return;
            }
            
            selectElement.innerHTML = '';
            const defaultOption = new Option(defaultText, '');
            selectElement.add(defaultOption);
            
            if (columns && Array.isArray(columns)) {
                columns.forEach(column => {
                    const option = new Option(column, column);
                    selectElement.add(option);
                });
                console.log('✅ [MANUAL INIT] Added', columns.length, 'options to select');
            }
        };
        
        // Función principal para manejar cambios en DataSource
        const handleDataSourceChange = async (event) => {
            console.log('🔧 [MANUAL INIT] DataSource change triggered');
            console.log('🔧 [MANUAL INIT] New value:', event.target.value);
            
            const datasourceId = event.target.value;
            
            // Reset dropdowns
            if (targetColumnSelect) {
                targetColumnSelect.innerHTML = '<option value="">Cargando...</option>';
                targetColumnSelect.disabled = true;
            }
            if (featuresAvailable) {
                featuresAvailable.innerHTML = '';
            }
            if (featuresSelected) {
                featuresSelected.innerHTML = '';
            }
            
            syncHiddenInputs();
            
            if (!datasourceId) {
                if (targetColumnSelect) {
                    targetColumnSelect.innerHTML = '<option value="">Primero selecciona una Fuente de Datos</option>';
                }
                console.log('⚠️ [MANUAL INIT] No datasource selected');
                return;
            }
            
            try {
                console.log('🌐 [MANUAL INIT] Making API call...');
                const apiUrl = getColumnsUrlTemplate.replace('00000000-0000-0000-0000-000000000000', datasourceId);
                console.log('🌐 [MANUAL INIT] API URL:', apiUrl);
                
                const response = await fetch(apiUrl);
                console.log('📡 [MANUAL INIT] Response status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                console.log('📦 [MANUAL INIT] API response data:', data);
                
                if (data.columns && Array.isArray(data.columns)) {
                    console.log('✅ [MANUAL INIT] Columns received:', data.columns.length);
                    
                    // Populate target column select
                    if (targetColumnSelect) {
                        populateSelectOptions(targetColumnSelect, data.columns, '-- Selecciona variable objetivo --');
                        targetColumnSelect.disabled = false;
                    }
                    
                    // Populate features available
                    if (featuresAvailable) {
                        populateSelectOptions(featuresAvailable, data.columns, '-- Selecciona columnas características --');
                    }
                } else {
                    throw new Error('No columns found in API response');
                }
                
            } catch (error) {
                console.error('❌ [MANUAL INIT] Error loading columns:', error);
                if (targetColumnSelect) {
                    targetColumnSelect.innerHTML = `<option value="">Error: ${error.message}</option>`;
                }
            }
        };
        
        // Registrar event listeners
        console.log('🔧 [MANUAL INIT] Registering event listeners...');
        
        // DataSource change listener
        datasourceSelect.addEventListener('change', handleDataSourceChange);
        console.log('✅ [MANUAL INIT] DataSource change listener registered');
        
        // Feature list movement listeners
        if (btnAdd && featuresAvailable && featuresSelected) {
            btnAdd.addEventListener('click', () => moveOptions(featuresAvailable, featuresSelected));
            console.log('✅ [MANUAL INIT] Add feature button listener registered');
        }
        
        if (btnRemove && featuresAvailable && featuresSelected) {
            btnRemove.addEventListener('click', () => moveOptions(featuresSelected, featuresAvailable));
            console.log('✅ [MANUAL INIT] Remove feature button listener registered');
        }
        
        // Target column change listener
        if (targetColumnSelect) {
            targetColumnSelect.addEventListener('change', syncHiddenInputs);
            console.log('✅ [MANUAL INIT] Target column change listener registered');
        }
        
        // Features selected change listener
        if (featuresSelected) {
            featuresSelected.addEventListener('change', syncHiddenInputs);
            console.log('✅ [MANUAL INIT] Features selected change listener registered');
        }
        
        // Model selection and hyperparameters logic
        const modelSelect = document.getElementById("id_model_name");
        const rfFields = document.getElementById("rf-fields");
        const gbFields = document.getElementById("gb-fields");
        
        if (modelSelect) {
            const updateHyperparameterFields = () => {
                // Hide all fields first
                if (rfFields) rfFields.classList.add("hidden");
                if (gbFields) gbFields.classList.add("hidden");
                
                // Show relevant fields
                const value = modelSelect.value;
                if (value === "RandomForestRegressor" && rfFields) {
                    rfFields.classList.remove("hidden");
                } else if (value === "GradientBoostingRegressor" && gbFields) {
                    gbFields.classList.remove("hidden");
                }
                console.log('🔧 [MANUAL INIT] Hyperparameter fields updated for model:', value);
            };
            
            modelSelect.addEventListener("change", updateHyperparameterFields);
            updateHyperparameterFields(); // Initial call
            console.log('✅ [MANUAL INIT] Model selection listener registered');
        }
        
        // Split strategy visibility logic
        const splitStrategy = document.getElementById('id_split_strategy');
        const randomStateField = document.getElementById('id_split_random_state');
        
        if (splitStrategy && randomStateField) {
            const updateRandomStateVisibility = () => {
                const randomStateDiv = randomStateField.closest('.form-group, .mb-4, div') || randomStateField.parentElement;
                
                if (splitStrategy.value === 'RANDOM') {
                    randomStateDiv.style.display = '';
                } else {
                    randomStateDiv.style.display = 'none';
                }
                console.log('🔧 [MANUAL INIT] Random state visibility updated');
            };
            
            splitStrategy.addEventListener('change', updateRandomStateVisibility);
            updateRandomStateVisibility(); // Initial call
            console.log('✅ [MANUAL INIT] Split strategy listener registered');
        }
        
        console.log('🎉 [MANUAL INIT] ML experiment form initialization completed successfully!');
        
        // Test the DataSource selector immediately
        if (datasourceSelect && datasourceSelect.options.length > 1) {
            console.log('🧪 [MANUAL INIT] Testing DataSource selector with available options...');
            console.log('🧪 [MANUAL INIT] Available options:', Array.from(datasourceSelect.options).map(opt => ({value: opt.value, text: opt.text})));
        }
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
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.closeNewExperimentPanel();
                this.showMessage(result.message, 'success');
                
                // Redirect if specified
                if (result.redirect_url) {
                    window.location.href = result.redirect_url;
                }
            } else {
                // Handle form errors
                this.showMessage('Error en el formulario. Revisa los campos.', 'error');
            }
        } catch (error) {
            console.error('Error submitting experiment form:', error);
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
    },
    
    // Function to refresh DataSource lists after upload
    async refreshDataSourceLists() {
        const projectId = this.getCurrentProjectId();
        if (!projectId) return;
        
        try {
            const response = await fetch(`/projects/${projectId}/datasources/api/`);
            const data = await response.json();
            
            if (data.success) {
                // Update the experiment form datasource dropdown if it exists
                this.updateExperimentFormDataSources(data.datasources);
                
                // Update the main page datasources table
                this.updateMainPageDataSources(data.datasources);
            }
        } catch (error) {
            console.error('Error refreshing datasource lists:', error);
        }
    },
    
    updateExperimentFormDataSources(datasources) {
        const select = document.getElementById('id_input_datasource');
        if (!select) return;
        
        // Clear current options except the first one (usually empty option)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Add new datasources
        datasources.forEach(ds => {
            const option = document.createElement('option');
            option.value = ds.id;
            option.textContent = ds.name;
            select.appendChild(option);
        });
    },
    
    updateMainPageDataSources(datasources) {
        // This would ideally update the main table, but for now we'll just reload
        // In a more sophisticated implementation, we'd update the DOM directly
        window.location.reload();
    }
});
