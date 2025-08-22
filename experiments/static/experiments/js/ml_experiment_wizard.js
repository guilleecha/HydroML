/**
 * ML Experiment Wizard - Multi-step form controller
 * 
 * This component manages the multi-step wizard interface for creating
 * ML experiments, providing navigation, validation, and state management.
 */

// Wizard step definitions
const WIZARD_STEPS = [
    {
        id: 'basic-info',
        title: 'Información Básica',
        description: 'Nombre, descripción y workspace del experimento',
        icon: '📝',
        validation: ['name', 'project']
    },
    {
        id: 'dataset-target',
        title: 'Dataset y Variable Objetivo',
        description: 'Selecciona la fuente de datos y variable objetivo',
        icon: '🎯',
        validation: ['input_datasource', 'target_column']
    },
    {
        id: 'feature-selection',
        title: 'Selección de Variables',
        description: 'Elige las variables predictoras para tu modelo',
        icon: '📊',
        validation: ['feature_set']
    },
    {
        id: 'model-config',
        title: 'Configuración del Modelo',
        description: 'Selecciona algoritmo e hiperparámetros',
        icon: '🤖',
        validation: ['model_name']
    },
    {
        id: 'training-setup',
        title: 'Configuración de Entrenamiento',
        description: 'Estrategia de validación y parámetros finales',
        icon: '⚙️',
        validation: ['split_strategy']
    }
];

/**
 * ML Experiment Wizard Alpine.js Component
 */
