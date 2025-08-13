document.addEventListener("DOMContentLoaded", function() {
    const chartDataElement = document.getElementById('chart-data');
    if (!chartDataElement) {
        return;
    }

    const scatterData = JSON.parse(chartDataElement.textContent);
    if (!scatterData) {
        return;
    }

    const ctx = document.getElementById('predictionScatterChart');
    if (!ctx) {
        return;
    }

    const formattedData = scatterData.map(p => ({
        x: p.actual,
        y: p.predicted
    }));

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Predicciones vs. Reales',
                data: formattedData,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
            }]
        },
        options: {
            responsive: true,
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
});
