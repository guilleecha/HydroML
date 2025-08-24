# projects/views/datasource_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.offline import plot
import logging
import traceback

from ..models import Project, DataSource
from ..forms.datasource_forms import DataSourceUpdateForm, DataSourceUploadForm
from data_tools.tasks import convert_file_to_parquet_task
from core.utils.breadcrumbs import create_breadcrumb

# Configure logger
logger = logging.getLogger(__name__)


@login_required
def project_datasources_api(request, project_id):
    """
    API endpoint to get DataSources for a project (for dynamic updates).
    """
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    datasources = project.datasources.filter(status='READY').values('id', 'name', 'filename', 'data_type')
    
    return JsonResponse({
        'success': True,
        'datasources': list(datasources)
    })


@login_required
def datasource_upload_form_partial(request):
    """
    Returns the upload form as a partial template for AJAX loading.
    Enhanced to support contextual UX modes for different use cases.
    """
    # Get parameters
    project_id = request.GET.get('project_id')
    force_selection = request.GET.get('force_selection', 'false').lower() == 'true'
    ux_mode = request.GET.get('ux_mode', 'auto')  # 'dashboard', 'project', 'data_tools', 'auto'
    
    project = None
    show_project_selection = False
    ux_context = {
        'mode': ux_mode,
        'show_project_change_option': False,
        'show_current_project_button': False,
        'contextual_message': None,
    }
    
    if project_id and not force_selection:
        try:
            project = get_object_or_404(Project, id=project_id, owner=request.user)
        except:
            project = None
    
    # Determine if we should show project selection
    user_projects = Project.objects.filter(owner=request.user)
    user_projects_count = user_projects.count()
    
    if user_projects_count == 0:
        return JsonResponse({
            'success': False,
            'error': 'No se encontró ningún proyecto. Crea un proyecto primero.'
        })
    
    # Apply UX Mode Logic
    if ux_mode == 'dashboard':
        # DASHBOARD MODE: Always show selector, with optional current project context
        show_project_selection = True
        if project:
            ux_context['show_current_project_button'] = True
            ux_context['contextual_message'] = f"Subiendo desde el dashboard. Proyecto actual: {project.name}"
        else:
            ux_context['contextual_message'] = "Selecciona el workspace donde subir los datos."
        project = project or user_projects.first()  # Default selection
        
    elif ux_mode == 'project':
        # PROJECT MODE: Pre-select current project, show option to change
        if project:
            show_project_selection = False
            ux_context['show_project_change_option'] = True
            ux_context['contextual_message'] = f"Los datos se subirán a '{project.name}'. ¿Quieres cambiar de workspace?"
        else:
            # Fallback if no project context in project mode
            show_project_selection = True
            ux_context['contextual_message'] = "Selecciona el workspace de destino."
            project = user_projects.first()
            
    elif ux_mode == 'data_tools':
        # DATA TOOLS MODE: Specific behavior for data analysis tools
        if project:
            show_project_selection = False
            ux_context['contextual_message'] = f"Subiendo datos para análisis en '{project.name}'."
        else:
            show_project_selection = True
            ux_context['contextual_message'] = "Selecciona el workspace para el análisis de datos."
            project = user_projects.first()
            
    else:
        # AUTO MODE: Legacy behavior for backward compatibility
        if user_projects_count == 1 and not project and not force_selection:
            # Only one project available, use it automatically
            project = user_projects.first()
            show_project_selection = False
        elif not project or force_selection:
            # Multiple projects but no context, or forced selection - show selection
            show_project_selection = True
            project = project or user_projects.first()  # Default selection
    
    if request.method == 'POST':
        logger.info(f"DataSource upload POST request initiated by user {request.user.id}")
        print(f"[DEBUG] DataSource upload POST request initiated by user {request.user.id}")
        
        try:
            # Log form data (excluding file content for security)
            form_data = request.POST.copy()
            file_info = {}
            if request.FILES:
                for key, file in request.FILES.items():
                    file_info[key] = {
                        'name': file.name,
                        'size': file.size,
                        'content_type': file.content_type
                    }
            
            logger.info(f"Form data: {form_data}")
            logger.info(f"File info: {file_info}")
            print(f"[DEBUG] Form data: {form_data}")
            print(f"[DEBUG] File info: {file_info}")
            
            # Create and validate form
            form = DataSourceUploadForm(
                request.POST, 
                request.FILES, 
                user=request.user, 
                project=project,
                show_project_selection=show_project_selection
            )
            
            logger.info(f"Form created successfully")
            print(f"[DEBUG] Form created successfully")
            
            if form.is_valid():
                logger.info(f"Form validation passed")
                print(f"[DEBUG] Form validation passed")
                
                # Handle project associations FIRST
                selected_projects = form.cleaned_data.get('projects', [])
                if not selected_projects and project:
                    # If no projects selected but we have a context project, use it
                    selected_projects = [project]
                    logger.info(f"Using context project: {project.id}")
                    print(f"[DEBUG] Using context project: {project.id}")
                    
                logger.info(f"Selected projects: {[p.id for p in selected_projects]}")
                print(f"[DEBUG] Selected projects: {[p.id for p in selected_projects]}")
                
                # Save datasource without committing to DB yet
                datasource = form.save(commit=False)
                logger.info(f"DataSource object created: {datasource.name}")
                print(f"[DEBUG] DataSource object created: {datasource.name}")
                
                # Set the owner
                datasource.owner = request.user
                logger.info(f"Owner set to user {request.user.id}")
                print(f"[DEBUG] Owner set to user {request.user.id}")
                
                # Handle project assignment
                if selected_projects:
                    # Set the required project field to first selected project
                    datasource.project = selected_projects[0]
                    logger.info(f"Project field set to: {datasource.project.id}")
                    print(f"[DEBUG] Project field set to: {datasource.project.id}")
                else:
                    # No workspace selected - use first available project as temporary assignment
                    # This allows "Sin asignar" UX while satisfying DB constraints
                    fallback_project = Project.objects.filter(owner=request.user).first()
                    if fallback_project:
                        datasource.project = fallback_project
                        logger.info(f"No workspace selected, using fallback project: {fallback_project.id}")
                        print(f"[DEBUG] No workspace selected, using fallback project: {fallback_project.id}")
                    else:
                        logger.error("No project available for DataSource upload")
                        return JsonResponse({
                            'success': False,
                            'error': 'No hay workspaces disponibles. Crea un workspace primero.'
                        })
                
                # Save to database
                datasource.save()
                logger.info(f"DataSource saved to database with ID: {datasource.id}")
                print(f"[DEBUG] DataSource saved to database with ID: {datasource.id}")
                
                # Associate the datasource with selected projects (many-to-many)
                # Only if projects were explicitly selected
                if selected_projects:
                    for proj in selected_projects:
                        proj.datasources.add(datasource)
                        logger.info(f"DataSource {datasource.id} associated with project {proj.id}")
                        print(f"[DEBUG] DataSource {datasource.id} associated with project {proj.id}")
                
                # Determine redirect URL based on selection
                if selected_projects:
                    # Projects were selected, redirect to first selected project
                    redirect_project = selected_projects[0]
                    redirect_url = f'/projects/{redirect_project.id}/'
                else:
                    # "Sin asignar" was selected, redirect to data sources list
                    redirect_url = '/data-sources/'
                logger.info(f"Redirect URL determined: {redirect_url}")
                print(f"[DEBUG] Redirect URL determined: {redirect_url}")
                
                # Trigger the Parquet conversion task in the background
                try:
                    task_result = convert_file_to_parquet_task.delay(datasource.id)
                    logger.info(f"Celery task triggered successfully: {task_result.id}")
                    print(f"[DEBUG] Celery task triggered successfully: {task_result.id}")
                except Exception as task_error:
                    logger.error(f"Failed to trigger Celery task: {str(task_error)}")
                    print(f"[ERROR] Failed to trigger Celery task: {str(task_error)}")
                    # Continue anyway - the datasource is saved, task can be retried
                
                # Return JSON response for AJAX
                response_data = {
                    'success': True,
                    'message': 'Fuente de datos creada exitosamente',
                    'redirect_url': redirect_url
                }
                logger.info(f"Successful response being returned: {response_data}")
                print(f"[DEBUG] Successful response being returned: {response_data}")
                
                return JsonResponse(response_data)
            else:
                # Form validation failed
                logger.warning(f"Form validation failed. Errors: {form.errors}")
                print(f"[DEBUG] Form validation failed. Errors: {form.errors}")
                
                # Return form with errors
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
                
        except Exception as e:
            # Catch all other exceptions and log them
            error_traceback = traceback.format_exc()
            logger.error(f"Unexpected error in datasource upload: {str(e)}")
            logger.error(f"Full traceback: {error_traceback}")
            print(f"[ERROR] Unexpected error in datasource upload: {str(e)}")
            print(f"[ERROR] Full traceback: {error_traceback}")
            
            return JsonResponse({
                'success': False,
                'error': f'Error del servidor: {str(e)}. Revisa los logs para más detalles.',
                'debug_info': str(e) if hasattr(request.user, 'is_staff') and request.user.is_staff else None
            })
    else:
        form = DataSourceUploadForm(
            user=request.user, 
            project=project,
            show_project_selection=show_project_selection
        )

    context = {
        'form': form,
        'project': project,
        'show_project_selection': show_project_selection,
        'user_projects_count': user_projects_count,
        'ux_context': ux_context,
        'user_projects': user_projects,  # For advanced UX features
    }
    return render(request, 'projects/forms/datasource_form_partial.html', context)


