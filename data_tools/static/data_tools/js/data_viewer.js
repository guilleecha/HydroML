// Se asegura de que el código se ejecute solo cuando el DOM esté completamente cargado.
document.addEventListener('DOMContentLoaded', function() {

    // --- OBTENER ELEMENTOS DEL DOM ---
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorContainer = document.getElementById('error-container');
    const tableContainer = document.getElementById('data-table-container');
    const tableHeader = document.getElementById('data-table-header');
    const tableBody = document.getElementById('data-table-body');

    // --- OBTENER DATOS DEL SCRIPT DE LA PLANTILLA ---
    // Leemos la URL de la API que Django nos pasó de forma segura.
    const scriptData = JSON.parse(document.getElementById('data-viewer-script-data').textContent);
    const apiUrl = scriptData.dataSourceUrl;

    // --- FUNCIÓN PRINCIPAL PARA CARGAR LOS DATOS ---
    async function loadData() {
        try {
            // Hacemos la petición a nuestra API
            const response = await fetch(apiUrl);

            if (!response.ok) {
                // Si la respuesta no es exitosa (ej: error 500), lanzamos un error.
                const errorData = await response.json();
                throw new Error(errorData.error || `Error del servidor: ${response.status}`);
            }

            const data = await response.json();

            // Si la API devuelve un error en el JSON, también lo manejamos.
            if (data.error) {
                throw new Error(data.error);
            }

            // Si todo sale bien, construimos la tabla.
            buildTable(data.columns, data.data);

            // Ocultamos el spinner y mostramos la tabla.
            loadingSpinner.classList.add('d-none');
            tableContainer.classList.remove('d-none');

        } catch (error) {
            // --- MANEJO DE ERRORES ---
            console.error('Error al cargar los datos:', error);
            // Mostramos el mensaje de error al usuario.
            errorContainer.textContent = `Error: ${error.message}`;
            errorContainer.classList.remove('d-none');
            // Ocultamos el spinner.
            loadingSpinner.classList.add('d-none');
        }
    }

    // --- FUNCIÓN PARA CONSTRUIR LA TABLA HTML ---
    function buildTable(columns, dataRows) {
        // 1. Limpiar cualquier contenido previo
        tableHeader.innerHTML = '';
        tableBody.innerHTML = '';

        // 2. Construir la cabecera (thead)
        const headerRow = document.createElement('tr');
        columns.forEach(columnName => {
            const th = document.createElement('th');
            th.textContent = columnName;
            headerRow.appendChild(th);
        });
        tableHeader.appendChild(headerRow);

        // 3. Construir el cuerpo (tbody)
        dataRows.forEach(rowData => {
            const bodyRow = document.createElement('tr');
            rowData.forEach(cellData => {
                const td = document.createElement('td');
                td.textContent = cellData;
                bodyRow.appendChild(td);
            });
            tableBody.appendChild(bodyRow);
        });
    }

    // --- INICIAR LA CARGA DE DATOS ---
    loadData();
});