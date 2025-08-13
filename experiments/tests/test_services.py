import pytest
import pandas as pd
from django.contrib.auth.models import User
from projects.models.project import Project
from projects.models.datasource import DataSource, DataSourceType
from experiments.models import MLExperiment
from experiments.services import perform_train_test_split, perform_model_training_and_validation, perform_final_evaluation, calculate_feature_importance
from django.core.files.base import ContentFile

@pytest.mark.django_db
def test_perform_train_test_split_success(tmp_path):
    # Arrange
    user = User.objects.create_user(username='splituser', password='splitpass')
    project = Project.objects.create(name='Split Project', owner=user)

    # DataFrame de prueba
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [10, 20, 30, 40, 50],
        'target': [0, 1, 0, 1, 0]
    })
    file = ContentFile(df.to_csv(index=False))

    ds = DataSource.objects.create(
        name='OriginalDS',
        data_type=DataSourceType.ORIGINAL,
        project=project
    )
    ds.file.save('original.csv', file)
    ds.save()

    experiment = MLExperiment.objects.create(
        project=project,
        input_datasource=ds,
        target_column='target',
        feature_set=['feature1', 'feature2']  # Debe ser una lista, no string
    )

    # Act
    perform_train_test_split(experiment)

    # Recargar el experimento para obtener los cambios en results
    experiment.refresh_from_db()
    results = experiment.results

    # Obtener los nuevos DataSource usando los IDs guardados en results
    train_ds = DataSource.objects.get(id=results['train_datasource_id'])
    test_ds = DataSource.objects.get(id=results['test_datasource_id'])

    # Assert
    assert train_ds is not None
    assert test_ds is not None
    assert ds in train_ds.parents.all()
    assert ds in test_ds.parents.all()

    df_original = pd.read_csv(ds.file.path)
    df_train = pd.read_csv(train_ds.file.path)
    df_test = pd.read_csv(test_ds.file.path)
    assert df_train.shape[1] == df_original.shape[1]
    assert df_test.shape[1] == df_original.shape[1]
    assert df_train.shape[0] + df_test.shape[0] == df_original.shape[0]

    # Verifica que los IDs estén en experiment.results
    assert 'train_datasource_id' in results
    assert 'test_datasource_id' in results
    assert results['train_datasource_id'] == str(train_ds.id)
    assert results['test_datasource_id'] == str(test_ds.id)

@pytest.mark.django_db
def test_perform_model_training_and_validation_success(tmp_path):
    # Arrange
    user = User.objects.create_user(username='modeluser', password='modelpass')
    project = Project.objects.create(name='Model Project', owner=user)

    # DataFrame de entrenamiento simulado
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [10, 20, 30, 40, 50],
        'target': [0.1, 0.2, 0.3, 0.4, 0.5]
    })
    file = ContentFile(df.to_csv(index=False))

    train_ds = DataSource.objects.create(
        name='TrainDS',
        data_type=DataSourceType.PREPARED,
        project=project
    )
    train_ds.file.save('train.csv', file)
    train_ds.save()

    experiment = MLExperiment.objects.create(
        project=project,
        input_datasource=train_ds,
        target_column='target',
        feature_set=['feature1', 'feature2'],
        model_name='RandomForestRegressor',
        results={'train_datasource_id': str(train_ds.id)}
    )

    # Act
    result = perform_model_training_and_validation(experiment)

    # Assert
    assert result is not None
    assert 'mean_nse' in result
    assert 'mean_rmse' in result
    assert isinstance(result['mean_nse'], float)
    assert isinstance(result['mean_rmse'], float)

@pytest.mark.django_db
def test_perform_final_evaluation_success(tmp_path):
    # Arrange
    user = User.objects.create_user(username='evaluser', password='evalpass')
    project = Project.objects.create(name='Eval Project', owner=user)

    # DataFrames de entrenamiento y prueba
    df_train = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [10, 20, 30, 40, 50],
        'target': [0.1, 0.2, 0.3, 0.4, 0.5]
    })
    df_test = pd.DataFrame({
        'feature1': [6, 7],
        'feature2': [60, 70],
        'target': [0.6, 0.7]
    })
    file_train = ContentFile(df_train.to_csv(index=False))
    file_test = ContentFile(df_test.to_csv(index=False))

    train_ds = DataSource.objects.create(
        name='TrainDS_eval',
        data_type=DataSourceType.PREPARED,
        project=project
    )
    train_ds.file.save('train_eval.csv', file_train)
    train_ds.save()

    test_ds = DataSource.objects.create(
        name='TestDS_eval',
        data_type=DataSourceType.PREPARED,
        project=project
    )
    test_ds.file.save('test_eval.csv', file_test)
    test_ds.save()

    experiment = MLExperiment.objects.create(
        project=project,
        input_datasource=train_ds,
        target_column='target',
        feature_set=['feature1', 'feature2'],
        model_name='RandomForestRegressor',
        results={
            'train_datasource_id': str(train_ds.id),
            'test_datasource_id': str(test_ds.id)
        }
    )

    # Act
    result = perform_final_evaluation(experiment)

    # Assert
    assert isinstance(result, dict)
    assert 'final_r2' in result
    assert 'final_rmse' in result
    assert isinstance(result['final_r2'], float)
    assert isinstance(result['final_rmse'], float)

@pytest.mark.django_db
def test_calculate_feature_importance_success(tmp_path):
    # Arrange
    user = User.objects.create_user(username='impuser', password='imppass')
    project = Project.objects.create(name='Imp Project', owner=user)

    df_train = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [10, 20, 30, 40, 50],
        'target': [0.1, 0.2, 0.3, 0.4, 0.5]
    })
    df_test = pd.DataFrame({
        'feature1': [6, 7],
        'feature2': [60, 70],
        'target': [0.6, 0.7]
    })
    file_train = ContentFile(df_train.to_csv(index=False))
    file_test = ContentFile(df_test.to_csv(index=False))

    train_ds = DataSource.objects.create(
        name='TrainDS_imp',
        data_type=DataSourceType.PREPARED,
        project=project
    )
    train_ds.file.save('train_imp.csv', file_train)
    train_ds.save()

    test_ds = DataSource.objects.create(
        name='TestDS_imp',
        data_type=DataSourceType.PREPARED,
        project=project
    )
    test_ds.file.save('test_imp.csv', file_test)
    test_ds.save()

    experiment = MLExperiment.objects.create(
        project=project,
        input_datasource=train_ds,
        target_column='target',
        feature_set=['feature1', 'feature2'],
        model_name='RandomForestRegressor',
        results={
            'train_datasource_id': str(train_ds.id),
            'test_datasource_id': str(test_ds.id)
        }
    )

    # Act
    result = calculate_feature_importance(experiment)

    # Assert
    assert isinstance(result, list)
    assert len(result) > 0
    for item in result:
        assert isinstance(item, dict)
        assert 'feature' in item
        assert 'importance' in item
        assert isinstance(item['feature'], str)
        assert isinstance(item['importance'], float)
    # Verifica que la lista esté ordenada de forma descendente por importancia
    importances = [item['importance'] for item in result]
    assert importances == sorted(importances, reverse=True)