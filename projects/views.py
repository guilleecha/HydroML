
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from django.core.files.base import ContentFile

import json
import io
import pandas as pd


from .forms import DataSourceForm, ProjectForm
from .models import Project, DataSource, DataSourceType

def project_list(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects/project_list.html', {'projects': projects})

# Vista para mostrar los detalles de un solo proyecto
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    # Ahora: DataSourceType.ORIGINAL
    original_datasources = project.datasources.filter(
        data_type=DataSourceType.ORIGINAL
    ).order_by('-uploaded_at')

    # El nombre 'data_sources' que usa la plantilla original ya no existe.
    # Lo cambiamos por 'original_datasources' para que coincida.
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'original_datasources': original_datasources
    })
# Vista para crear un nuevo proyecto
@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # --- PASO 3: Asignar el dueño antes de guardar ---
            # Guardamos la instancia en memoria sin enviarla a la BD todavía
            project = form.save(commit=False)
            # Asignamos el usuario actual (disponible en el objeto request)
            project.owner = request.user
            # Ahora sí, guardamos el objeto completo en la base de datos
            project.save()

            return redirect('projects:project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    return render(request, 'projects/create_project.html', {'form': form})

@login_required # Es buena idea proteger también esta vista
def upload_datasource(request, project_id):
    """
    Gestiona la subida de nuevos archivos de fuentes de datos para un proyecto específico.
    """
    # Obtenemos el proyecto al que pertenecerá esta fuente de datos.
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        # Si el método es POST, procesamos el formulario.
        form = DataSourceForm(request.POST, request.FILES)
        if form.is_valid():
            # Si el formulario es válido, guardamos el objeto pero sin confirmarlo en la BD.
            data_source = form.save(commit=False)
            # Asignamos el proyecto actual al objeto.
            data_source.project = project
            # Ahora sí, guardamos el objeto completo en la base de datos.
            data_source.save()
            # Redirigimos al usuario a la página de detalle del proyecto (aún no la creamos).
            # Por ahora, podemos redirigir a una URL temporal o a la misma página.
            return redirect('projects:project_detail', project_id=project.id)
    else:
        # Si el método es GET, creamos una instancia vacía del formulario.
        form = DataSourceForm()

    # Renderizamos la plantilla, pasándole el formulario y el proyecto.
    return render(request, 'projects/upload_datasource.html', {
        'form': form,
        'project': project
    })


def view_datasource(request, pk):
    """
    Lee una muestra de un archivo DataSource y la devuelve en formato JSON.
    Ahora con un mejor manejo de errores.
    """
    data_source = get_object_or_404(DataSource, pk=pk)
    try:
        file_path = data_source.file.path

        df = None
        if file_path.endswith('.csv'):
            # Añadimos un motor de lectura explícito que es bueno con diferentes formatos
            df = pd.read_csv(file_path, nrows=100, engine='python', encoding='latin-1')
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path, nrows=100)
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
            if len(df) > 100:
                df = df.head(100)
        else:
            return JsonResponse({'error': 'Formato de archivo no soportado'}, status=400)

        # Reemplazamos valores NaN (Not a Number) por strings vacíos para evitar errores en JSON
        df = df.fillna('')
        data_json = df.to_json(orient='split', index=False)

        return JsonResponse(json.loads(data_json))

    except Exception as e:
        # Imprimimos el error completo en la terminal para nuestro debug
        print(f"----------- ERROR LEYENDO ARCHIVO -----------")
        print(f"Archivo: {data_source.file.path}")
        print(f"Error: {e}")
        print(f"-------------------------------------------")
        # Devolvemos el mensaje de error específico al frontend
        return JsonResponse({'error': f"Error al leer el archivo: {str(e)}"}, status=500)


def data_viewer_page(request, pk):
    datasource = get_object_or_404(DataSource, pk=pk)
    return render(request, 'projects/data_viewer.html', {'datasource': datasource})