@login_required
def datasource_upload(request, project_id):
    """
    Gestiona la subida de un nuevo archivo DataSource a un proyecto.
    """
    # La consulta correcta: filtra por el campo 'owner' usando el objeto 'request.user'
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == 'POST':
        form = DataSourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            datasource = form.save(commit=False)
            datasource.project = project
            datasource.save()
            
            # Trigger the Parquet conversion task in the background
            convert_file_to_parquet_task.delay(datasource.id)
            
            return redirect('projects:datasource_upload_summary', datasource_id=datasource.id)
    else:
        form = DataSourceUploadForm()

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'projects/workflows/datasource_upload_form.html', context)


class DataSourceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar una fuente de datos.
    """
    model = DataSource
    form_class = DataSourceUpdateForm
    template_name = 'projects/forms/datasource_form.html'

    def get_queryset(self):
        # Security: ensure users can only edit their own datasources
        return super().get_queryset().filter(owner=self.request.user)

    def get_success_url(self):
        # After editing, return to the first project this datasource is associated with
        projects = self.object.projects.all()
        if projects.exists():
            return reverse_lazy('projects:project_detail', kwargs={'pk': projects.first().pk})
        else:
            # If no projects associated, go back to project list
            return reverse_lazy('projects:project_list')


class DataSourceDeleteView(LoginRequiredMixin, DeleteView):
    """
    Vista para confirmar y eliminar una fuente de datos.
    """
    model = DataSource
    template_name = 'projects/workflows/datasource_confirm_delete.html'

    def get_queryset(self):
        # Security: ensure users can only delete their own datasources
        return super().get_queryset().filter(owner=self.request.user)

    def get_success_url(self):
        # After deleting, return to the first project this datasource was associated with
        projects = self.object.projects.all()
        if projects.exists():
            return reverse_lazy('projects:project_detail', kwargs={'pk': projects.first().pk})
        else:
            # If no projects associated, go back to project list
            return reverse_lazy('projects:project_list')


@login_required
def datasource_upload_summary(request, datasource_id):
    """
    Comprehensive Data Quality and Lineage Report page.
    Shows data lineage, quality analysis, and interactive visualizations.
    """
    datasource = get_object_or_404(DataSource, id=datasource_id, owner=request.user)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # return JSON status for polling
        return JsonResponse({
            'status': datasource.status,
            'quality_report': datasource.quality_report,
        })

    # Build breadcrumbs - for datasources with multiple projects, show the first one
    projects = datasource.projects.all()
    project_breadcrumb = None
    if projects.exists():
        first_project = projects.first()
        project_breadcrumb = create_breadcrumb(first_project.name, f'/projects/{first_project.id}/')
    else:
        project_breadcrumb = create_breadcrumb('Projects', '/projects/')
    
    breadcrumbs = [
        create_breadcrumb('Workspace', '/'),
        project_breadcrumb,
        create_breadcrumb(datasource.name, None),
        create_breadcrumb('Reporte de Calidad')
    ]

    # Load quality report data
    quality_report_data = None
    if datasource.quality_report:
        try:
            if isinstance(datasource.quality_report, str):
                quality_report_data = json.loads(datasource.quality_report)
            else:
                quality_report_data = datasource.quality_report
        except (json.JSONDecodeError, TypeError):
            quality_report_data = None

    # Generate data lineage information
    lineage_info = _get_datasource_lineage(datasource)

    # Generate preview charts if data is ready
    preview_charts = None
    if datasource.status == DataSource.Status.READY and datasource.file:
        preview_charts = _generate_preview_charts(datasource)

    context = {
        'datasource': datasource,
        'breadcrumbs': breadcrumbs,
        'quality_report_data': quality_report_data,
        'lineage_info': lineage_info,
        'preview_charts': preview_charts,
    }

    return render(request, 'projects/workflows/datasource_upload_summary.html', context)


def _get_datasource_lineage(datasource):
    """Generate lineage/traceability information for a datasource."""
    lineage = {
        'type': 'unknown',
        'description': 'Origen desconocido',
        'sources': []
    }

    if not datasource.is_derived and datasource.file:
        # Original uploaded file
        lineage['type'] = 'uploaded'
        lineage['description'] = f'Archivo subido: "{datasource.filename}"'
    elif datasource.parents.exists():
        # Derived from other datasources
        parent_count = datasource.parents.count()
        if parent_count == 1:
            parent = datasource.parents.first()
            lineage['type'] = 'transformed'
            lineage['description'] = f'Transformación de: "{parent.name}"'
            lineage['sources'] = [{'name': parent.name, 'id': parent.id}]
        else:
            # Multiple parents = fusion
            lineage['type'] = 'fusion'
            parent_names = [p.name for p in datasource.parents.all()]
            lineage['description'] = f'Fusión de {parent_count} fuentes: {", ".join(parent_names)}'
            lineage['sources'] = [{'name': p.name, 'id': p.id} for p in datasource.parents.all()]

    return lineage


def _generate_preview_charts(datasource):
    """Generate Plotly preview charts for the datasource."""
    try:
        file_path = datasource.file.path
        if not os.path.exists(file_path):
            return None

        # Read the data
        if file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            # Try Parquet as fallback
            try:
                df = pd.read_parquet(file_path)
            except:
                return None

        charts = []
        
        # Limit to first 1000 rows for performance
        df_sample = df.head(1000)
        
        # Get numerical columns for histograms
        numerical_cols = df_sample.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # Generate up to 3 charts
        chart_count = 0
        max_charts = 3
        
        # Chart 1: Histogram of first numerical column
        if numerical_cols and chart_count < max_charts:
            col = numerical_cols[0]
            fig = px.histogram(
                df_sample, 
                x=col,
                title=f'Distribución de {col}',
                nbins=30
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            charts.append({
                'title': f'Histograma: {col}',
                'html': plot(fig, output_type='div', include_plotlyjs=False)
            })
            chart_count += 1
        
        # Chart 2: Box plot of second numerical column (if exists)
        if len(numerical_cols) > 1 and chart_count < max_charts:
            col = numerical_cols[1]
            fig = px.box(
                df_sample,
                y=col,
                title=f'Diagrama de Caja: {col}'
            )
            fig.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            charts.append({
                'title': f'Diagrama de Caja: {col}',
                'html': plot(fig, output_type='div', include_plotlyjs=False)
            })
            chart_count += 1
        
        # Chart 3: Missing values heatmap
        if chart_count < max_charts:
            missing_data = df.isnull().sum()
            if missing_data.sum() > 0:
                # Create missing values bar chart
                fig = px.bar(
                    x=missing_data.index,
                    y=missing_data.values,
                    title='Valores Faltantes por Columna'
                )
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title='Columnas',
                    yaxis_title='Cantidad de Valores Faltantes'
                )
                charts.append({
                    'title': 'Valores Faltantes',
                    'html': plot(fig, output_type='div', include_plotlyjs=False)
                })
                chart_count += 1

        return charts if charts else None

    except Exception as e:
        print(f"Error generating preview charts: {e}")
        return None


@login_required
def datasources_list(request):
    """
    Central page for all user DataSources with AG Grid table.
    """
    # Get all datasources for the current user
    datasources = DataSource.objects.filter(owner=request.user).select_related().prefetch_related('projects').order_by('-uploaded_at')
    
    # Build breadcrumbs
    breadcrumbs = [
        create_breadcrumb('Workspace', '/'),
        create_breadcrumb('Fuentes de Datos')
    ]
    
    # Statistics for the page
    stats = {
        'total': datasources.count(),
        'ready': datasources.filter(status='READY').count(),
        'processing': datasources.filter(status='PROCESSING').count(),
        'failed': datasources.filter(status='FAILED').count(),
    }
    
    context = {
        'datasources': datasources,
        'breadcrumbs': breadcrumbs,
        'stats': stats,
    }
    
    return render(request, 'projects/views/datasources_list.html', context)


@login_required
def add_datasource_to_project(request, project_pk):
    """
    Allows user to add existing DataSources to a specific project.
    GET: Shows available DataSources (excluding those already in the project)
    POST: Adds selected DataSources to the project using ManyToManyField.add()
    """
    # Get the project (ensure it belongs to the user)
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    
    if request.method == 'POST':
        # Get selected DataSource IDs from the form
        selected_datasource_ids = request.POST.getlist('datasources')
        
        if selected_datasource_ids:
            # Get the DataSource objects (ensure they belong to the user)
            selected_datasources = DataSource.objects.filter(
                id__in=selected_datasource_ids,
                owner=request.user
            )
            
            # Use ManyToManyField.add() to create the relationships
            project.datasources.add(*selected_datasources)
            
            # Success message could be added here with Django messages framework
            return redirect('projects:project_detail', pk=project.pk)
        else:
            # Handle case where no DataSources were selected
            # Could add error message here
            pass
    
    # GET request: Show available DataSources
    # Get all user's DataSources that are NOT already in this project
    available_datasources = DataSource.objects.filter(
        owner=request.user,
        status='READY'  # Only show ready DataSources
    ).exclude(
        projects=project  # Exclude DataSources already in this project
    ).order_by('-uploaded_at')
    
    # Build breadcrumbs
    breadcrumbs = [
        create_breadcrumb('Workspace', '/'),
        create_breadcrumb('Workspaces', '/projects/'),
        create_breadcrumb(project.name, f'/projects/{project.pk}/'),
        create_breadcrumb('Añadir Fuentes de Datos')
    ]
    
    context = {
        'project': project,
        'available_datasources': available_datasources,
        'breadcrumbs': breadcrumbs,
    }
    
    return render(request, 'projects/workflows/add_datasource_to_project.html', context)


@login_required
def datasource_create_iframe(request):
    """
    Simplified iframe view for datasource creation without layout overhead.
    This view provides a streamlined interface for embedding in modals.
    """
    if request.method == 'POST':
        form = DataSourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            datasource = form.save(commit=False)
            datasource.owner = request.user
            datasource.save()
            
            # Process the file in background
            if datasource.file:
                try:
                    convert_file_to_parquet_task.delay(str(datasource.id))
                except Exception as e:
                    logger.error(f"Failed to queue parquet conversion: {e}")
            
            return JsonResponse({
                'success': True,
                'datasource_id': str(datasource.id),
                'message': 'Datasource created successfully'
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    else:
        form = DataSourceUploadForm()
    
    return render(request, 'projects/forms/datasource_form_partial.html', {
        'form': form,
        'is_iframe': True
    })