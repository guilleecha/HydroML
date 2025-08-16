document.addEventListener('DOMContentLoaded', function () {
    const resultsBtn = document.getElementById('tab-results-btn');
    const interpretabilityBtn = document.getElementById('tab-interpretability-btn');
    const configBtn = document.getElementById('tab-config-btn');
    const resultsTab = document.getElementById('tab-results');
    const interpretabilityTab = document.getElementById('tab-interpretability');
    const configTab = document.getElementById('tab-config');

    // Si los elementos de las pestañas no existen en la página, no continuar.
    if (!resultsBtn || !configBtn || !resultsTab || !configTab) {
        return;
    }

    function showTab(targetTab, targetBtn) {
        // Ocultar todas las pestañas
        resultsTab.classList.add('hidden');
        if (interpretabilityTab) interpretabilityTab.classList.add('hidden');
        configTab.classList.add('hidden');

        // Desactivar todos los botones
        resultsBtn.classList.add('text-gray-500', 'border-transparent');
        resultsBtn.classList.remove('text-blue-600', 'border-blue-600');
        if (interpretabilityBtn) {
            interpretabilityBtn.classList.add('text-gray-500', 'border-transparent');
            interpretabilityBtn.classList.remove('text-blue-600', 'border-blue-600');
        }
        configBtn.classList.add('text-gray-500', 'border-transparent');
        configBtn.classList.remove('text-blue-600', 'border-blue-600');

        // Mostrar la pestaña objetivo y activar su botón
        targetTab.classList.remove('hidden');
        targetBtn.classList.add('text-blue-600', 'border-blue-600');
        targetBtn.classList.remove('text-gray-500', 'border-transparent');
    }

    resultsBtn.addEventListener('click', () => {
        showTab(resultsTab, resultsBtn);
    });

    if (interpretabilityBtn && interpretabilityTab) {
        interpretabilityBtn.addEventListener('click', () => {
            showTab(interpretabilityTab, interpretabilityBtn);
        });
    }

    configBtn.addEventListener('click', () => {
        showTab(configTab, configBtn);
    });
});