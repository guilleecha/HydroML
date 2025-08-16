/**
 * ML Experiment Detail Charts and Tabs
 * Handles Chart.js visualizations and tab functionality for ML experiment results
 */

class ExperimentCharts {
    constructor() {
        this.predictionChart = null;
        this.featureImportanceChart = null;
    }

    createPredictionScatterChart() {
        const predictionDataElement = document.getElementById('prediction-data');
        if (!predictionDataElement) return;

        const predictionData = JSON.parse(predictionDataElement.textContent);
        const scatterCtx = document.getElementById('predictionScatterChart');

        if (!predictionData || !scatterCtx) return;

        // Prepare scatter plot data
        const scatterPoints = predictionData.map(p => ({
            x: p.actual,
            y: p.predicted
        }));

        // Calculate min and max values for the perfect fit line
        const allValues = predictionData.flatMap(p => [p.actual, p.predicted]);
        const minVal = Math.min(...allValues);
        const maxVal = Math.max(...allValues);
        
        // Create perfect fit line data (y = x)
        const perfectFitLine = [
            { x: minVal, y: minVal },
            { x: maxVal, y: maxVal }
        ];

        this.predictionChart = new Chart(scatterCtx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Predicciones',
                    data: scatterPoints,
                    backgroundColor: 'rgba(59, 130, 246, 0.6)',
                    borderColor: 'rgba(37, 99, 235, 1)',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }, {
                    label: 'Línea Perfecta (y=x)',
                    data: perfectFitLine,
                    type: 'line',
                    borderColor: 'rgba(239, 68, 68, 0.8)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 0,
                    borderDash: [5, 5],
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Predicciones vs. Valores Reales',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (context.datasetIndex === 0) {
                                    return `Predicción: ${context.parsed.y.toFixed(3)}, Real: ${context.parsed.x.toFixed(3)}`;
                                }
                                return context.dataset.label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Valores Reales',
                            font: { size: 14, weight: 'bold' }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Valores Predichos',
                            font: { size: 14, weight: 'bold' }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'point'
                }
            }
        });
    }

    createFeatureImportanceChart() {
        const featureImportanceDataElement = document.getElementById('feature-importance-data');
        if (!featureImportanceDataElement) return;

        const featureImportanceData = JSON.parse(featureImportanceDataElement.textContent);
        const featureCtx = document.getElementById('featureImportanceChart');

        if (!featureImportanceData || !featureCtx) return;

        const topFeatures = featureImportanceData.slice(0, 10);
        const labels = topFeatures.map(item => item.feature);
        const data = topFeatures.map(item => item.importance);

        this.featureImportanceChart = new Chart(featureCtx, {
            type: 'bar',
            data: {
                labels: labels.reverse(), // Invertir para mostrar la más importante arriba
                datasets: [{
                    label: 'Importancia Relativa',
                    data: data.reverse(), // Invertir los datos para que coincidan
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: 'Top 10 Variables Más Influyentes',
                        font: { size: 16, weight: 'bold' }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Importancia',
                            font: { size: 14, weight: 'bold' }
                        }
                    }
                }
            }
        });
    }

    initializeCharts() {
        this.createPredictionScatterChart();
        this.createFeatureImportanceChart();
    }
}

class ExperimentTabs {
    constructor() {
        this.tabs = ['tab-results', 'tab-config', 'tab-report'];
        this.buttons = ['tab-results-btn', 'tab-config-btn', 'tab-report-btn'];
    }

    showTab(activeTabId, activeButtonId) {
        // Hide all tab contents
        this.tabs.forEach(tabId => {
            const tab = document.getElementById(tabId);
            if (tab) {
                tab.classList.add('hidden');
            }
        });
        
        // Reset all button styles
        this.buttons.forEach(buttonId => {
            const button = document.getElementById(buttonId);
            if (button) {
                button.className = 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm text-foreground-muted border-transparent hover:text-foreground-default transition-colors';
            }
        });
        
        // Show active tab and style active button
        const activeTab = document.getElementById(activeTabId);
        const activeButton = document.getElementById(activeButtonId);
        
        if (activeTab) {
            activeTab.classList.remove('hidden');
        }
        
        if (activeButton) {
            activeButton.className = 'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm text-brand-600 border-brand-600';
        }
    }

    initializeTabs() {
        // Add click event listeners for tab buttons
        document.getElementById('tab-results-btn')?.addEventListener('click', () => {
            this.showTab('tab-results', 'tab-results-btn');
        });
        
        document.getElementById('tab-config-btn')?.addEventListener('click', () => {
            this.showTab('tab-config', 'tab-config-btn');
        });
        
        document.getElementById('tab-report-btn')?.addEventListener('click', () => {
            this.showTab('tab-report', 'tab-report-btn');
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", function() {
    const charts = new ExperimentCharts();
    const tabs = new ExperimentTabs();
    
    charts.initializeCharts();
    tabs.initializeTabs();
});
