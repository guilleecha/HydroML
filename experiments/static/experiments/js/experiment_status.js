document.addEventListener('DOMContentLoaded', function () {
    const statusBadge = document.getElementById('experiment-status-badge');
    const errorAlert = document.getElementById('task-error-alert');
    const statusUrl = statusBadge.dataset.statusUrl;

    // Declarar la variable una sola vez fuera de la función de sondeo.
    let pollingInterval;

    const statusClasses = {
        DRAFT: 'bg-gray-200 text-gray-800',
        PENDING: 'bg-yellow-200 text-yellow-800 animate-pulse',
        SPLITTING: 'bg-blue-200 text-blue-800 animate-pulse',
        SPLIT: 'bg-blue-500 text-white',
        TRAINING: 'bg-indigo-200 text-indigo-800 animate-pulse',
        COMPLETED: 'bg-green-500 text-white',
        FAILED: 'bg-red-500 text-white',
    };

    function pollExperimentStatus() {
        fetch(statusUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Actualizar el badge de estado
                statusBadge.textContent = data.status_display;
                statusBadge.className = `px-3 py-1 rounded-full text-sm font-semibold ${statusClasses[data.status] || statusClasses['DRAFT']}`;

                // Si la tarea ha terminado (COMPLETED o FAILED), detener el sondeo.
                if (data.status === 'COMPLETED' || data.status === 'FAILED') {
                    clearInterval(pollingInterval);
                }

                // Si hay un error, mostrarlo en la alerta.
                if (data.status === 'FAILED' && data.results && data.results.error_message) {
                    errorAlert.innerHTML = `<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert"><strong class="font-bold">Error:</strong><span class="block sm:inline"> ${data.results.error_message}</span></div>`;
                }
            })
            .catch(error => {
                console.error('Error fetching experiment status:', error);
                clearInterval(pollingInterval); // Detener también si hay un error de red
            });
    }

    // Iniciar el sondeo
    // Se asigna el intervalo a la variable ya declarada.
    pollingInterval = setInterval(pollExperimentStatus, 5000);
    // Ejecutar una vez de inmediato al cargar la página
    pollExperimentStatus(); 
});