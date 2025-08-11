// static/js/projects/prepare_data.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('data-prep-form');
    if (!form) return;

    const table = document.getElementById('data-preview-table');
    const toggleEditBtn = document.getElementById('toggle-edit-btn');
    const undoBtn = document.getElementById('undo-btn');
    const removedColumnsInput = document.getElementById('removed_columns_input');

    if (!table || !toggleEditBtn || !undoBtn || !removedColumnsInput) {
        console.error("Faltan elementos esenciales en la página para el script.");
        return;
    }

    let isEditMode = false;
    let removedColumnsHistory = [];

    // --- FUNCIÓN 1: Activar/Desactivar el modo de edición ---
    toggleEditBtn.addEventListener('click', () => {
        isEditMode = !isEditMode;
        toggleEditBtn.textContent = isEditMode ? '✅ Terminar Edición' : '✏️ Editar Columnas';

        // Muestra u oculta todos los botones de eliminar (❌)
        table.querySelectorAll('.delete-col-btn').forEach(btn => {
            btn.style.display = isEditMode ? 'inline' : 'none';
        });

        // Muestra el botón de deshacer solo si estamos en modo edición y hay algo que deshacer
        undoBtn.style.display = isEditMode && removedColumnsHistory.length > 0 ? 'inline-block' : 'none';
    });

    // --- FUNCIÓN 2: Manejar el clic en el botón de eliminar (❌) ---
    table.addEventListener('click', function(e) {
        if (isEditMode && e.target && e.target.classList.contains('delete-col-btn')) {
            const th = e.target.closest('th'); // Busca el encabezado padre
            const colName = th.dataset.colName;
            const colIndex = Array.from(th.parentNode.children).indexOf(th);

            // Oculta la columna (cabecera y celdas del cuerpo)
            th.style.display = 'none';
            table.querySelectorAll('tbody tr').forEach(row => {
                if (row.children[colIndex]) row.children[colIndex].style.display = 'none';
            });

            // Guarda la columna eliminada en el historial
            removedColumnsHistory.push({ name: colName, index: colIndex });
            undoBtn.style.display = 'inline-block';
        }
    });

    // --- FUNCIÓN 3: Deshacer la última eliminación ---
    undoBtn.addEventListener('click', () => {
        if (removedColumnsHistory.length > 0) {
            const lastRemoved = removedColumnsHistory.pop();
            const header = table.querySelector(`thead th[data-col-name="${lastRemoved.name}"]`);

            // Muestra la columna de nuevo
            if (header) header.style.display = '';
            table.querySelectorAll('tbody tr').forEach(row => {
               if (row.children[lastRemoved.index]) row.children[lastRemoved.index].style.display = '';
            });
        }
        if (removedColumnsHistory.length === 0) {
            undoBtn.style.display = 'none';
        }
    });

    // --- FUNCIÓN 4: Antes de enviar el formulario, actualiza el campo oculto ---
    form.addEventListener('submit', () => {
        const finalRemovedColumns = removedColumnsHistory.map(item => item.name);
        removedColumnsInput.value = JSON.stringify(finalRemovedColumns);
    });
});