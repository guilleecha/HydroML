from django.shortcuts import render, redirect
from django.urls import reverse


def home(request):
    """
    Renderiza la página de bienvenida para usuarios no autenticados.
    Si el usuario ya ha iniciado sesión, lo redirige a su lista de proyectos.
    """
    if request.user.is_authenticated:
        # Si el usuario ya está logueado, lo mandamos a su dashboard.
        return redirect(reverse('projects:project_list'))

    # Si no, le mostramos la página de bienvenida.
    return render(request, 'core/home.html')