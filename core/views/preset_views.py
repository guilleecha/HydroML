
"""
Hyperparameter preset management views.
"""
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View
)
from django.contrib import messages
from django.utils.decorators import method_decorator
from core.models import HyperparameterPreset
from core.forms import HyperparameterPresetForm
import json


class PresetListView(LoginRequiredMixin, ListView):
    """
    List all hyperparameter presets for the current user.
    """
    model = HyperparameterPreset
    template_name = 'core/presets/preset_list.html'
    context_object_name = 'presets'
    
    def get_queryset(self):
        return HyperparameterPreset.objects.filter(user=self.request.user)


class PresetDetailView(LoginRequiredMixin, DetailView):
    """
    Display details of a specific hyperparameter preset.
    """
    model = HyperparameterPreset
    template_name = 'core/presets/preset_detail.html'
    context_object_name = 'preset'
    pk_url_kwarg = 'preset_id'
    
    def get_queryset(self):
        return HyperparameterPreset.objects.filter(user=self.request.user)


class PresetCreateView(LoginRequiredMixin, CreateView):
    """
    Create a new hyperparameter preset.
    """
    model = HyperparameterPreset
    form_class = HyperparameterPresetForm
    template_name = 'core/presets/preset_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f'Hyperparameter preset "{form.instance.name}" created successfully!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:preset_detail', kwargs={'preset_id': self.object.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Create Hyperparameter Preset',
            'submit_text': 'Create Preset',
        })
        return context


class PresetUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update an existing hyperparameter preset.
    """
    model = HyperparameterPreset
    form_class = HyperparameterPresetForm
    template_name = 'core/presets/preset_form.html'
    pk_url_kwarg = 'preset_id'
    
    def get_queryset(self):
        return HyperparameterPreset.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f'Hyperparameter preset "{form.instance.name}" updated successfully!'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('core:preset_detail', kwargs={'preset_id': self.object.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': f'Edit "{self.object.name}"',
            'submit_text': 'Update Preset',
        })
        return context


class PresetDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a hyperparameter preset.
    """
    model = HyperparameterPreset
    template_name = 'core/presets/preset_confirm_delete.html'
    context_object_name = 'preset'
    pk_url_kwarg = 'preset_id'
    success_url = reverse_lazy('core:preset_list')
    
    def get_queryset(self):
        return HyperparameterPreset.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        preset_name = self.get_object().name
        response = super().delete(request, *args, **kwargs)
        messages.success(
            request,
            f'Hyperparameter preset "{preset_name}" deleted successfully!'
        )
        return response


class PresetAPIListView(LoginRequiredMixin, View):
    """
    API endpoint to get filtered presets based on model_type.
    Used by the experiment form to populate preset dropdown dynamically.
    """
    
    def get(self, request):
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


class PresetAPIDetailView(LoginRequiredMixin, View):
    """
    API endpoint to get preset hyperparameters as JSON.
    Used by the experiment form to load preset values.
    """
    
    def get(self, request, preset_id):
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


# Legacy function-based views for backward compatibility

@login_required
def preset_list(request):
    """Legacy function-based view - redirects to class-based view."""
    view = PresetListView.as_view()
    return view(request)


@login_required
def preset_detail(request, preset_id):
    """Legacy function-based view - redirects to class-based view."""
    view = PresetDetailView.as_view()
    return view(request, preset_id=preset_id)


@login_required
def preset_create(request):
    """Legacy function-based view - redirects to class-based view."""
    view = PresetCreateView.as_view()
    return view(request)


@login_required
def preset_update(request, preset_id):
    """Legacy function-based view - redirects to class-based view."""
    view = PresetUpdateView.as_view()
    return view(request, preset_id=preset_id)


@login_required
def preset_delete(request, preset_id):
    """Legacy function-based view - redirects to class-based view."""
    view = PresetDeleteView.as_view()
    return view(request, preset_id=preset_id)


@login_required
@require_http_methods(["GET"])
def preset_api_list(request):
    """Legacy function-based view - redirects to class-based view."""
    view = PresetAPIListView.as_view()
    return view(request)


@login_required
@require_http_methods(["GET"])
def preset_api_detail(request, preset_id):
    """Legacy function-based view - redirects to class-based view."""
    view = PresetAPIDetailView.as_view()
    return view(request, preset_id=preset_id)
