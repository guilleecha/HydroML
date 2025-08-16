/**
 * Project Detail Tabs Management
 * Handles tab switching functionality between datasets and experiments tabs
 */

document.addEventListener('DOMContentLoaded', function() {
    const tabDatasetsBtn = document.getElementById('tab-datasets-btn');
    const tabExperimentsBtn = document.getElementById('tab-experiments-btn');
    const tabDatasets = document.getElementById('tab-datasets');
    const tabExperiments = document.getElementById('tab-experiments');

    function setActiveTab(activeBtn, inactiveBtn, activeTab, inactiveTab) {
        // Show/Hide content
        activeTab.classList.remove('hidden');
        inactiveTab.classList.add('hidden');
        
        // Style active button
        activeBtn.classList.remove('text-foreground-secondary', 'border-transparent', 'hover:text-foreground-default', 'hover:border-border-muted');
        activeBtn.classList.add('text-brand-600', 'border-brand-600');
        
        // Style inactive button
        inactiveBtn.classList.remove('text-brand-600', 'border-brand-600');
        inactiveBtn.classList.add('text-foreground-secondary', 'border-transparent', 'hover:text-foreground-default', 'hover:border-border-muted');
    }

    if (tabDatasetsBtn && tabExperimentsBtn && tabDatasets && tabExperiments) {
        tabDatasetsBtn.addEventListener('click', function() {
            setActiveTab(tabDatasetsBtn, tabExperimentsBtn, tabDatasets, tabExperiments);
        });

        tabExperimentsBtn.addEventListener('click', function() {
            setActiveTab(tabExperimentsBtn, tabDatasetsBtn, tabExperiments, tabDatasets);
        });
    }
});
