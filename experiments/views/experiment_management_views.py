# experiments/views/experiment_management_views.py
"""
Views for managing ML experiments in the HydroML project.

This module provides Django views for the complete lifecycle management of Machine Learning
experiments, including creation, editing, deletion, execution, and publication. The views
handle form processing, task orchestration, and user feedback through the Django messages
framework.

Key Features:
    - CRUD operations for ML experiments
    - Celery task integration for asynchronous ML pipeline execution
    - Permission-based access control ensuring users can only manage their own experiments
    - Status validation and state management throughout experiment lifecycle
    - Comprehensive error handling and user feedback

The views work closely with the MLExperiment model and forms to provide a complete
experiment management interface within the Django framework.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from core.utils.breadcrumbs import create_project_breadcrumbs
import logging
import sentry_sdk

from projects.models import Project
from ..models import MLExperiment
from ..forms import MLExperimentForm, ForkExperimentForm
# Se importan las tareas de Celery
from ..tasks import (
    run_full_experiment_pipeline_task # Importar la nueva tarea orquestadora
)

logger = logging.getLogger(__name__)


@login_required
def ml_experiment_form_partial(request, project_id=None):
    """
    Render the ML experiment form as a partial template for slide-over panel.
    
    This view returns only the form content without the base template,
    designed to be loaded dynamically into slide-over panels via AJAX.
    It also handles form submission for creating new experiments.
    
    Args:
        request (HttpRequest): The Django HTTP request object.
        project_id (int, optional): The ID of the project. If not provided,
                                   will try to extract from GET parameters.
        
    Returns:
        HttpResponse: For GET - rendered partial template with form content only.
                     For POST - JSON response indicating success/failure.
    """
    # Get project_id from URL parameter or GET parameter
    if not project_id:
        project_id = request.GET.get('project_id')
    
    if project_id:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
    else:
        # If no project_id, return an empty form without project context
        project = None
    
    if request.method == 'POST':
        logger.info(f"Processing POST request for experiment creation in slide-over - project {project_id}")
        form = MLExperimentForm(project=project, data=request.POST, user=request.user)
        
        if form.is_valid():
            try:
                # Create experiment object without saving
                experiment = form.save(commit=False)
                experiment.project = project
                experiment.status = MLExperiment.Status.DRAFT
                logger.info(f"Created experiment object: {experiment.name}")
                
                # Build hyperparameters dictionary
                hyperparams = {}
                model_name = form.cleaned_data.get('model_name')
                logger.info(f"Building hyperparameters for model: {model_name}")
                
                if model_name == 'RandomForestRegressor':
                    if form.cleaned_data.get('rf_n_estimators'):
                        hyperparams['n_estimators'] = form.cleaned_data['rf_n_estimators']
                    if form.cleaned_data.get('rf_max_depth'):
                        hyperparams['max_depth'] = form.cleaned_data['rf_max_depth']
                elif model_name == 'GradientBoostingRegressor':
                    if form.cleaned_data.get('gb_n_estimators'):
                        hyperparams['n_estimators'] = form.cleaned_data['gb_n_estimators']
                    if form.cleaned_data.get('gb_learning_rate'):
                        hyperparams['learning_rate'] = form.cleaned_data['gb_learning_rate']
                
                experiment.hyperparameters = hyperparams
                logger.info(f"Set hyperparameters: {hyperparams}")
                
                # Save the experiment
                experiment.save()
                logger.info(f"Successfully saved experiment {experiment.id}: {experiment.name}")
                
                # Return JSON response for AJAX
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True,
                    'message': f"Experimento '{experiment.name}' creado con éxito.",
                    'experiment_id': str(experiment.id),
                    'redirect_url': reverse('projects:project_detail', kwargs={'pk': project.id})
                })
                
            except Exception as e:
                # Enhanced error handling with Sentry context
                with sentry_sdk.configure_scope() as scope:
                    scope.set_tag("error_type", "experiment_save")
                    scope.set_context("experiment_data", {
                        "project_id": project.id if project else None,
                        "model_name": form.cleaned_data.get('model_name', 'unknown'),
                        "user": request.user.username
                    })
                
                logger.error(f"Error saving experiment: {str(e)}", exc_info=True)
                sentry_sdk.capture_exception(e)
                
                return JsonResponse({
                    'success': False,
                    'message': f"Error al guardar el experimento: {str(e)}"
                })
        else:
            # Form validation failed - return errors
            logger.error(f"Form validation failed. Errors: {form.errors}")
            return JsonResponse({
                'success': False,
                'message': 'Por favor, corrige los errores en el formulario.',
                'errors': form.errors
            })
    
    # GET request - render the form
    form = MLExperimentForm(project=project, user=request.user)
    
    context = {
        'form': form,
        'project': project,
    }
    
    return render(request, 'experiments/ml_experiment_form_partial.html', context)


class MLExperimentUpdateView(UpdateView):
    """
    Class-based view for updating existing ML experiments.
    
    This view provides a form-based interface for editing ML experiment properties.
    It inherits from Django's UpdateView and includes custom form initialization
    to pass the project context and generate appropriate form configurations.
    
    The view ensures that only experiment owners can edit their experiments through
    Django's built-in permission system and URL routing constraints.
    
    Attributes:
        model (Model): The MLExperiment model class.
        form_class (Form): The MLExperimentForm class for handling form validation.
        template_name (str): Path to the template used for rendering the form.
    """
    model = MLExperiment
    form_class = MLExperimentForm
    template_name = 'experiments/ml_experiment_edit.html'

    def get_context_data(self, **kwargs):
        """
        Add additional context data to the template.
        
        Args:
            **kwargs: Additional keyword arguments from parent class.
            
        Returns:
            dict: Template context dictionary with view title and project.
        """
        context = super().get_context_data(**kwargs)
        context['view_title'] = f"Editando Experimento: {self.object.name}"
        context['project'] = self.object.project
        return context

    def get_form_kwargs(self):
        """
        Return keyword arguments for instantiating the form.
        
        Extends the parent method to include the project context needed
        for proper form initialization and validation.
        
        Returns:
            dict: Keyword arguments for form instantiation including project.
        """
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.object.project
        return kwargs

    def get_success_url(self):
        """
        Return the URL to redirect to after successful form submission.
        
        Returns:
            str: URL path to the experiment detail view.
        """
        return reverse('experiments:ml_experiment_detail', kwargs={'pk': self.object.pk})


class MLExperimentDeleteView(DeleteView):
    """
    Class-based view for deleting ML experiments.
    
    This view provides a confirmation page and handles the deletion of ML experiments.
    It inherits from Django's DeleteView and includes proper success URL configuration
    to redirect users back to the project detail page after deletion.
    
    The view includes built-in protection against unauthorized deletions through
    Django's URL routing and permission system.
    
    Attributes:
        model (Model): The MLExperiment model class.
        template_name (str): Path to the confirmation template.
    """
    model = MLExperiment
    template_name = 'experiments/ml_experiment_confirm_delete.html'

    def get_success_url(self):
        """
        Return the URL to redirect to after successful deletion.
        
        Returns:
            str: URL path to the project detail view that contained the experiment.
        """
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.pk})

# --- TASK EXECUTION VIEWS ---

@login_required
@require_POST
def run_experiment_view(request, pk):
    """
    Trigger the complete ML experiment pipeline execution.
    
    This view initiates the full experiment pipeline using Celery tasks for
    asynchronous processing. It validates that the experiment is in DRAFT status
    before triggering execution and provides appropriate user feedback.
    
    The view uses the @require_POST decorator to ensure that experiment execution
    can only be triggered via POST requests, providing protection against
    accidental execution via GET requests.
    
    Args:
        request (HttpRequest): The Django HTTP request object.
        pk (str): The primary key (UUID) of the experiment to execute.
        
    Returns:
        HttpResponseRedirect: Redirect to the experiment detail page with
                            success or warning messages.
                            
    Raises:
        Http404: If the experiment doesn't exist or the user doesn't own it.
    """
    experiment = get_object_or_404(MLExperiment, pk=pk, project__owner=request.user)
    
    if experiment.status == MLExperiment.Status.DRAFT:
        # Trigger the Celery task
        run_full_experiment_pipeline_task.delay(str(experiment.id))
        messages.success(request, "El experimento ha sido iniciado con éxito.")
    else:
        messages.warning(request, "El experimento ya ha sido ejecutado o no está en estado borrador.")
        
    return redirect('experiments:ml_experiment_detail', pk=experiment.pk)


@login_required
@require_POST
def trigger_full_experiment_task(request, experiment_id):
    """
    Legacy view for triggering complete experiment pipeline execution.
    
    This view provides backward compatibility for existing URL patterns while
    maintaining the same functionality as run_experiment_view. It triggers
    the full ML experiment pipeline via Celery tasks.
    
    Args:
        request (HttpRequest): The Django HTTP request object.
        experiment_id (str): The ID of the experiment to execute.
        
    Returns:
        HttpResponseRedirect: Redirect to the experiment detail page with
                            success or warning messages.
                            
    Raises:
        Http404: If the experiment doesn't exist or the user doesn't own it.
    """
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)
    
    if experiment.status == MLExperiment.Status.DRAFT:
        run_full_experiment_pipeline_task.delay(experiment.id)
        messages.info(request, "El experimento completo ha sido iniciado. El estado se actualizará automáticamente.")
    else:
        messages.warning(request, "El experimento ya ha sido ejecutado.")
        
    return redirect('experiments:ml_experiment_detail', pk=experiment.id)


@login_required
@require_POST
def trigger_feature_importance_task(request, experiment_id):
    """
    Trigger feature importance analysis for a completed experiment.
    
    This view will initiate feature importance analysis tasks once implemented.
    Currently serves as a placeholder with user notification about future
    availability.
    
    The analysis can only be performed on experiments that have finished
    successfully (FINISHED status), ensuring that a trained model exists
    for feature importance calculation.
    
    Args:
        request (HttpRequest): The Django HTTP request object.
        experiment_id (str): The ID of the experiment to analyze.
        
    Returns:
        HttpResponseRedirect: Redirect to the experiment detail page with
                            informational or warning messages.
                            
    Raises:
        Http404: If the experiment doesn't exist or the user doesn't own it.
        
    Note:
        This feature is currently under development and will be implemented
        in future versions of the system.
    """
    experiment = get_object_or_404(MLExperiment, id=experiment_id, project__owner=request.user)

    if experiment.status == MLExperiment.Status.FINISHED:
        # TODO: Implement feature importance task
        # run_feature_importance_task.delay(experiment.id)
        messages.info(request, "El análisis de importancia de variables estará disponible próximamente.")
    else:
        messages.warning(request, "El análisis solo puede realizarse sobre un experimento finalizado.")

    return redirect('experiments:ml_experiment_detail', pk=experiment.id)

@login_required
@require_POST # Asegura que esta acción solo se pueda realizar con un método POST
def publish_experiment(request, pk):
    """
    Publish an experiment, making it publicly visible and immutable.
    
    This view handles the publication of ML experiments, transitioning them
    from a private draft or finished state to a public, read-only state.
    Published experiments become visible to other users and serve as a
    permanent record of the experiment configuration and results.
    
    The publication process includes:
    - Status validation to ensure the experiment has completed successfully
    - Setting the is_public flag to True
    - Recording the publication timestamp
    - Updating the status to PUBLISHED
    
    Only experiments in FINISHED or ANALYZED status can be published,
    ensuring that incomplete or failed experiments cannot be made public.
    
    Args:
        request (HttpRequest): The Django HTTP request object.
        pk (str): The primary key (UUID) of the experiment to publish.
        
    Returns:
        HttpResponseRedirect: Redirect to the experiment detail page with
                            success or error messages.
                            
    Raises:
        Http404: If the experiment doesn't exist or the user doesn't own it.
    """
    experiment = get_object_or_404(MLExperiment, pk=pk, project__owner=request.user)

    # Validation: Check experiment status for publication eligibility
    if experiment.status not in [MLExperiment.Status.FINISHED, MLExperiment.Status.ANALYZED]:
        messages.error(request, "El experimento no se puede publicar porque no ha finalizado.")
        return redirect('experiments:ml_experiment_detail', pk=experiment.pk)

    # Publication logic
    experiment.is_public = True
    experiment.published_at = timezone.now()
    experiment.status = MLExperiment.Status.PUBLISHED
    experiment.save()

    messages.success(request, f"El experimento '{experiment.name}' ha sido publicado exitosamente.")
    
    return redirect('experiments:ml_experiment_detail', pk=experiment.pk)


@login_required
@require_POST
def register_model_view(request, pk):
    """
    Register the experiment's trained model in MLflow Model Registry.
    
    This view allows users to register their trained models from successful experiments
    into the MLflow Model Registry for production deployment and version management.
    The registered model name is derived from the project and experiment names.
    
    Args:
        request (HttpRequest): The Django HTTP request object.
        pk (str): The primary key (UUID) of the experiment.
        
    Returns:
        HttpResponseRedirect: Redirect to the experiment detail page with
                            success or error messages.
                            
    Raises:
        Http404: If the experiment doesn't exist or the user doesn't own it.
    """
    experiment = get_object_or_404(MLExperiment, pk=pk, project__owner=request.user)
    
    # Check if experiment is finished
    if experiment.status != MLExperiment.Status.FINISHED:
        messages.error(request, "Solo se pueden registrar modelos de experimentos finalizados.")
        return redirect('experiments:ml_experiment_detail', pk=experiment.pk)
    
    # Check if experiment has MLflow run ID
    if not experiment.mlflow_run_id:
        messages.error(request, "Este experimento no tiene un Run ID de MLflow asociado.")
        return redirect('experiments:ml_experiment_detail', pk=experiment.pk)
    
    try:
        # Optimized imports - only import what we need
        from mlflow.tracking import MlflowClient
        import mlflow.models
        import mlflow
        
        # Set MLflow tracking URI
        mlflow.set_tracking_uri("http://mlflow:5000")
        
        # Construct model URI
        model_uri = f"runs:/{experiment.mlflow_run_id}/model"
        
        # Construct model name
        model_name = f"{experiment.project.name}-{experiment.name}".replace(" ", "_")
        
        # Register the model
        registered_model = mlflow.register_model(
            model_uri=model_uri,
            name=model_name
        )
        
        messages.success(
            request, 
            f"Modelo registrado exitosamente como '{model_name}' versión {registered_model.version} en MLflow."
        )
        
        logger.info(f"User {request.user.username} registered model {model_name} from experiment {experiment.id}")
        
    except Exception as e:
        logger.error(f"Error registering model for experiment {experiment.id}: {e}")
        messages.error(
            request, 
            f"Error al registrar el modelo: {str(e)}"
        )
    
    return redirect('experiments:ml_experiment_detail', pk=experiment.pk)


def public_experiment_list_view(request):
    """
    Display a list of publicly available experiments.
    
    This view queries the database for all MLExperiment objects where is_public=True
    and displays them in a card-based grid layout for the community gallery.
    
    Args:
        request (HttpRequest): The Django HTTP request object.
        
    Returns:
        HttpResponse: Rendered template with public experiments.
    """
    # Query for all public experiments, ordered by most recently created
    public_experiments = MLExperiment.objects.filter(
        is_public=True
    ).select_related(
        'project', 
        'project__owner'
    ).order_by('-created_at')
    
    context = {
        'public_experiments': public_experiments,
    }
    
    return render(request, 'experiments/public_experiments_list.html', context)


@login_required
def fork_experiment(request, pk):
    """
    Handle forking of a public experiment to create a personal copy.
    
    This view allows authenticated users to create a personal, editable copy
    of any public experiment. The forked experiment is linked to the original
    via the forked_from field and starts in DRAFT status.
    
    For GET requests: Displays a form asking the user to select one of their
    projects where they want to save the forked experiment.
    
    For POST requests: Creates the fork by copying all relevant settings from
    the original experiment and saving it to the selected project.
    
    Args:
        request (HttpRequest): The Django HTTP request object.
        pk (str): The primary key (UUID) of the experiment to fork.
        
    Returns:
        HttpResponse: For GET - rendered fork form template.
                     For POST - redirect to the new forked experiment detail page.
                     
    Raises:
        Http404: If the experiment doesn't exist or is not public.
    """
    # Get the original experiment - must be public
    original_experiment = get_object_or_404(MLExperiment, pk=pk, is_public=True)
    
    # Prevent users from forking their own experiments
    if original_experiment.project.owner == request.user:
        messages.error(request, "You cannot fork your own experiment.")
        return redirect('experiments:ml_experiment_detail', pk=original_experiment.pk)
    
    if request.method == 'GET':
        # Display the fork form
        form = ForkExperimentForm(user=request.user)
        context = {
            'form': form,
            'original_experiment': original_experiment,
        }
        return render(request, 'experiments/fork_experiment.html', context)
    
    elif request.method == 'POST':
        form = ForkExperimentForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            selected_project = form.cleaned_data['project']
            
            # Create the forked experiment
            forked_experiment = MLExperiment(
                # Copy all relevant fields from the original
                name=f"[Forked] {original_experiment.name}",
                description=original_experiment.description,
                input_datasource=original_experiment.input_datasource,
                target_column=original_experiment.target_column,
                model_name=original_experiment.model_name,
                feature_set=original_experiment.feature_set,
                hyperparameters=original_experiment.hyperparameters,
                test_split_size=original_experiment.test_split_size,
                split_random_state=original_experiment.split_random_state,
                split_strategy=original_experiment.split_strategy,
                
                # Set new experiment specific fields
                project=selected_project,
                status=MLExperiment.Status.DRAFT,
                is_public=False,
                forked_from=original_experiment,
                version=1,  # Start as version 1
            )
            
            try:
                forked_experiment.save()
                messages.success(
                    request, 
                    f"Successfully forked experiment '{original_experiment.name}' to your project '{selected_project.name}'."
                )
                logger.info(f"User {request.user.username} forked experiment {original_experiment.id} to project {selected_project.id}")
                
                return redirect('experiments:ml_experiment_detail', pk=forked_experiment.pk)
                
            except Exception as e:
                logger.error(f"Error forking experiment {original_experiment.id}: {e}")
                messages.error(request, "An error occurred while forking the experiment. Please try again.")
                
        # If form is invalid, redisplay with errors
        context = {
            'form': form,
            'original_experiment': original_experiment,
        }
        return render(request, 'experiments/fork_experiment.html', context)

@login_required
def promote_to_preset_view(request, pk):
    """
    Promote an experiment's hyperparameters to a reusable preset.
    
    This view allows users to create a HyperparameterPreset from a completed
    experiment's hyperparameters. The view pre-fills the preset creation form
    with the experiment's data for easy customization.
    
    Args:
        request: Django HTTP request object
        pk: UUID of the MLExperiment to promote
        
    Returns:
        HttpResponse: Redirects to preset creation form with pre-filled data
        
    Raises:
        Http404: If experiment doesn't exist or user doesn't have permission
    """
    from core.forms import HyperparameterPresetForm
    from core.models import HyperparameterPreset
    from django.urls import reverse
    import json
    
    # Get the experiment and verify permissions
    experiment = get_object_or_404(MLExperiment, pk=pk, user=request.user)
    
    # Validate experiment can be promoted
    if experiment.status != 'FINISHED':
        messages.error(request, "Only completed experiments can be promoted to presets.")
        return redirect('experiments:ml_experiment_detail', pk=pk)
    
    if not experiment.hyperparameters:
        messages.error(request, "This experiment has no hyperparameters to promote.")
        return redirect('experiments:ml_experiment_detail', pk=pk)
    
    # Handle POST request (form submission)
    if request.method == 'POST':
        form = HyperparameterPresetForm(request.POST, user=request.user)
        if form.is_valid():
            preset = form.save(commit=False)
            preset.user = request.user
            preset.save()
            
            messages.success(
                request, 
                f"Successfully created preset '{preset.name}' from experiment '{experiment.name}'."
            )
            logger.info(f"User {request.user.username} promoted experiment {experiment.id} to preset {preset.id}")
            
            return redirect('core:hyperparameter_preset_list')
        else:
            # If form has errors, we'll re-render with the form
            pass
    else:
        # Pre-fill form with experiment data
        initial_data = {
            'name': f"Preset from {experiment.name}",
            'description': f"Hyperparameter preset created from experiment '{experiment.name}' "
                          f"({experiment.model_type}) completed on {experiment.updated_at.strftime('%Y-%m-%d')}.",
            'model_type': experiment.model_type,
            'hyperparameters': json.dumps(experiment.hyperparameters, indent=2)
        }
        form = HyperparameterPresetForm(initial=initial_data, user=request.user)
    
    # Build breadcrumbs
    breadcrumbs = []
    if experiment.project:
        breadcrumbs = create_project_breadcrumbs(experiment.project)
        breadcrumbs.append({
            'url': reverse('experiments:ml_experiment_detail', kwargs={'pk': experiment.pk}),
            'title': experiment.name
        })
    breadcrumbs.append({
        'url': None,
        'title': 'Crear Preset'
    })
    
    context = {
        'form': form,
        'experiment': experiment,
        'breadcrumbs': breadcrumbs,
        'page_title': f'Crear Preset desde "{experiment.name}"'
    }
    
    return render(request, 'experiments/promote_to_preset.html', context)