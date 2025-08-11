document.addEventListener('DOMContentLoaded', function() {

    // Conjunto para almacenar las columnas que se van a eliminar.
    // Usamos un Set para evitar duplicados de forma automática.
    const removedColumns = new Set();

    // Elementos del DOM con los que vamos a interactuar.
    const removedColumnsList = document.getElementById('removed-columns-list');
    const removedColumnsInput = document.getElementById('removed_columns_input');
    const removeButtons = document.querySelectorAll('.remove-col-btn');

    // Función para actualizar la interfaz y el campo oculto del formulario.
    function updateRemovedColumnsDisplay() {
        // Limpiamos la lista visual.
        removedColumnsList.innerHTML = '';

        if (removedColumns.size === 0) {
            removedColumnsList.innerHTML = '<span class="text-muted">Ninguna seleccionada.</span>';
        } else {
            // Creamos una "píldora" (badge) por cada columna a eliminar.
            removedColumns.forEach(columnName => {
                const badge = document.createElement('span');
                badge.className = 'badge bg-danger me-1';
                badge.textContent = columnName;
                removedColumnsList.appendChild(badge);
            });
        }

        // Actualizamos el valor del campo oculto del formulario.
        // Lo enviamos como un string en formato JSON.
        removedColumnsInput.value = JSON.stringify(Array.from(removedColumns));
    }

    // Añadimos un "escuchador de eventos" a cada botón de "Eliminar".
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const columnName = this.getAttribute('data-column');

            // Alternamos la selección: si la columna ya está, la quitamos. Si no, la añadimos.
            if (removedColumns.has(columnName)) {
                removedColumns.delete(columnName);
                this.classList.remove('btn-danger');
                this.classList.add('btn-outline-danger');
            } else {
                removedColumns.add(columnName);
                this.classList.remove('btn-outline-danger');
                this.classList.add('btn-danger');
            }

            // Actualizamos la interfaz después de cada clic.
            updateRemovedColumnsDisplay();
        });
    });

    // Llamamos a la función una vez al principio para inicializar la pantalla.
    updateRemovedColumnsDisplay();
});