# projects/views/datasource_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from ..models import Project, DataSource
from ..forms import DataSourceUploadForm  # Crearemos este formulario en el siguiente paso


@login_required
def datasource_upload(request, project_id):
    """
    Gestiona la subida de un nuevo archivo DataSource a un proyecto.
    """
    project = get_object_or_404(Project, id=project_id, user=request.user)
    if request.method == 'POST':
        form = DataSourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            datasource = form.save(commit=False)
            datasource.project = project
            # Por defecto, un archivo subido es de tipo ORIGINAL
            # El modelo ya lo define, así que no hace falta especificarlo aquí.
            datasource.save()
            return redirect('projects:project_detail', pk=project.id)
    else:
        form = DataSourceUploadForm()

    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'projects/datasource_upload_form.html', context)


class DataSourceDeleteView(DeleteView):
    """
    Vista para confirmar y eliminar una fuente de datos.
    """
    model = DataSource
    template_name = 'projects/datasource_confirm_delete.html'

    def get_queryset(self):
        # Medida de seguridad: solo permite eliminar datasets del usuario logueado.
        return super().get_queryset().filter(project__user=self.request.user)

    def get_success_url(self):
        # Después de eliminar, volvemos a la página del proyecto.
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.pk})