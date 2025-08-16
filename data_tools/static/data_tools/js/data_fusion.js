// data_tools/static/data_tools/js/data_fusion.js

/**
 * Maneja la funcionalidad de la página de fusión de datos
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const datasourceASelect = document.getElementById('id_datasource_a');
    const datasourceBSelect = document.getElementById('id_datasource_b');
    const loadColumnsBtn = document.querySelector('button[type="submit"]');

    /**
     * Función para cargar las columnas de dos datasources seleccionados
     */
    async function loadFusionColumns() {
        const dsAId = datasourceASelect.value;
        const dsBId = datasourceBSelect.value;

        if (!dsAId || !dsBId) {
            console.log('Ambos datasources deben estar seleccionados');
            return;
        }

        if (dsAId === dsBId) {
            console.log('Los datasources deben ser diferentes');
            return;
        }

        try {
            loadColumnsBtn.disabled = true;
            loadColumnsBtn.textContent = 'Cargando columnas...';

            // Construir la URL del API con parámetros GET
            const apiUrl = `/data-tools/api/get-fusion-columns/?ds_a=${dsAId}&ds_b=${dsBId}`;
            
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Procesar la respuesta
            console.log('Columnas cargadas exitosamente:', data);
            
            // Aquí puedes agregar lógica para mostrar las columnas en la UI
            // Por ejemplo, redirigir a la siguiente página o mostrar un modal
            displayColumnData(data);

        } catch (error) {
            console.error('Error al cargar columnas:', error);
            alert('Error al cargar las columnas: ' + error.message);
        } finally {
            loadColumnsBtn.disabled = false;
            loadColumnsBtn.textContent = 'Cargar Columnas';
        }
    }

    /**
     * Función para mostrar los datos de columnas (placeholder)
     */
    function displayColumnData(data) {
        console.log('DataSource A:', data.datasource_a);
        console.log('DataSource B:', data.datasource_b);
        
        // Ejemplo de cómo se podría mostrar la información
        const message = `
DataSource A: ${data.datasource_a.name}
Columnas (${data.datasource_a.columns.length}): ${data.datasource_a.columns.join(', ')}

DataSource B: ${data.datasource_b.name} 
Columnas (${data.datasource_b.columns.length}): ${data.datasource_b.columns.join(', ')}
        `;
        
        alert(message);
    }

    /**
     * Interceptar el envío del formulario para usar AJAX en lugar de POST
     */
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            loadFusionColumns();
        });
    }

    /**
     * Opcional: Cargar columnas automáticamente cuando ambos selects cambien
     */
    function handleSelectChange() {
        if (datasourceASelect.value && datasourceBSelect.value && 
            datasourceASelect.value !== datasourceBSelect.value) {
            // Opcional: cargar automáticamente
            // loadFusionColumns();
        }
    }

    if (datasourceASelect && datasourceBSelect) {
        datasourceASelect.addEventListener('change', handleSelectChange);
        datasourceBSelect.addEventListener('change', handleSelectChange);
    }
});
