from django.shortcuts import redirect
from django.contrib import messages

def advanced_user_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.subscription_level != 'ADVANCED':
            messages.error(request, "Esta funcionalidad está disponible solo para usuarios Advanced.")
            return redirect('home')  # Redirige a la página principal o a una página de mejora de plan
        return view_func(request, *args, **kwargs)
    return _wrapped_view