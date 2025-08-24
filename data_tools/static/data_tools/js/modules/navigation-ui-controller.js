/**
 * NavigationUIController - Navigation User Interface Management
 * Responsabilidad única: Renderizado y actualización de UI de navegación (NO lógica de negocio)
 * 
 * Filosofía: Pure UI rendering, configurable selectors, event handling with proper cleanup
 */

class NavigationUIController {
    constructor(stateManager, config = {}) {
        this.stateManager = stateManager;
        
        // Configurable DOM selectors (fixes hard-coded DOM integration issue)
        this.config = {
            sectionSelector: '[data-section]',
            workflowContainer: '#workflow-progress-container',
            breadcrumbContainer: '#breadcrumb-container',
            ...config
        };

        // Event handlers cleanup map
        this.eventHandlers = new Map();
        this.activeCleanupTasks = [];

        // Setup state manager event listeners
        this.setupStateListeners();
    }

    // === STATE MANAGER EVENT LISTENERS ===

    setupStateListeners() {
        this.stateManager.addEventListener('section-changed', (event) => {
            this.updateSectionUI(event.detail);
        });

        this.stateManager.addEventListener('workflow-initialized', (event) => {
            this.renderWorkflowProgress(event.detail);
        });

        this.stateManager.addEventListener('workflow-step-updated', (event) => {
            this.updateWorkflowProgress(event.detail);
        });

        this.stateManager.addEventListener('workflow-reset', () => {
            this.hideWorkflowProgress();
        });

        this.stateManager.addEventListener('breadcrumb-updated', (event) => {
            this.updateBreadcrumbDisplay(event.detail);
        });
    }

    // === SECTION UI MANAGEMENT ===

    updateSectionUI(sectionData) {
        const { previousSection, currentSection } = sectionData;
        
        // Update all sections
        this.updateAllSections(currentSection);
        
        // Dispatch UI update event
        this.dispatchUIEvent('section-ui-updated', { 
            previousSection, 
            currentSection 
        });
    }

    updateAllSections(activeSection) {
        const sections = this.stateManager.getSidebarSections();
        
        sections.forEach(section => {
            const element = document.querySelector(`${this.config.sectionSelector}="${section}"]`);
            if (element) {
                this.updateSectionElement(element, section, activeSection);
            }
        });
    }

    updateSectionElement(element, section, activeSection) {
        const button = element.querySelector('button');
        const title = element.querySelector('.section-title') || button?.querySelector('span:not(.text-blue-600)');
        
        if (section === activeSection) {
            this.applySectionActiveState(button, title, element);
        } else {
            this.applySectionInactiveState(button, title, element);
        }
    }

    applySectionActiveState(button, title, element) {
        // Apply active CSS classes
        button?.classList.add('sidebar-section-active', 'border-l-4', 'border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
        button?.classList.remove('sidebar-section-inactive', 'bg-white', 'dark:bg-gray-800');
        title?.classList.add('text-blue-800', 'dark:text-blue-300', 'font-semibold');
        title?.classList.remove('text-gray-900', 'dark:text-gray-100');
        
        // Add active indicator if not present
        if (!element.querySelector('.active-indicator')) {
            const indicator = this.createActiveIndicator();
            button?.querySelector('div')?.appendChild(indicator);
        }
    }

    applySectionInactiveState(button, title, element) {
        // Apply inactive CSS classes
        button?.classList.remove('sidebar-section-active', 'border-l-4', 'border-blue-500', 'bg-blue-50', 'dark:bg-blue-900/20');
        button?.classList.add('sidebar-section-inactive', 'bg-white', 'dark:bg-gray-800');
        title?.classList.remove('text-blue-800', 'dark:text-blue-300', 'font-semibold');
        title?.classList.add('text-gray-900', 'dark:text-gray-100');
        
        // Remove active indicator
        const indicator = element.querySelector('.active-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    createActiveIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'w-2 h-2 bg-blue-500 rounded-full animate-pulse active-indicator';
        indicator.title = 'Active Section';
        return indicator;
    }

    // === WORKFLOW PROGRESS UI ===

    renderWorkflowProgress(workflowData) {
        const container = document.querySelector(this.config.workflowContainer);
        if (!container) {
            console.warn('Workflow progress container not found');
            return false;
        }

        const html = this.generateWorkflowHTML(workflowData);
        container.innerHTML = html;
        container.style.display = 'block';

        this.dispatchUIEvent('workflow-rendered', workflowData);
        return true;
    }

    updateWorkflowProgress(workflowData) {
        const container = document.querySelector(this.config.workflowContainer);
        if (!container) return false;

        // Update progress bar
        const progressBar = container.querySelector('.workflow-progress-fill');
        if (progressBar) {
            progressBar.style.width = `${workflowData.progress}%`;
        }

        // Update progress text
        const progressText = container.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `Progress: Step ${workflowData.currentStep} of ${workflowData.totalSteps}`;
        }

        const percentageText = container.querySelector('.percentage-text');
        if (percentageText) {
            percentageText.textContent = `${Math.round(workflowData.progress)}%`;
        }

        // Update step indicators
        this.updateStepIndicators(container, workflowData);

        this.dispatchUIEvent('workflow-updated', workflowData);
        return true;
    }

    generateWorkflowHTML(workflowData) {
        const { currentStep, totalSteps, progress } = workflowData;
        
        return `
            <div class="workflow-progress-container">
                <div class="flex items-center justify-between mb-2">
                    <span class="progress-text text-sm font-medium text-gray-900 dark:text-gray-100">
                        Progress: Step ${currentStep} of ${totalSteps}
                    </span>
                    <span class="percentage-text text-sm text-gray-600 dark:text-gray-400">${Math.round(progress)}%</span>
                </div>
                <div class="workflow-progress-bar">
                    <div class="workflow-progress-fill" style="width: ${progress}%"></div>
                </div>
                <div class="flex justify-between mt-3">
                    ${this.generateStepIndicators(currentStep, totalSteps)}
                </div>
            </div>
        `;
    }

    generateStepIndicators(currentStep, totalSteps) {
        return Array.from({length: totalSteps}, (_, i) => {
            const stepNum = i + 1;
            let stepClass = 'workflow-step ';
            
            if (stepNum < currentStep) {
                stepClass += 'workflow-step-completed';
            } else if (stepNum === currentStep) {
                stepClass += 'workflow-step-current';
            } else {
                stepClass += 'workflow-step-pending';
            }
            
            return `<div class="${stepClass}" data-step="${stepNum}">${stepNum}</div>`;
        }).join('');
    }

    updateStepIndicators(container, workflowData) {
        const { currentStep, totalSteps } = workflowData;
        
        for (let i = 1; i <= totalSteps; i++) {
            const stepElement = container.querySelector(`[data-step="${i}"]`);
            if (stepElement) {
                // Remove all step classes
                stepElement.classList.remove('workflow-step-completed', 'workflow-step-current', 'workflow-step-pending');
                
                // Add appropriate class
                if (i < currentStep) {
                    stepElement.classList.add('workflow-step-completed');
                } else if (i === currentStep) {
                    stepElement.classList.add('workflow-step-current');
                } else {
                    stepElement.classList.add('workflow-step-pending');
                }
            }
        }
    }

    hideWorkflowProgress() {
        const container = document.querySelector(this.config.workflowContainer);
        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
            this.dispatchUIEvent('workflow-hidden');
        }
    }

