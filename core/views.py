from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Count
from django.contrib import messages
from projects.models import DataSource, Project
from experiments.models import MLExperiment, ExperimentSuite
from .models import HyperparameterPreset
from .forms import HyperparameterPresetForm
# from core.models import Notification
import json


def home(request):
    """
    Renderiza la página de bienvenida para usuarios no autenticados.
    Si el usuario ya ha iniciado sesión, lo redirige a su dashboard.
    """
    if request.user.is_authenticated:
        # Si el usuario ya está logueado, lo mandamos a su dashboard.
        return redirect(reverse('core:dashboard'))

    # Si no, le mostramos la página de bienvenida.
    return render(request, 'core/home.html')


@login_required
def dashboard_view(request):
    """
    Dashboard principal para usuarios autenticados.
    Proporciona una visión general de su workspace con estadísticas clave y actividad reciente.
    """
    user = request.user
    
    # Obtener todos los proyectos del usuario para las consultas
    user_projects = Project.objects.filter(owner=user)
    
    # Calcular estadísticas
    total_datasources = DataSource.objects.filter(project__owner=user).count()
    total_experiments = MLExperiment.objects.filter(project__owner=user).count()
    total_suites = ExperimentSuite.objects.filter(project__owner=user).count()
    
    # Obtener los 10 experimentos más recientes
    recent_experiments = MLExperiment.objects.filter(
        project__owner=user
    ).select_related('project').order_by('-created_at')[:10]
    
    # Get featured public experiments (last 3)
    featured_public_experiments = MLExperiment.objects.filter(
        is_public=True
    ).select_related(
        'project', 
        'project__owner'
    ).order_by('-created_at')[:3]
    
    context = {
        'total_datasources': total_datasources,
        'total_experiments': total_experiments,
        'total_suites': total_suites,
        'recent_experiments': recent_experiments,
        'user_projects_count': user_projects.count(),
        'featured_public_experiments': featured_public_experiments,
    }
    
    return render(request, 'core/dashboard.html', context)


def help_page(request):
    """
    Renders the help/FAQ page with common questions and answers about HydroML.
    """
    return render(request, 'core/help_page.html')


# Notification views commented out until Notification model is implemented
# @method_decorator([login_required, csrf_exempt], name='dispatch')
# class NotificationAPIView(View):
#     """
#     API view for handling user notifications.
#     """
#     
#     def get(self, request):
#         """
#         Get unread notifications for the current user.
#         
#         Returns:
#             JsonResponse: List of unread notifications with id, message, timestamp, and link.
#         """
#         try:
#             notifications = Notification.objects.filter(
#                 user=request.user,
#                 is_read=False
#             ).order_by('-timestamp')[:20]  # Limit to 20 most recent
#             
#             notifications_data = []
#             for notification in notifications:
#                 notifications_data.append({
#                     'id': notification.id,
#                     'message': notification.message,
#                     'timestamp': notification.timestamp.isoformat(),
#                     'link': notification.link,
#                     'notification_type': notification.notification_type,
#                     'time_ago': self._time_ago(notification.timestamp)
#                 })
#             
#             return JsonResponse({
#                 'status': 'success',
#                 'notifications': notifications_data,
#                 'unread_count': len(notifications_data)
#             })
#             
#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=500)
#     
#     def post(self, request):
#         """
#         Mark a notification as read.
#         
#         Expects:
#             JSON body with 'notification_id' field.
#             
#         Returns:
#             JsonResponse: Success/error status.
#         """
#         try:
#             data = json.loads(request.body)
#             notification_id = data.get('notification_id')
#             
#             if not notification_id:
#                 return JsonResponse({
#                     'status': 'error',
#                     'message': 'notification_id is required'
#                 }, status=400)
#             
#             notification = Notification.objects.get(
#                 id=notification_id,
#                 user=request.user
#             )
#             
#             notification.mark_as_read()
#             
#             return JsonResponse({
#                 'status': 'success',
#                 'message': 'Notification marked as read'
#             })
#             
#         except Notification.DoesNotExist:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'Notification not found'
#             }, status=404)
#         except json.JSONDecodeError:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'Invalid JSON'
#             }, status=400)
#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=500)
#     
#     def delete(self, request):
#         """
#         Mark all notifications as read for the current user.
#         
#         Returns:
#             JsonResponse: Success status with count of marked notifications.
#         """
#         try:
#             updated_count = Notification.objects.filter(
#                 user=request.user,
#                 is_read=False
#             ).update(is_read=True)
#             
#             return JsonResponse({
#                 'status': 'success',
#                 'message': f'Marked {updated_count} notifications as read'
#             })
#             
#         except Exception as e:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': str(e)
#             }, status=500)
#     
#     def _time_ago(self, timestamp):
#         """
#         Calculate human-readable time difference.
#         
#         Args:
#             timestamp: Django datetime object
#             
#         Returns:
#             str: Human-readable time difference (e.g., "2 minutes ago")
#         """
#         from django.utils import timezone
#         
#         now = timezone.now()
#         diff = now - timestamp
#         
#         if diff.days > 0:
#             return f"{diff.days} día{'s' if diff.days != 1 else ''} atrás"
#         elif diff.seconds > 3600:
#             hours = diff.seconds // 3600
#             return f"{hours} hora{'s' if hours != 1 else ''} atrás"
#         elif diff.seconds > 60:
#             minutes = diff.seconds // 60
#             return f"{minutes} minuto{'s' if minutes != 1 else ''} atrás"
#         else:
#             return "Ahora mismo"


