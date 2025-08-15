from projects.models import DataSource, Transformation

def create_fusion_recipe(project, left_datasource, right_datasource, left_on_col, right_on_col, output_name):
    """
    Creates a new recipe-based fusion DataSource.

    Args:
        project (Project): The project to which the new DataSource belongs.
        left_datasource (DataSource): The left parent DataSource.
        right_datasource (DataSource): The right parent DataSource.
        left_on_col (str): The column to join on from the left DataSource.
        right_on_col (str): The column to join on from the right DataSource.
        output_name (str): The name of the resulting DataSource.

    Returns:
        DataSource: The newly created DataSource.
    """
    try:
        # Step 1: Create a new derived DataSource
        new_datasource = DataSource.objects.create(
            project=project,
            name=output_name,
            description=f"Fusion of {left_datasource.name} and {right_datasource.name}",
            is_derived=True
        )

        # Step 2: Set the parents of the new DataSource
        new_datasource.parents.set([left_datasource, right_datasource])

        # Step 3: Create a 'merge' Transformation for the new DataSource
        Transformation.objects.create(
            derived_datasource=new_datasource,
            order=1,
            operation_type='merge',
            parameters={
                'left_on': left_on_col,
                'right_on': right_on_col,
                'how': 'outer'
            }
        )

        # Step 4: Return the new DataSource
        return new_datasource
    except Exception as e:
        raise ValueError(f"Error creating fusion recipe: {str(e)}")

def create_feature_engineering_recipe(parent_datasource, new_column_name, formula_string):
    """
    Creates a new recipe-based feature engineering DataSource.

    Args:
        parent_datasource (DataSource): The parent DataSource.
        new_column_name (str): The name of the new column to be created.
        formula_string (str): The formula to compute the new column.

    Returns:
        DataSource: The newly created DataSource.
    """
    try:
        # Step 1: Create a new derived DataSource
        new_datasource = DataSource.objects.create(
            project=parent_datasource.project,
            name=f"{parent_datasource.name}_with_{new_column_name}",
            description=f"Derived from {parent_datasource.name} with new column {new_column_name}",
            is_derived=True
        )

        # Step 2: Set the parent of the new DataSource
        new_datasource.parents.set([parent_datasource])

        # Step 3: Create a 'add_column_from_formula' Transformation for the new DataSource
        Transformation.objects.create(
            derived_datasource=new_datasource,
            order=1,
            operation_type='add_column_from_formula',
            parameters={
                'new_column_name': new_column_name,
                'formula_string': formula_string
            }
        )

        # Step 4: Return the new DataSource
        return new_datasource
    except Exception as e:
        raise ValueError(f"Error creating feature engineering recipe: {str(e)}")