/**
 * Datasource Upload Status Polling
 * Handles real-time polling of datasource processing status and quality report display
 */

class DatasourceStatusPoller {
    constructor(datasourceId, statusUrl) {
        this.datasourceId = datasourceId;
        this.statusUrl = statusUrl;
        this.statusEl = document.getElementById('status');
        this.statusSection = document.getElementById('status-section');
        this.mainContent = document.getElementById('main-content');
        this.errorSection = document.getElementById('error-section');
    }

    async pollStatus() {
        try {
            const res = await fetch(this.statusUrl, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            const data = await res.json();
            
            if (this.statusEl) {
                this.statusEl.textContent = this.getStatusDisplayText(data.status);
            }
            
            if (data.status === 'READY') {
                if (this.statusSection) this.statusSection.style.display = 'none';
                if (this.mainContent) this.mainContent.style.display = 'block';
                this.displayQualityReport(data.quality_report);
                return;
            } else if (data.status === 'ERROR') {
                if (this.statusSection) this.statusSection.style.display = 'none';
                if (this.errorSection) this.errorSection.style.display = 'block';
                const errorMessage = document.getElementById('error-message');
                if (errorMessage) {
                    errorMessage.textContent = data.quality_report?.error || 'Error desconocido durante el procesamiento';
                }
                return;
            }
        } catch (err) {
            console.error('Error polling status:', err);
            if (this.statusEl) {
                this.statusEl.textContent = 'Error verificando estado';
            }
            if (this.statusSection) this.statusSection.style.display = 'none';
            if (this.errorSection) this.errorSection.style.display = 'block';
            const errorMessage = document.getElementById('error-message');
            if (errorMessage) {
                errorMessage.textContent = 'Error de conexión: ' + err.toString();
            }
            return;
        }
        setTimeout(() => this.pollStatus(), 2000);
    }

    getStatusDisplayText(status) {
        const statusMap = {
            'UPLOADING': 'Subiendo archivo...',
            'PROCESSING': 'Procesando datos...',
            'READY': 'Completado',
            'ERROR': 'Error'
        };
        return statusMap[status] || status;
    }

    displayQualityReport(report) {
        if (!report) {
            console.warn('No quality report data available');
            return;
        }

        try {
            // Update general statistics in Quality Summary tab
            this.updateGeneralStats(report);
            
            // Populate columns analysis table
            this.populateColumnsAnalysisTable(report);
            
        } catch (err) {
            console.error('Error displaying quality report:', err);
        }
    }

    updateGeneralStats(report) {
        // Update rows count
        const rowsCount = document.getElementById('rows-count');
        if (rowsCount && report.shape) {
            rowsCount.textContent = report.shape[0]?.toLocaleString() || '-';
        }

        // Update columns count
        const columnsCount = document.getElementById('columns-count');
        if (columnsCount && report.shape) {
            columnsCount.textContent = report.shape[1]?.toLocaleString() || '-';
        }

        // Update missing values total
        const missingValuesCount = document.getElementById('missing-values-count');
        if (missingValuesCount && report.missing_values) {
            const totalMissing = Object.values(report.missing_values).reduce((sum, count) => sum + count, 0);
            missingValuesCount.textContent = totalMissing.toLocaleString();
        }

        // Update duplicate rows count
        const duplicateRowsCount = document.getElementById('duplicate-rows-count');
        if (duplicateRowsCount) {
            duplicateRowsCount.textContent = report.duplicate_rows || '0';
        }
    }

    populateColumnsAnalysisTable(report) {
        const tableBody = document.getElementById('columns-analysis-table');
        if (!tableBody) return;

        tableBody.innerHTML = '';
        
        if (!report.data_types) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="5" class="px-6 py-4 text-center text-foreground-muted dark:text-darcula-foreground-muted">
                    No hay información de columnas disponible
                </td>
            `;
            tableBody.appendChild(row);
            return;
        }

        const totalRows = report.shape ? report.shape[0] : 0;
        
        for (const [column, dtype] of Object.entries(report.data_types)) {
            const missingCount = report.missing_values?.[column] || 0;
            const missingPercentage = totalRows > 0 ? ((missingCount / totalRows) * 100).toFixed(2) : '0.00';
            const uniqueCount = report.unique_values?.[column] || '-';
            
            const row = document.createElement('tr');
            row.className = 'hover:bg-background-secondary dark:hover:bg-darcula-background-lighter transition-colors';
            
            // Format data type with color coding
            let dtypeClass = 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
            if (dtype.includes('int') || dtype.includes('float')) {
                dtypeClass = 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200';
            } else if (dtype.includes('object') || dtype.includes('string')) {
                dtypeClass = 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200';
            } else if (dtype.includes('datetime')) {
                dtypeClass = 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200';
            } else if (dtype.includes('bool')) {
                dtypeClass = 'bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200';
            }
            
            // Format missing percentage with color coding
            let missingClass = '';
            const missingPct = parseFloat(missingPercentage);
            if (missingPct === 0) {
                missingClass = 'text-green-600 dark:text-green-400';
            } else if (missingPct < 5) {
                missingClass = 'text-amber-600 dark:text-amber-400';
            } else if (missingPct < 20) {
                missingClass = 'text-orange-600 dark:text-orange-400';
            } else {
                missingClass = 'text-danger-600 dark:text-danger-400';
            }
            
            row.innerHTML = `
                <td class="px-6 py-4">
                    <span class="font-mono text-sm text-foreground-primary dark:text-darcula-foreground">
                        ${column}
                    </span>
                </td>
                <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${dtypeClass}">
                        ${dtype}
                    </span>
                </td>
                <td class="px-6 py-4 text-foreground-default dark:text-darcula-foreground">
                    ${typeof uniqueCount === 'number' ? uniqueCount.toLocaleString() : uniqueCount}
                </td>
                <td class="px-6 py-4 text-foreground-default dark:text-darcula-foreground">
                    ${missingCount.toLocaleString()}
                </td>
                <td class="px-6 py-4">
                    <span class="font-medium ${missingClass}">
                        ${missingPercentage}%
                    </span>
                </td>
            `;
            
            tableBody.appendChild(row);
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
