document.addEventListener('DOMContentLoaded', function() {
    console.log('🧪 [FORM INIT] ML Experiment Form JavaScript Loading...');

    // Función para inicializar el formulario
    const initializeForm = () => {
        const experimentForm = document.getElementById('experiment-form');
        if (!experimentForm) {
            console.error('❌ [FORM INIT] Experiment form not found!');
            return;
        }
        console.log('✅ [FORM INIT] Experiment form found:', experimentForm);

        // Referencias a elementos del DOM
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
        
        console.log('🔍 [FORM INIT] DOM element validation:');
        console.log('🔍 [FORM INIT] - datasourceSelect:', !!datasourceSelect);
        console.log('🔍 [FORM INIT] - targetColumnSelect:', !!targetColumnSelect);
        console.log('🔍 [FORM INIT] - featuresAvailable:', !!featuresAvailable);
        console.log('🔍 [FORM INIT] - featuresSelected:', !!featuresSelected);
        
        const getColumnsUrlTemplate = experimentForm.dataset.getColumnsUrl;
        console.log('🌐 [FORM INIT] getColumnsUrlTemplate from dataset:', getColumnsUrlTemplate);
        
        if (!datasourceSelect || !targetColumnSelect) {
            console.error('❌ [FORM INIT] CRITICAL: Required elements not found!');
            return;
        }

        // Función para sincronizar inputs ocultos
        function syncHiddenInputs() {
            if (hiddenTargetInput && targetColumnSelect) {
                hiddenTargetInput.value = targetColumnSelect.value;
            }
            if (hiddenFeatureSet && featuresSelected) {
                const selectedFeatures = Array.from(featuresSelected.options).map(option => option.value);
                hiddenFeatureSet.value = JSON.stringify(selectedFeatures);
            }
        }

        // Función para limpiar dropdowns
        function clearDropdowns() {
            console.log('🔄 [FRONTEND DEBUG] Clearing all dropdowns...');
            targetColumnSelect.innerHTML = '<option value="">Primero selecciona una Fuente de Datos</option>';
            targetColumnSelect.disabled = true;
            if (featuresAvailable) featuresAvailable.innerHTML = '';
            if (featuresSelected) featuresSelected.innerHTML = '';
            syncHiddenInputs();
        }

        // Función principal para cargar columnas
        function loadColumnsForDataSource(datasourceId) {
            console.log('🌐 [FRONTEND DEBUG] Loading columns for DataSource:', datasourceId);
            
            // Reset dropdowns
            targetColumnSelect.innerHTML = '<option value="">Cargando...</option>';
            targetColumnSelect.disabled = true;
            if (featuresAvailable) featuresAvailable.innerHTML = '';
            if (featuresSelected) featuresSelected.innerHTML = '';
            syncHiddenInputs();

            if (!getColumnsUrlTemplate) {
                console.error('❌ [FRONTEND DEBUG] URL template not found');
                targetColumnSelect.innerHTML = '<option value="">Error: URL template not found</option>';
                return;
            }

            const url = getColumnsUrlTemplate.replace('__DATASOURCE_ID__', datasourceId);
            console.log('🌐 [FRONTEND DEBUG] Constructed API URL:', url);

            // Make API call
            fetch(url)
                .then(resp => {
                    console.log('📡 [FRONTEND DEBUG] Response status:', resp.status);
                    if (!resp.ok) {
                        throw new Error(`Error de red: ${resp.status}`);
                    }
                    return resp.json();
                })
                .then(data => {
                    console.log('✅ [FRONTEND DEBUG] Data received:', data);
                    
                    if (data.error) {
                        throw new Error(data.error);
                    }

                    if (!Array.isArray(data.columns)) {
                        throw new Error('Formato de respuesta inválido');
                    }

                    // Populate target column dropdown
                    targetColumnSelect.innerHTML = '<option value="">Selecciona una variable objetivo</option>';
                    data.columns.forEach(column => {
                        const option = document.createElement('option');
                        option.value = column;
                        option.textContent = column;
                        targetColumnSelect.appendChild(option);
                    });

                    // Populate features available
                    if (featuresAvailable) {
                        featuresAvailable.innerHTML = '';
                        data.columns.forEach(column => {
                            const option = document.createElement('option');
                            option.value = column;
                            option.textContent = column;
                            featuresAvailable.appendChild(option);
                        });
                    }

                    targetColumnSelect.disabled = false;
                    console.log('✅ [FRONTEND DEBUG] Columns loaded successfully');
                })
                .catch(error => {
                    console.error("❌ [FRONTEND DEBUG] Error loading columns:", error.message);
                    targetColumnSelect.innerHTML = `<option value="">Error: ${error.message}</option>`;
                });
        }

        // Event handler para cambio de DataSource
        function handleDataSourceChange(event) {
            console.log('🔧 [FRONTEND DEBUG] DataSource change event triggered!');
            console.log('🔧 [FRONTEND DEBUG] Selected value:', event.target.value);
            
            const datasourceId = event.target.value;
            
            if (!datasourceId) {
                clearDropdowns();
                return;
            }

            loadColumnsForDataSource(datasourceId);
        }

        // ✅ REGISTRO DEL EVENT LISTENER PRINCIPAL
        console.log('🔧 [FORM INIT] Registering DataSource change event listener...');
        datasourceSelect.addEventListener('change', handleDataSourceChange);
        console.log('✅ [FORM INIT] Event listener registered successfully!');

        // Event listeners para features
        if (btnAdd && btnRemove && featuresAvailable && featuresSelected) {
            btnAdd.addEventListener('click', function() {
                const selected = Array.from(featuresAvailable.selectedOptions);
                selected.forEach(option => {
                    featuresSelected.appendChild(option.cloneNode(true));
                    option.remove();
                });
                syncHiddenInputs();
            });

            btnRemove.addEventListener('click', function() {
                const selected = Array.from(featuresSelected.selectedOptions);
                selected.forEach(option => {
                    featuresAvailable.appendChild(option.cloneNode(true));
                    option.remove();
                });
                syncHiddenInputs();
            });
        }

        // Event listeners para sincronización
        targetColumnSelect.addEventListener('change', syncHiddenInputs);
        if (featuresSelected) {
            featuresSelected.addEventListener('change', syncHiddenInputs);
        }

        // Model selection logic
        if (modelSelect && rfFields && gbFields) {
            function toggleModelFields() {
                const selectedModel = modelSelect.value;
                if (selectedModel === 'random_forest') {
                    rfFields.style.display = 'block';
                    gbFields.style.display = 'none';
                } else if (selectedModel === 'gradient_boosting') {
                    rfFields.style.display = 'none';
                    gbFields.style.display = 'block';
                } else {
                    rfFields.style.display = 'none';
                    gbFields.style.display = 'none';
                }
            }

            modelSelect.addEventListener('change', toggleModelFields);
            toggleModelFields(); // Initialize on load
        }

        // Preset loading logic
        if (presetSelect) {
            function updatePresetDropdown(modelType) {
                if (!presetSelect) return;
                
                presetSelect.innerHTML = '<option value="">Loading presets...</option>';
                presetSelect.disabled = true;
                
                if (!modelType) {
                    presetSelect.innerHTML = '<option value="">Select a model first...</option>';
                    return;
                }
                
                const url = `/api/presets/?model_type=${encodeURIComponent(modelType)}`;
                
                fetch(url)
                    .then(response => {
                        if (!response.ok) throw new Error('Error loading presets');
                        return response.json();
                    })
                    .then(data => {
                        presetSelect.innerHTML = '<option value="">Select a preset to load hyperparameters...</option>';
                        
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
                            presetSelect.innerHTML = '<option value="">No presets available for this model</option>';
                        }
                    })
                    .catch(error => {
                        console.error('Error loading presets:', error);
                        presetSelect.innerHTML = '<option value="">Error loading presets</option>';
                    });
            }

            if (modelSelect) {
                modelSelect.addEventListener('change', () => updatePresetDropdown(modelSelect.value));
            }

            presetSelect.addEventListener('change', function() {
                const presetId = this.value;
                if (!presetId) return;
                
                fetch(`/api/presets/${presetId}/`)
                    .then(response => {
                        if (!response.ok) throw new Error('Error loading preset data');
                        return response.json();
                    })
                    .then(data => {
                        console.log('Preset loaded:', data);
                        // Apply preset data to form fields
                        if (data.hyperparameters) {
                            Object.keys(data.hyperparameters).forEach(key => {
                                const field = document.getElementById(`id_${key}`);
                                if (field) {
                                    field.value = data.hyperparameters[key];
                                }
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error loading preset:', error);
                    });
            });
        }

        console.log('✅ [FORM INIT] Form initialization completed successfully!');
    };

    // Inicializar después de Alpine.js si está presente
    if (window.Alpine) {
        console.log('🔧 [FORM INIT] Alpine.js detected, waiting for initialization...');
        document.addEventListener('alpine:init', initializeForm);
    } else {
        console.log('🔧 [FORM INIT] No Alpine.js detected, initializing immediately...');
        setTimeout(initializeForm, 100);
    }
});