function mlExperimentWizard() {
    return {
        // Wizard state
        currentStep: 0,
        steps: WIZARD_STEPS,
        isSubmitting: false,
        
        // Form state persistence
        formData: {
            name: '',
            description: '',
            project: '',
            input_datasource: '',
            target_column: '',
            feature_set: [],
            model_name: 'random_forest',
            split_strategy: 'random',
            test_split_size: 0.2,
            split_random_state: 42
        },
        
        // Validation state
        stepErrors: {},
        globalErrors: [],
        
        // UI state
        isNavigating: false,
        
        init() {
            console.log('🧙‍♂️ ML Experiment Wizard initialized');
            
            // Load any existing form data from localStorage (draft mode)
            this.loadDraftData();
            
            // Set up auto-save for draft functionality
            this.setupAutoSave();
            
            // Initialize step-specific logic
            this.initCurrentStep();
        },
        
        // Navigation methods
        get canGoNext() {
            return this.currentStep < this.steps.length - 1 && this.isCurrentStepValid();
        },
        
        get canGoPrev() {
            return this.currentStep > 0;
        },
        
        get isLastStep() {
            return this.currentStep === this.steps.length - 1;
        },
        
        get currentStepData() {
            return this.steps[this.currentStep];
        },
        
        get progressPercentage() {
            return Math.round(((this.currentStep + 1) / this.steps.length) * 100);
        },
        
        async nextStep() {
            if (!this.canGoNext) return;
            
            this.isNavigating = true;
            
            try {
                // Validate current step
                const isValid = await this.validateCurrentStep();
                if (!isValid) {
                    this.isNavigating = false;
                    return;
                }
                
                // Save current step data
                this.saveStepData();
                
                // Move to next step
                this.currentStep++;
                this.initCurrentStep();
                
                // Scroll to top of wizard
                this.scrollToWizard();
                
            } catch (error) {
                console.error('Error navigating to next step:', error);
                this.addGlobalError('Error al avanzar al siguiente paso');
            } finally {
                this.isNavigating = false;
            }
        },
        
        async prevStep() {
            if (!this.canGoPrev) return;
            
            this.isNavigating = true;
            
            try {
                // Save current step data (no validation required for going back)
                this.saveStepData();
                
                // Move to previous step
                this.currentStep--;
                this.initCurrentStep();
                
                // Scroll to top of wizard
                this.scrollToWizard();
                
            } catch (error) {
                console.error('Error navigating to previous step:', error);
            } finally {
                this.isNavigating = false;
            }
        },
        
        goToStep(stepIndex) {
            if (stepIndex < 0 || stepIndex >= this.steps.length) return;
            if (stepIndex > this.currentStep && !this.canGoNext) return;
            
            this.currentStep = stepIndex;
            this.initCurrentStep();
            this.scrollToWizard();
        },
        
        // Validation methods
        isCurrentStepValid() {
            const step = this.currentStepData;
            const requiredFields = step.validation || [];
            
            return requiredFields.every(field => {
                const value = this.formData[field];
                return value !== null && value !== undefined && value !== '' && 
                       (Array.isArray(value) ? value.length > 0 : true);
            });
        },
        
        async validateCurrentStep() {
            const step = this.currentStepData;
            this.clearStepErrors(this.currentStep);
            
            // Client-side validation
            const clientErrors = this.validateStepFields(step);
            if (clientErrors.length > 0) {
                this.stepErrors[this.currentStep] = clientErrors;
                return false;
            }
            
            // Server-side validation (for steps that need it)
            if (step.id === 'dataset-target' && this.formData.input_datasource) {
                try {
                    const isValid = await this.validateDatasetSelection();
                    if (!isValid) return false;
                } catch (error) {
                    this.addStepError(this.currentStep, 'Error validating dataset selection');
                    return false;
                }
            }
            
            return true;
        },
        
        validateStepFields(step) {
            const errors = [];
            const requiredFields = step.validation || [];
            
            requiredFields.forEach(field => {
                const value = this.formData[field];
                const isEmpty = value === null || value === undefined || value === '' || 
                               (Array.isArray(value) && value.length === 0);
                
                if (isEmpty) {
                    errors.push(`${this.getFieldLabel(field)} es requerido`);
                }
            });
            
            return errors;
        },
        
        async validateDatasetSelection() {
            // This would call an API to validate the selected dataset
            // For now, we'll just check if target column is compatible
            return true; // Placeholder
        },
        
        // Data management methods
        saveStepData() {
            // Save current form state to localStorage as draft
            localStorage.setItem('ml_experiment_draft', JSON.stringify(this.formData));
            localStorage.setItem('ml_experiment_draft_step', this.currentStep.toString());
        },
        
        loadDraftData() {
            try {
                const draftData = localStorage.getItem('ml_experiment_draft');
                const draftStep = localStorage.getItem('ml_experiment_draft_step');
                
                if (draftData) {
                    this.formData = { ...this.formData, ...JSON.parse(draftData) };
                }
                
                if (draftStep) {
                    this.currentStep = parseInt(draftStep);
                }
            } catch (error) {
                console.warn('Could not load draft data:', error);
            }
        },
        
        clearDraftData() {
            localStorage.removeItem('ml_experiment_draft');
            localStorage.removeItem('ml_experiment_draft_step');
        },
        
        setupAutoSave() {
            // Auto-save every 30 seconds
            setInterval(() => {
                this.saveStepData();
            }, 30000);
        },
        
        // Step-specific initialization
        initCurrentStep() {
            const step = this.currentStepData;
            
            // Clear any previous errors for this step
            this.clearStepErrors(this.currentStep);
            
            // Step-specific initialization
            switch (step.id) {
                case 'basic-info':
                    this.initBasicInfoStep();
                    break;
                case 'dataset-target':
                    this.initDatasetTargetStep();
                    break;
                case 'feature-selection':
                    this.initFeatureSelectionStep();
                    break;
                case 'model-config':
                    this.initModelConfigStep();
                    break;
                case 'training-setup':
                    this.initTrainingSetupStep();
                    break;
            }
        },
        
        initBasicInfoStep() {
            // Initialize workspace selector if needed
            this.$nextTick(() => {
                const workspaceSelector = document.querySelector('[x-data="workspaceSelector()"]');
                if (workspaceSelector && workspaceSelector._x_dataStack) {
                    // Workspace selector already initialized
                } else {
                    // Initialize workspace selector logic
                    this.initWorkspaceSelector();
                }
            });
        },
        
        initDatasetTargetStep() {
            // Initialize dataset selection logic
            this.$nextTick(() => {
                this.initDatasetSelector();
                this.initTargetColumnSelector();
            });
        },
        
        initFeatureSelectionStep() {
            // Initialize feature selection interface
            this.$nextTick(() => {
                this.initFeatureSelector();
            });
        },
        
        initModelConfigStep() {
            // Initialize model selection and hyperparameter controls
            this.$nextTick(() => {
                this.initModelSelector();
                this.initHyperparameterControls();
            });
        },
        
        initTrainingSetupStep() {
            // Initialize training configuration
            this.$nextTick(() => {
                this.initTrainingConfig();
            });
        },
        
        // Placeholder methods for step-specific logic (to be implemented)
        initWorkspaceSelector() {
            console.log('Initializing workspace selector...');
        },
        
        initDatasetSelector() {
            console.log('Initializing dataset selector...');
        },
        
        initTargetColumnSelector() {
            console.log('Initializing target column selector...');
        },
        
        initFeatureSelector() {
            console.log('Initializing feature selector...');
        },
        
        initModelSelector() {
            console.log('Initializing model selector...');
        },
        
        initHyperparameterControls() {
            console.log('Initializing hyperparameter controls...');
        },
        
        initTrainingConfig() {
            console.log('Initializing training configuration...');
        },
        
        // Form submission
        async submitExperiment() {
            if (this.isSubmitting) return;
            
            this.isSubmitting = true;
            this.clearGlobalErrors();
            
            try {
                // Final validation of all steps
                const isFormValid = await this.validateAllSteps();
                if (!isFormValid) {
                    this.addGlobalError('Por favor corrige los errores en el formulario');
                    this.isSubmitting = false;
                    return;
                }
                
                // Prepare form data for submission
                const submitData = this.prepareSubmissionData();
                
                // Submit to server
                const response = await this.submitToServer(submitData);
                
                if (response.success) {
                    // Clear draft data
                    this.clearDraftData();
                    
                    // Show success message and redirect
                    this.showSuccessMessage();
                    
                    // Close wizard or redirect
                    if (typeof isNewExperimentPanelOpen !== 'undefined') {
                        isNewExperimentPanelOpen = false;
                    }
                } else {
                    this.addGlobalError(response.error || 'Error al crear el experimento');
                }
                
            } catch (error) {
                console.error('Error submitting experiment:', error);
                this.addGlobalError('Error de conexión al enviar el experimento');
            } finally {
                this.isSubmitting = false;
            }
        },
        
        async validateAllSteps() {
            let isValid = true;
            
            for (let i = 0; i < this.steps.length; i++) {
                const step = this.steps[i];
                const stepErrors = this.validateStepFields(step);
                
                if (stepErrors.length > 0) {
                    this.stepErrors[i] = stepErrors;
                    isValid = false;
                }
            }
            
            return isValid;
        },
        
        prepareSubmissionData() {
            // Convert wizard form data to Django form format
            const formData = new FormData();
            
            Object.keys(this.formData).forEach(key => {
                const value = this.formData[key];
                if (Array.isArray(value)) {
                    value.forEach((item, index) => {
                        formData.append(`${key}[${index}]`, item);
                    });
                } else if (value !== null && value !== undefined) {
                    formData.append(key, value);
                }
            });
            
            // Add CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
            if (csrfToken) {
                formData.append('csrfmiddlewaretoken', csrfToken);
            }
            
            return formData;
        },
        
        async submitToServer(formData) {
            const response = await fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            return await response.json();
        },
        
        // Error handling
        clearStepErrors(stepIndex) {
            delete this.stepErrors[stepIndex];
        },
        
        clearGlobalErrors() {
            this.globalErrors = [];
        },
        
        addStepError(stepIndex, error) {
            if (!this.stepErrors[stepIndex]) {
                this.stepErrors[stepIndex] = [];
            }
            this.stepErrors[stepIndex].push(error);
        },
        
        addGlobalError(error) {
            this.globalErrors.push(error);
        },
        
        getStepErrors(stepIndex) {
            return this.stepErrors[stepIndex] || [];
        },
        
        hasStepErrors(stepIndex) {
            return this.getStepErrors(stepIndex).length > 0;
        },
        
        // Utility methods
        getFieldLabel(field) {
            const labels = {
                name: 'Nombre del experimento',
                description: 'Descripción',
                project: 'Workspace',
                input_datasource: 'Fuente de datos',
                target_column: 'Variable objetivo',
                feature_set: 'Variables predictoras',
                model_name: 'Modelo',
                split_strategy: 'Estrategia de división'
            };
            
            return labels[field] || field;
        },
        
        scrollToWizard() {
            this.$nextTick(() => {
                const wizardElement = this.$root;
                if (wizardElement) {
                    wizardElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        },
        
        showSuccessMessage() {
            // This could be enhanced with a toast notification system
            console.log('✅ Experiment created successfully!');
        }
    };
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { mlExperimentWizard, WIZARD_STEPS };
}