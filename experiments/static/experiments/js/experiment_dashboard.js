document.addEventListener('DOMContentLoaded', function () {
    const resultsBtn = document.getElementById('tab-results-btn');
    const configBtn = document.getElementById('tab-config-btn');
    const resultsTab = document.getElementById('tab-results');
    const configTab = document.getElementById('tab-config');

    // Si los elementos de las pestañas no existen en la página, no continuar.
    if (!resultsBtn || !configBtn || !resultsTab || !configTab) {
        return;
    }

    resultsBtn.addEventListener('click', () => {
        resultsTab.classList.remove('hidden');
        configTab.classList.add('hidden');
        resultsBtn.classList.add('text-blue-600', 'border-blue-600');
        resultsBtn.classList.remove('text-gray-500', 'border-transparent');
        configBtn.classList.add('text-gray-500', 'border-transparent');
        configBtn.classList.remove('text-blue-600', 'border-blue-600');
    });

    configBtn.addEventListener('click', () => {
        configTab.classList.remove('hidden');
        resultsTab.classList.add('hidden');
        configBtn.classList.add('text-blue-600', 'border-blue-600');
        configBtn.classList.remove('text-gray-500', 'border-transparent');
        resultsBtn.classList.add('text-gray-500', 'border-transparent');
        resultsBtn.classList.remove('text-blue-600', 'border-blue-600');
    });
});