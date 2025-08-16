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

    context = {
        'experiment': experiment,
        'scatter_data_json': scatter_data_json,
        'breadcrumbs': breadcrumbs,
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
