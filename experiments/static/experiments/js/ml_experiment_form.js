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
    
    const getColumnsUrlTemplate = experimentForm.dataset.getColumnsUrl;

    // --- Lógica para Hiperparámetros Dinámicos ---
    function updateHyperparameterFields() {
        const value = modelSelect.value;
        rfFields.classList.add("hidden");
        gbFields.classList.add("hidden");
        if (value === "RandomForestRegressor") {
            rfFields.classList.remove("hidden");
        } else if (value === "GradientBoostingRegressor") {
            gbFields.classList.remove("hidden");
        }
    }
    modelSelect.addEventListener("change", updateHyperparameterFields);
    updateHyperparameterFields(); // Llamar al inicio para el estado inicial

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
                    const option = new Option(col, col);
                    targetColumnSelect.add(option.cloneNode(true));
                    featuresAvailable.add(option);
                });

                targetColumnSelect.disabled = false;
            })
            .catch(error => {
                console.error("Error al poblar columnas:", error);
                targetColumnSelect.innerHTML = `<option value="">Error: ${error.message}</option>`;
            });
    });
});