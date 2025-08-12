# data_tools/views/fusion_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from projects.models import Project
from ..forms import DataFusionForm
from .. import services # <-- Importamos nuestro nuevo archivo de servicios

@login_required
def data_fusion_page(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)

    if request.method == 'POST':
        form = DataFusionForm(project, request.POST)
        if form.is_valid():
            # La vista ahora solo coordina. Pasa la orden a la cocina (el servicio).
            new_datasource, error = services.perform_data_fusion(
                project=project,
                datasources=form.cleaned_data['datasources_to_merge'],
                merge_col=form.cleaned_data['merge_column'],
                output_name=form.cleaned_data['output_name']
            )

            # La vista gestiona la respuesta al usuario.
            if error:
                messages.error(request, f"Ocurrió un error durante la fusión: {error}")
            else:
                messages.success(request, f"Fusión completada. Se ha creado el dataset '{new_datasource.name}'.")
                return redirect('projects:project_detail', pk=project.id)
    else:
        form = DataFusionForm(project)

    context = {'form': form, 'project': project}
    return render(request, 'data_tools/data_fusion_form.html', context)