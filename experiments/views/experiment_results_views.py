# experiments/views/experiment_results_views.py
import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from core.utils.breadcrumbs import create_experiment_breadcrumbs

# Importamos el modelo usando '..' para subir un nivel y encontrar la carpeta 'models'
from ..models import MLExperiment

# For PDF generation
try:
    import weasyprint
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


@login_required
def ml_experiment_detail(request, pk):
    """
    Muestra los detalles y la configuración de un experimento de ML.
    Este es el "Dashboard" del experimento.
    """
    # Se asegura de que el experimento exista y pertenezca al usuario logueado
    experiment = get_object_or_404(MLExperiment, pk=pk, project__owner=request.user)

    scatter_data_json = None
    if experiment.results and 'prediction_data' in experiment.results:
        scatter_data_json = json.dumps(experiment.results['prediction_data'])

    # Create breadcrumbs for navigation
    breadcrumbs = create_experiment_breadcrumbs(experiment)

    # Fetch MLflow data if mlflow_run_id exists
    mlflow_artifacts = []
    mlflow_params = {}
    mlflow_metrics = {}
    mlflow_error = None
    
    if experiment.mlflow_run_id:
        try:
            import mlflow
            from mlflow.tracking import MlflowClient
            
            # Set tracking URI and create client
            mlflow.set_tracking_uri("http://mlflow:5000")
            client = MlflowClient()
            
            # Get the run details
            run = client.get_run(experiment.mlflow_run_id)
            
            # Extract parameters
            mlflow_params = run.data.params
            
            # Extract metrics
            mlflow_metrics = run.data.metrics
            
            # Get artifacts list
            artifacts = mlflow.artifacts.list_artifacts(run_id=experiment.mlflow_run_id)
            mlflow_artifacts = [
                {
                    'path': artifact.path,
                    'is_dir': artifact.is_dir,
                    'size': getattr(artifact, 'file_size', None),
                    'download_url': f"http://localhost:5000/get-artifact?path={artifact.path}&run_uuid={experiment.mlflow_run_id}"
                }
                for artifact in artifacts
            ]
            
        except Exception as e:
            # Log the error but don't break the page
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not fetch MLflow data for experiment {experiment.id}: {e}")
            mlflow_error = str(e)

    # Gather lineage and traceability data
    lineage_datasources = []
    
    if experiment.input_datasource:
        # Build lineage chain for the primary data source
        def build_datasource_lineage(datasource, depth=0, max_depth=10):
            """Recursively build lineage chain avoiding infinite loops"""
            if depth > max_depth:
                return []
            
            lineage_chain = []
            
            # Add current datasource with appropriate styling based on type
            if datasource.data_type == 'ORIGINAL':
                color = 'blue'
                icon = '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"></path>'''
                title = 'Datos Originales'
            elif datasource.data_type == 'PREPARED':
                color = 'yellow'
                icon = '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>'''
                title = 'Datos Preparados'
            elif datasource.data_type == 'FUSED':
                color = 'purple'
                icon = '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>'''
                title = 'Datos Fusionados'
            else:
                color = 'gray'
                icon = '''<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>'''
                title = 'Fuente de Datos'
            
            lineage_item = {
                'datasource': datasource,
                'color': color,
                'icon': icon,
                'title': title,
                'type_display': datasource.get_data_type_display(),
                'depth': depth
            }
            lineage_chain.append(lineage_item)
            
            # Recursively add parent datasources
            for parent in datasource.parents.all():
                parent_chain = build_datasource_lineage(parent, depth + 1, max_depth)
                lineage_chain.extend(parent_chain)
            
            return lineage_chain
        
        # Build the complete lineage chain
        lineage_datasources = build_datasource_lineage(experiment.input_datasource)
        
        # Sort by depth (parents first, then children)
        lineage_datasources.sort(key=lambda x: x['depth'], reverse=True)

    context = {
        'experiment': experiment,
        'scatter_data_json': scatter_data_json,
        'breadcrumbs': breadcrumbs,
        'mlflow_artifacts': mlflow_artifacts,
        'mlflow_params': mlflow_params,
        'mlflow_metrics': mlflow_metrics,
        'mlflow_error': mlflow_error,
        'lineage_datasources': lineage_datasources,
    }

    return render(request, 'experiments/ml_experiment_detail.html', context)


@login_required
def experiment_report_view(request, pk):
    """
    Muestra el reporte del experimento en formato HTML para visualización en página.
    """
    experiment = get_object_or_404(MLExperiment, pk=pk, project__owner=request.user)
    
    context = {
        'experiment': experiment,
        'is_html_view': True,  # Flag to distinguish from PDF generation
    }
    
    return render(request, 'experiments/report_template.html', context)


@login_required 
def experiment_report_pdf(request, pk):
    """
    Genera y descarga el reporte del experimento en formato PDF.
    """
    experiment = get_object_or_404(MLExperiment, pk=pk, project__owner=request.user)
    
    if not WEASYPRINT_AVAILABLE:
        # Fallback: return HTML version if WeasyPrint is not available
        context = {
            'experiment': experiment,
            'is_pdf_fallback': True,
        }
        html_content = render_to_string('experiments/report_template.html', context, request=request)
        response = HttpResponse(html_content, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="reporte_{experiment.name}_{experiment.id}.html"'
        return response
    
    # Generate PDF using WeasyPrint
    context = {
        'experiment': experiment,
        'is_pdf_view': True,  # Flag for PDF-specific styling
    }
    
    html_content = render_to_string('experiments/report_template.html', context, request=request)
    
    # Create PDF
    html_doc = HTML(string=html_content, base_url=request.build_absolute_uri())
    pdf_file = html_doc.write_pdf()
    
    # Return PDF response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{experiment.name}_{experiment.id}.pdf"'
    
    return response
