# En core/pipeline/processor.py
import pandas as pd

def run_analysis_pipeline(file_path):
    """
    Toma la ruta de un archivo, lo lee con pandas y devuelve un
    diccionario con un resumen básico.
    """
    print(f"Pipeline iniciado. Procesando archivo: {file_path}")

    try:
        # Intentar leer el archivo, ya sea CSV o Excel
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            # Si el formato no es soportado, devolvemos un error.
            return {'error': 'Formato de archivo no soportado. Usar .csv o .xlsx'}

        # --- Aquí, en el futuro, irían todos los pasos del pipeline ---
        # 1. Fusión con datos de lluvia y cuenca.
        # 2. Filtrado inteligente.
        # 3. Entrenamiento del modelo.
        # 4. Generación de gráficos y resultados.
        # -------------------------------------------------------------

        # Por ahora, solo devolvemos un resumen simple para probar la conexión.
        results = {
            'file_name': file_path.split('/')[-1],
            'num_rows': len(df),
            'num_cols': len(df.columns),
            'columns': list(df.columns),
            'data_head': df.head().to_html(classes='table table-striped', justify='left'),
        }

        print("Pipeline completado exitosamente.")
        return results

    except Exception as e:
        # Si algo falla durante la lectura o procesamiento, capturamos el error.
        print(f"Error en el pipeline: {e}")
        return {'error': str(e)}