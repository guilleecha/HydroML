document.addEventListener('DOMContentLoaded', function() {
    const experimentForm = document.getElementById('experiment-form');
    if (!experimentForm) return;

    const datasourceSelectId = experimentForm.dataset.inputDatasourceId;
    const hiddenTargetInputId = experimentForm.dataset.targetColumnId;
    const hiddenFeaturesInputId = experimentForm.dataset.featureSetId;
    const getColumnsUrlTemplate = experimentForm.dataset.getColumnsUrl;

    const datasourceSelect = document.getElementById(datasourceSelectId);
    const targetColumnSelect = document.getElementById('id_target_column_select');
    const featureSetSelect = document.getElementById('id_feature_set_select');
    const hiddenTargetInput = document.getElementById(hiddenTargetInputId);
    const hiddenFeaturesInput = document.getElementById(hiddenFeaturesInputId);

    if (!datasourceSelect || !targetColumnSelect || !featureSetSelect || !hiddenTargetInput || !hiddenFeaturesInput) {
        console.error("Error: No se pudieron encontrar todos los elementos del formulario.");
        return;
    }

    function clearAndDisableColumnSelects() {
        targetColumnSelect.innerHTML = '<option selected>Primero selecciona una Fuente de Datos</option>';
        featureSetSelect.innerHTML = '';
        targetColumnSelect.disabled = true;
        featureSetSelect.disabled = true;
        hiddenTargetInput.value = '';
        hiddenFeaturesInput.value = '';
    }

    datasourceSelect.addEventListener('change', function() {
        const datasourceId = this.value;

        if (!datasourceId) {
            // Si el usuario selecciona la opción vacía, limpia y deshabilita los campos.
            clearAndDisableColumnSelects();
            return; // Detiene la ejecución
        }

        if (!datasourceId || datasourceId === "0") {
            clearAndDisableColumnSelects();
            return;
        }

        const url = getColumnsUrlTemplate.replace('0', datasourceId);

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error al obtener las columnas:', data.error);
                    clearAndDisableColumnSelects();
                    targetColumnSelect.innerHTML = '<option selected>Error al cargar columnas</option>';
                    return;
                }

                targetColumnSelect.innerHTML = '<option value="">Selecciona una columna...</option>';
                featureSetSelect.innerHTML = '';
                data.columns.forEach(column => {
                    const option = new Option(column, column);
                    targetColumnSelect.add(option.cloneNode(true));
                    featureSetSelect.add(option);
                });

                targetColumnSelect.disabled = false;
                featureSetSelect.disabled = false;
            })
            .catch(error => {
                console.error('Error en la llamada fetch:', error);
                clearAndDisableColumnSelects();
                targetColumnSelect.innerHTML = '<option selected>Error de conexión</option>';
            });
    });

    targetColumnSelect.addEventListener('change', function() {
        hiddenTargetInput.value = this.value;
    });

    featureSetSelect.addEventListener('change', function() {
        const selectedFeatures = Array.from(this.selectedOptions).map(option => option.value);
        // --- CAMBIO CLAVE AQUÍ ---
        hiddenFeaturesInput.value = selectedFeatures.join(',');
    });

    // Código para la otra herramienta (feature engineering)
    document.querySelectorAll('.col-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const colName = this.getAttribute('data-col');
            const formulaArea = document.getElementById('formula_string');
            if (formulaArea) {
                formulaArea.value += colName;
                formulaArea.focus();
            } else {
                console.error('Formula area not found');
            }
        });
    });
});