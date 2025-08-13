document.addEventListener("DOMContentLoaded", function() {
    // --- GRÁFICO DE DISPERSIÓN: PREDICCIONES VS. REALES ---
    const scatterDataElement = document.getElementById('scatter-data');
    if (scatterDataElement) {
        const scatterData = JSON.parse(scatterDataElement.textContent);
        const scatterCtx = document.getElementById('predictionScatterChart');

        if (scatterData && scatterCtx) {
            const formattedScatterData = scatterData.map(p => ({
                x: p.actual,
                y: p.predicted
            }));

            new Chart(scatterCtx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Predicciones vs. Reales',
                        data: formattedScatterData,
                        backgroundColor: 'rgba(59, 130, 246, 0.5)',
                        borderColor: 'rgba(37, 99, 235, 1)',
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Predicciones vs. Valores Reales'
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Valores Reales'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Valores Predichos'
                            }
                        }
                    }
                }
            });
        }
    }

    // --- GRÁFICO DE BARRAS: IMPORTANCIA DE VARIABLES ---
    const featureImportanceDataElement = document.getElementById('feature-importance-data');
    if (featureImportanceDataElement) {
        const featureImportanceData = JSON.parse(featureImportanceDataElement.textContent);
        const featureCtx = document.getElementById('featureImportanceChart');

        if (featureImportanceData && featureCtx) {
            const topFeatures = featureImportanceData.slice(0, 10);
            const labels = topFeatures.map(item => item.feature);
            const data = topFeatures.map(item => item.importance);

            new Chart(featureCtx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels: labels.reverse(), // Invertir para mostrar la más importante arriba
                    datasets: [{
                        label: 'Importancia Relativa',
                        data: data.reverse(), // Invertir los datos para que coincidan
                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    plugins: {
                        legend: { display: false },
                        title: {
                            display: true,
                            text: 'Top 10 Variables Más Influyentes'
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Importancia'
                            }
                        }
                    }
                }
            });
        }
    }
});