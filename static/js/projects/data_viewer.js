// static/js/data_viewer.js

$(document).ready(function() {
    const dataTableElement = $('#dataTable');
    // Si la tabla no existe en la página, no hacemos nada.
    if (dataTableElement.length === 0) {
        return;
    }

    // Obtenemos la URL de la API desde un atributo en la tabla HTML.
    const dataUrl = dataTableElement.data('url');

    // Hacemos la llamada a nuestra API para obtener los datos.
    fetch(dataUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('La respuesta de la red no fue exitosa.');
            }
            return response.json();
        })
        .then(data => {
            // Verificamos que tengamos columnas y datos
            if (!data || !data.columns || !data.data) {
                throw new Error('El formato de los datos recibidos es incorrecto.');
            }

            // --- ESTA ES LA FORMA CORRECTA DE INICIALIZAR DATATABLES ---
            // Le pasamos las columnas y los datos al mismo tiempo.
            dataTableElement.DataTable({
                columns: data.columns.map(column => ({ title: column })),
                data: data.data,
                responsive: true,
                processing: true,
                language: {
                    processing: "Cargando datos...",
                    search: "Buscar:",
                    lengthMenu: "Mostrar _MENU_ registros",
                    info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
                    infoEmpty: "Mostrando 0 a 0 de 0 registros",
                    infoFiltered: "(filtrado de _MAX_ registros totales)",
                    paginate: {
                        first: "Primero",
                        last: "Último",
                        next: "Siguiente",
                        previous: "Anterior"
                    }
                }
            });
        })
        .catch(error => {
            console.error("Error al cargar los datos:", error);
            // Mostramos un error en la tabla si algo falla
            dataTableElement.html('<tbody><tr><td class="text-center text-danger p-4">No se pudieron cargar los datos. Revisa la consola para más detalles.</td></tr></tbody>');
        });
});