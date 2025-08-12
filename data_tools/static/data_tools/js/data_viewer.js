// Se asegura de que el código se ejecute solo cuando el DOM esté completamente cargado.
document.addEventListener('DOMContentLoaded', function() {

    // --- OBTENER ELEMENTOS DEL DOM ---
    const loadingSpinner = document.getElementById('loading-spinner');
    const errorContainer = document.getElementById('error-container');
    const tableWrapper = document.getElementById('table-wrapper'); // Contenedor de la tabla

    // --- OBTENER DATOS DEL SCRIPT DE LA PLANTILLA ---
    const scriptData = JSON.parse(document.getElementById('data-viewer-script-data').textContent);
    const apiUrl = scriptData.dataSourceUrl;

    // --- FUNCIÓN PRINCIPAL PARA CARGAR DATOS E INICIALIZAR LA TABLA ---
    async function loadDataAndInitializeTable() {
        try {
            // Hacemos la petición a nuestra API
            const response = await fetch(apiUrl);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Error del servidor: ${response.status}`);
            }

            const jsonData = await response.json();

            if (jsonData.error) {
                throw new Error(jsonData.error);
            }

            // Ocultamos el spinner de carga
            loadingSpinner.style.display = 'none';
            // Mostramos el contenedor de la tabla
            tableWrapper.classList.remove('hidden');

            // --- LA MAGIA DE DATATABLES ---
            // Ya no construimos la tabla a mano.
            // Simplemente inicializamos DataTables en nuestro elemento <table>
            // y le pasamos los datos y la configuración.
            new DataTable('#data-table', {
                // Le decimos a DataTables cómo se llaman nuestras columnas
                columns: jsonData.columns.map(columnName => ({ title: columnName })),

                // Le pasamos el array de datos
                data: jsonData.data,

                // --- FUNCIONALIDADES EXTRA (GRATIS) ---
                paging: true,      // Activa la paginación (ej: Mostrar 10 de 100 registros)
                searching: true,   // Activa la barra de búsqueda
                responsive: true,  // Hace la tabla adaptable a pantallas pequeñas
                language: {        // Traducimos la interfaz a español
                    search: "Buscar:",
                    lengthMenu: "Mostrar _MENU_ registros por página",
                    info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
                    infoEmpty: "No se encontraron registros",
                    infoFiltered: "(filtrado de _MAX_ registros totales)",
                    zeroRecords: "No se encontraron registros que coincidan",
                    paginate: {
                        first: "Primero",
                        last: "Último",
                        next: "Siguiente",
                        previous: "Anterior"
                    }
                }
            });

        } catch (error) {
            // --- MANEJO DE ERRORES ---
            console.error('Error al cargar los datos:', error);
            errorContainer.textContent = `Error al cargar los datos: ${error.message}`;
            errorContainer.classList.remove('d-none');
            loadingSpinner.style.display = 'none';
        }
    }

    // --- INICIAR LA CARGA DE DATOS ---
    loadDataAndInitializeTable();
});