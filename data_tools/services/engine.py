import pandas as pd
from projects.models import DataSource, Transformation

def process_datasource_to_df(datasource_id):
    """
    Processes a DataSource into a pandas DataFrame, applying a chain of transformations recursively.
    """
    try:
        datasource = DataSource.objects.get(id=datasource_id)
    except DataSource.DoesNotExist:
        raise ValueError(f"DataSource with id {datasource_id} not found.")

    # --- BASE CASE ---
    if not datasource.is_derived:
        if not datasource.file:
            raise ValueError(f"Original DataSource {datasource_id} has no file.")
        return pd.read_csv(datasource.file.path)

    # --- RECURSIVE CASE ---
    parents = datasource.parents.all()
    if not parents:
        raise ValueError(f"Derived DataSource {datasource_id} has no parents.")

    # Process parent DataSources recursively
    initial_dfs = [process_datasource_to_df(p.id) for p in parents]

    # Apply transformations
    transformations = datasource.transformations.order_by('order')
    current_state = initial_dfs[0] if len(initial_dfs) == 1 else initial_dfs

    for trans in transformations:
        operation = trans.operation_type
        params = trans.parameters

        if operation == 'merge':
            if not isinstance(current_state, list) or len(current_state) < 2:
                raise ValueError("Merge operation requires a list of at least two DataFrames.")
            
            left_df = current_state[0]
            right_df = current_state[1]
            current_state = pd.merge(
                left=left_df,
                right=right_df,
                left_on=params.get('left_on'),
                right_on=params.get('right_on'),
                how=params.get('how', 'outer')
            )
        
        elif not isinstance(current_state, pd.DataFrame):
            raise TypeError(f"Operation '{operation}' requires a single DataFrame, but received a list. A 'merge' step might be missing.")

        elif operation == 'select_columns':
            current_state = current_state[params.get('columns', [])]
        
        elif operation == 'filter_rows':
            column = params.get('column')
            operator = params.get('operator')
            value = params.get('value')
            query_str = f"`{column}` {operator} {value}"
            current_state = current_state.query(query_str)
        
        elif operation == 'add_column_from_formula':
            new_column_name = params.get('new_column_name')
            formula_string = params.get('formula_string')
            if not new_column_name or not formula_string:
                raise ValueError("Both 'new_column_name' and 'formula_string' must be provided for 'add_column_from_formula' operation.")
            current_state[new_column_name] = current_state.eval(formula_string)
        
        else:
            raise NotImplementedError(f"Operation '{operation}' is not implemented.")

    return current_state