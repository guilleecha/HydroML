import pytest
import pandas as pd
from django.contrib.auth.models import User
from projects.models.project import Project
from projects.models.datasource import DataSource, DataSourceType
from data_tools.services import perform_data_fusion
from django.core.files.base import ContentFile

@pytest.mark.django_db
def test_perform_data_fusion_success(tmp_path):
    # Arrange
    user = User.objects.create_user(username='testuser', password='testpass')
    project = Project.objects.create(name='Test Project', owner=user)

    # Crear dos DataFrames de prueba
    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({'A': [1, 2], 'C': [5, 6]})

    # Guardar los DataFrames como archivos CSV en memoria
    file1 = ContentFile(df1.to_csv(index=False))
    file2 = ContentFile(df2.to_csv(index=False))

    ds1 = DataSource.objects.create(
        name='DS1',
        data_type=DataSourceType.ORIGINAL,
        project=project
    )
    ds1.file.save('ds1.csv', file1)
    ds1.save()

    ds2 = DataSource.objects.create(
        name='DS2',
        data_type=DataSourceType.ORIGINAL,
        project=project
    )
    ds2.file.save('ds2.csv', file2)
    ds2.save()

    # Act
    datasources = DataSource.objects.filter(id__in=[ds1.id, ds2.id])
    merge_col = 'A'
    output_name = 'fusion_test'
    nuevo_datasource, error = perform_data_fusion(project, datasources, merge_col, output_name)

    # Assert
    assert error is None
    assert isinstance(nuevo_datasource, DataSource)
    assert nuevo_datasource.data_type == DataSourceType.FUSED
    assert set(nuevo_datasource.parents.all()) == set([ds1, ds2])

    # Verificar el archivo fusionado (Parquet)
    fused_df = pd.read_parquet(nuevo_datasource.file.path)
    assert fused_df.shape[0] == 2  # Dos filas
    assert set(fused_df.columns) == {'A', 'B', 'C'}  # Columnas fusionadas

@pytest.mark.django_db
def test_perform_data_fusion_raises_error_on_missing_column(tmp_path):
    user = User.objects.create_user(username='testuser2', password='testpass')
    project = Project.objects.create(name='Test Project 2', owner=user)

    # DataFrame 1 tiene columna 'A', DataFrame 2 NO tiene columna 'A'
    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    df2 = pd.DataFrame({'X': [1, 2], 'C': [5, 6]})

    file1 = ContentFile(df1.to_csv(index=False))
    file2 = ContentFile(df2.to_csv(index=False))

    ds1 = DataSource.objects.create(
        name='DS1_missing_col',
        data_type=DataSourceType.ORIGINAL,
        project=project
    )
    ds1.file.save('ds1_missing_col.csv', file1)
    ds1.save()

    ds2 = DataSource.objects.create(
        name='DS2_missing_col',
        data_type=DataSourceType.ORIGINAL,
        project=project
    )
    ds2.file.save('ds2_missing_col.csv', file2)
    ds2.save()

    datasources = DataSource.objects.filter(id__in=[ds1.id, ds2.id])
    merge_col = 'A'
    output_name = 'fusion_error_missing_col'

    with pytest.raises(ValueError):
        perform_data_fusion(project, datasources, merge_col, output_name)

@pytest.mark.django_db
def test_perform_data_fusion_raises_error_on_single_source(tmp_path):
    user = User.objects.create_user(username='testuser3', password='testpass')
    project = Project.objects.create(name='Test Project 3', owner=user)

    df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    file1 = ContentFile(df1.to_csv(index=False))

    ds1 = DataSource.objects.create(
        name='DS1_single',
        data_type=DataSourceType.ORIGINAL,
        project=project
    )
    ds1.file.save('ds1_single.csv', file1)
    ds1.save()

    datasources = DataSource.objects.filter(id=ds1.id)
    merge_col = 'A'
    output_name = 'fusion_error_single_source'

    with pytest.raises(Exception):
        perform_data_fusion(project, datasources, merge_col, output_name)