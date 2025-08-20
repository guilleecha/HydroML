"""
HTML Report Generator for Data Quality Reports.
Modern, responsive HTML reports with enhanced visualizations.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from django.utils import timezone
import sentry_sdk

logger = logging.getLogger(__name__)


class HtmlReportGenerator:
    """
    Modern HTML report generator with responsive design and interactive elements.
    """
    
    def __init__(self, datasource_id: str):
        self.datasource_id = datasource_id
        
    def generate_comprehensive_report(self, 
                                    quality_data: Dict[str, Any],
                                    output_path: str,
                                    report_type: str = 'comprehensive') -> str:
        """
        Generate comprehensive HTML report.
        
        Args:
            quality_data: Combined quality data from all services
            output_path: Output directory path
            report_type: Type of report ('comprehensive', 'validation', 'cleaning')
            
        Returns:
            Path to generated HTML file
        """
        try:
            # Ensure output directory exists
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            # Generate report filename
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{report_type}_report_ds_{self.datasource_id}_{timestamp}.html"
            report_path = Path(output_path) / filename
            
            # Generate HTML content based on type
            if report_type == 'comprehensive':
                html_content = self._generate_comprehensive_html(quality_data)
            elif report_type == 'validation':
                html_content = self._generate_validation_html(quality_data)
            elif report_type == 'cleaning':
                html_content = self._generate_cleaning_html(quality_data)
            else:
                html_content = self._generate_basic_html(quality_data)
            
            # Save report
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            sentry_sdk.capture_exception(e)
            return self._generate_error_report(str(e), output_path)
    
    def _generate_comprehensive_html(self, quality_data: Dict[str, Any]) -> str:
        """Generate comprehensive HTML report."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Quality Report - DataSource {self.datasource_id}</title>
    {self._get_modern_css()}
    {self._get_chart_libraries()}
</head>
<body>
    <div class="container">
        {self._get_header(quality_data)}
        {self._get_summary_cards(quality_data)}
        {self._get_validation_section(quality_data)}
        {self._get_cleaning_section(quality_data)}
        {self._get_data_profile_section(quality_data)}
        {self._get_anomalies_section(quality_data)}
        {self._get_recommendations_section(quality_data)}
    </div>
    {self._get_interactive_scripts()}
</body>
</html>
        """
    
    def _get_modern_css(self) -> str:
        """Get modern CSS styles."""
        return """
