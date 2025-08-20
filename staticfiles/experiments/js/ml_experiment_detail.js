/**
 * ML Experiment Detail - Tab Management and UI Logic
 * Handles tab switching and experiment detail interactions
 */

class MLExperimentDetail {
    constructor() {
        this.tabs = ['tab-results', 'tab-interpretability', 'tab-mlflow-params', 'tab-mlflow-metrics', 'tab-config', 'tab-artifacts', 'tab-lineage', 'tab-report'];
        this.buttons = ['tab-results-btn', 'tab-interpretability-btn', 'tab-mlflow-params-btn', 'tab-mlflow-metrics-btn', 'tab-config-btn', 'tab-artifacts-btn', 'tab-lineage-btn', 'tab-report-btn'];
        
        this.init();
    }

    init() {
        this.bindTabEvents();
    }

    /**
     * Switch between tabs
     */
    switchTab(activeTabId, activeButtonId) {
        // Hide all tabs
        this.tabs.forEach(tabId => {
            const tabElement = document.getElementById(tabId);
            if (tabElement) {
                tabElement.classList.add('hidden');
            }
        });

        // Reset all buttons
        this.buttons.forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.classList.remove('text-brand-600', 'border-brand-600');
                button.classList.add('text-foreground-muted', 'border-transparent');
            }
        });

        // Show active tab
        const activeTab = document.getElementById(activeTabId);
        if (activeTab) {
            activeTab.classList.remove('hidden');
        }

        // Update active button
        const activeButton = document.getElementById(activeButtonId);
        if (activeButton) {
            activeButton.classList.remove('text-foreground-muted', 'border-transparent');
            activeButton.classList.add('text-brand-600', 'border-brand-600');
        }
    }

    /**
     * Bind event listeners to tab buttons
     */
    bindTabEvents() {
        // Standard tabs that always exist
        const standardTabs = [
            { tabId: 'tab-results', buttonId: 'tab-results-btn' },
            { tabId: 'tab-interpretability', buttonId: 'tab-interpretability-btn' },
            { tabId: 'tab-config', buttonId: 'tab-config-btn' },
            { tabId: 'tab-artifacts', buttonId: 'tab-artifacts-btn' },
            { tabId: 'tab-lineage', buttonId: 'tab-lineage-btn' },
            { tabId: 'tab-report', buttonId: 'tab-report-btn' }
        ];

        standardTabs.forEach(({ tabId, buttonId }) => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.addEventListener('click', () => this.switchTab(tabId, buttonId));
            }
        });

        // Optional MLflow tabs (only if they exist)
        const optionalTabs = [
            { tabId: 'tab-mlflow-params', buttonId: 'tab-mlflow-params-btn' },
            { tabId: 'tab-mlflow-metrics', buttonId: 'tab-mlflow-metrics-btn' }
        ];

        optionalTabs.forEach(({ tabId, buttonId }) => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.addEventListener('click', () => this.switchTab(tabId, buttonId));
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.mlExperimentDetail = new MLExperimentDetail();
});

// Export for use in other modules
window.MLExperimentDetail = MLExperimentDetail;