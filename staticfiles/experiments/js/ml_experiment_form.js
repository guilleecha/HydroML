document.addEventListener('DOMContentLoaded', function() {
    // --- Referencias a Elementos del DOM ---
    const experimentForm = document.getElementById('experiment-form');
    if (!experimentForm) return;

    const modelSelect = document.getElementById("id_model_name");
    const rfFields = document.getElementById("rf-fields");
    const gbFields = document.getElementById("gb-fields");
    
    const featuresAvailable = document.getElementById('features-available');
    const featuresSelected = document.getElementById('features-selected');
    const btnAdd = document.getElementById('btn-add-feature');
    const btnRemove = document.getElementById('btn-remove-feature');
    
    const datasourceSelect = document.getElementById('id_input_datasource');
    const targetColumnSelect = document.getElementById('id_target_column_select');
    const hiddenTargetInput = document.getElementById('id_target_column');
    const hiddenFeatureSet = document.getElementById('id_feature_set');
    
    // Elements for split strategy visibility toggle
    const splitStrategy = document.getElementById('id_split_strategy');
    const randomStateField = document.getElementById('id_split_random_state');
    
    // Preset loading elements
    const presetSelect = document.getElementById('id_load_preset');
    
    const getColumnsUrlTemplate = experimentForm.dataset.getColumnsUrl;

    // --- Lógica para Dynamic Preset Filtering ---
    function updatePresetDropdown(modelType) {
        if (!presetSelect) return;
        
        // Clear current options
        presetSelect.innerHTML = '<option value="">Loading presets...</option>';
        presetSelect.disabled = true;
        
        if (!modelType) {
            presetSelect.innerHTML = '<option value="">Select a model first...</option>';
            return;
        }
        
        // Fetch presets for the selected model type
        const url = `/api/presets/?model_type=${encodeURIComponent(modelType)}`;
        
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('Error loading presets');
                return response.json();
            })
            .then(data => {
                console.log('Filtered presets loaded:', data);
                
                // Clear loading message
                presetSelect.innerHTML = '';
                
                // Add default option
                const defaultOption = new Option('Select a preset to load hyperparameters...', '');
                presetSelect.add(defaultOption);
                
                // Add preset options
                if (data.presets && data.presets.length > 0) {
                    data.presets.forEach(preset => {
                        const option = new Option(preset.name, preset.id);
                        if (preset.description) {
                            option.title = preset.description;
                        }
                        presetSelect.add(option);
                    });
                    presetSelect.disabled = false;
                } else {
                    // No presets found for this model type
                    const noPresetsOption = new Option('No presets available for this model', '');
                    presetSelect.add(noPresetsOption);
                    presetSelect.disabled = true;
                }
            })
            .catch(error => {
                console.error('Error loading presets:', error);
                presetSelect.innerHTML = '<option value="">Error loading presets</option>';
                presetSelect.disabled = true;
                showPresetErrorFeedback('Error loading presets for selected model');
            });
    }

    // --- Lógica para Load Preset ---
    function loadPresetData(presetId) {
        if (!presetId) return;
        
        const url = `/api/presets/${presetId}/`;
        
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('Error loading preset data');
                return response.json();
            })
            .then(data => {
                console.log('Preset data loaded:', data);
                
                // Load hyperparameters into form fields
                if (data.hyperparameters) {
                    const params = data.hyperparameters;
                    
                    // Random Forest parameters
                    if (params.rf_n_estimators !== undefined) {
                        const rfNEstimators = document.getElementById('id_rf_n_estimators');
                        if (rfNEstimators) rfNEstimators.value = params.rf_n_estimators;
                    }
                    if (params.rf_max_depth !== undefined) {
                        const rfMaxDepth = document.getElementById('id_rf_max_depth');
                        if (rfMaxDepth) rfMaxDepth.value = params.rf_max_depth;
                    }
                    
                    // Gradient Boosting parameters
                    if (params.gb_n_estimators !== undefined) {
                        const gbNEstimators = document.getElementById('id_gb_n_estimators');
                        if (gbNEstimators) gbNEstimators.value = params.gb_n_estimators;
                    }
                    if (params.gb_learning_rate !== undefined) {
                        const gbLearningRate = document.getElementById('id_gb_learning_rate');
                        if (gbLearningRate) gbLearningRate.value = params.gb_learning_rate;
                    }
                    
                    // Model name
                    if (params.model_name !== undefined && modelSelect) {
                        modelSelect.value = params.model_name;
                        updateHyperparameterFields(); // Update visibility after setting model
                    }
                    
                    // Split strategy
                    if (params.split_strategy !== undefined && splitStrategy) {
                        splitStrategy.value = params.split_strategy;
                        updateRandomStateVisibility();
                    }
                    
                    // Test split size
                    if (params.test_split_size !== undefined) {
                        const testSplitSlider = document.getElementById('test_split_slider');
                        const hiddenTestSplit = document.getElementById('id_test_split_size');
                        if (testSplitSlider && hiddenTestSplit) {
                            const percentage = Math.round(params.test_split_size * 100);
                            testSplitSlider.value = percentage;
                            hiddenTestSplit.value = params.test_split_size;
                            
                            // Update Alpine.js data if available
                            const alpineComponent = testSplitSlider.closest('[x-data]');
                            if (alpineComponent && alpineComponent._x_dataStack) {
                                alpineComponent._x_dataStack[0].splitValue = percentage;
                            }
                            
                            // Update slider visual appearance
                            testSplitSlider.style.background = `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(percentage - 5) / (50 - 5) * 100}%, #e5e7eb ${(percentage - 5) / (50 - 5) * 100}%, #e5e7eb 100%)`;
                        }
                    }
                    
                    // Random state
                    if (params.split_random_state !== undefined && randomStateField) {
                        randomStateField.value = params.split_random_state;
                    }
                    
                    // Validation strategy
                    if (params.validation_strategy !== undefined) {
                        const validationStrategy = document.getElementById('id_validation_strategy');
                        if (validationStrategy) validationStrategy.value = params.validation_strategy;
                    }
                }
                
                // Show success feedback
                showPresetLoadedFeedback();
            })
            .catch(error => {
                console.error('Error loading preset:', error);
                showPresetErrorFeedback();
            });
    }
    
    function showPresetLoadedFeedback() {
        // Create and show a temporary success message
        const feedback = document.createElement('div');
        feedback.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded shadow-lg z-50';
        feedback.innerHTML = `
            <div class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Preset loaded successfully!
            </div>
        `;
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }
    
    function showPresetErrorFeedback(message = 'Error loading preset') {
        // Create and show a temporary error message
        const feedback = document.createElement('div');
        feedback.className = 'fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded shadow-lg z-50';
        feedback.innerHTML = `
            <div class="flex items-center">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
                ${message}
            </div>
        `;
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            feedback.remove();
        }, 3000);
    }

    // --- Lógica para Hiperparámetros Dinámicos ---
    function hideAllHyperparameterFields() {
        // Oculta todos los campos de hiperparámetros
        if (rfFields) rfFields.classList.add("hidden");
        if (gbFields) gbFields.classList.add("hidden");
    }
    
    function updateHyperparameterFields() {
        // Primero oculta todos los campos
        hideAllHyperparameterFields();
        
        // Luego muestra solo los campos correspondientes al modelo seleccionado
        const value = modelSelect?.value;
        if (value === "RandomForestRegressor" && rfFields) {
            rfFields.classList.remove("hidden");
        } else if (value === "GradientBoostingRegressor" && gbFields) {
            gbFields.classList.remove("hidden");
        }
    }
    
    // --- Lógica para Split Strategy y Random State Visibility ---
    function updateRandomStateVisibility() {
        if (!splitStrategy || !randomStateField) return;
        
        // Find the parent div of the random_state field
        const randomStateDiv = randomStateField.closest('.form-group, .mb-4, div') || randomStateField.parentElement;
        
        if (splitStrategy.value === 'RANDOM') {
            randomStateDiv.style.display = '';
        } else {
            randomStateDiv.style.display = 'none';
        }
    }
    
    // Agrega el listener para cambios en el selector de modelo
    if (modelSelect) {
        modelSelect.addEventListener("change", function() {
            updateHyperparameterFields();
            updatePresetDropdown(this.value); // Add preset filtering
        });
        // Ejecuta la función al cargar la página para configurar el estado inicial
        updateHyperparameterFields();
        updatePresetDropdown(modelSelect.value); // Initialize preset dropdown
    }

    // Agrega el listener para cambios en la estrategia de división
    if (splitStrategy) {
        splitStrategy.addEventListener('change', updateRandomStateVisibility);
        // Ejecuta la función al cargar la página para configurar el estado inicial
        updateRandomStateVisibility();
    }
    
    // Agrega el listener para cambios en el selector de preset
    if (presetSelect) {
        presetSelect.addEventListener('change', function() {
            const presetId = this.value;
            if (presetId) {
                loadPresetData(presetId);
            }
        });
    }

    // --- Lógica para el Dual Listbox y Sincronización ---
    function syncHiddenInputs() {
        hiddenTargetInput.value = targetColumnSelect.value;
        const values = Array.from(featuresSelected.options).map(opt => opt.value);
        // CORRECCIÓN: Usar JSON.stringify para que coincida con el backend
        hiddenFeatureSet.value = JSON.stringify(values);
    }

    function moveOptions(source, destination) {
        Array.from(source.selectedOptions).forEach(opt => {
            destination.appendChild(opt);
        });
        syncHiddenInputs(); // Sincronizar después de cada movimiento
    }

    btnAdd.addEventListener('click', () => moveOptions(featuresAvailable, featuresSelected));
    btnRemove.addEventListener('click', () => moveOptions(featuresSelected, featuresAvailable));
    targetColumnSelect.addEventListener('change', syncHiddenInputs);
    // Es importante sincronizar también cuando la lista de seleccionados cambia
    featuresSelected.addEventListener('change', syncHiddenInputs);


    // --- Lógica para Poblar Columnas Dinámicamente ---
    datasourceSelect.addEventListener('change', function() {
        const datasourceId = this.value;
        
        targetColumnSelect.innerHTML = '<option value="">Cargando...</option>';
        featuresAvailable.innerHTML = '';
        featuresSelected.innerHTML = '';
        targetColumnSelect.disabled = true;
        syncHiddenInputs();

        if (!datasourceId) {
            targetColumnSelect.innerHTML = '<option value="">Primero selecciona una Fuente de Datos</option>';
            return;
        }

        const url = getColumnsUrlTemplate.replace('00000000-0000-0000-0000-000000000000', datasourceId);

        fetch(url)
            .then(resp => {
                if (!resp.ok) throw new Error('Error de red al buscar columnas.');
                return resp.json();
            })
            .then(data => {
                if (data.error) throw new Error(data.error);

                targetColumnSelect.innerHTML = '<option value="">Selecciona una columna...</option>';
                featuresAvailable.innerHTML = '';
                
                data.columns.forEach(col => {
                    const targetOption = new Option(col, col);
                    const featuresOption = new Option(col, col);
                    targetColumnSelect.add(targetOption);
                    featuresAvailable.add(featuresOption);
                });

                targetColumnSelect.disabled = false;
            })
            .catch(error => {
                console.error("Error al poblar columnas:", error);
                targetColumnSelect.innerHTML = `<option value="">Error: ${error.message}</option>`;
            });
    });
});