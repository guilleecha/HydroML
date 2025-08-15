# projects/views/datasource_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from ..models import Project, DataSource
from ..forms.datasource_forms import DataSourceUpdateForm, DataSourceUploadForm
from data_tools.tasks import convert_file_to_parquet_task
from django.http import JsonResponse


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
    return render(request, 'projects/datasource_upload_form.html', context)


class DataSourceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para editar una fuente de datos.
    """
    model = DataSource
    form_class = DataSourceUpdateForm
    template_name = 'projects/datasource_form.html'

    def get_queryset(self):
        # Security: ensure users can only edit their own datasources
        return super().get_queryset().filter(project__owner=self.request.user)

    def get_success_url(self):
        # After editing, return to the project detail page
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.pk})


class DataSourceDeleteView(LoginRequiredMixin, DeleteView):
    """
    Vista para confirmar y eliminar una fuente de datos.
    """
    model = DataSource
    template_name = 'projects/datasource_confirm_delete.html'

    def get_queryset(self):
        # Esta medida de seguridad ya estaba correcta.
        return super().get_queryset().filter(project__owner=self.request.user)

    def get_success_url(self):
        # Después de eliminar, volvemos a la página del proyecto.
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.project.pk})


@login_required
def datasource_upload_summary(request, datasource_id):
    """
    Page shown immediately after upload; it polls the datasource status and
    displays a quality report once processing finishes.
    """
    datasource = get_object_or_404(DataSource, id=datasource_id, project__owner=request.user)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # return JSON status for polling
        return JsonResponse({
            'status': datasource.status,
            'quality_report': datasource.quality_report,
        })

    return render(request, 'projects/datasource_upload_summary.html', {'datasource': datasource})