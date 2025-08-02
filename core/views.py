# En core/views.py

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import Project, Dataset
from .pipeline.processor import run_analysis_pipeline

import os
import json
import pandas as pd
import numpy as np


class DatasetUploadView(View):
    template_name = 'core/upload.html'

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
            context = {'project': project}
            return render(request, self.template_name, context)
        except Project.DoesNotExist:
            return redirect('project_list')  # O mostrar un error 404

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
            archivo_subido = request.FILES.get('documento')

            if archivo_subido:
                # Creamos el objeto Dataset
                dataset = Dataset.objects.create(
                    project=project,
                    name=archivo_subido.name,
                    uploaded_file=archivo_subido
                )

                # Redirigimos a la nueva página de preparación para este dataset
                return redirect(f"{reverse('prepare_data')}?dataset_id={dataset.id}")

            # Si no se sube archivo, volvemos a mostrar la página de carga
            context = {'project': project, 'error': 'No se seleccionó ningún archivo.'}
            return render(request, self.template_name, context)

        except Project.DoesNotExist:
            return redirect('project_list')


class ProjectListView(ListView):
    model = Project  # 1. ¿Qué modelo vamos a listar?
    template_name = 'core/project_list.html'  # 2. ¿Qué plantilla usamos?
    context_object_name = 'projects'  # 3. ¿Cómo llamamos a la lista en la plantilla?

class PrepareDataView(View):
    template_name = 'core/prepare_data.html'

    # --- Método para peticiones GET ---
    def get(self, request, *args, **kwargs):
        context = {'all_datasets': Dataset.objects.all()}
        dataset_id = request.GET.get('dataset_id')

        if dataset_id:
            try:
                selected_dataset = Dataset.objects.get(id=dataset_id)
                context['selected_dataset'] = selected_dataset
                file_path = selected_dataset.uploaded_file.path

                df_full = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
                context['columns'] = df_full.columns.tolist()
                df_preview = df_full.head()

                html_preview_table = df_preview.style.format(smart_format).to_html(
                    classes='table table-striped',
                    justify='left',
                    table_id='preview-table',
                    index=False
                )
                context['data_preview_html'] = html_preview_table

            except (Dataset.DoesNotExist, FileNotFoundError) as e:
                context['error'] = f"No se pudo leer el dataset: {e}"

        return render(request, self.template_name, context)

    # --- Método para peticiones POST ---
    def post(self, request, *args, **kwargs):
        try:
            # 1. Recoger datos del formulario
            dataset_id = request.POST.get('dataset_id')
            new_dataset_name = request.POST.get('new_dataset_name')
            removed_columns_json = request.POST.get('removed_columns')
            removed_columns = json.loads(removed_columns_json) if removed_columns_json else []

            # 2. Cargar DataFrame
            original_dataset = Dataset.objects.get(id=dataset_id)
            file_path = original_dataset.uploaded_file.path
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)

            # 3. Aplicar transformaciones
            df_prepared = df.drop(columns=removed_columns, errors='ignore')

            # 4. Crear archivo Parquet
            new_filename = f"{new_dataset_name.replace(' ', '_')}_{original_dataset.id}.parquet"
            new_filepath = os.path.join(settings.MEDIA_ROOT, new_filename)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            df_prepared.to_parquet(new_filepath, index=False)

            # 5. Crear objeto en la base de datos
            Dataset.objects.create(
                project=original_dataset.project,
                name=new_dataset_name,
                uploaded_file=new_filename
            )
            return redirect('project_list')

        except Exception as e:
            print(f"Error al guardar el dataset preparado: {e}")
            return redirect('prepare_data')

def smart_format(val):
    """
    Formatea un valor numérico de forma inteligente para su visualización.
    """
    if pd.isna(val) or not isinstance(val, (int, float, np.number)):
        return val  # Devuelve valores no numéricos o nulos sin cambios

    # Si el número es muy grande o muy pequeño (fuera de este rango), usa notación científica
    if abs(val) > 10000 or (abs(val) < 0.001 and val != 0):
        return f"{val:.3e}"  # Notación científica con 3 decimales

    # Si es un entero, lo dejamos como está
    if float(val).is_integer():
        return f"{int(val)}"

    # Para otros flotantes, usamos 3 decimales
    return f"{val:.3f}"