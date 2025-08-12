# experiments/services.py
import pandas as pd
from sklearn.model_selection import train_test_split, TimeSeriesSplit, cross_validate
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
from django.core.files.base import ContentFile
import io
import numpy as np

from projects.models import DataSource, DataSourceType, Project
from .models import MLExperiment

def _create_datasource_from_df(df: pd.DataFrame, project: Project, name: str, description: str, file_name: str, parent_ds: DataSource) -> DataSource:
    """
    Crea un nuevo objeto DataSource a partir de un DataFrame de pandas.
    """
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    file_content = ContentFile(csv_buffer.getvalue().encode('utf-8'))

    new_ds = DataSource.objects.create(
        project=project,
        name=name,
        description=description,
        data_type=DataSourceType.PREPARED,
    )
    new_ds.file.save(file_name, file_content)
    new_ds.parents.add(parent_ds)
    return new_ds

def perform_train_test_split(experiment: MLExperiment, test_size=0.2, random_state=42):
    """
    Toma un experimento de ML, lee su datasource de entrada,
    y realiza una división en conjuntos de entrenamiento y prueba.
    Crea dos nuevos DataSources para los conjuntos resultantes.
    """
    try:
        # 1. Leer el datasource de entrada
        input_datasource = experiment.input_datasource
        df = pd.read_csv(input_datasource.file.path, encoding='latin-1')

        # 2. Realizar la división
        X = df.drop(columns=[experiment.target_column])
        y = df[experiment.target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Reconstruir los dataframes con la columna objetivo
        train_df = pd.concat([X_train, y_train], axis=1)
        test_df = pd.concat([X_test, y_test], axis=1)

        # 3. Guardar los nuevos DataFrames como nuevos DataSources usando la función auxiliar
        train_ds = _create_datasource_from_df(
            df=train_df,
            project=experiment.project,
            name=f"{input_datasource.name}_train",
            description=f"Conjunto de entrenamiento para el experimento '{experiment.name}'.",
            file_name=f"train_{experiment.id}.csv",
            parent_ds=input_datasource
        )

        test_ds = _create_datasource_from_df(
            df=test_df,
            project=experiment.project,
            name=f"{input_datasource.name}_test",
            description=f"Conjunto de prueba para el experimento '{experiment.name}'.",
            file_name=f"test_{experiment.id}.csv",
            parent_ds=input_datasource
        )

        # 4. Actualizar el experimento
        if experiment.results is None:
            experiment.results = {}
        experiment.results.update({
            'train_datasource_id': str(train_ds.id),
            'test_datasource_id': str(test_ds.id)
        })
        experiment.save()

        return f"División completada. Creados: {train_ds.name} y {test_ds.name}"

    except Exception as e:
        raise e

def perform_model_training_and_validation(experiment: MLExperiment):
    """
    Entrena y valida un modelo de ML usando validación cruzada.
    """
    try:
        # 1. Leer el datasource de entrenamiento
        train_ds_id = experiment.results['train_datasource_id']
        train_datasource = DataSource.objects.get(id=train_ds_id)
        train_df = pd.read_csv(train_datasource.file.path, encoding='latin-1')

        # 2. Preparar datos
        features = experiment.feature_set
        target = experiment.target_column
        X_train = train_df[features]
        y_train = train_df[target]

        # 3. Instanciar modelo y estrategia de validación
        model = RandomForestRegressor(random_state=42)
        cv_strategy = TimeSeriesSplit(n_splits=5)

        # 4. Realizar validación cruzada
        scoring_metrics = ['neg_root_mean_squared_error', 'r2']
        cv_results = cross_validate(
            model, X_train, y_train, cv=cv_strategy, scoring=scoring_metrics
        )

        # 5. Calcular y devolver resultados
        mean_nse = np.mean(cv_results['test_r2'])
        std_nse = np.std(cv_results['test_r2'])
        mean_rmse = np.mean(cv_results['test_neg_root_mean_squared_error']) * -1

        results = {
            'mean_nse': round(mean_nse, 4),
            'std_nse': round(std_nse, 4),
            'mean_rmse': round(mean_rmse, 4)
        }
        return results

    except Exception as e:
        raise e

def perform_final_evaluation(experiment: MLExperiment):
    """
    Realiza la evaluación final del modelo en el conjunto de prueba (hold-out test).
    """
    try:
        # 1. Leer los DataSources de entrenamiento y prueba
        train_ds_id = experiment.results['train_datasource_id']
        test_ds_id = experiment.results['test_datasource_id']
        train_datasource = DataSource.objects.get(id=train_ds_id)
        test_datasource = DataSource.objects.get(id=test_ds_id)

        # 2. Cargar los datasets
        train_df = pd.read_csv(train_datasource.file.path, encoding='latin-1')
        test_df = pd.read_csv(test_datasource.file.path, encoding='latin-1')

        # 3. Preparar los datos
        features = experiment.feature_set
        target = experiment.target_column
        X_train = train_df[features]
        y_train = train_df[target]
        X_test = test_df[features]
        y_test = test_df[target]

        # 4. Instanciar y entrenar el modelo
        model = RandomForestRegressor(random_state=42)
        model.fit(X_train, y_train)

        # 5. Realizar predicciones
        y_pred = model.predict(X_test)

        # 6. Calcular métricas finales
        final_r2 = r2_score(y_test, y_pred)
        final_rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        results = {
            'final_r2': round(final_r2, 4),
            'final_rmse': round(final_rmse, 4),
        }
        return results

    except Exception as e:
        raise e
