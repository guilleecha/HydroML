from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import SignUpForm, UserProfileForm


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')


class SettingsView(LoginRequiredMixin, View):
    """Settings page with multiple sections."""
    
    def get(self, request, section='profile'):
        """Handle GET requests for settings page."""
        context = {
            'current_section': section,
            'user': request.user,
        }
        
        if section == 'profile':
            context['profile_form'] = UserProfileForm(instance=request.user)
        
        return render(request, 'accounts/settings.html', context)
    
    def post(self, request, section='profile'):
        """Handle POST requests for settings updates."""
        if section == 'profile':
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('accounts:settings_section', section='profile')
            else:
                messages.error(request, 'Please correct the errors below.')
                context = {
                    'current_section': section,
                    'profile_form': form,
                    'user': request.user,
                }
                return render(request, 'accounts/settings.html', context)
        
        return redirect('accounts:settings')
