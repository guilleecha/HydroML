document.addEventListener('DOMContentLoaded', function() {
    const statusBadge = document.getElementById('experiment-status-badge');
    const errorAlert = document.getElementById('task-error-alert');

    if (!statusBadge) {
        return; // No hay nada que hacer si el badge no está en la página
    }

    const statusUrl = statusBadge.dataset.statusUrl;
    const initialStatus = statusBadge.dataset.initialStatus;

    if (!statusUrl) {
        console.error("Status URL no encontrada en el atributo data-status-url.");
        return;
    }
    
    // Usamos 'let' para poder reasignar el intervalo
    let pollingInterval;

    const pollStatus = () => {
        fetch(statusUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('La respuesta de la red no fue correcta.');
                }
                return response.json();
            })
            .then(data => {
                // Actualizar el texto del badge
                statusBadge.textContent = data.status_display;

                // Resetear y aplicar clases de color de Tailwind
                statusBadge.className = 'px-3 py-1 rounded-full text-sm font-semibold'; // Clases base
                
                if (['COMPLETED', 'FINISHED', 'ANALYZED'].includes(data.status)) {
                    statusBadge.classList.add('bg-green-100', 'text-green-800');
                } else if (data.status === 'FAILED') {
                    statusBadge.classList.add('bg-red-100', 'text-red-800');
                    // Mostrar el mensaje de error si existe
                    if (errorAlert && data.results && data.results.error_message) {
                        errorAlert.innerHTML = `<div class="p-4 text-sm text-red-800 rounded-lg bg-red-50" role="alert"><span class="font-medium">¡Error en la Tarea!</span> ${data.results.error_message}</div>`;
                        errorAlert.classList.remove('hidden');
                    }
                } else if (['PROCESSING', 'TRAINING', 'EVALUATING', 'ANALYZING', 'SPLITTING'].includes(data.status)) {
                    statusBadge.classList.add('bg-yellow-100', 'text-yellow-700', 'animate-pulse');
                } else { // DRAFT, SPLIT, etc.
                    statusBadge.classList.add('bg-blue-100', 'text-blue-800');
                }

                // Detener el sondeo y recargar si la tarea ha llegado a un estado final.
                const finalStates = ['SPLIT', 'COMPLETED', 'FINISHED', 'ANALYZED', 'FAILED'];
                if (finalStates.includes(data.status)) {
                    clearInterval(pollingInterval);
                    // Recargar la página después de 2 segundos para mostrar nuevos botones o resultados.
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                }
            })
            .catch(error => {
                console.error("Error durante el sondeo:", error);
                statusBadge.textContent = "Error de Conexión";
                statusBadge.className = 'px-3 py-1 rounded-full text-sm font-semibold bg-red-100 text-red-800';
                clearInterval(pollingInterval); // Detener en caso de error de red
            });
    };

    // Solo iniciar el sondeo si el estado inicial no es uno que requiera acción inmediata
    const initialFinalStates = ['FINISHED', 'ANALYZED', 'FAILED'];
    if (!initialFinalStates.includes(initialStatus)) {
        // Ejecutar una vez al principio para establecer el estado inicial
        pollStatus();
        // Iniciar el sondeo repetido
        pollingInterval = setInterval(pollStatus, 3000);
    } else {
        // Si la página carga en un estado final, solo actualiza la apariencia una vez
        pollStatus();
    }
});