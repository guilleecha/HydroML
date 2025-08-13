document.addEventListener("DOMContentLoaded", function() {
    const statusBadge = document.getElementById('experiment-status-badge');
    if (!statusBadge) {
        return; // No hay nada que hacer si el badge no está en la página
    }

    const statusUrl = statusBadge.dataset.statusUrl;
    const initialStatus = statusBadge.dataset.initialStatus;

    if (!statusUrl) {
        console.error("Status URL no encontrada en el atributo data-status-url.");
        return;
    }

    // Si el estado inicial ya es final, no hacemos nada.
    if (initialStatus === 'FINISHED' || initialStatus === 'FAILED') {
        return;
    }

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

                // Actualizar el color del badge según el estado
                statusBadge.className = 'badge'; // Reset class
                if (data.status === 'COMPLETED' || data.status === 'VALIDATED' || data.status === 'FINISHED') {
                    statusBadge.classList.add('bg-success');
                } else if (data.status === 'FAILED') {
                    statusBadge.classList.add('bg-danger');
                } else if (data.status === 'PROCESSING' || data.status === 'TRAINING' || data.status === 'EVALUATING') {
                    statusBadge.classList.add('bg-warning');
                } else {
                    statusBadge.classList.add('bg-info');
                }

                // Detener el sondeo y recargar si la tarea ha finalizado
                if (data.status === 'FINISHED' || data.status === 'FAILED') {
                    clearInterval(pollingInterval);
                    setTimeout(() => {
                        location.reload();
                    }, 2000); // Espera 2 segundos antes de recargar para que el usuario vea el estado final
                }
            })
            .catch(error => {
                console.error("Error durante el sondeo:", error);
                clearInterval(pollingInterval); // Detener en caso de error de red
            });
    };

    // Iniciar el sondeo inmediatamente y luego cada 3 segundos
    pollStatus();
    pollingInterval = setInterval(pollStatus, 3000);
});