    showWorkflowProgress() {
        const container = document.querySelector(this.config.workflowContainer);
        if (container) {
            container.style.display = 'block';
            this.dispatchUIEvent('workflow-shown');
        }
    }

    // === BREADCRUMB UI ===

    updateBreadcrumbDisplay(breadcrumbData) {
        const container = document.querySelector(this.config.breadcrumbContainer);
        if (!container) return false;

        const html = this.generateBreadcrumbHTML(breadcrumbData.breadcrumbPath);
        container.innerHTML = html;

        this.dispatchUIEvent('breadcrumb-updated', breadcrumbData);
        return true;
    }

    generateBreadcrumbHTML(breadcrumbPath) {
        if (!Array.isArray(breadcrumbPath) || breadcrumbPath.length === 0) {
            return '';
        }

        return breadcrumbPath.map((item, index) => {
            const isLast = index === breadcrumbPath.length - 1;
            const escapedItem = this.escapeHtml(item);
            
            if (isLast) {
                return `<span class="text-gray-600 dark:text-gray-400 font-medium">${escapedItem}</span>`;
            } else {
                return `
                    <span class="text-blue-600 dark:text-blue-400 hover:text-blue-800 cursor-pointer" data-breadcrumb-item="${index}">
                        ${escapedItem}
                    </span>
                    <span class="text-gray-400 mx-2">→</span>
                `;
            }
        }).join('');
    }

    // === NOTIFICATION SYSTEM ===

    showNotification(message, type = 'info', duration = 3000) {
        if (window.dataStudioNotifications && window.dataStudioNotifications.show) {
            window.dataStudioNotifications.show(message, type, duration);
        } else {
            console.log(`Navigation ${type}:`, message);
        }
    }

    // === UTILITY METHODS ===

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    dispatchUIEvent(eventName, detail = {}) {
        window.dispatchEvent(new CustomEvent(`navigation-ui-${eventName}`, { detail }));
    }

    // === CONFIGURATION ===

    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
        this.dispatchUIEvent('config-updated', { config: this.config });
    }

    getConfig() {
        return { ...this.config };
    }

    // === CLEANUP MANAGEMENT ===

    addCleanupTask(task) {
        this.activeCleanupTasks.push(task);
    }

    cleanup() {
        // Execute all cleanup tasks
        this.activeCleanupTasks.forEach(task => {
            try {
                task();
            } catch (error) {
                console.warn('Error during navigation UI cleanup:', error);
            }
        });
        
        this.activeCleanupTasks = [];
        this.eventHandlers.clear();
    }

    // === CLEANUP ===

    destroy() {
        this.cleanup();
        this.hideWorkflowProgress();
        this.stateManager = null;
        this.dispatchUIEvent('destroyed');
    }

    // === GETTERS ===

    get isWorkflowVisible() {
        const container = document.querySelector(this.config.workflowContainer);
        return container && container.style.display !== 'none';
    }
}

// Export for use in other modules
window.NavigationUIController = NavigationUIController;

// Export removed for script tag compatibility