def prepare_datasource_view(request, pk):
    """
    Vista para la herramienta de preparación de datos de un DataSource.
    Maneja la carga inicial (GET) y el procesamiento de tipos y columnas (POST).
    """
    datasource = get_object_or_404(DataSource, pk=pk)

    if request.method == 'POST':
        # --- LÓGICA COMPLETA PARA PROCESAR Y GUARDAR ---
        new_dataset_name = request.POST.get('new_dataset_name', f"{datasource.name} - Preparado")

        # 1. Leemos el dataframe original completo
        df = None
        file_path = datasource.file.path
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='latin-1')
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)

        # 2. Iteramos sobre las selecciones de tipo de dato del formulario
        for key, new_type in request.POST.items():
            if key.startswith('type-'):
                col_name = key.replace('type-', '')
                if col_name in df.columns:
                    original_type = str(df[col_name].dtype)
                    # Solo convertimos si el usuario eligió un tipo diferente
                    if new_type != original_type:
                        try:
                            if 'int' in new_type.lower() or 'float' in new_type.lower():
                                # errors='coerce' es la clave: convierte inválidos en Nulo (NaN)
                                df[col_name] = pd.to_numeric(df[col_name], errors='coerce')
                                df[col_name] = df[col_name].astype(new_type)
                            elif 'datetime' in new_type:
                                df[col_name] = pd.to_datetime(df[col_name], errors='coerce')
                            else:
                                df[col_name] = df[col_name].astype(new_type)
                            print(f"Columna '{col_name}' convertida a '{new_type}'.")
                        except Exception as e:
                            print(f"No se pudo convertir la columna '{col_name}' a '{new_type}': {e}")

        # 3. Eliminamos las columnas marcadas
        removed_columns_str = request.POST.get('removed_columns', '[]')
        removed_columns = json.loads(removed_columns_str)
        if removed_columns:
            df.drop(columns=removed_columns, inplace=True, errors='ignore')
            print(f"Columnas eliminadas: {removed_columns}")

        # 4. Guardamos el nuevo dataframe como un nuevo DataSource en formato Parquet
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, index=False)

        new_datasource = DataSource(
            project=datasource.project,
            name=new_dataset_name,
            description=f"Versión preparada de '{datasource.name}'.",
        )
        new_file = ContentFile(parquet_buffer.getvalue())
        new_datasource.file.save(f'prepared_{datasource.pk}.parquet', new_file)
        new_datasource.save()

        # --- AÑADIMOS ESTA LÍNEA ---
        # Establecemos la relación de linaje: el archivo original es el padre del nuevo
        new_datasource.parents.add(datasource)

        return redirect('projects:project_detail', project_id=datasource.project.id)

    # --- LÓGICA PARA MOSTRAR LA PÁGINA (GET) ---
    try:
        df_head = pd.read_csv(datasource.file.path, nrows=50, encoding='latin-1')

        column_info = {}
        warnings = []  # Lista para guardar los mensajes de advertencia

        for col in df_head.columns:
            dtype_str = str(df_head[col].dtype)
            user_friendly_type = "Texto"
            has_mixed_types = False

            # Lógica de detección de tipos mixtos (tu idea)
            if dtype_str == 'object':
                # Intentamos convertir a número de forma segura
                numeric_col = pd.to_numeric(df_head[col], errors='coerce')
                # Contamos cuántos valores no nulos originales se perdieron
                original_non_nulls = df_head[col].notna().sum()
                new_non_nulls = numeric_col.notna().sum()

                if original_non_nulls > 0 and new_non_nulls < original_non_nulls:
                    has_mixed_types = True
                    bad_values_count = original_non_nulls - new_non_nulls
                    warnings.append(
                        f"En '{col}': Se encontraron {bad_values_count} valores de texto que no son números.")

            # Lógica para el nombre amigable (existente)
            if "int" in dtype_str:
                user_friendly_type = "Número Entero"
            elif "float" in dtype_str:
                user_friendly_type = "Número Decimal"
            elif "datetime" in dtype_str:
                user_friendly_type = "Fecha/Hora"

            column_info[col] = {
                'detected': user_friendly_type,
                'pandas_dtype': dtype_str,
                'has_warning': has_mixed_types  # Pasamos el indicador de advertencia
            }

        table_body_html = \
        df_head.to_html(header=False, classes='table-body-class-placeholder', index=False).split('<tbody>')[1].split(
            '</tbody>')[0]

    except Exception as e:
        column_info = {}
        table_body_html = f"<tr><td colspan='99' class='text-center text-danger'>Error al leer el archivo: {e}</td></tr>"
        warnings = []

    return render(request, 'projects/prepare_data.html', {
        'datasource': datasource,
        'column_info': column_info,
        'table_body_html': table_body_html,
        'warnings': warnings,  # Pasamos las advertencias a la plantilla
    })


class DataSourceDeleteView(DeleteView):
    model = DataSource
    template_name = 'projects/datasource_confirm_delete.html'

    def get_success_url(self):
        # Volvemos al proyecto al que pertenecía el dataset
        project_id = self.object.project.id
        return reverse_lazy('projects:project_detail', kwargs={'project_id': project_id})