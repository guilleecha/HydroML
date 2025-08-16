# data_tools/views/fusion_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from projects.models import Project
from ..forms import DataFusionForm, DataFusionSelectionForm
from .. import services # <-- Importamos nuestro nuevo archivo de servicios

@login_required
def data_fusion_page(request, pk):
    """
    Vista para la fusión de datos - Primera etapa: selección de fuentes de datos
    """
    project = get_object_or_404(Project, id=pk, owner=request.user)

    if request.method == 'POST':
        form = DataFusionSelectionForm(project, request.POST)
        if form.is_valid():
            # TODO: Redirigir a la siguiente etapa (selección de columnas)
            # Por ahora, simplemente mostramos un mensaje de éxito
            datasource_a = form.cleaned_data['datasource_a']
            datasource_b = form.cleaned_data['datasource_b']
            
            messages.success(
                request, 
                f"Fuentes seleccionadas: '{datasource_a.name}' y '{datasource_b.name}'. "
                "Próximamente: selección de columnas para fusionar."
            )
            # En el futuro, esto redirigirá a la página de configuración de columnas
            # return redirect('data_tools:data_fusion_columns', pk=project.pk, 
            #                datasource_a_id=datasource_a.pk, datasource_b_id=datasource_b.pk)
    else:
        form = DataFusionSelectionForm(project)

    context = {
        'form': form, 
        'project': project,
        'title': 'Fusionar Fuentes de Datos',
        'breadcrumbs': [
            {'name': 'Workspace', 'url': 'projects:project_list'},
            {'name': project.name, 'url': 'projects:project_detail', 'args': [project.pk]},
            {'name': 'Fusionar Datos', 'url': None}
        ]
    }
    return render(request, 'data_tools/data_fusion.html', context)


@login_required 
def data_fusion_legacy_page(request, project_id):
    """
    Vista legacy para la fusión de datos con el flujo completo original
    """
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