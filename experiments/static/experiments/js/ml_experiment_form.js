document.addEventListener('DOMContentLoaded', function() {
    // --- Referencias a Elementos del DOM ---
    console.log('🧪 [FORM INIT] ================================');
    console.log('🧪 [FORM INIT] ML Experiment Form JavaScript Loading...');
    console.log('🧪 [FORM INIT] DOM ready state:', document.readyState);
    console.log('🧪 [FORM INIT] Alpine.js available:', !!window.Alpine);
    
    // Esperar a que Alpine.js se inicialice si está presente
    let initialized = false;
    const initializeForm = () => {
        if (initialized) {
            console.log('ℹ️ [FORM INIT] Initialization already performed – skipping');
            return;
        }
        const experimentForm = document.getElementById('experiment-form');
        if (!experimentForm) {
            console.error('❌ [FORM INIT] Experiment form not found!');
            return;
        }
        console.log('✅ [FORM INIT] Experiment form found:', experimentForm);

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
        
        console.log('🔍 [FORM INIT] DOM element validation:');
        console.log('🔍 [FORM INIT] - modelSelect:', !!modelSelect);
        console.log('🔍 [FORM INIT] - featuresAvailable:', !!featuresAvailable);
        console.log('🔍 [FORM INIT] - featuresSelected:', !!featuresSelected);
        console.log('🔍 [FORM INIT] - datasourceSelect:', !!datasourceSelect, datasourceSelect);
        console.log('🔍 [FORM INIT] - targetColumnSelect:', !!targetColumnSelect, targetColumnSelect);
        console.log('🔍 [FORM INIT] - hiddenTargetInput:', !!hiddenTargetInput);
        console.log('🔍 [FORM INIT] - hiddenFeatureSet:', !!hiddenFeatureSet);
        
        // Elements for split strategy visibility toggle
        const splitStrategy = document.getElementById('id_split_strategy');
        const randomStateField = document.getElementById('id_split_random_state');
        
        // Preset loading elements
        const presetSelect = document.getElementById('id_load_preset');
        
    const getColumnsUrlTemplate = experimentForm.dataset.getColumnsUrlTemplate || experimentForm.dataset.getColumnsUrl;
        console.log('🌐 [FORM INIT] getColumnsUrlTemplate from dataset:', getColumnsUrlTemplate);
        
        if (!getColumnsUrlTemplate) {
            console.error('❌ [FORM INIT] getColumnsUrlTemplate is missing from form dataset!');
            console.log('🔍 [FORM INIT] Available dataset attributes:', Object.keys(experimentForm.dataset));
        }
        
        if (!datasourceSelect) {
            console.error('❌ [FORM INIT] CRITICAL: datasourceSelect element not found!');
            console.log('🔍 [FORM INIT] All elements with id containing "datasource":', 
                Array.from(document.querySelectorAll('[id*="datasource"]')).map(el => ({id: el.id, element: el})));
            return;
        }
        
        if (!targetColumnSelect) {
            console.error('❌ [FORM INIT] CRITICAL: targetColumnSelect element not found!');
            console.log('🔍 [FORM INIT] All elements with id containing "target":', 
                Array.from(document.querySelectorAll('[id*="target"]')).map(el => ({id: el.id, element: el})));
            return;
        }

        // ✅ REGISTRO DEL EVENT LISTENER PRINCIPAL - MUY IMPORTANTE
        console.log('🔧 [FORM INIT] ================================');
        console.log('🔧 [FORM INIT] Registering DataSource change event listener...');
        console.log('🔧 [FORM INIT] DataSource select element:', datasourceSelect);
        console.log('🔧 [FORM INIT] DataSource select ID:', datasourceSelect?.id);
        console.log('🔧 [FORM INIT] DataSource select value:', datasourceSelect?.value);
        console.log('🔧 [FORM INIT] DataSource select options count:', datasourceSelect?.options?.length);
        
        // Log all available options
        if (datasourceSelect?.options) {
            console.log('🔧 [FORM INIT] Available DataSource options:');
            Array.from(datasourceSelect.options).forEach((option, index) => {
                console.log(`🔧 [FORM INIT]   Option ${index}: value="${option.value}", text="${option.text}"`);
            });
        }
        
    // Remover listener existente si hay alguno
    try { datasourceSelect.removeEventListener('change', handleDataSourceChange); } catch(e) {}
        
    // Agregar el listener principal
    datasourceSelect.addEventListener('change', handleDataSourceChange, { once: false });
        
        console.log('✅ [FORM INIT] DataSource change event listener registered successfully!');
        console.log('🔍 [FORM INIT] Current datasource value:', datasourceSelect.value);
        
    // Test inmediato
        console.log('🧪 [FORM INIT] Testing event listener registration...');
        const testEvent = new Event('change');
        setTimeout(() => {
            console.log('🧪 [FORM INIT] About to trigger test change event...');
            datasourceSelect.dispatchEvent(testEvent);
        }, 1000);

    initialized = true;
    };

    // Función principal para manejar el cambio de DataSource
    function handleDataSourceChange(event) {
        console.log('🔧 [DATASOURCE CHANGE] ================================');
        console.log('🔧 [DATASOURCE CHANGE] DataSource change event triggered!');
        console.log('🔧 [DATASOURCE CHANGE] Event type:', event.type);
        console.log('🔧 [DATASOURCE CHANGE] Event target:', event.target);
        console.log('🔧 [DATASOURCE CHANGE] Event target value:', event.target.value);
        
        const datasourceId = event.target.value;
        console.log('🔧 [DATASOURCE CHANGE] Selected DataSource ID:', datasourceId);
        
        if (!datasourceId) {
            console.log('🔧 [DATASOURCE CHANGE] No DataSource selected, clearing dropdowns...');
            clearDropdowns();
            return;
        }

        console.log('🔧 [DATASOURCE CHANGE] DataSource ID is valid, proceeding with API call...');
        loadColumnsForDataSource(datasourceId);
    }

    // Función para cargar columnas de un DataSource específico
    async function loadColumnsForDataSource(datasourceId) {
        console.log('🚀 [API CALL] ====================================');
        console.log('🚀 [API CALL] Starting loadColumnsForDataSource with ID:', datasourceId);
        
        if (!datasourceId) {
            console.log('⚠️ [API CALL] No datasourceId provided, skipping column load');
            return;
        }
        
        try {
            const experimentForm = document.getElementById('experiment-form');
            const getColumnsUrlTemplate = experimentForm.dataset.getColumnsUrlTemplate;
            
            console.log('🌐 [API CALL] Form element:', experimentForm);
            console.log('🌐 [API CALL] URL template from dataset:', getColumnsUrlTemplate);
            
            // Replace the dummy UUID with the actual datasource ID
            const dummyUuid = '00000000-0000-0000-0000-000000000000';
            const apiUrl = getColumnsUrlTemplate.replace(dummyUuid, datasourceId);
            console.log('🌐 [API CALL] Constructing API URL:', apiUrl);
            console.log('🔄 [API CALL] Replaced dummy UUID:', dummyUuid, '→', datasourceId);
            
            console.log('📡 [API CALL] Making fetch request to API...');
            const response = await fetch(apiUrl);
            console.log('📨 [API CALL] API response received:', response.status);
            console.log('📨 [API CALL] Response ok:', response.ok);
            console.log('📨 [API CALL] Response headers:', Object.fromEntries(response.headers.entries()));
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            console.log('📝 [API CALL] Parsing JSON data...');
            const data = await response.json();
            console.log('📦 [API CALL] Parsed data:', data);
            console.log('📦 [API CALL] Data type:', typeof data);
            console.log('📦 [API CALL] Data keys:', Object.keys(data));
            
            if (data.columns) {
                console.log('📦 [API CALL] Columns found:', data.columns);
                console.log('📦 [API CALL] Number of columns:', data.columns.length);
            } else {
                console.error('❌ [API CALL] No columns property in response data!');
            }
            
            console.log('🔧 [API CALL] Calling function to populate dropdowns...');
            
            // Populate target variable select (correct ID)
            populateSelectOptions('id_target_column_select', data.columns, '-- Selecciona variable objetivo --');
            console.log('✅ [API CALL] Target variable options populated');
            
            // Populate feature columns (correct ID for available features)
            populateSelectOptions('features-available', data.columns, '-- Selecciona columnas características --');
            console.log('✅ [API CALL] Feature columns options populated');
            
            console.log('🎉 [API CALL] Finished populating dropdowns.');
            console.log('🎉 [API CALL] Column loading completed successfully');
        } catch (error) {
            console.error('❌ [API CALL] Error loading columns:', error);
            console.error('❌ [API CALL] Error stack:', error.stack);
            
            // Clear the select options on error (correct IDs)
            clearSelectOptions('id_target_column_select', '-- Error cargando columnas --');
            clearSelectOptions('features-available', '-- Error cargando columnas --');
        }
    }

    // Función auxiliar para poblar opciones de select
    function populateSelectOptions(selectId, columns, defaultText) {
        console.log('🔧 [POPULATE] ================================');
        console.log('🔧 [POPULATE] Populating select options for:', selectId);
        console.log('🔧 [POPULATE] Columns to add:', columns);
        console.log('🔧 [POPULATE] Default text:', defaultText);
        
        const select = document.getElementById(selectId);
        console.log('🔧 [POPULATE] Found select element:', select);
        
        if (!select) {
            console.error(`❌ [POPULATE] Select element ${selectId} not found!`);
            console.log('🔧 [POPULATE] Available elements with similar IDs:', 
                Array.from(document.querySelectorAll('select')).map(el => ({id: el.id, element: el})));
            return;
        }
        
        console.log('🔧 [POPULATE] Current select innerHTML before clear:', select.innerHTML);
        
        // Clear existing options
        select.innerHTML = '';
        console.log('🔧 [POPULATE] Cleared existing options');
        
        // Add default option
        const defaultOption = new Option(defaultText, '');
        select.add(defaultOption);
        console.log('🔧 [POPULATE] Added default option:', defaultText);
        
        // Add column options
        if (columns && Array.isArray(columns)) {
            console.log('🔧 [POPULATE] Adding', columns.length, 'column options...');
            columns.forEach((column, index) => {
                const option = new Option(column, column);
                select.add(option);
                console.log(`🔧 [POPULATE] Added option ${index + 1}:`, column);
            });
        } else {
            console.error('❌ [POPULATE] Columns is not a valid array:', columns);
        }
        
        console.log('🔧 [POPULATE] Final select innerHTML:', select.innerHTML);
        console.log('🔧 [POPULATE] Final option count:', select.options.length);
        console.log('✅ [POPULATE] Finished populating', selectId);
    }

    // Función auxiliar para limpiar opciones de select
    function clearSelectOptions(selectId, defaultText) {
        const select = document.getElementById(selectId);
        if (!select) {
            console.warn(`❌ [CLEAR] Select element ${selectId} not found`);
            return;
        }
        
        select.innerHTML = '';
        const defaultOption = new Option(defaultText, '');
        select.add(defaultOption);
    }

    // Función para limpiar dropdowns
    function clearDropdowns() {
        console.log('🧹 [CLEAR] Clearing all dropdowns...');
        clearSelectOptions('id_target_column_select', '-- Selecciona un DataSource primero --');
        clearSelectOptions('features-available', '-- Selecciona un DataSource primero --');
        console.log('✅ [CLEAR] All dropdowns cleared');
    }

    // Inicializar inmediatamente o esperar a Alpine.js
    if (window.Alpine) {
        console.log('🧪 [FORM INIT] Alpine.js detected, waiting for it to initialize...');
        document.addEventListener('alpine:init', initializeForm, { once: true });
        // Safeguard timeout in case alpine:init never fires
        setTimeout(initializeForm, 1000);
    } else {
        console.log('🧪 [FORM INIT] No Alpine.js detected, initializing immediately...');
        setTimeout(initializeForm, 100); // Pequeño delay para asegurar que el DOM esté listo
    }

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
        console.log('� [FRONTEND DEBUG] DataSource selection event triggered');
        console.log('📊 [FRONTEND DEBUG] DataSource value changed to:', this.value);
        console.log('🔍 [FRONTEND DEBUG] Event target:', this);
        console.log('🔍 [FRONTEND DEBUG] Event type:', event.type);
        
        const datasourceId = this.value;
        console.log('🆔 [FRONTEND DEBUG] Extracted datasourceId:', datasourceId);
        console.log('📝 [FRONTEND DEBUG] datasourceId type:', typeof datasourceId);
        console.log('📏 [FRONTEND DEBUG] datasourceId length:', datasourceId.length);
        
        // Reset all dropdowns with detailed logging
        console.log('🔄 [FRONTEND DEBUG] Resetting target column dropdown');
        targetColumnSelect.innerHTML = '<option value="">Cargando...</option>';
        console.log('🔄 [FRONTEND DEBUG] Resetting features available');
        featuresAvailable.innerHTML = '';
        console.log('🔄 [FRONTEND DEBUG] Resetting features selected');
        featuresSelected.innerHTML = '';
        console.log('🔒 [FRONTEND DEBUG] Disabling target column dropdown');
        targetColumnSelect.disabled = true;
        
        console.log('🔄 [FRONTEND DEBUG] Calling syncHiddenInputs()');
        syncHiddenInputs();

        if (!datasourceId) {
            console.log('⚠️ [FRONTEND DEBUG] No datasource selected - early return');
            targetColumnSelect.innerHTML = '<option value="">Primero selecciona una Fuente de Datos</option>';
            console.log('ℹ️ [FRONTEND DEBUG] Reset dropdown to default message');
            return;
        }

        console.log('🌐 [FRONTEND DEBUG] Preparing URL construction');
        console.log('🔧 [FRONTEND DEBUG] URL template:', getColumnsUrlTemplate);
        const url = getColumnsUrlTemplate.replace('00000000-0000-0000-0000-000000000000', datasourceId);
        console.log('🌐 [FRONTEND DEBUG] Constructed API URL:', url);
        console.log('🌐 [FRONTEND DEBUG] URL validation - starts with http:', url.startsWith('http'));
        console.log('🌐 [FRONTEND DEBUG] URL validation - contains datasource ID:', url.includes(datasourceId));

        console.log('📤 [FRONTEND DEBUG] Starting fetch request...');
        fetch(url)
            .then(resp => {
                console.log('📡 [FRONTEND DEBUG] Fetch response received');
                console.log('📡 [FRONTEND DEBUG] Response status:', resp.status);
                console.log('📡 [FRONTEND DEBUG] Response statusText:', resp.statusText);
                console.log('📡 [FRONTEND DEBUG] Response ok:', resp.ok);
                console.log('📡 [FRONTEND DEBUG] Response headers:', resp.headers);
                console.log('📡 [FRONTEND DEBUG] Response url:', resp.url);
                
                if (!resp.ok) {
                    console.error('❌ [FRONTEND DEBUG] Non-OK response status');
                    throw new Error(`Error de red al buscar columnas. Status: ${resp.status}`);
                }
                
                console.log('📥 [FRONTEND DEBUG] Parsing JSON response...');
                return resp.json();
            })
            .then(data => {
                console.log('✅ [FRONTEND DEBUG] JSON data parsed successfully');
                console.log('📋 [FRONTEND DEBUG] Received data:', data);
                console.log('📋 [FRONTEND DEBUG] Data type:', typeof data);
                console.log('📋 [FRONTEND DEBUG] Data keys:', Object.keys(data));
                
                if (data.error) {
                    console.error('❌ [FRONTEND DEBUG] API returned error:', data.error);
                    throw new Error(data.error);
                }

                console.log('📋 [FRONTEND DEBUG] Checking columns property...');
                console.log('📋 [FRONTEND DEBUG] data.columns exists:', 'columns' in data);
                console.log('📋 [FRONTEND DEBUG] data.columns type:', typeof data.columns);
                console.log('📋 [FRONTEND DEBUG] data.columns value:', data.columns);
                
                if (Array.isArray(data.columns)) {
                    console.log('📋 [FRONTEND DEBUG] Columns is array with length:', data.columns.length);
                } else {
                    console.warn('⚠️ [FRONTEND DEBUG] Columns is not an array!');
                }

                console.log('🔄 [FRONTEND DEBUG] Updating target column dropdown...');
                targetColumnSelect.innerHTML = '<option value="">Selecciona una columna...</option>';
                console.log('🔄 [FRONTEND DEBUG] Clearing features available...');
                featuresAvailable.innerHTML = '';
                
                console.log('🔄 [FRONTEND DEBUG] Processing columns...');
                data.columns.forEach((col, index) => {
                    console.log(`📋 [FRONTEND DEBUG] Processing column ${index}: "${col}"`);
                    const targetOption = new Option(col, col);
                    const featuresOption = new Option(col, col);
                    targetColumnSelect.add(targetOption);
                    featuresAvailable.add(featuresOption);
                    console.log(`✅ [FRONTEND DEBUG] Added column "${col}" to both dropdowns`);
                });
                console.log(`✅ [FRONTEND DEBUG] Successfully added ${data.columns.length} columns to selectors`);

                console.log('🔓 [FRONTEND DEBUG] Enabling target column dropdown...');
                targetColumnSelect.disabled = false;
                console.log('✅ [FRONTEND DEBUG] Column population completed successfully');
            })
            .catch(error => {
                console.error("❌ [FRONTEND DEBUG] Error caught in fetch chain:");
                console.error("❌ [FRONTEND DEBUG] Error type:", typeof error);
                console.error("❌ [FRONTEND DEBUG] Error message:", error.message);
                console.error("❌ [FRONTEND DEBUG] Error stack:", error.stack);
                console.error("❌ [FRONTEND DEBUG] Full error object:", error);
                
                console.log('🔄 [FRONTEND DEBUG] Setting error message in dropdown...');
                targetColumnSelect.innerHTML = `<option value="">Error: ${error.message}</option>`;
                console.log('❌ [FRONTEND DEBUG] Error handling completed');
            });
    });
});