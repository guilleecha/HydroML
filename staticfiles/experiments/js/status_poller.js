document.addEventListener("DOMContentLoaded", function() {
    const experimentDetailCard = document.getElementById('experiment-detail-card');
    if (!experimentDetailCard) {
        return;
    }

    const statusApiUrl = experimentDetailCard.dataset.statusUrl;
    let pollingInterval;

    function updateResults(results) {
        const resultsContainer = document.getElementById('experiment-results-container');
        if (!resultsContainer) return;

        let content = '<div class="text-center text-muted p-4"><p>Los resultados aparecerán aquí.</p></div>';

        if (results.error) {
            content = `
                <div class="alert alert-danger">
                    <h6 class="alert-heading">¡Error en la ejecución!</h6>
                    <p><strong>Mensaje:</strong> ${results.error}</p>
                </div>`;
        } else if (results.mean_nse !== undefined) {
            let validationResults = `
                <div class="alert alert-secondary">
                    <h6 class="alert-heading">Resultados de la Validación Cruzada</h6>
                    <ul class="mb-0">
                        <li><strong>Coeficiente de Nash-Sutcliffe (NSE) Promedio:</strong> ${results.mean_nse}</li>
                        <li><strong>Desviación Estándar del NSE:</strong> ${results.std_nse}</li>
                        <li><strong>Error Cuadrático Medio (RMSE) Promedio:</strong> ${results.mean_rmse}</li>
                    </ul>
                </div>`;
            
            let finalTestResults = '';
            if (results.final_r2 !== undefined) {
                finalTestResults = `
                <div class="alert alert-success mt-3">
                    <h6 class="alert-heading">Métricas del Test Final (Hold-out)</h6>
                    <ul class="mb-0">
                        <li><strong>Coeficiente de Determinación (R²):</strong> ${results.final_r2}</li>
                        <li><strong>Raíz del Error Cuadrático Medio (RMSE):</strong> ${results.final_rmse}</li>
                    </ul>
                </div>`;
            }
            content = validationResults + finalTestResults;
        }
        resultsContainer.innerHTML = content;
    }

    function updateStatus(status, statusDisplay) {
        const statusBadge = document.getElementById('experiment-status-badge');
        if (statusBadge) {
            statusBadge.textContent = statusDisplay;
            statusBadge.className = 'badge bg-info'; // Reset class
            if (status === 'COMPLETED' || status === 'VALIDATED' || status === 'FINISHED') {
                statusBadge.classList.add('bg-success');
            } else if (status === 'FAILED') {
                statusBadge.classList.add('bg-danger');
            } else if (status === 'PROCESSING' || status === 'TRAINING' || status === 'EVALUATING') {
                statusBadge.classList.add('bg-warning');
            }
        }
    }

    function pollStatus() {
        fetch(statusApiUrl)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Error fetching status:", data.error);
                    clearInterval(pollingInterval);
                    return;
                }

                updateStatus(data.status, data.status_display);
                updateResults(data.results);

                // Actualizar estado de los botones
                document.getElementById('btn-split').classList.toggle('disabled', data.status !== 'DRAFT');
                document.getElementById('btn-train').classList.toggle('disabled', data.status !== 'PREPARED');
                document.getElementById('btn-evaluate').classList.toggle('disabled', data.status !== 'COMPLETED');

                const finalStates = ['COMPLETED', 'FAILED'];
                if (finalStates.includes(data.status)) {
                    clearInterval(pollingInterval);
                    // Recargar la página después de un breve instante para mostrar los resultados finales.
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                }
            })
            .catch(error => {
                console.error("Polling fetch error:", error);
                clearInterval(pollingInterval);
            });
    }

    // Iniciar polling solo si el estado no es final
    const initialStatus = experimentDetailCard.dataset.initialStatus;
    const terminalStates = ['COMPLETED', 'FAILED'];
    if (!terminalStates.includes(initialStatus)) {
        pollingInterval = setInterval(pollStatus, 3000); // Poll every 3 seconds
    }
});