<style>
    :root {
        --primary-color: #2563eb;
        --success-color: #059669;
        --warning-color: #d97706;
        --error-color: #dc2626;
        --bg-color: #f8fafc;
        --card-bg: #ffffff;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --border-color: #e5e7eb;
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--bg-color);
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .header {
        background: linear-gradient(135deg, var(--primary-color), #3b82f6);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
    }
    
    .header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    .summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .summary-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .summary-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    .card-icon {
        width: 3rem;
        height: 3rem;
        border-radius: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .icon-success { background-color: #d1fae5; color: var(--success-color); }
    .icon-warning { background-color: #fef3c7; color: var(--warning-color); }
    .icon-error { background-color: #fee2e2; color: var(--error-color); }
    .icon-info { background-color: #dbeafe; color: var(--primary-color); }
    
    .card-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .card-label {
        color: var(--text-secondary);
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .section {
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 0.75rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }
    
    .section h2 {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        color: var(--text-primary);
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 0.5rem;
    }
    
    .table-container {
        overflow-x: auto;
        margin-top: 1rem;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.875rem;
    }
    
    th, td {
        padding: 0.75rem;
        text-align: left;
        border-bottom: 1px solid var(--border-color);
    }
    
    th {
        background-color: var(--bg-color);
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-success {
        background-color: #d1fae5;
        color: var(--success-color);
    }
    
    .status-error {
        background-color: #fee2e2;
        color: var(--error-color);
    }
    
    .status-warning {
        background-color: #fef3c7;
        color: var(--warning-color);
    }
    
    .progress-bar {
        width: 100%;
        height: 0.5rem;
        background-color: var(--border-color);
        border-radius: 9999px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--success-color), #34d399);
        transition: width 0.3s ease;
    }
    
    .chart-container {
        height: 300px;
        margin: 1rem 0;
    }
    
    .recommendation {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .recommendation-icon {
        color: var(--primary-color);
        margin-right: 0.5rem;
    }
    
    @media (max-width: 768px) {
        .container {
            padding: 1rem;
        }
        
        .header h1 {
            font-size: 2rem;
        }
        
        .summary-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
        """
    
    def _get_chart_libraries(self) -> str:
        """Get chart library imports."""
        return """
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
        """
    
    def _get_header(self, quality_data: Dict[str, Any]) -> str:
        """Generate header section."""
        timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return f"""
<div class="header">
    <h1>🔍 Data Quality Report</h1>
    <p>DataSource ID: <strong>{self.datasource_id}</strong></p>
    <p>Generated: {timestamp}</p>
</div>
        """
    
    def _get_summary_cards(self, quality_data: Dict[str, Any]) -> str:
        """Generate summary cards."""
        # Extract key metrics
        validation_data = quality_data.get('validation_results', {})
        cleaning_data = quality_data.get('cleaning_report', {})
        profile_data = quality_data.get('data_profile', {})
        
        success_rate = validation_data.get('success_percent', 0)
        total_rows = profile_data.get('total_rows', 0)
        total_columns = profile_data.get('total_columns', 0)
        anomalies = len(quality_data.get('anomalies_detected', {}))
        
        return f"""
<div class="summary-grid">
    <div class="summary-card">
        <div class="card-header">
            <div class="card-icon icon-success">✓</div>
        </div>
        <div class="card-value">{success_rate:.1f}%</div>
        <div class="card-label">Validation Success</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {success_rate}%"></div>
        </div>
    </div>
    
    <div class="summary-card">
        <div class="card-header">
            <div class="card-icon icon-info">📊</div>
        </div>
        <div class="card-value">{total_rows:,}</div>
        <div class="card-label">Total Rows</div>
    </div>
    
    <div class="summary-card">
        <div class="card-header">
            <div class="card-icon icon-info">📋</div>
        </div>
        <div class="card-value">{total_columns}</div>
        <div class="card-label">Total Columns</div>
    </div>
    
    <div class="summary-card">
        <div class="card-header">
            <div class="card-icon icon-warning">⚠️</div>
        </div>
        <div class="card-value">{anomalies}</div>
        <div class="card-label">Anomalies Detected</div>
    </div>
</div>
        """
    
    def _get_validation_section(self, quality_data: Dict[str, Any]) -> str:
        """Generate validation results section."""
        validation_data = quality_data.get('validation_results', {})
        
        if not validation_data:
            return '<div class="section"><h2>Validation Results</h2><p>No validation data available.</p></div>'
        
        return f"""
<div class="section">
    <h2>📋 Validation Results</h2>
    <div class="table-container">
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr>
                <td>Overall Status</td>
                <td>
                    <span class="status-badge {'status-success' if validation_data.get('success', False) else 'status-error'}">
                        {'PASSED' if validation_data.get('success', False) else 'FAILED'}
                    </span>
                </td>
            </tr>
            <tr><td>Success Rate</td><td>{validation_data.get('success_percent', 0):.1f}%</td></tr>
            <tr><td>Expectations Evaluated</td><td>{validation_data.get('evaluated_expectations', 0)}</td></tr>
            <tr><td>Successful Expectations</td><td>{validation_data.get('successful_expectations', 0)}</td></tr>
            <tr><td>Failed Expectations</td><td>{validation_data.get('unsuccessful_expectations', 0)}</td></tr>
        </table>
    </div>
</div>
        """
    
    def _get_cleaning_section(self, quality_data: Dict[str, Any]) -> str:
        """Generate data cleaning section."""
        cleaning_data = quality_data.get('cleaning_report', {})
        
        if not cleaning_data:
            return '<div class="section"><h2>Data Cleaning</h2><p>No cleaning data available.</p></div>'
        
        operations = cleaning_data.get('operations_performed', [])
        
        operations_html = ""
        for op in operations:
            operations_html += f"""
            <tr>
                <td>{op.get('operation', 'Unknown')}</td>
                <td>{self._format_operation_details(op)}</td>
            </tr>
            """
        
        return f"""
<div class="section">
    <h2>🧹 Data Cleaning Operations</h2>
    <div class="table-container">
        <table>
            <tr><th>Operation</th><th>Details</th></tr>
            {operations_html}
        </table>
    </div>
</div>
        """
    
    def _get_data_profile_section(self, quality_data: Dict[str, Any]) -> str:
        """Generate data profile section."""
        profile_data = quality_data.get('data_profile', {})
        
        if not profile_data:
            return '<div class="section"><h2>Data Profile</h2><p>No profile data available.</p></div>'
        
        return f"""
<div class="section">
    <h2>📈 Data Profile</h2>
    <div class="table-container">
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Rows</td><td>{profile_data.get('total_rows', 0):,}</td></tr>
            <tr><td>Total Columns</td><td>{profile_data.get('total_columns', 0)}</td></tr>
            <tr><td>Memory Usage</td><td>{profile_data.get('memory_usage_mb', 0):.2f} MB</td></tr>
            <tr><td>Duplicate Rows</td><td>{profile_data.get('duplicate_rows', 0)}</td></tr>
            <tr><td>Numeric Columns</td><td>{profile_data.get('numeric_columns', 0)}</td></tr>
            <tr><td>Categorical Columns</td><td>{profile_data.get('categorical_columns', 0)}</td></tr>
            <tr><td>DateTime Columns</td><td>{profile_data.get('datetime_columns', 0)}</td></tr>
        </table>
    </div>
    <div class="chart-container">
        <canvas id="dataTypesChart"></canvas>
    </div>
</div>
        """
    
    def _get_anomalies_section(self, quality_data: Dict[str, Any]) -> str:
        """Generate anomalies section."""
        anomalies = quality_data.get('anomalies_detected', {})
        
        if not anomalies:
            return '<div class="section"><h2>Anomalies</h2><p>No anomalies detected.</p></div>'
        
        anomaly_rows = ""
        for column, data in anomalies.items():
            anomaly_rows += f"""
            <tr>
                <td>{column}</td>
                <td>{data.get('outlier_count', 0)}</td>
                <td>{data.get('outlier_percentage', 0):.2f}%</td>
                <td>{data.get('bounds', {}).get('lower', 'N/A'):.2f} - {data.get('bounds', {}).get('upper', 'N/A'):.2f}</td>
            </tr>
            """
        
        return f"""
<div class="section">
    <h2>⚠️ Anomalies Detected</h2>
    <div class="table-container">
        <table>
            <tr><th>Column</th><th>Outlier Count</th><th>Percentage</th><th>Normal Range</th></tr>
            {anomaly_rows}
        </table>
    </div>
</div>
        """
    
    def _get_recommendations_section(self, quality_data: Dict[str, Any]) -> str:
        """Generate recommendations section."""
        recommendations = self._generate_recommendations(quality_data)
        
        rec_html = ""
        for rec in recommendations:
            rec_html += f"""
            <div class="recommendation">
                <span class="recommendation-icon">💡</span>
                <strong>{rec['title']}</strong>: {rec['description']}
            </div>
            """
        
        return f"""
<div class="section">
    <h2>💡 Recommendations</h2>
    {rec_html}
</div>
        """
    
    def _get_interactive_scripts(self) -> str:
        """Generate interactive JavaScript."""
        return """
<script>
// Data types chart
const ctx = document.getElementById('dataTypesChart');
if (ctx) {
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Numeric', 'Categorical', 'DateTime', 'Other'],
            datasets: [{
                data: [3, 2, 1, 1], // Example data
                backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}
</script>
        """
    
    def _format_operation_details(self, operation: Dict[str, Any]) -> str:
        """Format operation details for display."""
        op_type = operation.get('operation', '')
        
        if op_type == 'remove_duplicates':
            return f"Removed {operation.get('duplicates_removed', 0)} duplicates ({operation.get('percentage', 0):.1f}%)"
        elif op_type == 'type_conversions':
            return f"Converted {len(operation.get('conversions', []))} columns"
        elif op_type == 'handle_missing_values':
            return f"Strategy: {operation.get('strategy', 'unknown')}"
        else:
            return str(operation)
    
    def _generate_recommendations(self, quality_data: Dict[str, Any]) -> list:
        """Generate smart recommendations based on data quality."""
        recommendations = []
        
        validation_data = quality_data.get('validation_results', {})
        profile_data = quality_data.get('data_profile', {})
        anomalies = quality_data.get('anomalies_detected', {})
        
        # Validation-based recommendations
        if validation_data.get('success_percent', 100) < 80:
            recommendations.append({
                'title': 'Improve Data Quality',
                'description': 'Validation success rate is below 80%. Consider reviewing and fixing data quality issues.'
            })
        
        # Missing data recommendations
        missing_values = profile_data.get('missing_values', {})
        high_missing = [col for col, count in missing_values.items() if count > 0]
        if high_missing:
            recommendations.append({
                'title': 'Handle Missing Data',
                'description': f'Consider imputation strategies for columns with missing values: {", ".join(high_missing[:3])}'
            })
        
        # Anomaly recommendations
        if anomalies:
            recommendations.append({
                'title': 'Review Anomalies',
                'description': f'Found {len(anomalies)} columns with outliers. Consider data cleaning or validation rules.'
            })
        
        # Performance recommendations
        memory_mb = profile_data.get('memory_usage_mb', 0)
        if memory_mb > 500:  # 500MB
            recommendations.append({
                'title': 'Optimize Memory Usage',
                'description': 'Dataset is large. Consider data sampling or chunked processing for better performance.'
            })
        
        return recommendations
    
    def _generate_error_report(self, error_message: str, output_path: str) -> str:
        """Generate error report when main report fails."""
        try:
            error_path = Path(output_path) / f"error_report_ds_{self.datasource_id}.html"
            
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Data Quality Error Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .error {{ color: #dc2626; background: #fee2e2; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>Data Quality Report - Error</h1>
    <div class="error">
        <h2>Report Generation Failed</h2>
        <p><strong>DataSource ID:</strong> {self.datasource_id}</p>
        <p><strong>Error:</strong> {error_message}</p>
        <p><strong>Time:</strong> {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
            """
            
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(error_path)
            
        except Exception as e:
            logger.error(f"Error report generation failed: {e}")
            return ""
    
    def _generate_validation_html(self, quality_data: Dict[str, Any]) -> str:
        """Generate validation-focused HTML report."""
        return self._generate_comprehensive_html(quality_data)
    
    def _generate_cleaning_html(self, quality_data: Dict[str, Any]) -> str:
        """Generate cleaning-focused HTML report."""
        return self._generate_comprehensive_html(quality_data)
    
    def _generate_basic_html(self, quality_data: Dict[str, Any]) -> str:
        """Generate basic HTML report."""
        return self._generate_comprehensive_html(quality_data)