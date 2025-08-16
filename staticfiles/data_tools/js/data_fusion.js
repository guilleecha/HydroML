/**
 * Data Fusion Interactive Frontend Logic
 * 
 * This script handles the interactive behavior for the data fusion page,
 * including loading columns from selected DataSources and enabling
 * dynamic form sections.
 */

class DataFusionManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupCSRF();
    }

    /**
     * Set up CSRF token for AJAX requests
     */
    setupCSRF() {
        // Get CSRF token from the form
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        this.csrfToken = csrfInput ? csrfInput.value : '';
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        const loadColumnsBtn = document.querySelector('button[type="submit"]');
        if (loadColumnsBtn) {
            loadColumnsBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleLoadColumns();
            });
        }

        // Back to selection button
        const backBtn = document.getElementById('back-to-selection');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.hideColumnSelectionSection();
            });
        }

        // Also listen for changes in the dropdowns to reset the form state
        const datasourceSelects = document.querySelectorAll('select[name="datasource_a"], select[name="datasource_b"]');
        datasourceSelects.forEach(select => {
            select.addEventListener('change', () => {
                this.hideColumnSelectionSection();
                this.clearPreviousErrors();
            });
        });

        // Handle fusion configuration form submission
        const fusionForm = document.getElementById('fusion-config-form');
        if (fusionForm) {
            fusionForm.addEventListener('submit', (e) => {
                this.handleFusionSubmission(e);
            });
        }
    }

    /**
     * Handle the "Cargar Columnas" button click
     */
    async handleLoadColumns() {
        this.clearPreviousErrors();

        // Step 1: Client-side validation
        if (!this.validateDataSourceSelection()) {
            return;
        }

        // Step 2: Show loading indicator
        this.showLoadingIndicator();

        try {
            // Step 3: Make API call
            const response = await this.fetchColumns();
            
            if (response.success) {
                // Step 4: Update UI with columns
                this.populateColumnSelections(response.data);
                this.showColumnSelectionSection();
            } else {
                this.showError(response.error || 'Error al cargar las columnas');
            }
        } catch (error) {
            console.error('Error fetching columns:', error);
            this.showError('Error de conexión. Por favor, inténtalo de nuevo.');
        } finally {
            // Always hide loading indicator
            this.hideLoadingIndicator();
        }
    }

    /**
     * Validate that two different DataSources are selected
     */
    validateDataSourceSelection() {
        const datasourceA = document.querySelector('select[name="datasource_a"]').value;
        const datasourceB = document.querySelector('select[name="datasource_b"]').value;

        if (!datasourceA || !datasourceB) {
            this.showError('Por favor, selecciona ambas fuentes de datos.');
            return false;
        }

        if (datasourceA === datasourceB) {
            this.showError('Por favor, selecciona dos fuentes de datos diferentes.');
            return false;
        }

        return true;
    }

    /**
     * Fetch columns from the API
     */
    async fetchColumns() {
        const datasourceA = document.querySelector('select[name="datasource_a"]').value;
        const datasourceB = document.querySelector('select[name="datasource_b"]').value;

        const url = `/tools/api/get-fusion-columns/?ds_a=${encodeURIComponent(datasourceA)}&ds_b=${encodeURIComponent(datasourceB)}`;

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken,
            },
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Populate the column selection multi-select boxes
     */
    populateColumnSelections(data) {
        const { datasource_a, datasource_b } = data;

        // Populate DataSource A columns
        const selectA = document.getElementById('columns-datasource-a');
        if (selectA) {
            selectA.innerHTML = '';
            datasource_a.columns.forEach(column => {
                const option = document.createElement('option');
                option.value = column;
                option.textContent = column;
                selectA.appendChild(option);
            });
        }

        // Populate DataSource B columns
        const selectB = document.getElementById('columns-datasource-b');
        if (selectB) {
            selectB.innerHTML = '';
            datasource_b.columns.forEach(column => {
                const option = document.createElement('option');
                option.value = column;
                option.textContent = column;
                selectB.appendChild(option);
            });
        }

        // Populate merge key options for both DataSources
        this.populateMergeKeyOptions(datasource_a.columns, datasource_b.columns);

        // Update the section titles with DataSource names
        this.updateSectionTitles(datasource_a.name, datasource_b.name);
    }

    /**
     * Populate merge key dropdown options
     */
    populateMergeKeyOptions(columnsA, columnsB) {
        // Find common columns for potential merge keys
        const commonColumns = columnsA.filter(col => columnsB.includes(col));
        
        const mergeKeySelectA = document.getElementById('merge-key-a');
        const mergeKeySelectB = document.getElementById('merge-key-b');

        if (mergeKeySelectA && mergeKeySelectB) {
            // Clear existing options
            mergeKeySelectA.innerHTML = '<option value="">Seleccionar columna clave...</option>';
            mergeKeySelectB.innerHTML = '<option value="">Seleccionar columna clave...</option>';

            // Add all columns as options
            columnsA.forEach(column => {
                const option = document.createElement('option');
                option.value = column;
                option.textContent = column;
                // Highlight common columns
                if (commonColumns.includes(column)) {
                    option.textContent += ' (común)';
                    option.style.fontWeight = 'bold';
                }
                mergeKeySelectA.appendChild(option);
            });

            columnsB.forEach(column => {
                const option = document.createElement('option');
                option.value = column;
                option.textContent = column;
                // Highlight common columns
                if (commonColumns.includes(column)) {
                    option.textContent += ' (común)';
                    option.style.fontWeight = 'bold';
                }
                mergeKeySelectB.appendChild(option);
            });

            // If there are common columns, pre-select the first one
            if (commonColumns.length > 0) {
                mergeKeySelectA.value = commonColumns[0];
                mergeKeySelectB.value = commonColumns[0];
            }
        }
    }

    /**
     * Update section titles with DataSource names
     */
    updateSectionTitles(nameA, nameB) {
        const titleA = document.getElementById('datasource-a-title');
        const titleB = document.getElementById('datasource-b-title');

        if (titleA) titleA.textContent = `Columnas de: ${nameA}`;
        if (titleB) titleB.textContent = `Columnas de: ${nameB}`;
    }

    /**
     * Show the column selection section
     */
    showColumnSelectionSection() {
        const section = document.getElementById('column-selection-section');
        if (section) {
            section.classList.remove('hidden');
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    /**
     * Hide the column selection section
     */
    hideColumnSelectionSection() {
        const section = document.getElementById('column-selection-section');
        if (section) {
            section.classList.add('hidden');
        }
    }

    /**
     * Show loading indicator
     */
    showLoadingIndicator() {
        const button = document.querySelector('button[type="submit"]');
        const indicator = document.getElementById('loading-indicator');
        
        if (button) {
            button.disabled = true;
            button.innerHTML = `
                <svg class="animate-spin h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Cargando...
            `;
        }

        if (indicator) {
            indicator.classList.remove('hidden');
        }
    }

    /**
     * Hide loading indicator
     */
    hideLoadingIndicator() {
        const button = document.querySelector('button[type="submit"]');
        const indicator = document.getElementById('loading-indicator');
        
        if (button) {
            button.disabled = false;
            button.innerHTML = `
                Cargar Columnas
                <svg class="h-4 w-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                </svg>
            `;
        }

        if (indicator) {
            indicator.classList.add('hidden');
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        this.clearPreviousErrors();
        
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="rounded-md bg-red-50 p-4 border border-red-200">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                            </svg>
                        </div>
                        <div class="ml-3">
                            <h3 class="text-sm font-medium text-red-800">Error</h3>
                            <div class="mt-2 text-sm text-red-700">
                                <p>${message}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            errorContainer.classList.remove('hidden');
        }
    }

    /**
     * Handle fusion configuration form submission
     */
    handleFusionSubmission(e) {
        e.preventDefault();
        
        // Validate fusion configuration
        if (!this.validateFusionConfiguration()) {
            return;
        }

        // Add the original DataSource IDs to the form
        const form = e.target;
        const datasourceA = document.querySelector('select[name="datasource_a"]').value;
        const datasourceB = document.querySelector('select[name="datasource_b"]').value;

        // Create hidden inputs for the DataSource IDs
        const hiddenA = document.createElement('input');
        hiddenA.type = 'hidden';
        hiddenA.name = 'datasource_a';
        hiddenA.value = datasourceA;
        form.appendChild(hiddenA);

        const hiddenB = document.createElement('input');
        hiddenB.type = 'hidden';
        hiddenB.name = 'datasource_b';
        hiddenB.value = datasourceB;
        form.appendChild(hiddenB);

        // Submit the form
        form.submit();
    }

    /**
     * Validate fusion configuration before submission
     */
    validateFusionConfiguration() {
        const mergeKeyA = document.getElementById('merge-key-a').value;
        const mergeKeyB = document.getElementById('merge-key-b').value;
        const fusionName = document.getElementById('fusion-name').value.trim();
        const columnsA = document.getElementById('columns-datasource-a').selectedOptions;
        const columnsB = document.getElementById('columns-datasource-b').selectedOptions;

        if (!mergeKeyA || !mergeKeyB) {
            this.showError('Por favor, selecciona las columnas clave para la fusión en ambas fuentes de datos.');
            return false;
        }

        if (!fusionName) {
            this.showError('Por favor, ingresa un nombre para el dataset fusionado.');
            return false;
        }

        if (columnsA.length === 0 && columnsB.length === 0) {
            this.showError('Por favor, selecciona al menos una columna de alguna de las fuentes de datos.');
            return false;
        }

        return true;
    }

    /**
     * Clear previous error messages
     */
    clearPreviousErrors() {
        const errorContainer = document.getElementById('error-container');
        if (errorContainer) {
            errorContainer.innerHTML = '';
            errorContainer.classList.add('hidden');
        }
    }
}

// Initialize the Data Fusion Manager when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new DataFusionManager();
});
