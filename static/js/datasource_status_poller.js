/**
 * Datasource Upload Status Polling
 * Handles real-time polling of datasource processing status and quality report display
 */

class DatasourceStatusPoller {
    constructor(datasourceId, statusUrl) {
        this.datasourceId = datasourceId;
        this.statusUrl = statusUrl;
        this.statusEl = document.getElementById('status');
        this.processingIndicator = document.getElementById('processing-indicator');
        this.qualityReport = document.getElementById('quality-report');
        this.errorSection = document.getElementById('error-section');
    }

    async pollStatus() {
        try {
            const res = await fetch(this.statusUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await res.json();
            this.statusEl.textContent = data.status;
            
            if (data.status === 'READY') {
                this.processingIndicator.style.display = 'none';
                this.qualityReport.style.display = 'block';
                this.displayQualityReport(data.quality_report);
                return;
            } else if (data.status === 'ERROR') {
                this.processingIndicator.style.display = 'none';
                this.errorSection.style.display = 'block';
                document.getElementById('error-message').textContent = data.quality_report?.error || 'Error desconocido';
                return;
            }
        } catch (err) {
            this.statusEl.textContent = 'Error verificando estado';
            this.processingIndicator.style.display = 'none';
            this.errorSection.style.display = 'block';
            document.getElementById('error-message').textContent = err.toString();
            return;
        }
        setTimeout(() => this.pollStatus(), 2000);
    }

    displayQualityReport(report) {
        // Update general statistics
        document.getElementById('rows-count').textContent = report.shape[0];
        document.getElementById('columns-count').textContent = report.shape[1];

        // Populate data types table
        const dataTypesTable = document.getElementById('data-types-table');
        dataTypesTable.innerHTML = '';
        for (const [column, dtype] of Object.entries(report.data_types)) {
            const row = document.createElement('tr');
            row.className = 'bg-white border-b hover:bg-gray-50';
            row.innerHTML = `
                <td class="px-6 py-4 font-mono">${column}</td>
                <td class="px-6 py-4 font-mono">${dtype}</td>
            `;
            dataTypesTable.appendChild(row);
        }

        // Populate missing values table
        const missingValuesTable = document.getElementById('missing-values-table');
        missingValuesTable.innerHTML = '';
        const totalRows = report.shape[0];
        for (const [column, missingCount] of Object.entries(report.missing_values)) {
            const percentage = totalRows > 0 ? ((missingCount / totalRows) * 100).toFixed(2) : 0;
            const row = document.createElement('tr');
            row.className = 'bg-white border-b hover:bg-gray-50';
            row.innerHTML = `
                <td class="px-6 py-4 font-mono">${column}</td>
                <td class="px-6 py-4">${missingCount}</td>
                <td class="px-6 py-4">${percentage}%</td>
            `;
            missingValuesTable.appendChild(row);
        }
    }

    start() {
        this.pollStatus();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // This will be configured by the template that includes this script
    if (window.datasourcePollerConfig) {
        const poller = new DatasourceStatusPoller(
            window.datasourcePollerConfig.datasourceId,
            window.datasourcePollerConfig.statusUrl
        );
        poller.start();
    }
});