# @login_required
# @require_http_methods(["GET"])
# def get_unread_count(request):
#     """
#     Get the count of unread notifications for the current user.
#     
#     Returns:
#         JsonResponse: Unread notification count.
#     """
#     try:
#         unread_count = Notification.objects.filter(
#             user=request.user,
#             is_read=False
#         ).count()
#         
#         return JsonResponse({
#             'status': 'success',
#             'unread_count': unread_count
#         })
#         
#     except Exception as e:
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=500)


# ===== HYPERPARAMETER PRESETS VIEWS =====

@login_required
def preset_list(request):
    """
    List all hyperparameter presets for the current user.
    """
    presets = HyperparameterPreset.objects.filter(user=request.user)
    
    context = {
        'presets': presets,
    }
    
    return render(request, 'core/presets/preset_list.html', context)


@login_required
def preset_detail(request, preset_id):
    """
    Display details of a specific hyperparameter preset.
    """
    preset = get_object_or_404(
        HyperparameterPreset,
        id=preset_id,
        user=request.user
    )
    
    context = {
        'preset': preset,
    }
    
    return render(request, 'core/presets/preset_detail.html', context)


@login_required
def preset_create(request):
    """
    Create a new hyperparameter preset.
    """
    if request.method == 'POST':
        form = HyperparameterPresetForm(request.POST, user=request.user)
        if form.is_valid():
            preset = form.save()
            messages.success(
                request,
                f'Hyperparameter preset "{preset.name}" created successfully!'
            )
            return redirect('core:preset_detail', preset_id=preset.id)
    else:
        form = HyperparameterPresetForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create Hyperparameter Preset',
        'submit_text': 'Create Preset',
    }
    
    return render(request, 'core/presets/preset_form.html', context)


@login_required
def preset_update(request, preset_id):
    """
    Update an existing hyperparameter preset.
    """
    preset = get_object_or_404(
        HyperparameterPreset,
        id=preset_id,
        user=request.user
    )
    
    if request.method == 'POST':
        form = HyperparameterPresetForm(
            request.POST,
            instance=preset,
            user=request.user
        )
        if form.is_valid():
            preset = form.save()
            messages.success(
                request,
                f'Hyperparameter preset "{preset.name}" updated successfully!'
            )
            return redirect('core:preset_detail', preset_id=preset.id)
    else:
        form = HyperparameterPresetForm(instance=preset, user=request.user)
    
    context = {
        'form': form,
        'preset': preset,
        'title': f'Edit "{preset.name}"',
        'submit_text': 'Update Preset',
    }
    
    return render(request, 'core/presets/preset_form.html', context)


@login_required
def preset_delete(request, preset_id):
    """
    Delete a hyperparameter preset.
    """
    preset = get_object_or_404(
        HyperparameterPreset,
        id=preset_id,
        user=request.user
    )
    
    if request.method == 'POST':
        preset_name = preset.name
        preset.delete()
        messages.success(
            request,
            f'Hyperparameter preset "{preset_name}" deleted successfully!'
        )
        return redirect('core:preset_list')
    
    context = {
        'preset': preset,
    }
    
    return render(request, 'core/presets/preset_confirm_delete.html', context)


@login_required
@require_http_methods(["GET"])
def preset_api_list(request):
    """
    API endpoint to get filtered presets based on model_type.
    Used by the experiment form to populate preset dropdown dynamically.
    """
    model_type = request.GET.get('model_type')
    
    if not model_type:
        return JsonResponse({
            'status': 'error',
            'message': 'model_type parameter is required'
        }, status=400)
    
    try:
        presets = HyperparameterPreset.objects.filter(
            user=request.user,
            model_type=model_type
        ).values('id', 'name', 'description')
        
        return JsonResponse({
            'status': 'success',
            'presets': list(presets)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def preset_api_detail(request, preset_id):
    """
    API endpoint to get preset hyperparameters as JSON.
    Used by the experiment form to load preset values.
    """
    try:
        preset = get_object_or_404(
            HyperparameterPreset,
            id=preset_id,
            user=request.user
        )
        
        return JsonResponse({
            'status': 'success',
            'preset': {
                'id': preset.id,
                'name': preset.name,
                'description': preset.description,
                'hyperparameters': preset.hyperparameters,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)