from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from projects.models import Project
from ..models import ExperimentSuite
from ..forms.suite_forms import AblationSuiteForm, ExperimentSuiteForm
from ..tasks import run_experiment_suite_task
import json


class ExperimentSuiteCreateView(LoginRequiredMixin, CreateView):
    """
    Class-based view for creating a new ExperimentSuite.
    """
    model = ExperimentSuite
    form_class = ExperimentSuiteForm
    template_name = 'experiments/suite_form.html'
    
    def get_project(self):
        """Get the project from URL parameter and verify ownership."""
        return get_object_or_404(
            Project, 
            id=self.kwargs['project_pk'], 
            owner=self.request.user
        )
    
    def get_form_kwargs(self):
        """Pass the project to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add project and breadcrumbs to context."""
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        
        context.update({
            'project': project,
            'view_title': 'Crear Nuevo Suite de Experimentos',
            'breadcrumbs': [
                {'name': 'Proyectos', 'url': reverse('projects:project_list')},
                {'name': project.name, 'url': reverse('projects:project_detail', kwargs={'pk': project.pk})},
                {'name': 'Crear Suite', 'url': None}
            ]
        })
        return context
    
    def form_valid(self, form):
        """Save the suite with the correct project association."""
        form.instance.project = self.get_project()
        messages.success(
            self.request, 
            f'Suite de experimentos "{form.instance.name}" creado exitosamente.'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirect to project detail page after successful creation."""
        return reverse('projects:project_detail', kwargs={'pk': self.get_project().pk})


class ExperimentSuiteDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for analyzing ExperimentSuite results and child experiments.
    """
    model = ExperimentSuite
    template_name = 'experiments/suite_detail.html'
    context_object_name = 'suite'
    
    def get_object(self):
        """Get the suite and verify ownership through project."""
        return get_object_or_404(
            ExperimentSuite,
            id=self.kwargs['pk'],
            project__owner=self.request.user
        )
    
    def get_context_data(self, **kwargs):
        """Add child experiments and analysis data to context."""
        context = super().get_context_data(**kwargs)
        suite = self.object
        
        # Get all child experiments
        child_experiments = suite.experiments.all().order_by('-created_at')
        
        # Separate experiments by status for analysis
        completed_experiments = child_experiments.filter(status='FINISHED')
        
        # Prepare experiment data for the results table
        experiment_data = []
        hyperparameter_keys = set()
        
        for exp in child_experiments:
            # Extract hyperparameters for table columns
            hyperparams = exp.hyperparameters or {}
            hyperparameter_keys.update(hyperparams.keys())
            
            # Extract performance metrics
            performance_metrics = {}
            if exp.results and 'performance_metrics' in exp.results:
                performance_metrics = exp.results['performance_metrics']
            
            experiment_data.append({
                'experiment': exp,
                'hyperparameters': hyperparams,
                'performance_metrics': performance_metrics,
                'optimization_metric_value': performance_metrics.get(suite.optimization_metric, None)
            })
        
        # Sort experiments by optimization metric for ranking
        optimization_metric = suite.optimization_metric
        lower_is_better_metrics = ['mse', 'mae', 'rmse', 'mean_squared_error', 'mean_absolute_error']
        is_lower_better = any(metric in optimization_metric.lower() for metric in lower_is_better_metrics)
        
        # Sort completed experiments by optimization metric
        completed_data = [data for data in experiment_data if data['experiment'].status == 'FINISHED' and data['optimization_metric_value'] is not None]
        completed_data.sort(
            key=lambda x: x['optimization_metric_value'],
            reverse=not is_lower_better  # reverse=True for "higher is better", False for "lower is better"
        )
        
        # Prepare chart data for top 10 experiments
        chart_data = []
        top_experiments = completed_data[:10]
        for i, data in enumerate(top_experiments):
            chart_data.append({
                'experiment_name': data['experiment'].name,
                'metric_value': data['optimization_metric_value'],
                'rank': i + 1
            })
        
        # Prepare Optuna optimization data for hyperparameter sweep suites
        trial_data_json = None
        param_importances_json = None
        has_optuna_data = False
        
        if (suite.study_type == 'HYPERPARAMETER_SWEEP' and 
            suite.status == 'COMPLETED'):
            
            # Check if we have trial data and parameter importances
            if suite.trial_data:
                trial_data_json = json.dumps(suite.trial_data)
                has_optuna_data = True
                
            if suite.param_importances:
                param_importances_json = json.dumps(suite.param_importances)
                has_optuna_data = True

        # Create breadcrumbs
        breadcrumbs = [
            {'name': 'Proyectos', 'url': reverse('projects:project_list')},
            {'name': suite.project.name, 'url': reverse('projects:project_detail', kwargs={'pk': suite.project.pk})},
            {'name': f'Suite: {suite.name}', 'url': None}
        ]
        
        context.update({
            'child_experiments': child_experiments,
            'completed_experiments': completed_experiments,
            'experiment_data': experiment_data,
            'hyperparameter_keys': sorted(list(hyperparameter_keys)),
            'chart_data': chart_data,
            'chart_data_json': json.dumps(chart_data),
            'optimization_metric': optimization_metric,
            'is_lower_better': is_lower_better,
            'breadcrumbs': breadcrumbs,
            'total_experiments': child_experiments.count(),
            'completed_count': completed_experiments.count(),
            'progress_percentage': suite.get_progress_percentage(),
            # Optuna visualization data
            'trial_data_json': trial_data_json,
            'param_importances_json': param_importances_json,
            'has_optuna_data': has_optuna_data,
        })
        
        return context


@login_required
def ablation_suite_create(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if request.method == 'POST':
        form = AblationSuiteForm(project=project, data=request.POST)
        if form.is_valid():
            suite = form.save(commit=False)
            suite.project = project
            suite.suite_type = ExperimentSuite.SuiteType.ABLATION_STUDY
            suite.status = ExperimentSuite.Status.DRAFT
            suite.save()
            
            # La lógica para crear los experimentos se manejará con una tarea de Celery
            # que llamaremos desde la página de detalle de la suite.
            
            # Redirigir a la página del proyecto por ahora
            return redirect(reverse('projects:project_detail', kwargs={'pk': project.id}))
    else:
        form = AblationSuiteForm(project=project)
        
    context = {
        'form': form,
        'project': project,
        'view_title': 'Crear Nueva Suite de Análisis de Ablación'
    }
    return render(request, 'experiments/ablation_suite_form.html', context)


@login_required
def run_experiment_suite(request, pk):
    """
    Trigger the execution of an ExperimentSuite.
    
    This view validates suite ownership, updates the status to QUEUED,
    and launches the Celery task to execute all child experiments.
    """
    # Get the suite and verify ownership through project
    suite = get_object_or_404(
        ExperimentSuite, 
        id=pk, 
        project__owner=request.user
    )
    
    # Check if suite is in a state that can be executed
    if suite.status not in [ExperimentSuite.Status.DRAFT, ExperimentSuite.Status.FAILED]:
        messages.error(
            request, 
            f'El suite "{suite.name}" no puede ejecutarse en su estado actual: {suite.get_status_display()}'
        )
        return redirect('projects:project_detail', pk=suite.project.pk)
    
    # Check if suite has a valid search space
    if not suite.search_space:
        messages.error(
            request, 
            f'El suite "{suite.name}" no tiene un espacio de búsqueda definido.'
        )
        return redirect('projects:project_detail', pk=suite.project.pk)
    
    # Check if suite has a base experiment
    if not suite.base_experiment:
        messages.error(
            request, 
            f'El suite "{suite.name}" no tiene un experimento base definido.'
        )
        return redirect('projects:project_detail', pk=suite.project.pk)
    
    try:
        # Update suite status to QUEUED
        suite.status = ExperimentSuite.Status.QUEUED
        suite.save(update_fields=['status', 'updated_at'])
        
        # Launch the Celery task
        task_result = run_experiment_suite_task.delay(str(suite.id))
        
        messages.success(
            request, 
            f'Suite "{suite.name}" ha sido puesto en cola para ejecución. '
            f'Se generarán múltiples experimentos basados en el espacio de búsqueda definido.'
        )
        
    except Exception as e:
        # Revert status on error
        suite.status = ExperimentSuite.Status.DRAFT
        suite.save(update_fields=['status', 'updated_at'])
        
        messages.error(
            request, 
            f'Error al iniciar la ejecución del suite "{suite.name}": {str(e)}'
        )
    
    # Redirect back to project detail page
    return redirect('projects:project_detail', pk=suite.project.pk)